from sqlalchemy import String, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String, default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Policy rules (stored as JSON)
    conditions: Mapped[dict] = mapped_column(String)  # JSON schema for conditions
    actions: Mapped[dict] = mapped_column(String)  # JSON schema for actions

    # Temporal tracking
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_by_id: Mapped[Optional[str]] = mapped_column(String)