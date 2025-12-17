"""
WorkmateOS - Time Tracking Models
ACHTUNG: TimeEntry ist bereits in projects/models.py definiert!

Dieses Modul könnte verwendet werden für:
- Aggregierte Zeit-Reports
- Time Tracking Templates
- Working Hour Rules
- Overtime Tracking

Falls du TimeEntry hier haben willst, lösche es aus projects/models.py!
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.misc.mixins import UUIDMixin, TimestampMixin

from app.core.settings.database import Base

if TYPE_CHECKING:
    from app.modules.employees.models import Employee
    from app.modules.backoffice.projects.models import Project



# === OPTION 1: TimeEntry hier (dann aus projects/models.py löschen!) ===
class TimeEntry(Base, UUIDMixin, TimestampMixin):
    """
    Tracks working sessions per employee and project.

    ACHTUNG: Wenn du diese Version verwendest, lösche TimeEntry aus projects/models.py!
    """

    __tablename__ = "time_entries"

    # Foreign Keys
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        comment="Optional - for internal time without project"
    )

    # Time Tracking
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime)

    # Duration in minutes (calculated or manual)
    duration_minutes: Mapped[int | None] = mapped_column(
        comment="Duration in minutes"
    )

    # Billing
    billable: Mapped[bool] = mapped_column(
        default=True,
        comment="Can this time be billed to customer?"
    )
    hourly_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Rate for this entry"
    )

    # Content
    note: Mapped[str | None] = mapped_column(Text, comment="What was worked on")
    task_type: Mapped[str | None] = mapped_column(
        String(100),
        comment="development, meeting, support, documentation, etc."
    )

    # Status
    is_approved: Mapped[bool] = mapped_column(default=False)
    is_invoiced: Mapped[bool] = mapped_column(default=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="time_entries")
    employee: Mapped["Employee"] = relationship("Employee")

    @property
    def duration_hours(self) -> float | None:
        """Get duration in hours"""
        if self.duration_minutes:
            return round(self.duration_minutes / 60, 2)
        elif self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 3600, 2)
        return None

    def __repr__(self) -> str:
        return f"<TimeEntry(id={self.id}, employee={self.employee_id}, duration={self.duration_hours}h)>"


# === OPTION 2: Zusätzliche Zeit-bezogene Models ===
class WorkingHoursTemplate(Base, UUIDMixin, TimestampMixin):
    """
    Defines standard working hours for employees.

    Kann verwendet werden für:
    - Überstunden-Berechnung
    - Urlaubsberechnung
    - Arbeitszeitkonten
    """

    __tablename__ = "working_hours_templates"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Weekly hours
    monday_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=8.0)
    tuesday_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=8.0)
    wednesday_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=8.0)
    thursday_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=8.0)
    friday_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=8.0)
    saturday_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0)
    sunday_hours: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0)

    # Or just total per week
    weekly_hours: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=40.0,
        comment="Total hours per week"
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee")

    def __repr__(self) -> str:
        return f"<WorkingHoursTemplate(employee={self.employee_id}, weekly={self.weekly_hours}h)>"
