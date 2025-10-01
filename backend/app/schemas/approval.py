from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema


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


class ApprovalBase(BaseSchema):
    run_id: str
    type: ApprovalType
    title: str
    description: Optional[str] = None
    risk_level: Optional[RiskLevel] = RiskLevel.LOW
    policy_id: Optional[str] = None
    policy_snapshot: Optional[Dict[str, Any]] = None
    approver_id: Optional[str] = None
    decision: Optional[bool] = None
    justification: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ApprovalCreate(ApprovalBase):
    # Required fields for creating an approval
    run_id: str
    type: ApprovalType
    title: str


class ApprovalUpdate(BaseSchema):
    status: Optional[ApprovalStatus] = None
    approver_id: Optional[str] = None
    decision: Optional[bool] = None
    justification: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ApprovalInDB(ApprovalBase):
    id: str
    status: ApprovalStatus
    requested_at: datetime
    responded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Approval(ApprovalInDB):
    pass