from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from enum import Enum


class ExceptionType(str, Enum):
    DATA_VALIDATION = "DATA_VALIDATION"
    INTEGRATION_ERROR = "INTEGRATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


class ExceptionStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class ResolutionType(str, Enum):
    AUTO_REPAIR = "AUTO_REPAIR"
    MANUAL_FIX = "MANUAL_FIX"
    IGNORE = "IGNORE"
    ESCALATE = "ESCALATE"


class Exception(Base):
    __tablename__ = "exceptions"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    run_id: Mapped[str] = mapped_column(String)
    
    type: Mapped[ExceptionType] = mapped_column(String)
    status: Mapped[ExceptionStatus] = mapped_column(String, default=ExceptionStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Exception details
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String)

    # Resolution
    resolution_type: Mapped[Optional[ResolutionType]] = mapped_column(String)
    resolution_data: Mapped[Optional[dict]] = mapped_column(String)  # JSON data
    resolved_by_id: Mapped[Optional[str]] = mapped_column(String)

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(String)  # JSON data

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())