"""
Onboarding Routes
REST API Endpoints für Onboarding-Management.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions

from . import crud, schemas


router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


# ============================================================================
# TEMPLATES
# ============================================================================

@router.get("/templates", response_model=list[schemas.TemplateResponse])
@require_permissions(["hr.view"])
async def list_templates(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste aller Onboarding-Templates (benötigt: hr.view)"""
    return crud.get_templates(db, is_active)


@router.post("/templates", response_model=schemas.TemplateResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def create_template(
    data: schemas.TemplateCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Erstellt ein Onboarding-Template (benötigt: hr.manage)"""
    return crud.create_template(db, data)


# ============================================================================
# PROCESSES
# ============================================================================

@router.post("/processes", response_model=schemas.ProcessResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def start_onboarding(
    data: schemas.ProcessCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Startet Onboarding-Prozess für Mitarbeiter (benötigt: hr.manage)"""
    return crud.start_onboarding(db, data.employee_id, data.template_id, data.start_date)


@router.get("/processes/{process_id}", response_model=schemas.ProcessResponse)
@require_permissions(["hr.view"])
async def get_process(
    process_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt einen Onboarding-Prozess (benötigt: hr.view)"""
    process = crud.get_process(db, process_id)
    if not process:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prozess nicht gefunden")
    return process


@router.get("/employees/{employee_id}/onboarding", response_model=list[schemas.ProcessResponse])
@require_permissions(["hr.view"])
async def get_employee_onboarding(
    employee_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt alle Onboarding-Prozesse eines Mitarbeiters (benötigt: hr.view)"""
    return crud.get_employee_onboarding(db, employee_id)


# ============================================================================
# TASKS
# ============================================================================

@router.patch("/tasks/{task_id}", response_model=schemas.ProcessTaskResponse)
@require_permissions(["hr.manage"])
async def update_task_status(
    task_id: UUID,
    data: schemas.TaskStatusUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Aktualisiert Status einer Onboarding-Aufgabe (benötigt: hr.manage)"""
    task = crud.update_task_status(db, task_id, data.status, data.notes)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aufgabe nicht gefunden")
    return task
