#!/usr/bin/env python3
import requests
import json
import hashlib
import hmac
import time

# Mock HubSpot webhook data
webhook_data = [
    {
        "eventId": 12345,
        "subscriptionId": 67890,
        "portalId": 123456,
        "appId": 789012,
        "occurredAt": int(time.time() * 1000),
        "subscriptionType": "contact.creation",
        "attemptNumber": 0,
        "objectId": 98765,
        "changeSource": "CRM_UI",
        "propertyName": "email",
        "propertyValue": "john.doe@acme-corp.com"
    }
]

# HubSpot webhook secret (from backend .env)
webhook_secret = "510b7e09-4c1b-4ca0-80f3-1c18798a9685"

# Create proper HubSpot v3 signature
def create_hubspot_v3_signature(method, url, payload, timestamp, secret):
    payload_str = json.dumps(payload, separators=(',', ':'))
    source_string = method + url + payload_str + timestamp
    signature = hmac.new(
        secret.encode('utf-8'),
        source_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

# Test webhook
def test_webhook():
    url = "http://localhost:8000/webhooks/hubspot"
    timestamp = str(int(time.time() * 1000))
    
    signature = create_hubspot_v3_signature("POST", url, webhook_data, timestamp, webhook_secret)
    
    headers = {
        "Content-Type": "application/json",
        "x-hubspot-signature-v3": signature,
        "x-hubspot-request-timestamp": timestamp
    }
    
    print("Testing HubSpot webhook...")
    print(f"Payload: {json.dumps(webhook_data, indent=2)}")
    print(f"Signature: {signature}")
    
    response = requests.post(url, json=webhook_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response.status_code == 200

if __name__ == "__main__":
    test_webhook()
