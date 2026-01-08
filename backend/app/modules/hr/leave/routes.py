"""
Leave Management Routes
REST API Endpoints für Urlaubsverwaltung.
"""
from typing import Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_roles
from app.modules.hr.enums import LeaveStatus

from . import crud, schemas


router = APIRouter(prefix="/leave", tags=["Leave Management"])


# ============================================================================
# LEAVE POLICY ENDPOINTS (HR Admin only)
# ============================================================================

@router.get("/policies", response_model=schemas.LeavePolicyListResponse)
@require_roles(["hr_admin", "hr_manager"])
async def list_leave_policies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste alle Leave Policies (HR only)"""
    policies, total = crud.get_leave_policies(db, skip, limit, is_active)
    return {
        "items": policies,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/policies/{policy_id}", response_model=schemas.LeavePolicyResponse)
@require_roles(["hr_admin", "hr_manager"])
async def get_leave_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt eine spezifische Leave Policy"""
    policy = crud.get_leave_policy(db, policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave policy not found"
        )
    return policy


@router.post("/policies", response_model=schemas.LeavePolicyResponse, status_code=status.HTTP_201_CREATED)
@require_roles(["hr_admin"])
async def create_leave_policy(
    policy_data: schemas.LeavePolicyCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Erstellt eine neue Leave Policy (HR Admin only)"""
    return crud.create_leave_policy(db, policy_data)


@router.put("/policies/{policy_id}", response_model=schemas.LeavePolicyResponse)
@require_roles(["hr_admin"])
async def update_leave_policy(
    policy_id: UUID,
    policy_data: schemas.LeavePolicyUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Aktualisiert eine Leave Policy (HR Admin only)"""
    policy = crud.update_leave_policy(db, policy_id, policy_data)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave policy not found"
        )
    return policy


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(["hr_admin"])
async def delete_leave_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Löscht eine Leave Policy (HR Admin only)"""
    success = crud.delete_leave_policy(db, policy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave policy not found"
        )


# ============================================================================
# LEAVE BALANCE ENDPOINTS
# ============================================================================

@router.get("/balances", response_model=schemas.LeaveBalanceListResponse)
@require_roles(["hr_admin", "hr_manager"])
async def list_leave_balances(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    employee_id: Optional[UUID] = Query(None),
    year: Optional[int] = Query(None, ge=2020, le=2100),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste alle Leave Balances (HR only)"""
    balances, total = crud.get_leave_balances(db, skip, limit, employee_id, year)
    return {
        "items": balances,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/balances/employee/{employee_id}", response_model=schemas.LeaveBalanceResponse)
@require_roles(["hr_admin", "hr_manager"])
async def get_employee_balance(
    employee_id: UUID,
    year: int = Query(..., ge=2020, le=2100),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt Balance für spezifischen Mitarbeiter und Jahr (HR only)"""
    balance = crud.get_employee_balance(db, employee_id, year)
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balance not found for employee and year"
        )
    return balance


@router.post("/balances", response_model=schemas.LeaveBalanceResponse, status_code=status.HTTP_201_CREATED)
@require_roles(["hr_admin"])
async def create_leave_balance(
    balance_data: schemas.LeaveBalanceCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Erstellt/Initialisiert einen Leave Balance (HR Admin only)"""
    return crud.create_leave_balance(db, balance_data)


@router.put("/balances/{balance_id}", response_model=schemas.LeaveBalanceResponse)
@require_roles(["hr_admin"])
async def update_leave_balance(
    balance_id: UUID,
    balance_data: schemas.LeaveBalanceUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Aktualisiert einen Leave Balance (HR Admin only)"""
    balance = crud.update_leave_balance(db, balance_id, balance_data)
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balance not found"
        )
    return balance


# ============================================================================
# LEAVE REQUEST ENDPOINTS (HR)
# ============================================================================

@router.get("/requests", response_model=schemas.LeaveRequestListResponse)
@require_roles(["hr_admin", "hr_manager"])
async def list_leave_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    employee_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    leave_type: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste alle Leave Requests (HR only)"""
    requests, total = crud.get_leave_requests(
        db, skip, limit, employee_id, status, leave_type, date_from, date_to
    )
    return {
        "items": requests,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/requests/{request_id}", response_model=schemas.LeaveRequestResponse)
@require_roles(["hr_admin", "hr_manager"])
async def get_leave_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt einen spezifischen Leave Request (HR only)"""
    leave_request = crud.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    return leave_request


@router.post("/requests", response_model=schemas.LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
@require_roles(["hr_admin", "hr_manager"])
async def create_leave_request_for_employee(
    request_data: schemas.LeaveRequestCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Erstellt Leave Request für Mitarbeiter (HR only)"""
    if not request_data.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="employee_id is required"
        )

    return crud.create_leave_request(db, request_data, request_data.employee_id)


@router.put("/requests/{request_id}", response_model=schemas.LeaveRequestResponse)
@require_roles(["hr_admin", "hr_manager"])
async def update_leave_request(
    request_id: UUID,
    request_data: schemas.LeaveRequestUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Aktualisiert einen Leave Request (HR only, nur pending)"""
    leave_request = crud.update_leave_request(db, request_id, request_data)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found or cannot be updated"
        )
    return leave_request


@router.post("/requests/{request_id}/approve", response_model=schemas.LeaveRequestResponse)
@require_roles(["hr_admin", "hr_manager"])
async def approve_leave_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Genehmigt einen Leave Request (HR Manager/Admin only)"""
    # Hole user ID aus user object
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to identify approver"
        )

    leave_request = crud.approve_leave_request(db, request_id, user_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found or cannot be approved"
        )
    return leave_request


@router.post("/requests/{request_id}/reject", response_model=schemas.LeaveRequestResponse)
@require_roles(["hr_admin", "hr_manager"])
async def reject_leave_request(
    request_id: UUID,
    reject_data: schemas.LeaveRequestReject,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Lehnt einen Leave Request ab (HR Manager/Admin only)"""
    # Hole user ID aus user object
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to identify approver"
        )

    leave_request = crud.reject_leave_request(
        db, request_id, user_id, reject_data.rejection_reason
    )
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found or cannot be rejected"
        )
    return leave_request


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(["hr_admin"])
async def delete_leave_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Löscht einen Leave Request (HR Admin only, nur pending)"""
    success = crud.delete_leave_request(db, request_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found or cannot be deleted"
        )


# ============================================================================
# SELF-SERVICE ENDPOINTS (All Employees)
# ============================================================================

@router.get("/my-requests", response_model=schemas.LeaveRequestListResponse)
async def list_my_leave_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste eigene Leave Requests (Self-Service)"""
    # Hole user ID aus user object
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to identify user"
        )

    requests, total = crud.get_leave_requests(
        db, skip, limit, employee_id=user_id, status=status
    )
    return {
        "items": requests,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/my-requests", response_model=schemas.LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_my_leave_request(
    request_data: schemas.LeaveRequestCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Erstellt eigenen Leave Request (Self-Service)"""
    # Hole user ID aus user object
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to identify user"
        )

    return crud.create_leave_request(db, request_data, user_id)


@router.get("/my-balance", response_model=schemas.LeaveBalanceResponse)
async def get_my_leave_balance(
    year: int = Query(..., ge=2020, le=2100),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt eigenen Leave Balance (Self-Service)"""
    # Hole user ID aus user object
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to identify user"
        )

    balance = crud.get_employee_balance(db, user_id, year)
    if not balance:
        # Initialisiere Balance wenn nicht vorhanden
        balance = crud.initialize_employee_balance(db, user_id, year)

    return balance


@router.post("/my-requests/{request_id}/cancel", response_model=schemas.LeaveRequestResponse)
async def cancel_my_leave_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Storniert eigenen Leave Request (Self-Service)"""
    # Hole user ID aus user object
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to identify user"
        )

    # Prüfe ob Request dem User gehört
    leave_request = crud.get_leave_request(db, request_id)
    if not leave_request or leave_request.employee_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    leave_request = crud.cancel_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request cannot be cancelled"
        )

    return leave_request


# ============================================================================
# ABSENCE CALENDAR ENDPOINTS
# ============================================================================

@router.get("/calendar", response_model=schemas.AbsenceCalendarListResponse)
@require_roles(["hr_admin", "hr_manager"])
async def get_absence_calendar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    employee_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt Absence Calendar (Team-Abwesenheiten)"""
    entries, total = crud.get_absence_calendar(
        db, skip, limit, date_from, date_to, employee_id
    )
    return {
        "items": entries,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/calendar/{target_date}", response_model=list[schemas.AbsenceCalendarResponse])
@require_roles(["hr_admin", "hr_manager"])
async def get_absences_for_date(
    target_date: date,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt alle Abwesenheiten für ein bestimmtes Datum"""
    return crud.get_team_absences_for_date(db, target_date)
