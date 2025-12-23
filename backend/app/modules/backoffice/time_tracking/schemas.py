# app/modules/backoffice/time_tracking/schemas.py
from datetime import datetime
from typing import Optional
from decimal import Decimal
import uuid
from pydantic import BaseModel


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

    class Config:
        from_attributes = True
