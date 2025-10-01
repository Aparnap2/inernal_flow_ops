from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RunBase(BaseSchema):
    correlation_id: str
    workflow_id: str
    status: Optional[RunStatus] = RunStatus.PENDING
    event_type: str
    object_type: str
    object_id: str
    created_by_id: Optional[str] = None
    account_id: Optional[str] = None
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    checkpoint_data: Optional[Dict[str, Any]] = None


class RunCreate(RunBase):
    pass


class RunUpdate(BaseSchema):
    status: Optional[RunStatus] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    checkpoint_data: Optional[Dict[str, Any]] = None


class RunInDB(RunBase):
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Run(RunInDB):
    pass