# app/modules/backoffice/projects/models.py
"""
WorkmateOS - Backoffice Projects Models (IMPROVED)
Project management & ticket tracking

CHANGES:
- ✅ ProjectStatus Enum hinzugefügt
- ✅ TimeEntry import aus time_tracking (nicht projects!)
- ✅ Budget tracking properties
- ✅ Bessere Indizes
- ✅ Validation für Dates
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, Text, ForeignKey, Date, Numeric, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import UUIDMixin, TimestampMixin
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.backoffice.crm.models import Customer
    from app.modules.employees.models import Employee, Department
    from app.modules.backoffice.invoices.models import Invoice
    from app.modules.backoffice.finance.models import Expense
    from app.modules.backoffice.chat.models import ChatMessage
    from app.modules.backoffice.time_tracking.models import TimeEntry


# ============================================================================
# ENUMS
# ============================================================================

class ProjectStatus(str, Enum):
    """Status eines Projekts."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, Enum):
    """Priorität eines Projekts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ============================================================================
# MODELS
# ============================================================================

class Project(Base, UUIDMixin, TimestampMixin):
    """
    Represents a project or internal/external assignment.

    Projects belong to customers and can have time entries, expenses, and invoices.

    Attributes:
        title: Projekttitel
        project_number: Eindeutige Projektnummer (z.B. PRJ-2025-001)
        status: Aktueller Status (planning, active, on_hold, completed, cancelled)
        priority: Priorität des Projekts
        start_date: Projektstart
        end_date: Projektende (geplant)
        deadline: Finale Deadline
        budget: Projektbudget in EUR
        hourly_rate: Standard-Stundensatz für Abrechnung
        customer: Zugehöriger Kunde
        department: Zugehörige Abteilung
        project_manager: Verantwortlicher Projektmanager
        time_entries: Zeiterfassungen
        invoices: Rechnungen
        expenses: Ausgaben
    """
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_customer_id", "customer_id"),
        Index("ix_projects_department_id", "department_id"),
        Index("ix_projects_project_manager_id", "project_manager_id"),
        Index("ix_projects_status", "status"),
        Index("ix_projects_priority", "priority"),
        Index("ix_projects_start_date", "start_date"),
        Index("ix_projects_deadline", "deadline"),
        Index("ix_projects_project_number", "project_number"),
        CheckConstraint(
            "status IN ('planning', 'active', 'on_hold', 'completed', 'cancelled')",
            name="check_project_status_valid"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')",
            name="check_project_priority_valid"
        ),
        CheckConstraint("budget IS NULL OR budget >= 0", name="check_budget_positive"),
        CheckConstraint("hourly_rate IS NULL OR hourly_rate >= 0", name="check_hourly_rate_positive"),
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="check_end_after_start"
        ),
    )

    # Foreign Keys
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Zugehöriger Kunde"
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        index=True,
        comment="Zugehörige Abteilung"
    )
    project_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"),
        comment="Verantwortlicher Projektmanager"
    )

    # Basic Info
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Projekttitel"
    )
    project_number: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        comment="Eindeutige Projektnummer (z.B. PRJ-2025-001)"
    )

    # Status & Priority
    status: Mapped[str] = mapped_column(
        String(50),
        default=ProjectStatus.PLANNING.value,
        server_default=ProjectStatus.PLANNING.value,
        comment="Status: planning, active, on_hold, completed, cancelled"
    )
    priority: Mapped[str] = mapped_column(
        String(50),
        default=ProjectPriority.MEDIUM.value,
        server_default=ProjectPriority.MEDIUM.value,
        comment="Priorität: low, medium, high, urgent"
    )

    # Dates
    start_date: Mapped[date | None] = mapped_column(
        Date,
        comment="Projektstartdatum"
    )
    end_date: Mapped[date | None] = mapped_column(
        Date,
        comment="Geplantes Projektende"
    )
    deadline: Mapped[date | None] = mapped_column(
        Date,
        comment="Finale Deadline"
    )

    # Financial
    budget: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Gesamtbudget in EUR"
    )
    hourly_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Standard-Stundensatz für Abrechnung"
    )

    # Content
    description: Mapped[str | None] = mapped_column(
        Text,
        comment="Projektbeschreibung"
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment="Interne Notizen"
    )

    # Relationships
    customer: Mapped[Customer] = relationship(
        "Customer",
        back_populates="projects"
    )
    department: Mapped[Department | None] = relationship(
        "Department"
    )
    project_manager: Mapped[Employee | None] = relationship(
        "Employee",
        foreign_keys=[project_manager_id]
    )

    # WICHTIG: TimeEntry kommt aus time_tracking module!
    time_entries: Mapped[list[TimeEntry]] = relationship(
        "TimeEntry",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="TimeEntry.start_time.desc()"
    )

    # Invoices: SET NULL on delete (Rechnung bleibt, Projekt-Referenz verschwindet)
    invoices: Mapped[list[Invoice]] = relationship(
        "Invoice",
        back_populates="project",
        cascade="save-update, merge"
    )

    expenses: Mapped[list[Expense]] = relationship(
        "Expense",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    chat_messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at.desc()"
    )

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def is_active(self) -> bool:
        """Prüft ob Projekt aktiv ist."""
        return self.status == ProjectStatus.ACTIVE.value

    @property
    def is_completed(self) -> bool:
        """Prüft ob Projekt abgeschlossen ist."""
        return self.status == ProjectStatus.COMPLETED.value

    @property
    def is_overdue(self) -> bool:
        """
        Prüft ob Projekt überfällig ist.

        Returns:
            True wenn Deadline überschritten und nicht completed/cancelled
        """
        if self.deadline is None:
            return False
        if self.status in [ProjectStatus.COMPLETED.value, ProjectStatus.CANCELLED.value]:
            return False
        return date.today() > self.deadline

    @property
    def days_until_deadline(self) -> int | None:
        """
        Tage bis zur Deadline (negativ = überfällig).

        Returns:
            Anzahl Tage oder None wenn keine Deadline
        """
        if self.deadline is None:
            return None
        delta = self.deadline - date.today()
        return delta.days

    @property
    def total_hours_tracked(self) -> Decimal:
        """
        Summe aller erfassten Stunden.

        Returns:
            Gesamtstunden aus allen TimeEntries
        """
        total_minutes = sum(
            entry.duration_minutes or 0
            for entry in self.time_entries
        )
        return Decimal(total_minutes) / Decimal("60")

    @property
    def billable_hours(self) -> Decimal:
        """
        Summe aller abrechenbaren Stunden.

        Returns:
            Gesamtstunden aus billable TimeEntries
        """
        total_minutes = sum(
            entry.duration_minutes or 0
            for entry in self.time_entries
            if entry.billable
        )
        return Decimal(total_minutes) / Decimal("60")

    @property
    def total_revenue(self) -> Decimal:
        """
        Umsatz aus allen bezahlten Rechnungen.

        Returns:
            Summe aller paid invoices
        """
        from app.modules.backoffice.invoices.models import InvoiceStatus
        return sum(
            inv.total for inv in self.invoices
            if inv.status == InvoiceStatus.PAID.value
        )

    @property
    def total_expenses(self) -> Decimal:
        """
        Summe aller Ausgaben.

        Returns:
            Gesamtbetrag aller Expenses
        """
        return sum(
            exp.amount for exp in self.expenses
        )

    @property
    def budget_utilization(self) -> float | None:
        """
        Budget-Auslastung in Prozent.

        Returns:
            0.0 bis 100.0+ oder None wenn kein Budget definiert
        """
        if self.budget is None or self.budget <= Decimal("0.00"):
            return None

        # Kosten = Ausgaben + abrechenbare Stunden * Stundensatz
        costs = self.total_expenses
        if self.hourly_rate:
            costs += self.billable_hours * self.hourly_rate

        return float((costs / self.budget) * Decimal("100"))

    @property
    def profit_margin(self) -> Decimal | None:
        """
        Gewinnmarge (Umsatz - Kosten).

        Returns:
            Gewinn oder None wenn keine Daten
        """
        revenue = self.total_revenue
        costs = self.total_expenses

        if self.hourly_rate:
            costs += self.billable_hours * self.hourly_rate

        return revenue - costs if revenue > Decimal("0.00") else None

    @property
    def completion_percentage(self) -> float | None:
        """
        Fertigstellungsgrad basierend auf Zeitraum.

        Returns:
            0.0 bis 100.0 oder None wenn keine Dates
        """
        if not self.start_date or not self.end_date:
            return None

        today = date.today()
        if today < self.start_date:
            return 0.0
        if today > self.end_date:
            return 100.0

        total_days = (self.end_date - self.start_date).days
        elapsed_days = (today - self.start_date).days

        if total_days <= 0:
            return 100.0

        return round((elapsed_days / total_days) * 100, 1)

    def __repr__(self) -> str:
        return (
            f"<Project(id={self.id}, title='{self.title}', "
            f"status='{self.status}', customer={self.customer_id})>"
        )
