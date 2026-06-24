"""
WorkmateOS - Reminders API Routes
REST endpoints for reminder/notification system
"""
from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.reminders import crud, schemas

router = APIRouter(prefix="/reminders", tags=["Reminders"])


def calculate_days_until_due(due_date: Optional[date]) -> Optional[int]:
    """Calculate days until due date"""
    if due_date is None:
        return None
    today = date.today()
    delta = (due_date - today).days
    return delta


# ============================================================================
# REMINDER ENDPOINTS
# ============================================================================

@router.get("", response_model=schemas.ReminderListResponse)
def list_reminders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    owner_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None, description="open, done, overdue"),
    priority: Optional[str] = Query(None, description="low, medium, high, critical"),
    overdue_only: bool = Query(False, description="Show only overdue reminders"),
    db: Session = Depends(get_db)
):
    """
    Get list of reminders with filtering and pagination
    
    - **owner_id**: Filter by owner
    - **status**: Filter by status (open, done, overdue)
    - **priority**: Filter by priority (low, medium, high, critical)
    - **overdue_only**: Show only overdue reminders
    """
    reminders, total = crud.get_reminders(
        db,
        skip=skip,
        limit=limit,
        owner_id=owner_id,
        status=status,
        priority=priority,
        overdue_only=overdue_only
    )
    
    # Add calculated fields
    today = date.today()
    for reminder in reminders:
        if reminder.due_date is not None:
            reminder.days_until_due = calculate_days_until_due(reminder.due_date)  # type: ignore[attr-defined]
            reminder.is_overdue = reminder.due_date < today and reminder.status != "done"  # type: ignore[attr-defined]
    
    page = (skip // limit) + 1
    
    return {
        "total": total,
        "page": page,
        "page_size": limit,
        "reminders": reminders
    }


@router.get("/{reminder_id}", response_model=schemas.ReminderResponse)
def get_reminder(
    reminder_id: UUID,
    db: Session = Depends(get_db)
):
    """Get reminder by ID"""
    reminder = crud.get_reminder(db, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Add calculated fields
    if reminder.due_date is not None:
        reminder.days_until_due = calculate_days_until_due(reminder.due_date)  # type: ignore[attr-defined]
        reminder.is_overdue = reminder.due_date < date.today() and reminder.status != "done"  # type: ignore[attr-defined]
    
    return reminder


@router.post("", response_model=schemas.ReminderResponse, status_code=201)
def create_reminder(
    reminder: schemas.ReminderCreate,
    db: Session = Depends(get_db)
):
    """
    Create new reminder
    
    **Required fields:**
    - title: Reminder title
    - owner_id: UUID of the owner
    
    **Optional fields:**
    - description: Detailed description
    - due_date: When the reminder is due
    - priority: low, medium, high, critical (default: medium)
    - linked_entity_type: Type of linked entity (Document, Ticket, etc.)
    - linked_entity_id: UUID of linked entity
    """
    return crud.create_reminder(db, reminder)


@router.put("/{reminder_id}", response_model=schemas.ReminderResponse)
def update_reminder(
    reminder_id: UUID,
    reminder_update: schemas.ReminderUpdate,
    db: Session = Depends(get_db)
):
    """Update reminder"""
    reminder = crud.update_reminder(db, reminder_id, reminder_update)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.post("/{reminder_id}/mark-done", response_model=schemas.ReminderResponse)
def mark_reminder_done(
    reminder_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark reminder as done"""
    reminder = crud.mark_as_done(db, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete reminder"""
    success = crud.delete_reminder(db, reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return None