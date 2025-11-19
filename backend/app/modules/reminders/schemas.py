"""
WorkmateOS - Reminders Schemas
Pydantic models for reminder/notification system
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class ReminderBase(BaseModel):
    """Base reminder fields"""
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: str = Field(default="medium", description="low, medium, high, critical")
    linked_entity_type: Optional[str] = Field(None, description="Document, Ticket, Employee, etc.")
    linked_entity_id: Optional[UUID] = None


class ReminderCreate(ReminderBase):
    """Create new reminder"""
    owner_id: UUID


class ReminderUpdate(BaseModel):
    """Update existing reminder"""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = Field(None, description="open, done, overdue")
    notified: Optional[bool] = None


class ReminderResponse(ReminderBase):
    """Reminder response with all fields"""
    id: UUID
    owner_id: UUID
    status: str = Field(default="open")
    created_at: Optional[datetime] = None
    notified: bool = Field(default=False)
    
    # Helper fields
    is_overdue: Optional[bool] = Field(None, description="Calculated field")
    days_until_due: Optional[int] = Field(None, description="Calculated field")
    
    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """Paginated list of reminders"""
    total: int
    page: int
    page_size: int
    reminders: list[ReminderResponse]