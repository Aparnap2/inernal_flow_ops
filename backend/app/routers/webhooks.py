import json
from fastapi import APIRouter, Request, Depends, HTTPException
from app.dependencies import verify_hubspot_signature
from app.services.workflow_engine import workflow_engine
from app.services.inngest_service import inngest_service
from app.services.logging_service import backend_logger
from app.middleware.error_handler import ErrorHandler, BusinessLogicError, ExternalServiceError
from typing import Dict, Any, List
from datetime import datetime
import hashlib
import uuid

router = APIRouter()

def create_event_envelope(hubspot_event: Dict[str, Any], source: str = "hubspot") -> Dict[str, Any]:
    """
    Create an event envelope according to the development plan specification
    """
    # Generate correlation ID based on event properties for deduplication
    correlation_source = f"{hubspot_event.get('subscriptionType', '')}-{hubspot_event.get('objectId', '')}-{hubspot_event.get('occurredAt', '')}"
    correlation_id = hashlib.sha256(correlation_source.encode()).hexdigest()[:16]
    
    # Determine object type from subscription type
    subscription_type = hubspot_event.get("subscriptionType", "")
    if subscription_type.startswith("contact."):
        object_type = "contact"
    elif subscription_type.startswith("company."):
        object_type = "company"
    elif subscription_type.startswith("deal."):
        object_type = "deal"
    else:
        object_type = "unknown"
    
    envelope = {
        "meta": {
            "eventId": str(hubspot_event.get("eventId", uuid.uuid4())),
            "source": source,
            "objectType": object_type,
            "objectId": str(hubspot_event.get("objectId", "")),
            "occurredAt": datetime.fromtimestamp(hubspot_event.get("occurredAt", 0) / 1000).isoformat(),
            "receivedAt": datetime.utcnow().isoformat(),
            "correlationId": correlation_id,
            "version": "1.0"
        },
        "required": {
            "eventType": hubspot_event.get("subscriptionType"),
            "objectId": str(hubspot_event.get("objectId", "")),
            "occurredAt": hubspot_event.get("occurredAt"),
        },
        "payload": hubspot_event,
        "rawPayloadRef": f"hubspot_event_{hubspot_event.get('eventId', 'unknown')}"
    }
    
    return envelope

@router.post(
    "/hubspot",
    status_code=202,  # Accepted
    dependencies=[Depends(verify_hubspot_signature)],
    tags=["Webhooks"],
    summary="Receive and Enqueue HubSpot Webhooks",
)
async def hubspot_webhook_endpoint(request: Request):
    """
    This endpoint receives webhooks from HubSpot, verifies the signature,
    creates event envelopes, and triggers appropriate workflows via Inngest.
    """
    try:
        events = await request.json()
        if not isinstance(events, list):
            backend_logger.warn(
                "Invalid webhook payload format - expected JSON array",
                context={"payload_type": type(events)},
                component="WebhookEndpoint"
            )
            raise HTTPException(status_code=400, detail="Request body must be a JSON array of events")

        processed_events = []
        
        backend_logger.info(
            f"Received {len(events)} events from HubSpot. Processing with event envelopes.",
            context={"event_count": len(events)},
            component="WebhookEndpoint"
        )
        
        for event in events:
            try:
                # Create event envelope
                envelope = create_event_envelope(event)
                
                # Process via Inngest service
                result = await inngest_service.process_webhook_event(envelope)
                
                processed_events.append({
                    "eventId": envelope["meta"]["eventId"],
                    "correlationId": envelope["meta"]["correlationId"],
                    "status": result["status"],
                    "workflow": result.get("workflow_name", "none")
                })
                
                # Add to Redis queue for local processing as backup
                await workflow_engine.redis_service.queue_push("hubspot_event_queue", envelope)
                
            except Exception as e:
                backend_logger.error(
                    f"Failed to process individual HubSpot event",
                    context={
                        "event": event,
                        "error": str(e),
                        "error_type": type(e).__name__
                    },
                    component="WebhookEndpoint",
                    exception=e
                )
                # Continue processing other events even if one fails
                continue

        backend_logger.info(
            f"Successfully processed {len(processed_events)} out of {len(events)} HubSpot events",
            context={
                "total_events": len(events),
                "processed_events": len(processed_events),
                "success_rate": len(processed_events) / len(events) if events else 0
            },
            component="WebhookEndpoint"
        )
        
        return {
            "status": "ok", 
            "message": f"Processed {len(events)} events with event envelopes.",
            "processed_events": processed_events
        }
    except json.JSONDecodeError as e:
        backend_logger.error(
            "Failed to parse JSON from HubSpot webhook",
            context={"error": str(e)},
            component="WebhookEndpoint",
            exception=e
        )
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        backend_logger.error(
            "Unexpected error processing HubSpot webhook",
            context={"error": str(e)},
            component="WebhookEndpoint",
            exception=e
        )
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")
