"""
Onboarding Models
Templates und Prozesse für das Mitarbeiter-Onboarding.
"""
from __future__ import annotations
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, ForeignKey, Date, Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.employees.models import Employee, Department


class OnboardingTemplate(Base, UUIDMixin, TimestampMixin):
    """Vorlage für Onboarding-Prozess"""
    __tablename__ = "hr_onboarding_templates"
    __table_args__ = (
        Index("ix_onboarding_templates_is_active", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    tasks: Mapped[list["OnboardingTemplateTask"]] = relationship(
        "OnboardingTemplateTask",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="OnboardingTemplateTask.order_index"
    )
    processes: Mapped[list["OnboardingProcess"]] = relationship(
        "OnboardingProcess",
        back_populates="template"
    )
    department: Mapped[Optional["Department"]] = relationship("Department")


class OnboardingTemplateTask(Base, UUIDMixin, TimestampMixin):
    """Aufgabe in einem Onboarding-Template"""
    __tablename__ = "hr_onboarding_template_tasks"
    __table_args__ = (
        Index("ix_onboarding_template_tasks_template_id", "template_id"),
    )

    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hr_onboarding_templates.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    responsible_role: Mapped[Optional[str]] = mapped_column(String(100))
    due_days_offset: Mapped[int] = mapped_column(Integer, default=0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    template: Mapped["OnboardingTemplate"] = relationship("OnboardingTemplate", back_populates="tasks")


class OnboardingProcess(Base, UUIDMixin, TimestampMixin):
    """Aktiver Onboarding-Prozess für einen Mitarbeiter"""
    __tablename__ = "hr_onboarding_processes"
    __table_args__ = (
        Index("ix_onboarding_processes_employee_id", "employee_id"),
        Index("ix_onboarding_processes_status", "status"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("hr_onboarding_templates.id", ondelete="SET NULL")
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    completed_at: Mapped[Optional[date]] = mapped_column(Date)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")
    template: Mapped[Optional["OnboardingTemplate"]] = relationship(
        "OnboardingTemplate", back_populates="processes"
    )
    tasks: Mapped[list["OnboardingProcessTask"]] = relationship(
        "OnboardingProcessTask",
        back_populates="process",
        cascade="all, delete-orphan",
        order_by="OnboardingProcessTask.order_index"
    )


class OnboardingProcessTask(Base, UUIDMixin, TimestampMixin):
    """Konkrete Aufgabe in einem laufenden Onboarding-Prozess"""
    __tablename__ = "hr_onboarding_process_tasks"
    __table_args__ = (
        Index("ix_onboarding_process_tasks_process_id", "process_id"),
    )

    process_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hr_onboarding_processes.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    responsible_role: Mapped[Optional[str]] = mapped_column(String(100))
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    completed_at: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    process: Mapped["OnboardingProcess"] = relationship("OnboardingProcess", back_populates="tasks")
