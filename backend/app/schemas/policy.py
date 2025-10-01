from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseSchema


class PolicyBase(BaseSchema):
    name: str
    description: Optional[str] = None
    version: Optional[str] = "1.0"
    is_active: Optional[bool] = True
    conditions: Dict[str, Any]  # JSON schema for conditions
    actions: Dict[str, Any]     # JSON schema for actions
    valid_to: Optional[datetime] = None
    created_by_id: Optional[str] = None


class PolicyCreate(PolicyBase):
    name: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]


class PolicyUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None
    valid_to: Optional[datetime] = None


class PolicyInDB(PolicyBase):
    id: str
    valid_from: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Policy(PolicyInDB):
    pass