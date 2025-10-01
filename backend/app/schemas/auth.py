from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: Optional[str] = "viewer"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
