"""
Leave Management Models
Urlaubsverwaltung und Abwesenheiten.
"""
from __future__ import annotations
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, Date, Numeric, Index, CheckConstraint, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin
from app.modules.hr.enums import LeaveType, LeaveStatus

if TYPE_CHECKING:
    from app.modules.employees.models import Employee


class LeavePolicy(Base, UUIDMixin, TimestampMixin):
    """
    Urlaubsregelungen für verschiedene Mitarbeitergruppen.

    Definiert jährliche Urlaubsansprüche und Regeln.
    """
    __tablename__ = "hr_leave_policies"
    __table_args__ = (
        Index("ix_leave_policy_name", "name"),
    )

    # Policy Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Ansprüche (Tage pro Jahr)
    vacation_days: Mapped[int] = mapped_column(default=20)
    sick_days: Mapped[int] = mapped_column(default=10)
    parental_days: Mapped[int] = mapped_column(default=0)

    # Regeln
    carryover_allowed: Mapped[bool] = mapped_column(default=True)
    max_carryover_days: Mapped[int] = mapped_column(default=5)

    # Aktiv
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    balances: Mapped[list["LeaveBalance"]] = relationship(
        "LeaveBalance",
        back_populates="policy",
        cascade="all, delete-orphan"
    )


class LeaveBalance(Base, UUIDMixin, TimestampMixin):
    """
    Urlaubssaldo-Tracking pro Mitarbeiter pro Jahr.
    """
    __tablename__ = "hr_leave_balances"
    __table_args__ = (
        Index("ix_leave_balance_employee_year", "employee_id", "year"),
        Index("ix_leave_balance_employee_id", "employee_id"),
    )

    # Jahr
    year: Mapped[int] = mapped_column(nullable=False)

    # Salden (in Tagen)
    vacation_total: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    vacation_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    vacation_remaining: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))

    sick_total: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    sick_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))

    other_total: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    other_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))

    # Foreign Keys
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    policy_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("hr_leave_policies.id", ondelete="SET NULL")
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")
    policy: Mapped["LeavePolicy"] = relationship("LeavePolicy", back_populates="balances")


class LeaveRequest(Base, UUIDMixin, TimestampMixin):
    """
    Mitarbeiter-Urlaubsanträge.

    Trackt alle Arten von Urlaub mit Genehmigungsworkflow.
    """
    __tablename__ = "hr_leave_requests"
    __table_args__ = (
        Index("ix_leave_request_employee_id", "employee_id"),
        Index("ix_leave_request_status", "status"),
        Index("ix_leave_request_start_date", "start_date"),
        Index("ix_leave_request_type", "leave_type"),
        CheckConstraint(
            "leave_type IN ('vacation', 'sick', 'unpaid', 'parental', 'bereavement', 'training', 'remote', 'other')",
            name="check_leave_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'cancelled')",
            name="check_leave_status"
        ),
    )

    # Urlaubs-Details
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Dauer
    total_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    half_day_start: Mapped[bool] = mapped_column(default=False)
    half_day_end: Mapped[bool] = mapped_column(default=False)

    # Antrags-Details
    reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    # Anhänge (Krankenscheine, Nachweise)
    attachment_path: Mapped[str | None] = mapped_column(Text)

    # Status & Genehmigung
    status: Mapped[str] = mapped_column(
        String(50),
        default=LeaveStatus.PENDING.value
    )
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL")
    )
    approved_date: Mapped[date | None] = mapped_column(Date)
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    # Foreign Keys
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    approved_by: Mapped["Employee"] = relationship("Employee", foreign_keys=[approved_by_id])
    absence_entries: Mapped[list["AbsenceCalendar"]] = relationship(
        "AbsenceCalendar",
        back_populates="leave_request",
        cascade="all, delete-orphan"
    )

    @property
    def is_approved(self) -> bool:
        """Prüft ob Antrag genehmigt ist"""
        return self.status == LeaveStatus.APPROVED.value

    @property
    def is_pending(self) -> bool:
        """Prüft ob Antrag pending ist"""
        return self.status == LeaveStatus.PENDING.value


class AbsenceCalendar(Base, UUIDMixin, TimestampMixin):
    """
    Team-Abwesenheitskalender.

    Aggregierte Ansicht aller genehmigten Urlaube für Team-Planung.
    """
    __tablename__ = "hr_absence_calendar"
    __table_args__ = (
        Index("ix_absence_calendar_date", "absence_date"),
        Index("ix_absence_calendar_employee_id", "employee_id"),
    )

    # Abwesenheits-Details
    absence_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_full_day: Mapped[bool] = mapped_column(default=True)
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Foreign Keys
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    leave_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hr_leave_requests.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")
    leave_request: Mapped["LeaveRequest"] = relationship("LeaveRequest", back_populates="absence_entries")
