from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema


class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class RunStepBase(BaseSchema):
    run_id: str
    step_name: str
    status: Optional[StepStatus] = StepStatus.PENDING
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = 0


class RunStepCreate(RunStepBase):
    pass


class RunStepUpdate(BaseSchema):
    status: Optional[StepStatus] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None


class RunStepInDB(RunStepBase):
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RunStep(RunStepInDB):
    pass