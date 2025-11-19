# app/modules/backoffice/invoices/crud.py
"""
WorkmateOS - Invoices CRUD (IMPROVED)

CHANGES:
- ✅ Pagination support
- ✅ Validation (customer/project exists, duplicate invoice_number)
- ✅ Transaction safety with try/except
- ✅ Uses Invoice.recalculate_totals() method
- ✅ PDF generation as optional parameter (Background-Task ready)
- ✅ Better error handling
- ✅ Query optimization with selectinload
- ✅ Filter support (status, customer_id, date_range)
"""
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, func
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List
import uuid
import os

from app.modules.backoffice.invoices import models, schemas
from app.modules.backoffice.invoices.pdf_generator import generate_invoice_pdf
from app.modules.documents.models import Document
from app.modules.backoffice.crm.models import Customer
from app.modules.backoffice.projects.models import Project
from fastapi import HTTPException


# ============================================================================
# HELPERS
# ============================================================================

def _validate_customer_exists(db: Session, customer_id: uuid.UUID) -> Customer:
    """Prüft ob Customer existiert."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer


def _validate_project_exists(db: Session, project_id: uuid.UUID) -> Optional[Project]:
    """Prüft ob Project existiert (optional)."""
    if project_id is None:
        return None
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


def _validate_invoice_number_unique(db: Session, invoice_number: str, exclude_id: Optional[uuid.UUID] = None):
    """Prüft ob invoice_number bereits existiert."""
    query = db.query(models.Invoice).filter(models.Invoice.invoice_number == invoice_number)
    if exclude_id:
        query = query.filter(models.Invoice.id != exclude_id)

    existing = query.first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Invoice number '{invoice_number}' already exists"
        )


# ============================================================================
# READ OPERATIONS
# ============================================================================

def get_invoices(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    customer_id: Optional[uuid.UUID] = None,
    project_id: Optional[uuid.UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> List[models.Invoice]:
    """
    Holt Invoices mit Pagination und Filtern.

    Args:
        db: Database Session
        skip: Offset für Pagination
        limit: Max Anzahl Ergebnisse
        status: Filter nach Status
        customer_id: Filter nach Kunde
        project_id: Filter nach Projekt
        date_from: Filter nach Datum (ab)
        date_to: Filter nach Datum (bis)

    Returns:
        Liste von Invoices
    """
    query = db.query(models.Invoice).options(
        selectinload(models.Invoice.customer),
        selectinload(models.Invoice.line_items),
        selectinload(models.Invoice.payments)
    )

    # Filter anwenden
    if status:
        query = query.filter(models.Invoice.status == status)
    if customer_id:
        query = query.filter(models.Invoice.customer_id == customer_id)
    if project_id:
        query = query.filter(models.Invoice.project_id == project_id)
    if date_from:
        query = query.filter(models.Invoice.issued_date >= date_from)
    if date_to:
        query = query.filter(models.Invoice.issued_date <= date_to)

    # Sortierung und Pagination
    query = query.order_by(models.Invoice.issued_date.desc(), models.Invoice.created_at.desc())
    query = query.offset(skip).limit(limit)

    return query.all()


def count_invoices(
    db: Session,
    status: Optional[str] = None,
    customer_id: Optional[uuid.UUID] = None,
) -> int:
    """Zählt Invoices mit optionalen Filtern."""
    query = db.query(func.count(models.Invoice.id))

    if status:
        query = query.filter(models.Invoice.status == status)
    if customer_id:
        query = query.filter(models.Invoice.customer_id == customer_id)

    return query.scalar()


def get_invoice(db: Session, invoice_id: uuid.UUID) -> Optional[models.Invoice]:
    """
    Holt eine einzelne Invoice inkl. Relations.

    Args:
        db: Database Session
        invoice_id: Invoice UUID

    Returns:
        Invoice oder None
    """
    return (
        db.query(models.Invoice)
        .options(
            selectinload(models.Invoice.customer),
            selectinload(models.Invoice.project),
            selectinload(models.Invoice.line_items),
            selectinload(models.Invoice.payments)
        )
        .filter(models.Invoice.id == invoice_id)
        .first()
    )


def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[models.Invoice]:
    """Holt Invoice nach invoice_number."""
    return (
        db.query(models.Invoice)
        .options(
            selectinload(models.Invoice.customer),
            selectinload(models.Invoice.line_items)
        )
        .filter(models.Invoice.invoice_number == invoice_number)
        .first()
    )


# ============================================================================
# CREATE OPERATIONS
# ============================================================================

def create_invoice(
    db: Session,
    data: schemas.InvoiceCreate,
    generate_pdf: bool = True
) -> models.Invoice:
    """
    Erstellt neue Invoice mit Line Items.

    Args:
        db: Database Session
        data: Invoice Create Schema
        generate_pdf: PDF direkt generieren? (False für Background Task)

    Returns:
        Erstellte Invoice

    Raises:
        HTTPException: Bei Validierungsfehlern
    """
    try:
        # 1. Validierung
        _validate_customer_exists(db, data.customer_id)
        if data.project_id:
            _validate_project_exists(db, data.project_id)
        _validate_invoice_number_unique(db, data.invoice_number)

        # 2. Invoice erstellen
        invoice = models.Invoice(
            **data.model_dump(exclude={"line_items"}),
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total=Decimal("0.00"),
        )
        db.add(invoice)
        db.flush()  # ID generieren

        # 3. Line Items erstellen
        if data.line_items:
            for pos, item_data in enumerate(data.line_items, start=1):
                item = models.InvoiceLineItem(
                    invoice_id=invoice.id,
                    position=pos,
                    **item_data.model_dump()
                )
                db.add(item)

            db.flush()  # Line Items speichern

        # 4. Totals neu berechnen (verwendet neue Model-Method!)
        invoice.recalculate_totals()

        # 5. Commit
        db.commit()
        db.refresh(invoice)

        # 6. Invoice mit Relations neu laden
        invoice = get_invoice(db, invoice.id)

        # 7. PDF generieren (optional)
        if generate_pdf:
            try:
                pdf_path = _generate_and_save_pdf(db, invoice)
                invoice.pdf_path = pdf_path
                db.commit()
            except Exception as e:
                print(f"⚠️ PDF generation failed: {e}")
                # Invoice bleibt bestehen, nur PDF fehlt

        return invoice

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")


def _generate_and_save_pdf(db: Session, invoice: models.Invoice) -> str:
    """
    Generiert PDF und registriert Dokument.

    Args:
        db: Database Session
        invoice: Invoice Object (mit Relations!)

    Returns:
        PDF file path
    """
    # PDF Directory
    pdf_dir = "/root/workmate_os_uploads/invoices"
    os.makedirs(pdf_dir, exist_ok=True)

    # PDF Path
    pdf_filename = f"{invoice.invoice_number}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # PDF generieren
    generate_invoice_pdf(invoice, pdf_path)

    # Dokument registrieren
    if os.path.exists(pdf_path):
        doc = Document(
            id=uuid.uuid4(),
            title=f"Rechnung {invoice.invoice_number}",
            file_path=pdf_path,
            type="pdf",
            category="Rechnungen",
            owner_id=None,
            linked_module="invoices",
            checksum=None,
            is_confidential=False,
        )
        db.add(doc)

    return pdf_path


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_invoice(
    db: Session,
    invoice_id: uuid.UUID,
    data: schemas.InvoiceUpdate
) -> Optional[models.Invoice]:
    """
    Aktualisiert Invoice.

    Args:
        db: Database Session
        invoice_id: Invoice UUID
        data: Update Schema

    Returns:
        Aktualisierte Invoice oder None
    """
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    try:
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(invoice, key, value)

        db.commit()
        db.refresh(invoice)
        return invoice

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")


def update_invoice_status(
    db: Session,
    invoice_id: uuid.UUID,
    new_status: str
) -> Optional[models.Invoice]:
    """
    Aktualisiert nur den Status einer Invoice.

    Args:
        db: Database Session
        invoice_id: Invoice UUID
        new_status: Neuer Status

    Returns:
        Aktualisierte Invoice
    """
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    # Validierung: Status muss gültig sein
    valid_statuses = ["draft", "sent", "paid", "partial", "overdue", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    invoice.status = new_status
    db.commit()
    db.refresh(invoice)
    return invoice


def recalculate_invoice_totals(
    db: Session,
    invoice_id: uuid.UUID
) -> Optional[models.Invoice]:
    """
    Berechnet Invoice-Totals neu (z.B. nach manueller Line-Item-Änderung).

    Args:
        db: Database Session
        invoice_id: Invoice UUID

    Returns:
        Aktualisierte Invoice
    """
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    invoice.recalculate_totals()
    db.commit()
    db.refresh(invoice)
    return invoice


# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def delete_invoice(db: Session, invoice_id: uuid.UUID) -> bool:
    """
    Löscht Invoice inkl. Line Items (CASCADE).

    Args:
        db: Database Session
        invoice_id: Invoice UUID

    Returns:
        True wenn gelöscht, False wenn nicht gefunden
    """
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return False

    try:
        # PDF löschen (optional)
        if invoice.pdf_path and os.path.exists(invoice.pdf_path):
            try:
                os.remove(invoice.pdf_path)
            except Exception as e:
                print(f"⚠️ Failed to delete PDF: {e}")

        db.delete(invoice)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")


# ============================================================================
# STATISTICS
# ============================================================================

def get_invoice_statistics(
    db: Session,
    customer_id: Optional[uuid.UUID] = None
) -> dict:
    """
    Berechnet Statistiken über Invoices.

    Args:
        db: Database Session
        customer_id: Optional Customer Filter

    Returns:
        Dict mit Statistiken
    """
    query = db.query(models.Invoice)
    if customer_id:
        query = query.filter(models.Invoice.customer_id == customer_id)

    invoices = query.all()

    stats = {
        "total_count": len(invoices),
        "total_revenue": sum(inv.total for inv in invoices if inv.status == "paid"),
        "outstanding_amount": sum(inv.outstanding_amount for inv in invoices if inv.status not in ["paid", "cancelled"]),
        "overdue_count": sum(1 for inv in invoices if inv.is_overdue),
        "draft_count": sum(1 for inv in invoices if inv.status == "draft"),
        "sent_count": sum(1 for inv in invoices if inv.status == "sent"),
        "paid_count": sum(1 for inv in invoices if inv.status == "paid"),
        "cancelled_count": sum(1 for inv in invoices if inv.status == "cancelled"),
    }

    return stats
