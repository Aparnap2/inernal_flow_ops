from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseSchema


class DealBase(BaseSchema):
    hubspot_id: str
    name: str
    stage: str
    amount: Optional[float] = None
    close_date: Optional[datetime] = None
    probability: Optional[float] = None
    last_modified_date: datetime
    account_id: Optional[str] = None
    contact_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseSchema):
    name: Optional[str] = None
    stage: Optional[str] = None
    amount: Optional[float] = None
    close_date: Optional[datetime] = None
    probability: Optional[float] = None
    last_modified_date: Optional[datetime] = None
    account_id: Optional[str] = None
    contact_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class DealInDB(DealBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Deal(DealInDB):
    pass