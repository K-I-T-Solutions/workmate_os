"""
Compensation Models
Gehaltshistorie, Boni und Benefits.
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


class SalaryRecord(Base, UUIDMixin, TimestampMixin):
    """Gehaltshistorie eines Mitarbeiters"""
    __tablename__ = "hr_salary_records"
    __table_args__ = (
        Index("ix_salary_records_employee_id", "employee_id"),
        Index("ix_salary_records_effective_date", "effective_date"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    compensation_type: Mapped[str] = mapped_column(String(50), default="base_salary")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    created_by: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[created_by_id])


class Bonus(Base, UUIDMixin, TimestampMixin):
    """Bonus-Zahlung für einen Mitarbeiter"""
    __tablename__ = "hr_bonuses"
    __table_args__ = (
        Index("ix_bonuses_employee_id", "employee_id"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    bonus_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    created_by: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[created_by_id])


class Benefit(Base, UUIDMixin, TimestampMixin):
    """Benefit / Sachleistung für einen Mitarbeiter"""
    __tablename__ = "hr_benefits"
    __table_args__ = (
        Index("ix_benefits_employee_id", "employee_id"),
        Index("ix_benefits_is_active", "is_active"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    benefit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")
