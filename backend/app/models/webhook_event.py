from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    IGNORED = "IGNORED"


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    hubspot_event_id: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String)
    object_type: Mapped[str] = mapped_column(String)
    object_id: Mapped[str] = mapped_column(String)
    correlation_id: Mapped[str] = mapped_column(String)

    # Event data
    payload: Mapped[dict] = mapped_column(String)  # JSON data
    signature: Mapped[Optional[str]] = mapped_column(String)

    # Processing status
    status: Mapped[EventStatus] = mapped_column(String, default=EventStatus.RECEIVED)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    occurred_at: Mapped[datetime] = mapped_column(DateTime)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())