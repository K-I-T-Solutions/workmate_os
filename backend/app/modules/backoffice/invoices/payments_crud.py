# app/modules/backoffice/invoices/payments_crud.py
"""
WorkmateOS - Payment CRUD Operations

Handles payment creation, updates and auto-status updates for invoices.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import uuid

from app.modules.backoffice.invoices import models, schemas
from fastapi import HTTPException, status


# ============================================================================
# READ OPERATIONS
# ============================================================================

def get_payments(
    db: Session,
    invoice_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Payment]:
    """
    Holt Payments mit optionalem Invoice-Filter.

    Args:
        db: Database Session
        invoice_id: Optional filter by invoice
        skip: Offset für Pagination
        limit: Max Anzahl

    Returns:
        Liste von Payments
    """
    query = db.query(models.Payment)

    if invoice_id:
        query = query.filter(models.Payment.invoice_id == invoice_id)

    query = query.order_by(models.Payment.payment_date.desc())
    query = query.offset(skip).limit(limit)

    return query.all()


def get_payment(db: Session, payment_id: uuid.UUID) -> Optional[models.Payment]:
    """Holt einzelnes Payment."""
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()


# ============================================================================
# CREATE OPERATIONS
# ============================================================================

def create_payment(
    db: Session,
    invoice_id: uuid.UUID,
    data: schemas.PaymentCreate
) -> models.Payment:
    """
    Erstellt neues Payment für eine Invoice.

    WICHTIG: Status wird automatisch via SQLAlchemy Event aktualisiert!

    Args:
        db: Database Session
        invoice_id: Invoice UUID
        data: Payment Create Schema

    Returns:
        Erstelltes Payment

    Raises:
        HTTPException: Bei Validierungsfehlern
    """
    # 1. Prüfe ob Invoice existiert
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    # 2. Validierung: Betrag nicht höher als outstanding amount
    if data.amount > invoice.outstanding_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({data.amount}) exceeds outstanding amount ({invoice.outstanding_amount})"
        )

    try:
        # 3. Payment erstellen
        payment = models.Payment(
            invoice_id=invoice_id,
            amount=data.amount,
            payment_date=data.payment_date or date.today(),
            method=data.method,
            reference=data.reference,
            note=data.note
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # 4. Invoice Status manuell aktualisieren (da Event manchmal nicht triggert)
        invoice.update_status_from_payments()
        db.commit()
        db.refresh(invoice)

        return payment

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_payment(
    db: Session,
    payment_id: uuid.UUID,
    data: schemas.PaymentUpdate
) -> Optional[models.Payment]:
    """
    Aktualisiert Payment.

    Args:
        db: Database Session
        payment_id: Payment UUID
        data: Update Schema

    Returns:
        Aktualisiertes Payment
    """
    payment = get_payment(db, payment_id)
    if not payment:
        return None

    try:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(payment, key, value)

        db.commit()
        db.refresh(payment)

        # Invoice Status aktualisieren
        payment.invoice.update_status_from_payments()
        db.commit()

        return payment

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update payment: {str(e)}"
        )


# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def delete_payment(db: Session, payment_id: uuid.UUID) -> bool:
    """
    Löscht Payment.

    Args:
        db: Database Session
        payment_id: Payment UUID

    Returns:
        True wenn gelöscht
    """
    payment = get_payment(db, payment_id)
    if not payment:
        return False

    try:
        invoice = payment.invoice  # Invoice merken vor dem Löschen

        db.delete(payment)
        db.commit()

        # Invoice Status aktualisieren
        invoice.update_status_from_payments()
        db.commit()

        return True

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete payment: {str(e)}"
        )
