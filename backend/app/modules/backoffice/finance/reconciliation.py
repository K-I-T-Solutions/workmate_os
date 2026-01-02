"""
Automatischer Zahlungsabgleich (Payment Reconciliation)

Matched Banktransaktionen automatisch mit:
- Invoice Payments (Rechnungszahlungen)
- Expenses (Ausgaben)

Algorithmus:
1. Suche nach Rechnungsnummer im Verwendungszweck
2. Vergleiche Betrag (mit Toleranz)
3. Berechne Confidence Score
4. Auto-Match wenn Confidence > 90%
"""
from decimal import Decimal
from typing import Optional, List, Tuple
import re
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_, func

from .models import BankTransaction, ReconciliationStatus
from app.modules.backoffice.invoices.models import Invoice, Payment


# ============================================================================
# MATCHING CONFIGURATION
# ============================================================================

AUTO_MATCH_THRESHOLD = Decimal("0.90")  # 90% Confidence für Auto-Matching
AMOUNT_TOLERANCE = Decimal("1.00")  # ±1 EUR Toleranz
DATE_TOLERANCE_DAYS = 14  # ±14 Tage Toleranz


# ============================================================================
# MATCHING ALGORITHM
# ============================================================================

def find_invoice_number_in_text(text: str) -> Optional[str]:
    """
    Extrahiert Rechnungsnummer aus Verwendungszweck.

    Sucht nach Patterns wie:
    - RE-2026-0001
    - RE-2026-001
    - Rechnung RE-2026-0001
    - Rechnungsnr. RE-2026-0001
    - Invoice RE-2026-0001

    Returns:
        Invoice Number oder None
    """
    if not text:
        return None

    # Pattern: RE-YYYY-NNNN oder RE-YYYY-NNN
    patterns = [
        r'RE-\d{4}-\d{3,4}',  # RE-2026-0001 oder RE-2026-001
        r'AN-\d{4}-\d{3,4}',  # Angebot AN-2026-0001
        r'GS-\d{4}-\d{3,4}',  # Gutschrift GS-2026-0001
    ]

    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(0)

    return None


def calculate_match_confidence(
    transaction: BankTransaction,
    invoice: Invoice,
    payment: Optional[Payment] = None,
) -> Decimal:
    """
    Berechnet Confidence Score (0.0 - 1.0) für ein Match.

    Faktoren:
    - Invoice Number im Verwendungszweck: +50%
    - Betrag exakt: +40%
    - Betrag mit Toleranz: +20%
    - Datum-Nähe: +10%
    - IBAN-Match (wenn vorhanden): +10%

    Args:
        transaction: Banktransaktion
        invoice: Rechnung
        payment: Optional bestehendes Payment

    Returns:
        Confidence Score zwischen 0.0 und 1.0
    """
    confidence = Decimal("0.0")

    # 1. Invoice Number im Verwendungszweck
    found_invoice_number = find_invoice_number_in_text(transaction.purpose)
    if found_invoice_number and found_invoice_number == invoice.invoice_number:
        confidence += Decimal("0.50")

    # 2. Betrag
    transaction_amount = abs(transaction.amount)
    invoice_total = invoice.total
    payment_amount = payment.amount if payment else invoice_total

    if transaction_amount == payment_amount:
        # Exakt
        confidence += Decimal("0.40")
    elif abs(transaction_amount - payment_amount) <= AMOUNT_TOLERANCE:
        # Mit Toleranz
        confidence += Decimal("0.20")

    # 3. Datum-Nähe (innerhalb von 14 Tagen)
    if invoice.issued_date and transaction.transaction_date:
        days_diff = abs((transaction.transaction_date - invoice.issued_date).days)
        if days_diff <= DATE_TOLERANCE_DAYS:
            # Je näher, desto besser (max +10%)
            date_confidence = Decimal("0.10") * (1 - Decimal(str(days_diff)) / Decimal(str(DATE_TOLERANCE_DAYS)))
            confidence += date_confidence

    # 4. IBAN-Match (wenn Customer IBAN vorhanden wäre)
    # TODO: Implementieren wenn Customer.iban existiert
    # if transaction.counterparty_iban and customer.iban:
    #     if transaction.counterparty_iban == customer.iban:
    #         confidence += Decimal("0.10")

    return min(confidence, Decimal("1.0"))


