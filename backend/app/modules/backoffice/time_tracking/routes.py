# app/modules/backoffice/time_tracking/routes.py
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.modules.backoffice.time_tracking import crud, schemas
from app.modules.backoffice.invoices.schemas import InvoiceResponse

router = APIRouter(prefix="/backoffice/time-tracking", tags=["Backoffice Time Tracking"])


# ─── Statistics (VOR /{entry_id} um Route-Konflikte zu vermeiden) ───

@router.get("/stats", response_model=schemas.TimeTrackingStatsResponse)
@require_permissions(["backoffice.time_tracking.view", "backoffice.*"])
def get_stats(
    employee_id: Optional[UUID] = Query(None, description="Filter nach Mitarbeiter"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return crud.get_stats(db, employee_id=employee_id)


@router.get("/summary", response_model=schemas.WeeklySummaryResponse)
@require_permissions(["backoffice.time_tracking.view", "backoffice.*"])
def get_weekly_summary(
    employee_id: UUID = Query(..., description="Mitarbeiter-ID"),
    week: str = Query(..., description="ISO-Woche, z.B. 2026-W06"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
        parts = week.split("-W")
        year = int(parts[0])
        week_num = int(parts[1])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ungueltiges Wochenformat. Erwartet: YYYY-Www (z.B. 2026-W06)",
        )
    return crud.get_weekly_summary(db, employee_id, year, week_num)


# ─── Billable / Invoice Endpoints ────────────────────────────

@router.get("/billable-uninvoiced", response_model=schemas.BillableUninvoicedResponse)
@require_permissions(["backoffice.time_tracking.view", "backoffice.*"])
def get_billable_uninvoiced(
    customer_id: Optional[UUID] = Query(None, description="Filter nach Kunde (über Projekt)"),
    project_id: Optional[UUID] = Query(None, description="Filter nach Projekt"),
    employee_id: Optional[UUID] = Query(None, description="Filter nach Mitarbeiter"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return crud.get_billable_uninvoiced(
        db,
        customer_id=customer_id,
        project_id=project_id,
        employee_id=employee_id,
    )


@router.post("/create-invoice", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["backoffice.time_tracking.write", "backoffice.*"])
def create_invoice_from_entries(
    data: schemas.CreateInvoiceFromEntries,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return crud.create_invoice_from_entries(db, data)


# ─── CRUD Endpoints ─────────────────────────────────────────

@router.get("/", response_model=list[schemas.TimeEntryResponse])
@require_permissions(["backoffice.time_tracking.view", "backoffice.*"])
def list_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    employee_id: Optional[UUID] = Query(None),
    project_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    task_type: Optional[str] = Query(None),
    billable: Optional[bool] = Query(None),
    is_approved: Optional[bool] = Query(None),
    is_invoiced: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return crud.get_entries(
        db,
        skip=skip, limit=limit,
        employee_id=employee_id, project_id=project_id,
        start_date=start_date, end_date=end_date,
        task_type=task_type, billable=billable,
        is_approved=is_approved, is_invoiced=is_invoiced,
        search=search,
    )


@router.get("/{entry_id}", response_model=schemas.TimeEntryResponse)
@require_permissions(["backoffice.time_tracking.view", "backoffice.*"])
def get_entry(entry_id: UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    entry = crud.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry


@router.post("/", response_model=schemas.TimeEntryResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["backoffice.time_tracking.write", "backoffice.*"])
def create_entry(data: schemas.TimeEntryCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.create_entry(db, data)


@router.put("/{entry_id}", response_model=schemas.TimeEntryResponse)
@require_permissions(["backoffice.time_tracking.write", "backoffice.*"])
def update_entry(entry_id: UUID, data: schemas.TimeEntryUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    entry = crud.update_entry(db, entry_id, data)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["backoffice.time_tracking.delete", "backoffice.*"])
def delete_entry(entry_id: UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    ok = crud.delete_entry(db, entry_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return None


# ─── Approval Endpoints ─────────────────────────────────────

@router.put("/{entry_id}/approve", response_model=schemas.TimeEntryResponse)
@require_permissions(["backoffice.time_tracking.approve", "backoffice.*"])
def approve_entry(entry_id: UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    entry = crud.approve_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry


@router.put("/{entry_id}/reject", response_model=schemas.TimeEntryResponse)
@require_permissions(["backoffice.time_tracking.approve", "backoffice.*"])
def reject_entry(entry_id: UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    entry = crud.reject_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry
