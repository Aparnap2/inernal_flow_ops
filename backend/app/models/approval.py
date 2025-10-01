from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from enum import Enum


class ApprovalType(str, Enum):
    PROCUREMENT = "PROCUREMENT"
    RISK_THRESHOLD = "RISK_THRESHOLD"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    POLICY_EXCEPTION = "POLICY_EXCEPTION"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    run_id: Mapped[str] = mapped_column(String)
    
    type: Mapped[ApprovalType] = mapped_column(String)
    status: Mapped[ApprovalStatus] = mapped_column(String, default=ApprovalStatus.PENDING)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Approval context
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    risk_level: Mapped[RiskLevel] = mapped_column(String, default=RiskLevel.LOW)

    # Policy context
    policy_id: Mapped[Optional[str]] = mapped_column(String)
    policy_snapshot: Mapped[Optional[dict]] = mapped_column(String)  # JSON data

    # Response
    approver_id: Mapped[Optional[str]] = mapped_column(String)
    decision: Mapped[Optional[bool]] = mapped_column()
    justification: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(String)  # JSON data

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())