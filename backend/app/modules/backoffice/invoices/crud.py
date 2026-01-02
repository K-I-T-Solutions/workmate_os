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
import hashlib

from fastapi import HTTPException

from app.modules.backoffice.invoices import models, schemas
from app.modules.backoffice.invoices.pdf_generator import generate_invoice_pdf
from app.modules.backoffice.invoices.audit import (
    log_invoice_creation,
    log_invoice_update,
    log_invoice_status_change,
    log_invoice_deletion,
    serialize_for_audit,
)
from app.modules.backoffice.invoices.compliance import (
    validate_invoice_update,
    validate_invoice_deletion,
    validate_invoice_status_change,
)
from app.modules.documents.models import Document
from app.modules.backoffice.crm.models import Customer
from app.modules.backoffice.projects.models import Project
from app.core.storage.factory import get_storage
from app.core.settings.config import settings


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

    Format:
      RE-2025-0001 (invoice)
      AN-2025-0001 (quote)
      GS-2025-0001 (credit_note)
      AB-2025-0001 (order_confirmation)
    """
    mapping = {
        "invoice": "RE",
        "quote": "AN",
        "credit_note": "GS",
        "order_confirmation": "AB",  # Auftragsbestätigung
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
    include_deleted: bool = False,
) -> List[models.Invoice]:
    """
    Holt Invoices mit Pagination und Filtern.

    Args:
        include_deleted: If True, include soft-deleted invoices (default: False)
    """
    query = db.query(models.Invoice).options(
        selectinload(models.Invoice.customer),
        selectinload(models.Invoice.line_items),
        selectinload(models.Invoice.payments),
    )

    # SOFT-DELETE FILTER (GoBD compliance)
    if not include_deleted:
        query = query.filter(models.Invoice.deleted_at.is_(None))

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


def get_invoice(db: Session, invoice_id: uuid.UUID, include_deleted: bool = False) -> Optional[models.Invoice]:
    """
    Holt eine einzelne Invoice inkl. Relations.

    Args:
        include_deleted: If True, include soft-deleted invoices (default: False)
    """
    query = (
        db.query(models.Invoice)
        .options(
            selectinload(models.Invoice.customer),
            selectinload(models.Invoice.project),
            selectinload(models.Invoice.line_items),
            selectinload(models.Invoice.payments),
        )
        .filter(models.Invoice.id == invoice_id)
    )

    # SOFT-DELETE FILTER (GoBD compliance)
    if not include_deleted:
        query = query.filter(models.Invoice.deleted_at.is_(None))

    return query.first()


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

        # Dokumenttyp aus data oder Default "invoice"
        doc_type = data.document_type if hasattr(data, 'document_type') and data.document_type else "invoice"

        if auto_mode:
            # automatische Nummernvergabe mit korrektem Dokumenttyp
            invoice_number = _generate_invoice_number(
                db=db,
                issued_date=data.issued_date,
                doc_type=doc_type,
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

        # 8. AUDIT LOG (GoBD Compliance)
        try:
            log_invoice_creation(db, invoice)
            db.commit()
        except Exception as audit_error:
            print(f"⚠️ Audit logging failed: {audit_error}")

        # 9. PDF generieren (optional)
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
        raise  # Re-raise HTTPException with original status code
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")


def _calculate_checksum(content: bytes) -> str:
    """Calculate SHA256 checksum of file content."""
    return hashlib.sha256(content).hexdigest()


def _generate_and_save_pdf(db: Session, invoice: models.Invoice) -> str:
    """
    Generiert PDF und lädt es zu Storage hoch (Nextcloud/S3/Local).

    Dateiname: {invoice_number}.pdf (z.B. RE-2025-0001.pdf)
    Remote Path: workmate/invoices/{invoice_number}.pdf

    Returns:
        Remote path in storage
    """
    storage = get_storage()

    # PDF-Dateiname: direkt die Rechnungsnummer verwenden
    pdf_filename = f"{invoice.invoice_number}.pdf"

    # Remote path in storage (configurable via INVOICE_STORAGE_PATH)
    storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
    remote_path = f"{storage_path}/{pdf_filename}"

    # PDF als Bytes generieren
    pdf_content = generate_invoice_pdf(invoice, output_path=None)

    if not pdf_content:
        raise ValueError("PDF generation returned no content")

    # Checksum berechnen
    checksum = _calculate_checksum(pdf_content)

    # PDF zu Storage hochladen
    storage.upload(remote_path, pdf_content)

    # Dokument in Documents-Tabelle registrieren
    doc = Document(
        id=uuid.uuid4(),
        title=f"Rechnung {invoice.invoice_number}",
        file_path=remote_path,  # Remote path, NOT local filesystem path
        type="pdf",
        category="Rechnungen",
        owner_id=None,  # TODO: Assign proper owner (invoice creator or customer contact)
        linked_module="invoices",
        checksum=checksum,
        is_confidential=False,
    )
    db.add(doc)

    return remote_path


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_invoice(
    db: Session,
    invoice_id: uuid.UUID,
    data: schemas.InvoiceUpdate,
) -> Optional[models.Invoice]:
    """Aktualisiert Invoice mit Compliance-Validierung (§238 HGB)."""
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    try:
        update_data = data.model_dump(exclude_unset=True)

        # IMMUTABILITY VALIDATION (GoBD/HGB Compliance)
        update_fields = set(update_data.keys())
        validate_invoice_update(invoice, update_fields)

        # Capture old values for audit log
        old_invoice_data = serialize_for_audit(invoice)

        # Handle line_items separately
        new_line_items = update_data.pop("line_items", None)

        # Update regular fields
        for key, value in update_data.items():
            setattr(invoice, key, value)

        # Update line items if provided
        if new_line_items is not None:
            # Delete existing line items
            db.query(models.InvoiceLineItem).filter(
                models.InvoiceLineItem.invoice_id == invoice_id
            ).delete()

            # Create new line items
            for idx, item_data in enumerate(new_line_items, start=1):
                # Extract only the fields that the model expects
                line_item = models.InvoiceLineItem(
                    invoice_id=invoice_id,
                    position=idx,
                    description=item_data.get('description', ''),
                    quantity=item_data.get('quantity', 1),
                    unit=item_data.get('unit', 'Stück'),
                    unit_price=item_data.get('unit_price', 0),
                    tax_rate=item_data.get('tax_rate', 19),
                    discount_percent=item_data.get('discount_percent', 0),
                )
                db.add(line_item)

            # Recalculate totals
            db.flush()  # Flush to get line_items populated
            db.refresh(invoice)

            subtotal = sum(item.subtotal_after_discount for item in invoice.line_items)
            tax_amount = sum(item.tax_amount for item in invoice.line_items)
            total = subtotal + tax_amount

            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total = total

        db.commit()
        db.refresh(invoice)

        # AUDIT LOG (GoBD Compliance)
        try:
            log_invoice_update(db, invoice, old_invoice_data)
            db.commit()
        except Exception as audit_error:
            print(f"⚠️ Audit logging failed: {audit_error}")

        # Regenerate PDF if line_items were updated
        if new_line_items is not None:
            try:
                # Reload invoice with full relations for PDF generation
                invoice = get_invoice(db, invoice_id)
                pdf_path = _generate_and_save_pdf(db, invoice)
                invoice.pdf_path = pdf_path
                db.commit()
                db.refresh(invoice)
            except Exception as pdf_error:
                # PDF generation error should not fail the update
                print(f"Warning: PDF generation failed: {pdf_error}")

        return invoice

    except HTTPException:
        db.rollback()
        raise  # Re-raise HTTPException with original status code
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")


def update_invoice_status(
    db: Session,
    invoice_id: uuid.UUID,
    new_status: str,
) -> Optional[models.Invoice]:
    """Aktualisiert nur den Status einer Invoice mit State Machine Validation."""
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    valid_statuses = ["draft", "sent", "paid", "partial", "overdue", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    # STATE MACHINE VALIDATION (GoBD Compliance)
    old_status = invoice.status
    validate_invoice_status_change(invoice, new_status)

    invoice.status = new_status
    db.commit()
    db.refresh(invoice)

    # AUDIT LOG (GoBD Compliance)
    try:
        log_invoice_status_change(db, invoice, old_status, new_status)
        db.commit()
    except Exception as audit_error:
        print(f"⚠️ Audit logging failed: {audit_error}")

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

def delete_invoice(db: Session, invoice_id: uuid.UUID, hard_delete: bool = False) -> bool:
    """
    Soft-Delete einer Invoice (GoBD Compliance).

    Markiert Invoice als gelöscht (deleted_at), löscht aber NICHT physisch.
    Dies ermöglicht Audit-Trail und Wiederherstellung.

    Args:
        db: Database Session
        invoice_id: UUID der Invoice
        hard_delete: If True, perform physical deletion (admin only, not recommended)

    Returns:
        True bei Erfolg

    Raises:
        HTTPException 403: Wenn Invoice bezahlt ist (darf nicht gelöscht werden)
        HTTPException 404: Wenn Invoice nicht existiert
    """
    invoice = get_invoice(db, invoice_id, include_deleted=False)
    if not invoice:
        return False

    try:
        # SOFT-DELETE VALIDATION (GoBD Compliance)
        validate_invoice_deletion(invoice)

        if hard_delete:
            # HARD DELETE (nur für Admin-Zwecke, nicht empfohlen)
            # Delete PDF from storage if exists
            if invoice.pdf_path:
                try:
                    storage = get_storage()
                    if storage.exists(invoice.pdf_path):
                        storage.delete(invoice.pdf_path)
                except Exception as e:
                    print(f"⚠️ Failed to delete PDF from storage: {e}")

            db.delete(invoice)
            db.commit()
            return True

        # SOFT DELETE (empfohlen für GoBD)
        invoice.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(invoice)

        # AUDIT LOG (GoBD Compliance)
        try:
            log_invoice_deletion(db, invoice)
            db.commit()
        except Exception as audit_error:
            print(f"⚠️ Audit logging failed: {audit_error}")

        return True

    except HTTPException:
        db.rollback()
        raise  # Re-raise HTTPException with original status code
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")


# ============================================================================
# AUDIT LOGS
# ============================================================================

def get_audit_logs(
    db: Session,
    entity_type: Optional[str] = None,
    entity_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.AuditLog]:
    """
    Holt Audit-Log-Einträge mit Filtern.

    Args:
        db: Database Session
        entity_type: Filter nach Entitätstyp (Invoice, Payment, Expense)
        entity_id: Filter nach Entitäts-ID
        action: Filter nach Aktion (create, update, delete, status_change)
        skip: Pagination offset
        limit: Max Anzahl Ergebnisse

    Returns:
        Liste von AuditLog-Einträgen
    """
    query = db.query(models.AuditLog)

    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(models.AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(models.AuditLog.action == action)

    query = query.order_by(models.AuditLog.timestamp.desc())
    query = query.offset(skip).limit(limit)

    return query.all()


def count_audit_logs(
    db: Session,
    entity_type: Optional[str] = None,
    entity_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
) -> int:
    """Zählt Audit-Log-Einträge mit optionalen Filtern."""
    query = db.query(func.count(models.AuditLog.id))

    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(models.AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(models.AuditLog.action == action)

    return query.scalar()


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
