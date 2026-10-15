# app/modules/backoffice/contracts/routes.py
"""
WorkmateOS - Verträge & Abos (v5.0)

Abrechnungslauf:
- manuell:  POST /api/backoffice/contracts/billing/run          (JWT, backoffice.contracts.write)
- n8n:      POST /api/backoffice/contracts/jobs/billing          (API-Key, Scope contracts:billing)
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.core.settings.database import get_db
from app.modules.backoffice.contracts import billing, crud, schemas
from app.modules.email_intake.auth import require_api_key_scope

router = APIRouter(prefix="/backoffice/contracts", tags=["Backoffice Contracts"])


def _billing_response(db: Session, result: billing.BillingResult) -> schemas.BillingRunResponse:
    return schemas.BillingRunResponse(
        run_date=result.run_date,
        invoices_created=result.invoices_created,
        contracts_renewed=result.contracts_renewed,
        contracts_expired=result.contracts_expired,
        errors=result.errors,
        notice_deadlines=billing.upcoming_notice_deadlines(db, within_days=30),
    )


# ─── Statische Routen (VOR /{contract_id}) ───────────────────

@router.get("/stats", response_model=schemas.ContractStatsResponse)
@require_permissions(["backoffice.contracts.read", "backoffice.*"])
def get_stats(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.get_stats(db)


@router.get("/notice-deadlines")
@require_permissions(["backoffice.contracts.read", "backoffice.*"])
def get_notice_deadlines(
    within_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return billing.upcoming_notice_deadlines(db, within_days=within_days)


@router.post("/billing/run", response_model=schemas.BillingRunResponse)
@require_permissions(["backoffice.contracts.write", "backoffice.*"])
def run_billing_manual(
    data: schemas.BillingRunRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Alle fälligen Verträge abrechnen → Rechnungsentwürfe."""
    return _billing_response(db, billing.run_billing(db, run_date=data.run_date))


@router.post("/jobs/billing", response_model=schemas.BillingRunResponse)
def run_billing_job(
    data: schemas.BillingRunRequest,
    db: Session = Depends(get_db),
    api_key=Depends(require_api_key_scope("contracts:billing")),
):
    """Täglicher n8n-Job: fällige Verträge abrechnen (nur Entwürfe, kein Versand)."""
    return _billing_response(db, billing.run_billing(db, run_date=data.run_date))


# ─── CRUD ────────────────────────────────────────────────────

@router.get("/", response_model=schemas.ContractListResponse)
@require_permissions(["backoffice.contracts.read", "backoffice.*"])
def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    contract_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    items, total = crud.get_contracts(
        db, skip=skip, limit=limit, customer_id=customer_id,
        status=status_filter, contract_type=contract_type, search=search,
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/", response_model=schemas.ContractResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["backoffice.contracts.write", "backoffice.*"])
def create_contract(
    data: schemas.ContractCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return crud.create_contract(db, data)


@router.get("/{contract_id}", response_model=schemas.ContractResponse)
@require_permissions(["backoffice.contracts.read", "backoffice.*"])
def get_contract(contract_id: uuid.UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    contract = crud.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    return contract


@router.put("/{contract_id}", response_model=schemas.ContractResponse)
@require_permissions(["backoffice.contracts.write", "backoffice.*"])
def update_contract(
    contract_id: uuid.UUID,
    data: schemas.ContractUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    contract = crud.update_contract(db, contract_id, data)
    if not contract:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    return contract


@router.post("/{contract_id}/cancel", response_model=schemas.ContractResponse)
@require_permissions(["backoffice.contracts.write", "backoffice.*"])
def cancel_contract(
    contract_id: uuid.UUID,
    data: schemas.ContractCancelRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    contract = crud.cancel_contract(db, contract_id, data)
    if not contract:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    return contract


@router.post("/{contract_id}/bill", response_model=schemas.BillingRunResponse)
@require_permissions(["backoffice.contracts.write", "backoffice.*"])
def bill_contract_now(
    contract_id: uuid.UUID,
    data: schemas.BillingRunRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Nur diesen Vertrag abrechnen (alle bis Stichtag fälligen Zeiträume)."""
    if not crud.get_contract(db, contract_id):
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    return _billing_response(db, billing.run_billing(db, run_date=data.run_date, contract_id=contract_id))


@router.get("/{contract_id}/invoices", response_model=list[schemas.ContractInvoiceBrief])
@require_permissions(["backoffice.contracts.read", "backoffice.*"])
def get_contract_invoices(contract_id: uuid.UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.get_contract_invoices(db, contract_id)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["backoffice.contracts.delete", "backoffice.*"])
def delete_contract(contract_id: uuid.UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if not crud.delete_contract(db, contract_id):
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
