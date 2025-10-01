from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Mock user database for testing
MOCK_USERS = {
    "admin@example.com": {
        "id": 1,
        "email": "admin@example.com", 
        "name": "Admin User",
        "password": "password123",  # In production, this would be hashed
        "role": "admin",
        "is_active": True
    },
    "operator@example.com": {
        "id": 2,
        "email": "operator@example.com",
        "name": "Operator User", 
        "password": "password123",
        "role": "operator",
        "is_active": True
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest):
    user = MOCK_USERS.get(credentials.email)
    
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Mock JWT token
    token = f"mock_jwt_token_for_{user['id']}"
    
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            is_active=user["is_active"]
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user():
    # Mock current user for testing
    return UserResponse(
        id=1,
        email="admin@example.com",
        name="Admin User",
        role="admin",
        is_active=True
    )
