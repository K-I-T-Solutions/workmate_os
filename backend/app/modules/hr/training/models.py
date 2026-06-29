"""
Training & Certifications Models
Schulungen, Teilnahmen und Zertifizierungen.
"""
from __future__ import annotations
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, ForeignKey, Date, Numeric, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.employees.models import Employee


class TrainingCourse(Base, UUIDMixin, TimestampMixin):
    """Schulungskurs / Training-Angebot"""
    __tablename__ = "hr_training_courses"
    __table_args__ = (
        Index("ix_training_courses_is_active", "is_active"),
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    provider: Mapped[Optional[str]] = mapped_column(String(100))
    course_type: Mapped[str] = mapped_column(String(50), nullable=False, default="internal")
    duration_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1))
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    participants: Mapped[list["TrainingParticipant"]] = relationship(
        "TrainingParticipant",
        back_populates="course",
        cascade="all, delete-orphan"
    )


class TrainingParticipant(Base, UUIDMixin, TimestampMixin):
    """Schulungsteilnahme eines Mitarbeiters"""
    __tablename__ = "hr_training_participants"
    __table_args__ = (
        Index("ix_training_participants_employee_id", "employee_id"),
        Index("ix_training_participants_course_id", "course_id"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hr_training_courses.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="planned")
    enrolled_at: Mapped[date] = mapped_column(Date, nullable=False)
    completed_at: Mapped[Optional[date]] = mapped_column(Date)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    course: Mapped["TrainingCourse"] = relationship("TrainingCourse", back_populates="participants")
    employee: Mapped["Employee"] = relationship("Employee")


class HRCertification(Base, UUIDMixin, TimestampMixin):
    """Zertifizierung eines Mitarbeiters"""
    __tablename__ = "hr_certifications"
    __table_args__ = (
        Index("ix_certifications_employee_id", "employee_id"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer: Mapped[Optional[str]] = mapped_column(String(100))
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    certificate_url: Mapped[Optional[str]] = mapped_column(String(500))
    skill_level: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")
