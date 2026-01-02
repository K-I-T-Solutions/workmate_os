# app/modules/backoffice/invoices/routes.py
"""
WorkmateOS - Invoices Routes (IMPROVED)

CHANGES:
- ✅ Pagination (skip, limit)
- ✅ Filters (status, customer_id, date_range)
- ✅ Statistics endpoint
- ✅ Background Tasks für PDF generation
- ✅ Proper HTTP status codes
- ✅ Better error handling
- ✅ Bulk operations
- ✅ Recalculate endpoint
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import uuid
import os
from io import BytesIO

from app.core.settings.database import get_db
from app.modules.backoffice.invoices import crud, schemas
from app.modules.backoffice.invoices.pdf_generator import generate_invoice_pdf
from app.modules.backoffice.invoices import payments_crud
from app.modules.backoffice.invoices.dependencies import RequestContext
from app.core.storage.factory import get_storage
from app.core.settings.config import settings


router = APIRouter(prefix="/backoffice/invoices", tags=["Backoffice Invoices"])


# ============================================================================
# LIST & FILTERS
# ============================================================================

@router.get("", response_model=schemas.InvoiceListResponse)
def list_invoices(
    skip: int = Query(0, ge=0, description="Offset für Pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max Anzahl Ergebnisse"),
    status: Optional[str] = Query(None, description="Filter nach Status"),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter nach Kunde"),
    project_id: Optional[uuid.UUID] = Query(None, description="Filter nach Projekt"),
    date_from: Optional[date] = Query(None, description="Rechnungsdatum ab"),
    date_to: Optional[date] = Query(None, description="Rechnungsdatum bis"),
    db: Session = Depends(get_db)
):
    """
    Liste aller Invoices mit Pagination und Filtern.

    **Filter-Optionen:**
    - `status`: draft, sent, paid, partial, overdue, cancelled
    - `customer_id`: UUID des Kunden
    - `project_id`: UUID des Projekts
    - `date_from` / `date_to`: Datumsbereich

    **Pagination:**
    - `skip`: Offset (Standard: 0)
    - `limit`: Max Anzahl (Standard: 100, Max: 500)
    """
    invoices = crud.get_invoices(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        customer_id=customer_id,
        project_id=project_id,
        date_from=date_from,
        date_to=date_to
    )

    total = crud.count_invoices(db=db, status=status, customer_id=customer_id)

    return schemas.InvoiceListResponse(
        items=invoices,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/statistics", response_model=schemas.InvoiceStatisticsResponse)
def get_statistics(
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter nach Kunde"),
    db: Session = Depends(get_db)
):
    """
    Statistiken über Invoices.

    **Metriken:**
    - Gesamtumsatz (paid invoices)
    - Offene Forderungen
    - Anzahl überfälliger Rechnungen
    - Anzahl nach Status
    """
    stats = crud.get_invoice_statistics(db=db, customer_id=customer_id)
    return schemas.InvoiceStatisticsResponse(**stats)


# ============================================================================
# AUDIT LOGS (GoBD COMPLIANCE)
# ============================================================================

@router.get("/audit-logs", response_model=schemas.AuditLogListResponse)
def list_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter nach Entitätstyp (Invoice, Payment, Expense)"),
    entity_id: Optional[uuid.UUID] = Query(None, description="Filter nach Entitäts-ID"),
    action: Optional[str] = Query(None, description="Filter nach Aktion (create, update, delete, status_change)"),
    skip: int = Query(0, ge=0, description="Offset für Pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max Anzahl Ergebnisse"),
    db: Session = Depends(get_db)
):
    """
    Liste aller Audit-Log-Einträge mit Pagination und Filtern.

    **Compliance:** Erfüllt GoBD-Anforderungen für lückenlose Nachvollziehbarkeit.

    **Filter-Optionen:**
    - `entity_type`: Invoice, Payment, Expense
    - `entity_id`: UUID der Entität
    - `action`: create, update, delete, status_change

    **Pagination:**
    - `skip`: Offset (Standard: 0)
    - `limit`: Max Anzahl (Standard: 100, Max: 500)
    """
    logs = crud.get_audit_logs(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        skip=skip,
        limit=limit
    )

    total = crud.count_audit_logs(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action
    )

    return schemas.AuditLogListResponse(
        items=logs,
        total=total,
        skip=skip,
        limit=limit
    )


# ============================================================================
# SINGLE INVOICE
# ============================================================================

@router.get("/{invoice_id}", response_model=schemas.InvoiceResponse)
def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Einzelne Invoice abrufen."""
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )
    return invoice


