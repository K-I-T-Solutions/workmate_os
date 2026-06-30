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
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import uuid
import os
import tempfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.core.storage.factory import get_storage
from app.modules.backoffice.invoices import crud, schemas
from app.modules.backoffice.invoices.pdf_generator import generate_invoice_pdf
from app.modules.backoffice.invoices import payments_crud


router = APIRouter(prefix="/backoffice/invoices", tags=["Backoffice Invoices"])


def _pdf_remote_path(invoice_number: str) -> str:
    return f"invoices/{invoice_number}.pdf"


def _generate_and_upload_pdf(invoice, db) -> bytes:
    """PDF generieren, in Storage hochladen, pdf_path in DB speichern. Gibt PDF-Bytes zurück."""
    remote_path = _pdf_remote_path(invoice.invoice_number)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        generate_invoice_pdf(invoice, tmp_path)
        with open(tmp_path, "rb") as f:
            content = f.read()
        get_storage().upload(remote_path, content)
        invoice.pdf_path = remote_path
        db.commit()
        return content
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _get_pdf_bytes(invoice, db) -> bytes:
    """PDF-Bytes holen — aus Storage oder neu generieren."""
    if invoice.pdf_path and not os.path.isabs(invoice.pdf_path):
        try:
            return get_storage().download(invoice.pdf_path)
        except FileNotFoundError:
            pass
    return _generate_and_upload_pdf(invoice, db)


# ============================================================================
# LIST & FILTERS
# ============================================================================

@router.get("/", response_model=schemas.InvoiceListResponse)
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
    "/",
    response_model=schemas.InvoiceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_invoice(
    data: schemas.InvoiceCreate,
    background_tasks: BackgroundTasks,
    generate_pdf: bool = Query(True, description="PDF sofort generieren?"),
    db: Session = Depends(get_db)
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
            invoice = crud.create_invoice(db=db, data=data, generate_pdf=True)
        else:
            # Asynchrone PDF-Generierung via Background Task
            invoice = crud.create_invoice(db=db, data=data, generate_pdf=False)
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
    """Background Task für PDF-Generierung."""
    try:
        invoice = crud.get_invoice(db, invoice_id)
        if invoice and not invoice.pdf_path:
            _generate_and_upload_pdf(invoice, db)
    except Exception as e:
        print(f"❌ Background PDF generation failed: {e}")


# ============================================================================
# UPDATE
# ============================================================================

@router.patch("/{invoice_id}", response_model=schemas.InvoiceResponse)
def update_invoice(
    invoice_id: uuid.UUID,
    data: schemas.InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Invoice aktualisieren (Partial Update).

    **Erlaubte Felder:**
    - status
    - notes
    - terms

    **Nicht änderbar:**
    - invoice_number (einmalig)
    - customer_id (nach Erstellung fixiert)
    - totals (automatisch berechnet)
    """
    invoice = crud.update_invoice(db, invoice_id, data)
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
    db: Session = Depends(get_db)
):
    """
    Nur Status ändern.

    **Erlaubte Status:**
    - draft → sent
    - sent → paid / overdue / cancelled
    - partial → paid / overdue
    """
    invoice = crud.update_invoice_status(db, invoice_id, status_update.status)
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
    db: Session = Depends(get_db)
):
    """
    Invoice löschen.

    **Cascade:**
    - Line Items werden mitgelöscht
    - Payments werden mitgelöscht
    - PDF wird gelöscht (falls vorhanden)
    """
    success = crud.delete_invoice(db, invoice_id)
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

    try:
        content = _get_pdf_bytes(invoice, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PDF-Fehler: {e}")

    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{invoice.invoice_number}.pdf"'},
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
        # Altes PDF aus Storage löschen
        if invoice.pdf_path and not os.path.isabs(invoice.pdf_path):
            try:
                get_storage().delete(invoice.pdf_path)
            except Exception:
                pass
        _generate_and_upload_pdf(invoice, db)
        db.refresh(invoice)
        return invoice
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PDF-Fehler: {e}")


# ============================================================================
# SEND VIA EMAIL
# ============================================================================

class InvoiceSendRequest(BaseModel):
    to_email: EmailStr
    cc_email: Optional[EmailStr] = None
    message: Optional[str] = None


@router.post("/{invoice_id}/send", status_code=status.HTTP_204_NO_CONTENT)
def send_invoice_email(
    invoice_id: uuid.UUID,
    data: InvoiceSendRequest,
    db: Session = Depends(get_db),
):
    """Rechnung per E-Mail versenden (PDF als Anhang). Setzt Status auf 'sent'."""
    from app.core.settings.config import settings

    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    # PDF sicherstellen
    try:
        pdf_bytes = _get_pdf_bytes(invoice, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PDF-Generierung fehlgeschlagen: {e}")

    # E-Mail aufbauen
    msg = MIMEMultipart()
    msg["From"] = f"{settings.NOREPLY_SMTP_FROM_NAME} <{settings.NOREPLY_SMTP_FROM}>"
    msg["To"] = data.to_email
    msg["Subject"] = f"Rechnung {invoice.invoice_number}"
    if data.cc_email:
        msg["Cc"] = data.cc_email

    body = data.message or (
        f"Sehr geehrte Damen und Herren,\n\n"
        f"anbei erhalten Sie unsere Rechnung {invoice.invoice_number}.\n\n"
        f"Mit freundlichen Grüßen\nK.I.T. Solutions"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # PDF anhängen
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{invoice.invoice_number}.pdf"')
    msg.attach(part)

    recipients = [data.to_email]
    if data.cc_email:
        recipients.append(data.cc_email)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(settings.NOREPLY_SMTP_USER, settings.NOREPLY_SMTP_PASSWORD)
            smtp.sendmail(settings.NOREPLY_SMTP_FROM, recipients, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"E-Mail-Versand fehlgeschlagen: {e}")

    # Status auf sent setzen
    crud.update_invoice_status(db, invoice_id, "sent")


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


# ============================================================================
# MAHNWESEN (Reminders)
# ============================================================================

@router.get("/{invoice_id}/reminders", response_model=List[schemas.InvoiceReminderResponse])
def list_reminders(invoice_id: uuid.UUID, db: Session = Depends(get_db)):
    """Alle Mahnungen einer Rechnung."""
    return crud.get_reminders(db, invoice_id)


@router.post(
    "/{invoice_id}/reminders",
    response_model=schemas.InvoiceReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
@require_permissions(["backoffice.invoices"])
def create_reminder(
    invoice_id: uuid.UUID,
    data: schemas.InvoiceReminderCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Neue Mahnung erstellen."""
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return crud.create_reminder(db, invoice_id, data)


@router.patch("/reminders/{reminder_id}", response_model=schemas.InvoiceReminderResponse)
@require_permissions(["backoffice.invoices"])
def update_reminder(
    reminder_id: uuid.UUID,
    data: schemas.InvoiceReminderUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Mahnung aktualisieren."""
    reminder = crud.update_reminder(db, reminder_id, data)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.post("/reminders/{reminder_id}/mark-sent", response_model=schemas.InvoiceReminderResponse)
@require_permissions(["backoffice.invoices"])
def mark_reminder_sent(
    reminder_id: uuid.UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Mahnung als gesendet markieren (setzt sent_at = now)."""
    reminder = crud.mark_reminder_sent(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["backoffice.invoices"])
def delete_reminder(
    reminder_id: uuid.UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Mahnung löschen."""
    success = crud.delete_reminder(db, reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return None
