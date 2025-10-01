from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
from datetime import datetime
from enum import Enum


class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class RunStep(Base):
    __tablename__ = "run_steps"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    run_id: Mapped[str] = mapped_column(String)
    
    step_name: Mapped[str] = mapped_column(String)
    status: Mapped[StepStatus] = mapped_column(String, default=StepStatus.PENDING)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Step data
    input_data: Mapped[Optional[dict]] = mapped_column(String)  # JSON data
    output_data: Mapped[Optional[dict]] = mapped_column(String)  # JSON data

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())