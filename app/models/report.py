"""
MediScribe AI — Database Models.

Defines the MedicalReport ORM model.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class ReportStatus(str, enum.Enum):
    """Lifecycle status of a medical report."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class MedicalReport(Base):
    """Stores a generated medical report."""

    __tablename__ = "medical_reports"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    patient_id: str = Column(String(100), nullable=False, index=True)
    raw_transcription: str = Column(Text, nullable=False)
    structured_report: dict = Column(JSON, nullable=True)
    status: str = Column(
        Enum(ReportStatus),
        default=ReportStatus.PENDING,
        nullable=False,
    )
    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<MedicalReport(id={self.id}, patient={self.patient_id}, "
            f"status={self.status})>"
        )
