"""
Compensation Routes
REST API Endpoints für Vergütungsverwaltung.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions

from . import crud, schemas


router = APIRouter(prefix="/compensation", tags=["Compensation"])


# ============================================================================
# SALARY
# ============================================================================

@router.get("/employees/{employee_id}/salary", response_model=list[schemas.SalaryRecordResponse])
@require_permissions(["hr.manage"])
async def get_salary_history(
    employee_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Gehaltshistorie eines Mitarbeiters (benötigt: hr.manage)"""
    return crud.get_salary_history(db, employee_id)


@router.post("/employees/{employee_id}/salary", response_model=schemas.SalaryRecordResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def create_salary_record(
    employee_id: UUID,
    data: schemas.SalaryRecordCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Neuen Gehaltseintrag anlegen (benötigt: hr.manage)"""
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)
    return crud.create_salary_record(db, employee_id, data, user_id)


@router.get("/employees/{employee_id}/salary/current", response_model=schemas.SalaryRecordResponse)
@require_permissions(["hr.manage"])
async def get_current_salary(
    employee_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Aktuelles Gehalt eines Mitarbeiters (benötigt: hr.manage)"""
    record = crud.get_current_salary(db, employee_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kein Gehaltseintrag gefunden")
    return record


# ============================================================================
# BONUSES
# ============================================================================

@router.get("/employees/{employee_id}/bonuses", response_model=list[schemas.BonusResponse])
@require_permissions(["hr.manage"])
async def get_bonuses(
    employee_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Boni eines Mitarbeiters (benötigt: hr.manage)"""
    return crud.get_bonuses(db, employee_id)


@router.post("/employees/{employee_id}/bonuses", response_model=schemas.BonusResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def create_bonus(
    employee_id: UUID,
    data: schemas.BonusCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Bonus anlegen (benötigt: hr.manage)"""
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)
    return crud.create_bonus(db, employee_id, data, user_id)


# ============================================================================
# BENEFITS
# ============================================================================

@router.get("/employees/{employee_id}/benefits", response_model=list[schemas.BenefitResponse])
@require_permissions(["hr.view"])
async def get_benefits(
    employee_id: UUID,
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Benefits eines Mitarbeiters (benötigt: hr.view)"""
    return crud.get_benefits(db, employee_id, is_active)


@router.post("/employees/{employee_id}/benefits", response_model=schemas.BenefitResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def create_benefit(
    employee_id: UUID,
    data: schemas.BenefitCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Benefit anlegen (benötigt: hr.manage)"""
    return crud.create_benefit(db, employee_id, data)


@router.delete("/benefits/{benefit_id}", response_model=schemas.BenefitResponse)
@require_permissions(["hr.manage"])
async def deactivate_benefit(
    benefit_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Benefit deaktivieren (benötigt: hr.manage)"""
    benefit = crud.deactivate_benefit(db, benefit_id)
    if not benefit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benefit nicht gefunden")
    return benefit
