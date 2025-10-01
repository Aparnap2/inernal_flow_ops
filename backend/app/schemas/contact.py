from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseSchema


class ContactBase(BaseSchema):
    hubspot_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    lifecycle_stage: Optional[str] = None
    last_modified_date: datetime
    account_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseSchema):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    lifecycle_stage: Optional[str] = None
    last_modified_date: Optional[datetime] = None
    account_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ContactInDB(ContactBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Contact(ContactInDB):
    pass