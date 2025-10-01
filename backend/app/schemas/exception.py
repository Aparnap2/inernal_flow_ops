from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema


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


class ExceptionBase(BaseSchema):
    run_id: str
    type: ExceptionType
    title: str
    description: str
    error_code: Optional[str] = None
    resolution_type: Optional[ResolutionType] = None
    resolution_data: Optional[Dict[str, Any]] = None
    resolved_by_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ExceptionCreate(ExceptionBase):
    # Required fields for creating an exception
    run_id: str
    type: ExceptionType
    title: str
    description: str


class ExceptionUpdate(BaseSchema):
    status: Optional[ExceptionStatus] = None
    resolved_at: Optional[datetime] = None
    resolution_type: Optional[ResolutionType] = None
    resolution_data: Optional[Dict[str, Any]] = None
    resolved_by_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ExceptionInDB(ExceptionBase):
    id: str
    status: ExceptionStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class Exception(ExceptionInDB):
    pass