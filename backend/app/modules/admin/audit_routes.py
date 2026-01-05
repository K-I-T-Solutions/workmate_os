"""
Audit Log API Routes

Provides endpoints to query audit logs for compliance and debugging.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.core.settings.database import get_db
from app.modules.backoffice.invoices import schemas as invoice_schemas
from app.modules.admin import service

router = APIRouter(prefix="/api/audit-logs", tags=["Audit"])


@router.get("", response_model=invoice_schemas.AuditLogListResponse)
async def list_audit_logs(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=500, description="Max items per page"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action (create, update, delete, status_change)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Invoice, Payment, Employee, etc.)"),
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO 8601)"),
    db: Session = Depends(get_db)
):
    """
    List all audit logs with optional filtering and pagination.

    **Permissions required:** admin.audit.*, admin.*, or *

    **Filters:**
    - user_id: Filter by user who made the change
    - action: Filter by action type (create, update, delete, status_change)
    - entity_type: Filter by entity type (Invoice, Payment, Employee, Department, Role, Customer, Project, etc.)
    - date_from: Filter changes from this date
    - date_to: Filter changes until this date

    **Returns:** List of audit log entries with pagination info
    """
    try:
        logs, total = await service.get_audit_logs(
            db=db,
            skip=skip,
            limit=limit,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            date_from=date_from,
            date_to=date_to
        )

        return {
            "items": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {str(e)}")


@router.get("/{audit_log_id}", response_model=invoice_schemas.AuditLogResponse)
async def get_audit_log(
    audit_log_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a single audit log entry by ID.

    **Permissions required:** admin.audit.*, admin.*, or *
    """
    log = await service.get_audit_log_by_id(db, audit_log_id)

    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return log