@router.get("/by-number/{invoice_number}", response_model=schemas.InvoiceResponse)
def get_invoice_by_number(
    invoice_number: str,
    db: Session = Depends(get_db)
):
    """Invoice nach Rechnungsnummer abrufen."""
    invoice = crud.get_invoice_by_number(db, invoice_number)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice '{invoice_number}' not found"
        )
    return invoice


# ============================================================================
# CREATE
# ============================================================================

@router.post(
    "",
    response_model=schemas.InvoiceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_invoice(
    data: schemas.InvoiceCreate,
    background_tasks: BackgroundTasks,
    generate_pdf: bool = Query(True, description="PDF sofort generieren?"),
    db: Session = Depends(get_db),
    ctx: RequestContext = Depends()
):
    """
    Neue Invoice erstellen.

    **PDF-Generierung:**
    - `generate_pdf=true`: PDF wird sofort erstellt (synchron)
    - `generate_pdf=false`: PDF wird im Hintergrund erstellt (async)

    **Line Items:**
    - Mindestens 1 Line Item erforderlich
    - Position wird automatisch gesetzt
    - Totals werden automatisch berechnet
    """
    try:
        if generate_pdf:
            # Synchrone PDF-Generierung
            invoice = crud.create_invoice(
                db=db,
                data=data,
                generate_pdf=True,
                user_id=ctx.user_id,
                ip_address=ctx.ip_address
            )
        else:
            # Asynchrone PDF-Generierung via Background Task
            invoice = crud.create_invoice(
                db=db,
                data=data,
                generate_pdf=False,
                user_id=ctx.user_id,
                ip_address=ctx.ip_address
            )
            background_tasks.add_task(
                _generate_pdf_background,
                invoice.id,
                db
            )

        return invoice

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}"
        )


def _generate_pdf_background(invoice_id: uuid.UUID, db: Session):
    """Background Task für PDF-Generierung mit Storage-Backend."""
    try:
        invoice = crud.get_invoice(db, invoice_id)
        if invoice and not invoice.pdf_path:
            storage = get_storage()

            # PDF-Dateiname und remote path
            pdf_filename = f"{invoice.invoice_number}.pdf"
            storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
            remote_path = f"{storage_path}/{pdf_filename}"

            # PDF als Bytes generieren
            pdf_content = generate_invoice_pdf(invoice, output_path=None)

            if pdf_content:
                # PDF zu Storage hochladen
                storage.upload(remote_path, pdf_content)
                invoice.pdf_path = remote_path
                db.commit()

    except Exception as e:
        print(f"❌ Background PDF generation failed: {e}")


# ============================================================================
# UPDATE
# ============================================================================

@router.patch("/{invoice_id}", response_model=schemas.InvoiceResponse)
def update_invoice(
    invoice_id: uuid.UUID,
    data: schemas.InvoiceUpdate,
    db: Session = Depends(get_db),
    ctx: RequestContext = Depends()
):
    """
    Invoice aktualisieren (Partial Update).

    **Erlaubte Felder:**
    - status
    - notes
    - terms
    - line_items (ersetzt ALLE Positionen!)

    **Nicht änderbar:**
    - invoice_number (einmalig)
    - customer_id (nach Erstellung fixiert)
    - totals (automatisch berechnet)

    **Wichtig:** Wenn line_items übergeben werden, werden alle existierenden Positionen gelöscht und durch die neuen ersetzt!
    """
    invoice = crud.update_invoice(db, invoice_id, data, user_id=ctx.user_id, ip_address=ctx.ip_address)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )
    return invoice


@router.patch("/{invoice_id}/status", response_model=schemas.InvoiceResponse)
def update_invoice_status(
    invoice_id: uuid.UUID,
    status_update: schemas.InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    ctx: RequestContext = Depends()
):
    """
    Nur Status ändern.

    **Erlaubte Status:**
    - draft → sent
    - sent → paid / overdue / cancelled
    - partial → paid / overdue
    """
    invoice = crud.update_invoice_status(db, invoice_id, status_update.status, user_id=ctx.user_id, ip_address=ctx.ip_address)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )
    return invoice


