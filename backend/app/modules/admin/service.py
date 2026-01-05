"""
Admin Service - Business logic for Admin APIs
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Tuple, List
from datetime import datetime
from uuid import UUID

from app.modules.backoffice.invoices.models import AuditLog
from app.modules.admin.models import SystemSettings


async def get_audit_logs(
    db: Session,
    skip: int,
    limit: int,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> Tuple[List[AuditLog], int]:
    """
    Retrieve audit logs with filtering and pagination.

    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Max number of records to return
        user_id: Optional filter by user ID
        action: Optional filter by action type
        entity_type: Optional filter by entity type
        date_from: Optional filter from date
        date_to: Optional filter to date

    Returns:
        Tuple of (logs list, total count)
    """
    query = db.query(AuditLog)

    # Apply filters
    filters = []

    if user_id:
        filters.append(AuditLog.user_id == user_id)

    if action:
        filters.append(AuditLog.action == action.lower())

    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)

    if date_from:
        filters.append(AuditLog.timestamp >= date_from)

    if date_to:
        filters.append(AuditLog.timestamp <= date_to)

    if filters:
        query = query.filter(and_(*filters))

    # Get total count before pagination
    total = query.count()

    # Apply pagination and ordering
    logs = (
        query
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return logs, total


async def get_audit_log_by_id(db: Session, audit_log_id: UUID) -> Optional[AuditLog]:
    """
    Get a single audit log entry by ID.

    Args:
        db: Database session
        audit_log_id: UUID of the audit log

    Returns:
        AuditLog object or None if not found
    """
    return db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()


# ============================================================================
# System Settings Service Functions
# ============================================================================

async def get_or_create_settings(db: Session) -> SystemSettings:
    """
    Get system settings or create default settings if they don't exist.

    Singleton pattern: Only one SystemSettings record should exist.

    Args:
        db: Database session

    Returns:
        SystemSettings object
    """
    settings = db.query(SystemSettings).first()

    if not settings:
        # Create default settings
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


async def update_settings(db: Session, settings_update: dict) -> SystemSettings:
    """
    Update system settings.

    Args:
        db: Database session
        settings_update: Dictionary of fields to update

    Returns:
        Updated SystemSettings object
    """
    settings = await get_or_create_settings(db)

    # Update only provided fields
    for field, value in settings_update.items():
        if hasattr(settings, field):
            setattr(settings, field, value)

    settings.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(settings)

    return settings
