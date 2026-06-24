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
- ✅ Automatische Nummernkreise pro Dokumenttyp & Jahr
"""
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List
import uuid
import os

from fastapi import HTTPException

from app.modules.backoffice.invoices import models, schemas
from app.modules.backoffice.invoices.pdf_generator import generate_invoice_pdf
from app.modules.documents.models import Document
from app.modules.backoffice.crm.models import Customer
from app.modules.backoffice.projects.models import Project


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


def _validate_invoice_number_unique(
    db: Session,
    invoice_number: str,
    exclude_id: Optional[uuid.UUID] = None,
) -> None:
    """Prüft ob invoice_number bereits existiert."""
    query = db.query(models.Invoice).filter(models.Invoice.invoice_number == invoice_number)
    if exclude_id:
        query = query.filter(models.Invoice.id != exclude_id)

    existing = query.first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Invoice number '{invoice_number}' already exists",
        )


# ---------------- Nummernkreis-Helfer ---------------- #

def _get_prefix_for_doc_type(doc_type: str) -> str:
    """
    Liefert Präfix für Nummernformat je Dokumenttyp.

    Format (deine Wahl 1:A):
      RE-2025-0001 (invoice)
      AN-2025-0001 (quote)
      GS-2025-0001 (credit_note)
      ST-2025-0001 (cancellation)
    """
    mapping = {
        "invoice": "RE",
        "quote": "AN",
        "credit_note": "GS",
        "cancellation": "ST",
    }
    return mapping.get(doc_type, "RE")  # Fallback: RE


def _get_doc_type_for_invoice() -> str:
    """
    Dokumenttyp für diese CRUD-Datei.
    Später kannst du in einem eigenen Quote-CRUD z.B. "quote" verwenden.
    """
    return "invoice"


def _generate_next_number(
    db: Session,
    doc_type: str,
    year: int,
) -> int:
    """
    Holt die nächste laufende Nummer aus number_sequences.

    - Legt bei Bedarf einen neuen Eintrag an (startet bei 1)
    - Verwendet SELECT ... FOR UPDATE für concurrency safety
    """
    # Row mit FOR UPDATE sperren (Postgres)
    seq_row = (
        db.query(models.NumberSequence)
        .filter(
            models.NumberSequence.doc_type == doc_type,
            models.NumberSequence.year == year,
        )
        .with_for_update()
        .first()
    )

    if not seq_row:
        seq_row = models.NumberSequence(
            doc_type=doc_type,
            year=year,
            current_number=1,
        )
        db.add(seq_row)
        db.flush()
        return 1

    seq_row.current_number += 1
    db.flush()
    return seq_row.current_number


def _generate_invoice_number(
    db: Session,
    issued_date: Optional[date],
    doc_type: Optional[str] = None,
) -> str:
    """
    Generiert eine neue Rechnungs-/Dokumentnummer nach deinem Schema:

      <PREFIX>-<YEAR>-<SEQRUN>

    Beispiele (doc_type = "invoice"):
      RE-2025-0001
      RE-2025-0002

    Reset pro Jahr, eigener Counter pro doc_type.
    """
    if doc_type is None:
        doc_type = _get_doc_type_for_invoice()

    year = (issued_date or date.today()).year
    prefix = _get_prefix_for_doc_type(doc_type)

    # Laufende Nummer (atomic)
    next_num = _generate_next_number(db, doc_type=doc_type, year=year)

    # 4-stellige laufende Nummer, z.B. 0001
    seq_str = f"{next_num:04d}"
    return f"{prefix}-{year}-{seq_str}"


def _extract_seq_from_invoice_number(invoice_number: str) -> str:
    """
    Extrahiert die laufende Nummer aus der Rechnungsnummer.

    Erwartetes Format: PREFIX-YEAR-SEQ (z.B. RE-2025-0001)
    -> gibt '0001' zurück.

    Fallback: letzte Token-Komponente.
    """
    if not invoice_number:
        return "0001"
    parts = invoice_number.split("-")
    if len(parts) >= 3:
        return parts[-1]
    return parts[-1]


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
    """
    query = db.query(models.Invoice).options(
        selectinload(models.Invoice.customer),
        selectinload(models.Invoice.line_items),
        selectinload(models.Invoice.payments),
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
    query = query.order_by(
        models.Invoice.issued_date.desc(),
        models.Invoice.created_at.desc(),
    )
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
    """
    return (
        db.query(models.Invoice)
        .options(
            selectinload(models.Invoice.customer),
            selectinload(models.Invoice.project),
            selectinload(models.Invoice.line_items),
            selectinload(models.Invoice.payments),
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
            selectinload(models.Invoice.line_items),
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
    generate_pdf: bool = True,
) -> models.Invoice:
    """
    Erstellt neue Invoice mit Line Items.

    Logik für invoice_number:
    - Wenn data.invoice_number gesetzt & nicht 'AUTO' → wird verwendet (nach Unique-Check)
    - Wenn leer oder 'AUTO' → automatische Nummernvergabe nach Nummernkreis
    """
    try:
        # 1. Validierung: Kunde / Projekt
        _validate_customer_exists(db, data.customer_id)
        if data.project_id:
            _validate_project_exists(db, data.project_id)

        # 2. Invoice-Nummer bestimmen
        raw_number = (data.invoice_number or "").strip() if data.invoice_number is not None else ""
        auto_mode = raw_number == "" or raw_number.upper() == "AUTO"

        if auto_mode:
            # automatische Nummernvergabe
            invoice_number = _generate_invoice_number(
                db=db,
                issued_date=data.issued_date,
                doc_type=_get_doc_type_for_invoice(),
            )
        else:
            # manuelle Nummer -> Einzigartigkeit prüfen
            _validate_invoice_number_unique(db, raw_number)
            invoice_number = raw_number

        # 3. Invoice-Objekt erstellen
        payload = data.model_dump(exclude={"line_items", "invoice_number"})
        invoice = models.Invoice(
            **payload,
            invoice_number=invoice_number,
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total=Decimal("0.00"),
        )
        db.add(invoice)
        db.flush()  # ID generieren + Sequence ggf. persistieren

        # 4. Line Items erstellen
        if data.line_items:
            for pos, item_data in enumerate(data.line_items, start=1):
                item = models.InvoiceLineItem(
                    invoice_id=invoice.id,
                    position=pos,
                    # Position aus Schema ignorieren, wir zählen sauber durch
                    **item_data.model_dump(exclude={"position"}),
                )
                db.add(item)

            db.flush()  # Line Items speichern

        # 5. Totals neu berechnen
        invoice.recalculate_totals()

        # 6. Commit + refresh
        db.commit()
        db.refresh(invoice)

        # 7. Invoice mit Relations neu laden
        invoice = get_invoice(db, invoice.id)

        # 8. PDF generieren (optional)
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

    Dateiname (deine Wahl 6):
      KIT-RE-001.pdf

    Umsetzung:
    - aus invoice.invoice_number z.B. 'RE-2025-0001'
    - extrahieren wir '0001'
    - daraus 'KIT-RE-0001.pdf'
    """
    # PDF Directory
    pdf_dir = "/root/workmate_os_uploads/invoices"
    os.makedirs(pdf_dir, exist_ok=True)

    # Laufende Nummer aus Rechnungsnummer extrahieren
    seq_str = _extract_seq_from_invoice_number(invoice.invoice_number)

    # Standard für Rechnungen → KIT-RE-<SEQ>.pdf
    # (Wenn du später Angebote hier drüber laufen lässt, kannst du z.B. KIT-AN- etc. machen)
    pdf_filename = f"KIT-RE-{seq_str}.pdf"
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
    data: schemas.InvoiceUpdate,
) -> Optional[models.Invoice]:
    """Aktualisiert Invoice."""
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    try:
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
    new_status: str,
) -> Optional[models.Invoice]:
    """Aktualisiert nur den Status einer Invoice."""
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    valid_statuses = ["draft", "sent", "paid", "partial", "overdue", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    invoice.status = new_status
    db.commit()
    db.refresh(invoice)
    return invoice


def recalculate_invoice_totals(
    db: Session,
    invoice_id: uuid.UUID,
) -> Optional[models.Invoice]:
    """Berechnet Invoice-Totals neu (z.B. nach manueller Line-Item-Änderung)."""
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
    """Löscht Invoice inkl. Line Items (CASCADE)."""
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return False

    try:
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
    customer_id: Optional[uuid.UUID] = None,
) -> dict:
    """Berechnet Statistiken über Invoices."""
    query = db.query(models.Invoice)
    if customer_id:
        query = query.filter(models.Invoice.customer_id == customer_id)

    invoices = query.all()

    stats = {
        "total_count": len(invoices),
        "total_revenue": sum(inv.total for inv in invoices if inv.status == "paid"),
        "outstanding_amount": sum(
            inv.outstanding_amount
            for inv in invoices
            if inv.status not in ["paid", "cancelled"]
        ),
        "overdue_count": sum(1 for inv in invoices if inv.is_overdue),
        "draft_count": sum(1 for inv in invoices if inv.status == "draft"),
        "sent_count": sum(1 for inv in invoices if inv.status == "sent"),
        "paid_count": sum(1 for inv in invoices if inv.status == "paid"),
        "cancelled_count": sum(1 for inv in invoices if inv.status == "cancelled"),
    }

    return stats