@router.post("/{invoice_id}/recalculate", response_model=schemas.InvoiceResponse)
def recalculate_totals(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Totals neu berechnen (z.B. nach manueller Line-Item-Änderung).

    Berechnet:
    - subtotal
    - tax_amount
    - total
    """
    invoice = crud.recalculate_invoice_totals(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )
    return invoice


# ============================================================================
# DELETE
# ============================================================================

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: RequestContext = Depends()
):
    """
    Invoice löschen.

    **Cascade:**
    - Line Items werden mitgelöscht
    - Payments werden mitgelöscht
    - PDF wird gelöscht (falls vorhanden)
    """
    success = crud.delete_invoice(db, invoice_id, user_id=ctx.user_id, ip_address=ctx.ip_address)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )
    return None


# ============================================================================
# PDF OPERATIONS
# ============================================================================

@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    PDF herunterladen.

    **Falls PDF fehlt:** Wird automatisch generiert.
    """
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    storage = get_storage()

    # PDF generieren falls nicht vorhanden
    if not invoice.pdf_path or not storage.exists(invoice.pdf_path):
        try:
            # PDF-Dateiname und remote path
            pdf_filename = f"{invoice.invoice_number}.pdf"
            storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
            remote_path = f"{storage_path}/{pdf_filename}"

            # PDF als Bytes generieren
            pdf_content = generate_invoice_pdf(invoice, output_path=None)

            if not pdf_content:
                raise ValueError("PDF generation returned no content")

            # PDF zu Storage hochladen
            storage.upload(remote_path, pdf_content)
            invoice.pdf_path = remote_path
            db.commit()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF: {str(e)}"
            )

    # PDF aus Storage herunterladen
    try:
        pdf_content = storage.download(invoice.pdf_path)
        filename = f"{invoice.invoice_number}.pdf"

        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download PDF: {str(e)}"
        )


@router.post("/{invoice_id}/regenerate-pdf", response_model=schemas.InvoiceResponse)
def regenerate_pdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    PDF neu generieren (z.B. nach Template-Änderung).
    """
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    try:
        storage = get_storage()

        # Altes PDF aus Storage löschen
        if invoice.pdf_path and storage.exists(invoice.pdf_path):
            storage.delete(invoice.pdf_path)

        # PDF-Dateiname und remote path
        pdf_filename = f"{invoice.invoice_number}.pdf"
        storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
        remote_path = f"{storage_path}/{pdf_filename}"

        # Neues PDF generieren
        pdf_content = generate_invoice_pdf(invoice, output_path=None)

        if not pdf_content:
            raise ValueError("PDF generation returned no content")

        # PDF zu Storage hochladen
        storage.upload(remote_path, pdf_content)
        invoice.pdf_path = remote_path
        db.commit()
        db.refresh(invoice)

        return invoice

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate PDF: {str(e)}"
        )


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/bulk/status-update", response_model=schemas.BulkUpdateResponse)
def bulk_update_status(
    data: schemas.BulkStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Status für mehrere Invoices gleichzeitig ändern.

    **Beispiel:** Alle draft Invoices auf sent setzen.
    """
    success_count = 0
    failed_ids = []

    for invoice_id in data.invoice_ids:
        try:
            invoice = crud.update_invoice_status(db, invoice_id, data.new_status)
            if invoice:
                success_count += 1
            else:
                failed_ids.append(str(invoice_id))
        except Exception as e:
            failed_ids.append(str(invoice_id))
            print(f"❌ Failed to update {invoice_id}: {e}")

    return schemas.BulkUpdateResponse(
        success_count=success_count,
        failed_count=len(failed_ids),
        failed_ids=failed_ids
    )


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/{invoice_id}/payments", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
def add_payment(
    invoice_id: uuid.UUID,
    data: schemas.PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Zahlung zu Invoice hinzufügen.

    **Auto-Status-Update:**
    - Wenn vollständig bezahlt → Status: paid
    - Wenn teilweise bezahlt → Status: partial

    **Validierung:**
    - Betrag darf nicht höher als outstanding_amount sein
    """
    return payments_crud.create_payment(db=db, invoice_id=invoice_id, data=data)


@router.get("/{invoice_id}/payments", response_model=List[schemas.PaymentResponse])
def list_invoice_payments(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Liste aller Payments für eine Invoice."""
    # Prüfe ob Invoice existiert
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    return payments_crud.get_payments(db=db, invoice_id=invoice_id)


@router.get("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Einzelnes Payment abrufen."""
    payment = payments_crud.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found"
        )
    return payment


@router.patch("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def update_payment(
    payment_id: uuid.UUID,
    data: schemas.PaymentUpdate,
    db: Session = Depends(get_db)
):
    """Payment aktualisieren."""
    payment = payments_crud.update_payment(db, payment_id, data)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found"
        )
    return payment


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Payment löschen."""
    success = payments_crud.delete_payment(db, payment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found"
        )
    return None
