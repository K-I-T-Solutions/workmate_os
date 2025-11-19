"""
WorkmateOS - Reminders CRUD Operations
Database operations for reminder system
"""
from datetime import date
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.modules.reminders.models import Reminder
from app.modules.reminders.schemas import ReminderCreate, ReminderUpdate


def get_reminder(db: Session, reminder_id: UUID) -> Optional[Reminder]:
    """Get reminder by ID"""
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()


def get_reminders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[UUID] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    overdue_only: bool = False
) -> tuple[list[Reminder], int]:
    """
    Get reminders with filtering and pagination
    Returns: (reminders list, total count)
    """
    query = db.query(Reminder)
    
    # Apply filters
    if owner_id:
        query = query.filter(Reminder.owner_id == owner_id)
    
    if status:
        query = query.filter(Reminder.status == status)
    
    if priority:
        query = query.filter(Reminder.priority == priority)
    
    if overdue_only:
        today = date.today()
        query = query.filter(
            Reminder.due_date < today,
            Reminder.status != "done"
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order
    reminders = query.order_by(Reminder.due_date.asc()).offset(skip).limit(limit).all()
    
    return reminders, total


def create_reminder(db: Session, reminder: ReminderCreate) -> Reminder:
    """Create new reminder"""
    db_reminder = Reminder(**reminder.model_dump())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def update_reminder(
    db: Session,
    reminder_id: UUID,
    reminder_update: ReminderUpdate
) -> Optional[Reminder]:
    """Update reminder"""
    db_reminder = get_reminder(db, reminder_id)
    if db_reminder is None:
        return None
    
    update_data = reminder_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reminder, field, value)
    
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def delete_reminder(db: Session, reminder_id: UUID) -> bool:
    """Delete reminder"""
    db_reminder = get_reminder(db, reminder_id)
    if db_reminder is None:
        return False
    
    db.delete(db_reminder)
    db.commit()
    return True


def mark_as_done(db: Session, reminder_id: UUID) -> Optional[Reminder]:
    """Mark reminder as done"""
    db_reminder = get_reminder(db, reminder_id)
    if db_reminder is None:
        return None
    
    db_reminder.status = "done"  # type: ignore[assignment]
    db.commit()
    db.refresh(db_reminder)
    return db_reminder