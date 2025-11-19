# app/modules/backoffice/time_tracking/schemas.py
from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel


class TimeEntryBase(BaseModel):
    project_id: uuid.UUID
    employee_id: uuid.UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    note: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    end_time: Optional[datetime] = None
    note: Optional[str] = None


class TimeEntryResponse(TimeEntryBase):
    id: uuid.UUID
    duration: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
