"""
Retention Policy für Rechnungen (GoBD Compliance)

§ 147 AO (Abgabenordnung):
- Aufbewahrungspflicht: 10 Jahre
- Aufbewahrungsfrist beginnt mit Schluss des Kalenderjahrs der Entstehung
- Nach 10 Jahren: Automatisches Hard-Delete

§ 257 HGB (Handelsgesetzbuch):
- Ebenfalls 10 Jahre Aufbewahrungspflicht für Handelsbriefe

Implementierung:
- Scheduled Task (Cronjob) läuft täglich
- Prüft alle Invoices mit deleted_at > 10 Jahre
- Hard-Delete nach 10 Jahren
- Audit Log wird erstellt
"""
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.modules.backoffice.invoices.models import Invoice
from app.modules.backoffice.invoices.audit import log_audit

logger = logging.getLogger(__name__)


# ============================================================================
# RETENTION POLICY CONSTANTS
# ============================================================================

RETENTION_PERIOD_YEARS = 10  # § 147 AO & § 257 HGB
RETENTION_PERIOD_DAYS = RETENTION_PERIOD_YEARS * 365  # ca. 3650 Tage


# ============================================================================
# RETENTION CHECK
# ============================================================================

def get_retention_deadline() -> date:
    """
    Berechnet das Retention-Deadline-Datum.

    Gemäß § 147 AO: Aufbewahrungsfrist beginnt mit Schluss des Kalenderjahrs.

    Beispiel:
    - Invoice vom 15.03.2015
    - Kalenderjahr-Ende: 31.12.2015
    - Aufbewahrungsfrist: 10 Jahre
    - Löschdatum: 01.01.2026

    Returns:
        Datum vor dem Invoices gelöscht werden dürfen
    """
    today = date.today()
    # 10 Jahre zurück vom heutigen Jahr
    retention_year = today.year - RETENTION_PERIOD_YEARS
    # Deadline: 31.12. des Retention-Jahres
    return date(retention_year, 12, 31)


def is_eligible_for_deletion(invoice: Invoice) -> bool:
    """
    Prüft ob eine Invoice für Hard-Delete eligible ist.

    Bedingungen:
    1. Invoice ist soft-deleted (deleted_at != NULL)
    2. deleted_at ist älter als Retention-Periode (10 Jahre)

    Args:
        invoice: Invoice-Objekt

    Returns:
        True wenn Invoice gelöscht werden darf
    """
    if not invoice.deleted_at:
        return False

    # Berechne Retention-Deadline basierend auf deleted_at
    deleted_date = invoice.deleted_at.date() if isinstance(invoice.deleted_at, datetime) else invoice.deleted_at
    retention_deadline = get_retention_deadline()

    return deleted_date <= retention_deadline


# ============================================================================
# RETENTION POLICY EXECUTION
# ============================================================================

def find_eligible_invoices(db: Session) -> list[Invoice]:
    """
    Findet alle Invoices die für Hard-Delete eligible sind.

    Returns:
        Liste von Invoice-Objekten die gelöscht werden können
    """
    retention_deadline = get_retention_deadline()

    stmt = select(Invoice).where(
        and_(
            Invoice.deleted_at.isnot(None),
            Invoice.deleted_at <= datetime.combine(retention_deadline, datetime.min.time())
        )
    )

    invoices = list(db.scalars(stmt).all())
    return invoices


