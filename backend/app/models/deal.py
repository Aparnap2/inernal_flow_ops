from sqlalchemy import String, DateTime, Numeric, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    hubspot_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    stage: Mapped[str] = mapped_column(String)
    amount: Mapped[Optional[float]] = mapped_column(Numeric(precision=15, scale=2))
    close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    probability: Mapped[Optional[float]] = mapped_column(Float)
    last_modified_date: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Foreign key references
    account_id: Mapped[Optional[str]] = mapped_column(String)
    contact_id: Mapped[Optional[str]] = mapped_column(String)

    # JSON columns for metadata
    properties: Mapped[Optional[dict]] = mapped_column(String)  # JSON data
    custom_fields: Mapped[Optional[dict]] = mapped_column(String)  # JSON data