# app/modules/backoffice/contracts/billing.py
"""
Wiederkehrende Abrechnung für Verträge.

Ablauf pro fälligem Vertrag (next_billing_date <= Stichtag):
1. Auto-Verlängerung prüfen (end_date überschritten + auto_renew)
2. Rechnungs-ENTWURF mit allen Vertragspositionen + Leistungszeitraum anlegen
3. next_billing_date um ein Intervall weiterschieben

Vertragsänderungen und Rechnung werden in derselben Transaktion committet
(create_invoice committet die Session) – ein Abbruch erzeugt also keine
Doppelabrechnung beim nächsten Lauf.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.backoffice.contracts.models import (
    INTERVAL_MONTHS,
    Contract,
    ContractStatus,
)

logger = logging.getLogger(__name__)

# Schutz gegen Rechnungsflut bei lange nicht gelaufenem Job
MAX_PERIODS_PER_RUN = 12


@dataclass
class BillingResult:
    run_date: date
    invoices_created: list[dict] = field(default_factory=list)
    contracts_renewed: list[str] = field(default_factory=list)
    contracts_expired: list[str] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)


def period_end(start: date, interval: str) -> date:
    return start + relativedelta(months=INTERVAL_MONTHS.get(interval, 1)) - timedelta(days=1)


def _apply_renewal(contract: Contract, period_start: date, result: BillingResult) -> bool:
    """
    Verlängert bzw. beendet einen Vertrag, wenn der nächste Zeitraum hinter end_date liegt.
    Returns: True wenn der Zeitraum abgerechnet werden darf.
    """
    if contract.end_date is None or period_start <= contract.end_date:
        return True

    if contract.auto_renew and contract.status == ContractStatus.ACTIVE.value:
        while contract.end_date < period_start:
            contract.end_date = contract.end_date + relativedelta(months=contract.renewal_months or 12)
        result.contracts_renewed.append(contract.contract_number)
        return True

    contract.status = ContractStatus.EXPIRED.value
    contract.next_billing_date = None
    result.contracts_expired.append(contract.contract_number)
    return False


def _build_invoice_payload(contract: Contract, start: date, end: date, issued: date):
    from app.modules.backoffice.invoices import schemas as invoice_schemas

    period = f"Leistungszeitraum: {start:%d.%m.%Y} – {end:%d.%m.%Y}"
    line_items = [
        invoice_schemas.InvoiceLineItemCreate(
            position=item.position,
            description=f"{item.description}\n{period}",
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            tax_rate=item.tax_rate,
            discount_percent=item.discount_percent,
        )
        for item in contract.items
    ]
    return invoice_schemas.InvoiceCreate(
        invoice_number="AUTO",
        customer_id=contract.customer_id,
        issued_date=issued,
        due_date=issued + timedelta(days=contract.payment_terms_days or 14),
        status="draft",
        notes=f"Automatisch erzeugt aus Vertrag {contract.contract_number} ({period})",
        terms=f"Zahlbar innerhalb von {contract.payment_terms_days or 14} Tagen ohne Abzug.",
        line_items=line_items,
    )


def bill_next_period(db: Session, contract: Contract, run_date: date, result: BillingResult) -> bool:
    """
    Rechnet genau EINEN fälligen Zeitraum ab und committet.
    Returns: True wenn eine Rechnung erzeugt wurde.
    """
    from app.modules.backoffice.invoices import crud as invoices_crud

    start = contract.next_billing_date
    if start is None or start > run_date:
        return False
    if contract.status not in (ContractStatus.ACTIVE.value, ContractStatus.CANCELLED.value):
        return False
    if not _apply_renewal(contract, start, result):
        db.commit()
        return False
    if not contract.items:
        result.errors.append({
            "contract_number": contract.contract_number,
            "error": "Vertrag hat keine Positionen",
        })
        return False

    end = period_end(start, contract.billing_interval)
    if contract.end_date and end > contract.end_date:
        end = contract.end_date

    payload = _build_invoice_payload(contract, start, end, issued=run_date)

    # Vertrag VOR dem Commit in create_invoice weiterschieben → gleiche Transaktion
    contract.last_billed_date = start
    contract.next_billing_date = start + relativedelta(months=INTERVAL_MONTHS.get(contract.billing_interval, 1))
    db.flush()

    invoice = invoices_crud.create_invoice(db, payload, generate_pdf=False)
    invoice.contract_id = contract.id
    db.commit()

    result.invoices_created.append({
        "contract_number": contract.contract_number,
        "invoice_id": str(invoice.id),
        "invoice_number": invoice.invoice_number,
        "customer_id": str(contract.customer_id),
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "total": str(invoice.total),
    })
    return True


def run_billing(db: Session, run_date: Optional[date] = None, contract_id=None) -> BillingResult:
    """
    Rechnet alle fälligen Verträge ab (oder nur einen, wenn contract_id gesetzt).
    Pro Zeitraum wird die Vertragszeile neu gesperrt (FOR UPDATE SKIP LOCKED),
    damit parallele Läufe keinen Zeitraum doppelt abrechnen.
    """
    run_date = run_date or date.today()
    result = BillingResult(run_date=run_date)

    query = db.query(Contract.id, Contract.contract_number).filter(
        Contract.status.in_([ContractStatus.ACTIVE.value, ContractStatus.CANCELLED.value]),
        Contract.next_billing_date.isnot(None),
        Contract.next_billing_date <= run_date,
    )
    if contract_id:
        query = query.filter(Contract.id == contract_id)
    due = query.all()

    for cid, number in due:
        try:
            for _ in range(MAX_PERIODS_PER_RUN):
                contract = (
                    db.query(Contract)
                    .filter(Contract.id == cid)
                    .with_for_update(skip_locked=True)
                    .populate_existing()
                    .first()
                )
                if contract is None or not bill_next_period(db, contract, run_date, result):
                    db.rollback()  # Sperre freigeben
                    break
        except HTTPException as e:
            db.rollback()
            result.errors.append({"contract_number": number, "error": str(e.detail)})
        except Exception as e:  # noqa: BLE001 – ein Vertrag darf den Lauf nicht abbrechen
            db.rollback()
            logger.exception("Abrechnung für Vertrag %s fehlgeschlagen", number)
            result.errors.append({"contract_number": number, "error": str(e)})

    return result


def upcoming_notice_deadlines(db: Session, within_days: int = 30, today: Optional[date] = None) -> list[dict]:
    """Verträge, deren Kündigungsfrist in den nächsten `within_days` Tagen abläuft."""
    today = today or date.today()
    contracts = (
        db.query(Contract)
        .filter(
            Contract.status == ContractStatus.ACTIVE.value,
            Contract.end_date.isnot(None),
        )
        .all()
    )
    result = []
    for c in contracts:
        deadline = c.end_date - timedelta(days=c.notice_period_days or 0)
        if today <= deadline <= today + timedelta(days=within_days):
            result.append({
                "contract_id": str(c.id),
                "contract_number": c.contract_number,
                "title": c.title,
                "customer_name": c.customer_name,
                "end_date": c.end_date.isoformat(),
                "notice_deadline": deadline.isoformat(),
                "auto_renew": c.auto_renew,
            })
    return sorted(result, key=lambda r: r["notice_deadline"])
