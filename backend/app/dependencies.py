import hmac
import hashlib
import time
from fastapi import Request, Header, HTTPException
from app.config import settings

async def verify_hubspot_signature(
    request: Request,
    x_hubspot_request_timestamp: str = Header(None),
    x_hubspot_signature_v3: str = Header(None),
):
    """
    Dependency to verify the HubSpot webhook signature (v3).
    See: https://developers.hubspot.com/docs/api/webhooks/validating-requests
    """
    # If the secret is not set, we can't verify. This is useful for local dev.
    if not settings.HUBSPOT_WEBHOOK_SECRET or settings.HUBSPOT_WEBHOOK_SECRET == "your-webhook-secret":
        print("WARNING: HubSpot webhook secret is not set. Skipping signature verification.")
        return

    if not x_hubspot_signature_v3 or not x_hubspot_request_timestamp:
        raise HTTPException(status_code=400, detail="Missing HubSpot signature headers")

    # Check timestamp (5 minutes tolerance)
    current_time_ms = int(time.time() * 1000)
    if abs(current_time_ms - int(x_hubspot_request_timestamp)) > 300000:
        raise HTTPException(status_code=401, detail="Request timestamp too old")

    body = await request.body()
    
    # V3 signature uses the method, full URI, body, and timestamp
    # Note: HubSpot docs say URI, not just path. We use the full URL for safety.
    source_string = request.method + str(request.url) + body.decode('utf-8') + x_hubspot_request_timestamp
    
    hashed_string = hmac.new(
        settings.HUBSPOT_WEBHOOK_SECRET.encode('utf-8'),
        source_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(hashed_string, x_hubspot_signature_v3):
        raise HTTPException(status_code=401, detail="Invalid signature")