def find_matching_invoices(
    db: Session,
    transaction: BankTransaction,
) -> List[Tuple[Invoice, Optional[Payment], Decimal]]:
    """
    Findet passende Rechnungen für eine Transaktion.

    Returns:
        Liste von (Invoice, Payment, Confidence) Tupeln,
        sortiert nach Confidence (höchste zuerst)
    """
    matches = []

    # Nur Eingänge (positive Beträge) mit Invoices matchen
    if transaction.amount <= 0:
        return matches

    # 1. Suche nach Invoice Number im Verwendungszweck
    found_invoice_number = find_invoice_number_in_text(transaction.purpose)

    if found_invoice_number:
        # Direkte Suche nach Invoice Number
        invoice = db.scalar(
            select(Invoice).where(Invoice.invoice_number == found_invoice_number)
        )

        if invoice:
            # Prüfe ob bereits ein Payment existiert
            payment = db.scalar(
                select(Payment)
                .where(Payment.invoice_id == invoice.id)
                .order_by(Payment.created_at.desc())
            )

            confidence = calculate_match_confidence(transaction, invoice, payment)
            matches.append((invoice, payment, confidence))

    # 2. Fallback: Betrag-basierte Suche (wenn keine Invoice Number gefunden)
    if not matches:
        transaction_amount = abs(transaction.amount)

        # Suche offene Rechnungen mit ähnlichem Betrag
        date_from = transaction.transaction_date - timedelta(days=DATE_TOLERANCE_DAYS)
        date_to = transaction.transaction_date + timedelta(days=DATE_TOLERANCE_DAYS)

        invoices = db.scalars(
            select(Invoice)
            .where(
                and_(
                    Invoice.status.in_(['sent', 'partial', 'overdue']),
                    Invoice.total >= transaction_amount - AMOUNT_TOLERANCE,
                    Invoice.total <= transaction_amount + AMOUNT_TOLERANCE,
                    Invoice.issued_date >= date_from,
                    Invoice.issued_date <= date_to,
                )
            )
            .limit(10)
        ).all()

        for invoice in invoices:
            payment = db.scalar(
                select(Payment)
                .where(Payment.invoice_id == invoice.id)
                .order_by(Payment.created_at.desc())
            )

            confidence = calculate_match_confidence(transaction, invoice, payment)
            if confidence > Decimal("0.30"):  # Min. 30% Confidence
                matches.append((invoice, payment, confidence))

    # Sortiere nach Confidence (höchste zuerst)
    matches.sort(key=lambda x: x[2], reverse=True)

    return matches


def auto_reconcile_transaction(
    db: Session,
    transaction: BankTransaction,
    user_id: Optional[str] = None,
) -> bool:
    """
    Versucht eine Transaktion automatisch abzugleichen.

    Returns:
        True wenn erfolgreich gematched, False sonst
    """
    # Nur unmatched Transaktionen
    if transaction.reconciliation_status != ReconciliationStatus.UNMATCHED.value:
        return False

    # Finde passende Invoices
    matches = find_matching_invoices(db, transaction)

    if not matches:
        return False

    # Nehme besten Match
    invoice, payment, confidence = matches[0]

    # Auto-Match nur wenn Confidence > Threshold
    if confidence < AUTO_MATCH_THRESHOLD:
        return False

    # Erstelle Payment wenn noch keins existiert
    if not payment:
        from app.modules.backoffice.invoices import payments_crud
        from app.modules.backoffice.invoices.schemas import PaymentCreate

        payment_data = PaymentCreate(
            amount=abs(transaction.amount),
            payment_date=transaction.transaction_date,
            method="bank_transfer",
            reference=transaction.reference,
            note=f"Automatisch abgeglichen von Banktransaktion (Confidence: {confidence:.0%})",
        )

        payment = payments_crud.create_payment(
            db=db,
            invoice_id=invoice.id,
            data=payment_data,
        )

    # Reconcile Transaction
    transaction.matched_payment_id = payment.id
    transaction.reconciliation_status = ReconciliationStatus.MATCHED.value
    transaction.reconciliation_note = f"Automatisch abgeglichen (Confidence: {confidence:.0%})"
    transaction.reconciled_at = datetime.utcnow()
    transaction.reconciled_by = user_id or "auto-reconciliation"

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return True


def auto_reconcile_all_unmatched(
    db: Session,
    account_id: Optional[str] = None,
) -> dict:
    """
    Gleicht alle unmatched Transaktionen automatisch ab.

    Args:
        account_id: Optional - nur für bestimmtes Konto

    Returns:
        Statistics dict mit matched/failed counts
    """
    # Hole alle unmatched Transaktionen
    stmt = select(BankTransaction).where(
        BankTransaction.reconciliation_status == ReconciliationStatus.UNMATCHED.value
    )

    if account_id:
        stmt = stmt.where(BankTransaction.account_id == account_id)

    transactions = db.scalars(stmt).all()

    stats = {
        "total": len(transactions),
        "matched": 0,
        "failed": 0,
        "details": []
    }

    for transaction in transactions:
        success = auto_reconcile_transaction(db, transaction)

        if success:
            stats["matched"] += 1
            stats["details"].append({
                "transaction_id": str(transaction.id),
                "amount": float(transaction.amount),
                "status": "matched"
            })
        else:
            stats["failed"] += 1
            # Finde Matches für Debugging
            matches = find_matching_invoices(db, transaction)
            best_match = matches[0] if matches else None

            stats["details"].append({
                "transaction_id": str(transaction.id),
                "amount": float(transaction.amount),
                "status": "failed",
                "reason": "no_match" if not best_match else f"low_confidence_{best_match[2]:.0%}"
            })

    return stats


def get_reconciliation_suggestions(
    db: Session,
    transaction: BankTransaction,
    limit: int = 5,
) -> List[dict]:
    """
    Gibt Vorschläge für manuelle Reconciliation.

    Returns:
        Liste von Suggestion-Dicts mit Invoice, Payment, Confidence
    """
    matches = find_matching_invoices(db, transaction)[:limit]

    suggestions = []
    for invoice, payment, confidence in matches:
        suggestions.append({
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "invoice_total": float(invoice.total),
            "invoice_status": invoice.status,
            "payment_id": str(payment.id) if payment else None,
            "payment_amount": float(payment.amount) if payment else None,
            "confidence": float(confidence),
            "confidence_percent": f"{confidence:.0%}",
            "auto_match": confidence >= AUTO_MATCH_THRESHOLD,
        })

    return suggestions
