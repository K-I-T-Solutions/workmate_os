"""
WorkmateOS - Backoffice Projects Models
Project management (WITHOUT TimeEntry - that's in time_tracking module!)
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Text, ForeignKey, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.mixins import UUIDMixin, TimestampMixin
from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.backoffice.crm.models import Customer
    from app.modules.employees.models import Employee, Department
    from app.modules.backoffice.finance.models import Invoice, Expense
    from app.modules.backoffice.chat.models import ChatMessage
    from app.modules.backoffice.time_tracking.models import TimeEntry





# === Models ===
class Project(Base, UUIDMixin, TimestampMixin):
    """
    Represents a project or internal/external assignment.
    
    Projects belong to customers and can have time entries, expenses, and invoices.
    """

    __tablename__ = "projects"

    # Foreign Keys
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        index=True
    )
    project_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"),
        comment="Responsible project manager"
    )

    # Basic Info
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    project_number: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        comment="Unique project identifier like PRJ-2025-001"
    )
    
    # Status & Dates
    status: Mapped[str] = mapped_column(
        String(50),
        default="planning",
        comment="planning, active, on_hold, completed, cancelled"
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    deadline: Mapped[date | None] = mapped_column(Date, comment="Final deadline")
    
    # Financial
    budget: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Total project budget in EUR"
    )
    hourly_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Default hourly rate for billing"
    )
    
    # Content
    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text, comment="Internal notes")

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="projects")
    department: Mapped["Department"] = relationship("Department")
    project_manager: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[project_manager_id]
    )
    
    # TimeEntry ist in time_tracking module!
    time_entries: Mapped[list["TimeEntry"]] = relationship(
        "TimeEntry",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, title='{self.title}', status='{self.status}')>"