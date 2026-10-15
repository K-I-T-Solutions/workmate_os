# app/modules/backoffice/contracts/crud.py
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.modules.backoffice.contracts import schemas
from app.modules.backoffice.contracts.billing import upcoming_notice_deadlines
from app.modules.backoffice.contracts.models import Contract, ContractItem, ContractStatus
from app.modules.backoffice.crm.models import Customer


def _next_contract_number(db: Session, year: int) -> str:
    # Gleicher Nummernkreis-Mechanismus wie Rechnungen (FOR UPDATE auf number_sequences)
    from app.modules.backoffice.invoices.crud import _generate_next_number

    n = _generate_next_number(db, doc_type="contract", year=year)
    return f"VT-{year}-{n:04d}"


def _query(db: Session):
    return db.query(Contract).options(
        selectinload(Contract.items), selectinload(Contract.customer)
    )


def get_contracts(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    contract_type: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Contract], int]:
    query = _query(db)
    if customer_id:
        query = query.filter(Contract.customer_id == customer_id)
    if status:
        query = query.filter(Contract.status == status)
    if contract_type:
        query = query.filter(Contract.contract_type == contract_type)
    if search:
        like = f"%{search}%"
        query = query.join(Customer, Contract.customer_id == Customer.id).filter(
            or_(Contract.title.ilike(like), Contract.contract_number.ilike(like), Customer.name.ilike(like))
        )
    total = query.count()
    items = query.order_by(Contract.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_contract(db: Session, contract_id: uuid.UUID) -> Optional[Contract]:
    return _query(db).filter(Contract.id == contract_id).first()


def _set_items(db: Session, contract: Contract, items: list[schemas.ContractItemCreate]) -> None:
    contract.items.clear()
    db.flush()
    for pos, item in enumerate(items, start=1):
        contract.items.append(ContractItem(**item.model_dump(exclude={"position"}), position=pos))


def create_contract(db: Session, data: schemas.ContractCreate) -> Contract:
    if not db.get(Customer, data.customer_id):
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    payload = data.model_dump(exclude={"items", "next_billing_date"})
    contract = Contract(
        **payload,
        contract_number=_next_contract_number(db, data.start_date.year),
        next_billing_date=data.next_billing_date or data.start_date,
    )
    db.add(contract)
    db.flush()
    _set_items(db, contract, data.items)
    db.commit()
    return get_contract(db, contract.id)


def update_contract(db: Session, contract_id: uuid.UUID, data: schemas.ContractUpdate) -> Optional[Contract]:
    contract = get_contract(db, contract_id)
    if not contract:
        return None
    changes = data.model_dump(exclude_unset=True, exclude={"items"})
    for k, v in changes.items():
        setattr(contract, k, v)
    if contract.end_date and contract.end_date < contract.start_date:
        raise HTTPException(status_code=422, detail="end_date darf nicht vor start_date liegen")
    if data.items is not None:
        _set_items(db, contract, data.items)
    # Reaktivierter Vertrag ohne Abrechnungsdatum → ab heute abrechnen
    if contract.status == ContractStatus.ACTIVE.value and contract.next_billing_date is None:
        contract.next_billing_date = max(date.today(), contract.start_date)
    db.commit()
    return get_contract(db, contract.id)


def cancel_contract(db: Session, contract_id: uuid.UUID, data: schemas.ContractCancelRequest) -> Optional[Contract]:
    """Kündigung: Vertrag läuft bis end_date weiter und wird bis dahin abgerechnet."""
    contract = get_contract(db, contract_id)
    if not contract:
        return None
    if data.end_date < contract.start_date:
        raise HTTPException(status_code=422, detail="Vertragsende liegt vor Vertragsbeginn")
    contract.status = ContractStatus.CANCELLED.value
    contract.end_date = data.end_date
    contract.auto_renew = False
    if data.reason:
        note = f"[{date.today():%d.%m.%Y}] Gekündigt zum {data.end_date:%d.%m.%Y}: {data.reason}"
        contract.notes = f"{contract.notes}\n{note}" if contract.notes else note
    db.commit()
    return get_contract(db, contract.id)


def delete_contract(db: Session, contract_id: uuid.UUID) -> bool:
    from app.modules.backoffice.invoices.models import Invoice

    contract = db.get(Contract, contract_id)
    if not contract:
        return False
    if db.query(Invoice.id).filter(Invoice.contract_id == contract_id).first():
        raise HTTPException(
            status_code=409,
            detail="Vertrag hat bereits Rechnungen – bitte kündigen statt löschen",
        )
    db.delete(contract)
    db.commit()
    return True


def get_contract_invoices(db: Session, contract_id: uuid.UUID):
    from app.modules.backoffice.invoices.models import Invoice

    return (
        db.query(Invoice)
        .filter(Invoice.contract_id == contract_id)
        .order_by(Invoice.issued_date.desc().nullslast(), Invoice.created_at.desc())
        .all()
    )


def get_stats(db: Session) -> dict:
    active = _query(db).filter(Contract.status == ContractStatus.ACTIVE.value).all()
    mrr = sum((c.monthly_recurring_revenue for c in active), Decimal("0.00"))
    due = (
        db.query(func.count(Contract.id))
        .filter(
            Contract.status.in_([ContractStatus.ACTIVE.value, ContractStatus.CANCELLED.value]),
            Contract.next_billing_date.isnot(None),
            Contract.next_billing_date <= date.today(),
        )
        .scalar()
        or 0
    )
    return {
        "active_contracts": len(active),
        "monthly_recurring_revenue": mrr,
        "annual_recurring_revenue": mrr * 12,
        "due_for_billing": due,
        "notice_deadlines_30d": len(upcoming_notice_deadlines(db, within_days=30)),
    }
