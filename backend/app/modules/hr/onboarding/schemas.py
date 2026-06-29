"""
Onboarding Schemas
Pydantic Schemas für Onboarding-Templates und Prozesse.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================================
# TEMPLATE SCHEMAS
# ============================================================================

class TemplateTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    responsible_role: Optional[str] = None
    due_days_offset: int = 0
    order_index: int = 0
    is_required: bool = True


class TemplateTaskResponse(BaseModel):
    id: UUID
    template_id: UUID
    title: str
    description: Optional[str] = None
    responsible_role: Optional[str] = None
    due_days_offset: int
    order_index: int
    is_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: Optional[UUID] = None
    is_active: bool = True
    tasks: list[TemplateTaskCreate] = []


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    department_id: Optional[UUID] = None
    is_active: bool
    tasks: list[TemplateTaskResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PROCESS SCHEMAS
# ============================================================================

class ProcessTaskResponse(BaseModel):
    id: UUID
    process_id: UUID
    title: str
    description: Optional[str] = None
    responsible_role: Optional[str] = None
    due_date: Optional[date] = None
    status: str
    completed_at: Optional[date] = None
    notes: Optional[str] = None
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProcessCreate(BaseModel):
    employee_id: UUID
    template_id: UUID
    start_date: date


class ProcessResponse(BaseModel):
    id: UUID
    employee_id: UUID
    template_id: Optional[UUID] = None
    start_date: date
    status: str
    completed_at: Optional[date] = None
    tasks: list[ProcessTaskResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TASK STATUS UPDATE
# ============================================================================

class TaskStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