def hard_delete_expired_invoices(
    db: Session,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Löscht alle Invoices die älter als 10 Jahre sind (Hard-Delete).

    **Hinweis:**
    Dies ist ein IRREVERSIBLER Vorgang! Invoices werden permanent gelöscht.

    Args:
        db: Database Session
        dry_run: Wenn True, wird nur simuliert (kein echtes Löschen)

    Returns:
        Dict mit Statistiken
    """
    stats = {
        "total_found": 0,
        "deleted": 0,
        "failed": 0,
        "errors": [],
        "retention_deadline": get_retention_deadline().isoformat(),
        "dry_run": dry_run,
    }

    try:
        # Finde eligible Invoices
        invoices = find_eligible_invoices(db)
        stats["total_found"] = len(invoices)

        logger.info(f"Retention Policy: Found {len(invoices)} invoices eligible for deletion")

        for invoice in invoices:
            try:
                invoice_number = invoice.invoice_number
                invoice_id = invoice.id
                deleted_at = invoice.deleted_at

                if not dry_run:
                    # Delete PDF from storage
                    if invoice.pdf_path:
                        try:
                            from app.core.storage.factory import get_storage
                            storage = get_storage()
                            if storage.exists(invoice.pdf_path):
                                storage.delete(invoice.pdf_path)
                                logger.info(f"Deleted PDF: {invoice.pdf_path}")
                        except Exception as pdf_error:
                            logger.warning(f"Failed to delete PDF {invoice.pdf_path}: {pdf_error}")

                    # Delete XRechnung XML
                    if invoice.xml_path:
                        try:
                            from app.core.storage.factory import get_storage
                            storage = get_storage()
                            if storage.exists(invoice.xml_path):
                                storage.delete(invoice.xml_path)
                                logger.info(f"Deleted XML: {invoice.xml_path}")
                        except Exception as xml_error:
                            logger.warning(f"Failed to delete XML {invoice.xml_path}: {xml_error}")

                    # Delete ZUGFeRD PDF
                    if invoice.zugferd_path:
                        try:
                            from app.core.storage.factory import get_storage
                            storage = get_storage()
                            if storage.exists(invoice.zugferd_path):
                                storage.delete(invoice.zugferd_path)
                                logger.info(f"Deleted ZUGFeRD: {invoice.zugferd_path}")
                        except Exception as zugferd_error:
                            logger.warning(f"Failed to delete ZUGFeRD {invoice.zugferd_path}: {zugferd_error}")

                    # AUDIT LOG (before deletion)
                    try:
                        log_audit(
                            db=db,
                            entity_type="Invoice",
                            entity_id=invoice_id,
                            action="delete",
                            old_values={
                                "invoice_number": invoice_number,
                                "deleted_at": deleted_at.isoformat() if deleted_at else None,
                            },
                            new_values={
                                "hard_deleted": True,
                                "reason": "retention_policy",
                                "retention_years": RETENTION_PERIOD_YEARS,
                                "note": f"Automatisches Löschen nach {RETENTION_PERIOD_YEARS} Jahren (§ 147 AO)"
                            },
                            user_id="system_retention_policy",
                            ip_address="127.0.0.1"
                        )
                    except Exception as audit_error:
                        logger.warning(f"Audit logging failed: {audit_error}")

                    # HARD DELETE
                    db.delete(invoice)
                    db.commit()

                    logger.info(f"Hard-deleted invoice {invoice_number} (ID: {invoice_id})")

                stats["deleted"] += 1

            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append({
                    "invoice_id": str(invoice.id),
                    "invoice_number": invoice.invoice_number,
                    "error": str(e)
                })
                logger.error(f"Failed to delete invoice {invoice.invoice_number}: {e}")
                db.rollback()

        return stats

    except Exception as e:
        logger.error(f"Retention policy execution failed: {e}")
        stats["errors"].append({"general_error": str(e)})
        return stats


# ============================================================================
# RETENTION REPORT
# ============================================================================

def get_retention_report(db: Session) -> Dict[str, Any]:
    """
    Erstellt einen Report über Invoices und Retention Status.

    Returns:
        Dict mit Report-Daten
    """
    retention_deadline = get_retention_deadline()

    # Alle soft-deleted Invoices
    stmt = select(Invoice).where(Invoice.deleted_at.isnot(None))
    all_deleted = list(db.scalars(stmt).all())

    # Eligible für Deletion
    eligible = find_eligible_invoices(db)

    # Noch in Retention-Periode
    in_retention = [inv for inv in all_deleted if inv not in eligible]

    return {
        "retention_deadline": retention_deadline.isoformat(),
        "retention_period_years": RETENTION_PERIOD_YEARS,
        "total_soft_deleted": len(all_deleted),
        "eligible_for_deletion": len(eligible),
        "still_in_retention": len(in_retention),
        "eligible_invoices": [
            {
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "deleted_at": inv.deleted_at.isoformat() if inv.deleted_at else None,
                "years_since_deletion": (date.today() - (inv.deleted_at.date() if isinstance(inv.deleted_at, datetime) else inv.deleted_at)).days // 365,
            }
            for inv in eligible
        ],
    }
