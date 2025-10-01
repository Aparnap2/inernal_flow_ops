from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from enum import Enum


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    correlation_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String)
    status: Mapped[RunStatus] = mapped_column(String, default=RunStatus.PENDING)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Context
    event_type: Mapped[str] = mapped_column(String)
    object_type: Mapped[str] = mapped_column(String)
    object_id: Mapped[str] = mapped_column(String)

    # Foreign key references
    created_by_id: Mapped[Optional[str]] = mapped_column(String)
    account_id: Mapped[Optional[str]] = mapped_column(String)
    contact_id: Mapped[Optional[str]] = mapped_column(String)
    deal_id: Mapped[Optional[str]] = mapped_column(String)

    # JSON columns for metadata
    payload: Mapped[Optional[dict]] = mapped_column(String)  # JSON data
    checkpoint_data: Mapped[Optional[dict]] = mapped_column(String)  # JSON data

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())