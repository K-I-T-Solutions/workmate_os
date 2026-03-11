"""
Admin Service - Business logic for Admin APIs
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Tuple, List, Dict
from datetime import datetime
from uuid import UUID

from app.modules.backoffice.invoices.models import AuditLog
from app.modules.admin.models import SystemSettings
from app.modules.admin.schemas import AdminAuditLogResponse


def _build_user_cache(db: Session, user_ids: List[str]) -> Dict[str, dict]:
    """Lädt Employee-Daten für eine Liste von user_ids in einer Query."""
    if not user_ids:
        return {}
    from app.modules.employees.models import Employee
    employees = (
        db.query(Employee.id, Employee.first_name, Employee.last_name, Employee.email)
        .filter(Employee.id.in_(user_ids))
        .all()
    )
    return {
        str(e.id): {
            "name": f"{e.first_name} {e.last_name}".strip(),
            "email": e.email,
        }
        for e in employees
    }


def _enrich_log(log: AuditLog, user_cache: Dict[str, dict]) -> AdminAuditLogResponse:
    """Reichert einen AuditLog-Eintrag mit User-Infos an."""
    user_info = user_cache.get(str(log.user_id), {}) if log.user_id else {}
    return AdminAuditLogResponse(
        id=log.id,
        user_id=str(log.user_id) if log.user_id else None,
        user_name=user_info.get("name"),
        user_email=user_info.get("email"),
        timestamp=log.timestamp,
        action=log.action,
        resource_type=log.entity_type,
        resource_name=None,
        details=None,
        ip_address=log.ip_address,
        old_values=log.old_values,
        new_values=log.new_values,
    )


async def get_audit_logs(
    db: Session,
    skip: int,
    limit: int,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> Tuple[List[AdminAuditLogResponse], int]:
    """
    Retrieve audit logs with filtering, pagination and user enrichment.

    Returns:
        Tuple of (enriched logs list, total count)
    """
    query = db.query(AuditLog)

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

    total = query.count()

    logs = (
        query
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Enrich with user info (single query for all users)
    user_ids = list({str(log.user_id) for log in logs if log.user_id})
    user_cache = _build_user_cache(db, user_ids)

    return [_enrich_log(log, user_cache) for log in logs], total


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
