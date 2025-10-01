from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema


class EventStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    IGNORED = "IGNORED"


class WebhookEventBase(BaseSchema):
    hubspot_event_id: Optional[str] = None
    event_type: str
    object_type: str
    object_id: str
    correlation_id: str
    payload: Dict[str, Any]  # JSON data
    signature: Optional[str] = None


class WebhookEventCreate(WebhookEventBase):
    event_type: str
    object_type: str
    object_id: str
    correlation_id: str
    payload: Dict[str, Any]


class WebhookEventUpdate(BaseSchema):
    status: Optional[EventStatus] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None


class WebhookEventInDB(WebhookEventBase):
    id: str
    status: EventStatus
    occurred_at: datetime
    received_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookEvent(WebhookEventInDB):
    pass