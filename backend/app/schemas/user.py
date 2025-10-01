from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
from .base import BaseSchema


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class UserBase(BaseSchema):
    email: EmailStr
    name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseSchema):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserInDBWithPassword(UserInDB):
    password: str

    class Config:
        from_attributes = True