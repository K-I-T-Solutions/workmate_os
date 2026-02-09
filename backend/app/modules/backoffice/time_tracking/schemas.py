# app/modules/backoffice/time_tracking/schemas.py
from datetime import datetime
from typing import Optional
from decimal import Decimal
import uuid

from pydantic import BaseModel, ConfigDict


# ─── Time Entry Schemas ──────────────────────────────────────

class TimeEntryBase(BaseModel):
    employee_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    note: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    task_type: Optional[str] = None
    billable: bool = True
    hourly_rate: Optional[Decimal] = None


class TimeEntryUpdate(BaseModel):
    end_time: Optional[datetime] = None
    note: Optional[str] = None
    task_type: Optional[str] = None
    billable: Optional[bool] = None
    hourly_rate: Optional[Decimal] = None


class TimeEntryResponse(TimeEntryBase):
    id: uuid.UUID
    duration_minutes: Optional[int]
    task_type: Optional[str]
    billable: bool
    hourly_rate: Optional[Decimal]
    is_approved: bool
    is_invoiced: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ─── Statistics Schemas ──────────────────────────────────────

class ProjectHours(BaseModel):
    project_id: str
    hours: float


class TaskTypeHours(BaseModel):
    task_type: str
    hours: float


class TimeTrackingStatsResponse(BaseModel):
    total_hours_today: float
    total_hours_week: float
    total_hours_month: float
    total_entries: int
    billable_hours: float
    non_billable_hours: float
    hours_by_project: list[ProjectHours]
    hours_by_task_type: list[TaskTypeHours]


# ─── Weekly Summary Schemas ──────────────────────────────────

class DaySummary(BaseModel):
    date: str
    hours: float
    entries_count: int


class WeeklySummaryResponse(BaseModel):
    employee_id: uuid.UUID
    week: str
    total_hours: float
    daily_breakdown: list[DaySummary]
