from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class BaseSchema(BaseModel):
    """Base schema with common fields for all schemas."""
    pass


class BaseResponse(BaseSchema):
    """Base response schema with common fields."""
    success: bool = True
    message: Optional[str] = None


class BasePaginatedResponse(BaseResponse):
    """Base response schema with pagination fields."""
    page: int = 1
    limit: int = 10
    total: int = 0
    pages: int = 0