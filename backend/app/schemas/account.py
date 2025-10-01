from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseSchema


class AccountBase(BaseSchema):
    hubspot_id: str
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    lifecycle_stage: Optional[str] = None
    last_modified_date: datetime
    properties: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseSchema):
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    lifecycle_stage: Optional[str] = None
    last_modified_date: Optional[datetime] = None
    properties: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class AccountInDB(AccountBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Account(AccountInDB):
    pass