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
import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import uuid
import os
from io import BytesIO

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.core.errors import ErrorCode, get_error_detail

logger = logging.getLogger(__name__)
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

# ============================================================================
# GoBD EXPORT
# ============================================================================

@router.get("/gobd-export", response_class=StreamingResponse)
def export_gobd_data(
    from_date: Optional[date] = Query(None, description="Start-Datum (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End-Datum (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    GoBD-konformer Export aller Daten als ZIP-Archiv.
    
    **Inhalt:**
    - invoices.csv (alle Rechnungen inkl. gelöschte)
    - invoice_line_items.csv
    - payments.csv
    - audit_logs.csv
    - metadata.json
    - README.txt
    
    **GoBD-Konformität:**
    - ✓ Vollständigkeit (inkl. gelöschter Einträge)
    - ✓ Nachvollziehbarkeit (Audit Trail)
    - ✓ Unveränderbarkeit (Zeitstempel)
    - ✓ Maschinenlesbarkeit (CSV-Format)
    
    **Filter:**
    - `from_date`: Nur Daten ab diesem Datum
    - `to_date`: Nur Daten bis zu diesem Datum
    
    **Verwendung:**
    Für Betriebsprüfungen gemäß § 147 Abs. 6 AO (Datenzugriff).
    """
    from app.modules.backoffice.invoices.gobd_export import generate_gobd_export
    from datetime import datetime
    
    # Convert date to datetime for filtering
    from_datetime = datetime.combine(from_date, datetime.min.time()) if from_date else None
    to_datetime = datetime.combine(to_date, datetime.max.time()) if to_date else None
    
    # Generate export
    zip_buffer = generate_gobd_export(db, from_datetime, to_datetime)
    
    # Generate filename
    date_suffix = ""
    if from_date and to_date:
        date_suffix = f"_{from_date.isoformat()}_to_{to_date.isoformat()}"
    elif from_date:
        date_suffix = f"_from_{from_date.isoformat()}"
    elif to_date:
        date_suffix = f"_until_{to_date.isoformat()}"
    
    filename = f"gobd_export{date_suffix}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

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
        logger.error("❌ Background PDF generation failed: %s", e)


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
@require_permissions(["backoffice.invoices.delete", "backoffice.*"])
def delete_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: RequestContext = Depends(),
    user: dict = Depends(get_current_user)
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


@router.post("/{invoice_id}/restore", response_model=schemas.InvoiceResponse)
@require_permissions(["backoffice.invoices.write", "backoffice.*"])
def restore_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: RequestContext = Depends(),
    user: dict = Depends(get_current_user)
):
    """
    Stellt eine gelöschte Invoice wieder her (Restore).

    **Hinweis:**
    - Nur soft-deleted Invoices können wiederhergestellt werden
    - Hard-deleted Invoices sind permanent gelöscht
    - Audit Log wird erstellt

    **Use Case:**
    - Versehentlich gelöschte Rechnung wiederherstellen
    - Stornierung rückgängig machen
    """
    invoice = crud.restore_invoice(
        db,
        invoice_id,
        user_id=ctx.user_id,
        ip_address=ctx.ip_address
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found or not deleted"
        )

    return invoice


# ============================================================================
# PDF OPERATIONS
# ============================================================================

@router.get("/{invoice_id}/pdf")
@require_permissions(["backoffice.invoices.view", "backoffice.*"])
def download_invoice_pdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
            logger.error("Failed to generate PDF: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_detail(ErrorCode.INVOICE_PDF_FAILED)
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


# ============================================================================
# E-RECHNUNG (XRechnung/ZUGFeRD)
# ============================================================================

@router.get("/{invoice_id}/xrechnung")
@require_permissions(["backoffice.invoices.export", "backoffice.*"])
def download_xrechnung_xml(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    XRechnung-XML herunterladen (EN16931).

    **E-Rechnung Pflicht:** Gemäß § 14 UStG ab 01.01.2025 für B2B.

    **Format:** XML nach EN16931 Standard (XRechnung 3.0)

    **Verwendung:**
    - Öffentliche Auftraggeber (Pflicht)
    - B2B-Rechnungen in Deutschland
    - Automatisierte Rechnungsverarbeitung
    """
    from app.modules.backoffice.invoices.xrechnung_generator import generate_xrechnung_xml

    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    storage = get_storage()

    # XML generieren falls nicht vorhanden
    if not invoice.xml_path or not storage.exists(invoice.xml_path):
        try:
            # XML generieren
            xml_content = generate_xrechnung_xml(invoice)

            # XML-Dateiname und remote path
            xml_filename = f"{invoice.invoice_number}.xml"
            storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
            remote_path = f"{storage_path}/xml/{xml_filename}"

            # XML zu Storage hochladen
            storage.upload(remote_path, xml_content)
            invoice.xml_path = remote_path
            db.commit()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate XRechnung XML: {str(e)}"
            )

    # XML aus Storage herunterladen
    try:
        xml_content = storage.download(invoice.xml_path)
        filename = f"{invoice.invoice_number}_xrechnung.xml"

        return StreamingResponse(
            BytesIO(xml_content),
            media_type="application/xml",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download XRechnung XML: {str(e)}"
        )


@router.get("/{invoice_id}/zugferd")
@require_permissions(["backoffice.invoices.export", "backoffice.*"])
def download_zugferd_pdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    ZUGFeRD-PDF herunterladen (Hybrid-PDF mit eingebetteter XML).

    **Format:** PDF/A-3 mit eingebetteter XRechnung-XML

    **Vorteile:**
    - Menschenlesbar (PDF) + Maschinenlesbar (XML)
    - Kompatibel mit allen PDF-Readern
    - Automatische Verarbeitung möglich
    - GoBD-konform

    **Standard:** ZUGFeRD 2.1 / Factur-X (EN16931 Profil)
    """
    from app.modules.backoffice.invoices.xrechnung_generator import generate_zugferd_pdf

    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    storage = get_storage()

    # ZUGFeRD-PDF generieren falls nicht vorhanden
    if not invoice.zugferd_path or not storage.exists(invoice.zugferd_path):
        try:
            # Erst normales PDF generieren/laden
            if not invoice.pdf_path or not storage.exists(invoice.pdf_path):
                # PDF generieren
                pdf_filename = f"{invoice.invoice_number}.pdf"
                storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
                pdf_remote_path = f"{storage_path}/{pdf_filename}"

                pdf_content = generate_invoice_pdf(invoice, output_path=None)
                if not pdf_content:
                    raise ValueError("PDF generation returned no content")

                storage.upload(pdf_remote_path, pdf_content)
                invoice.pdf_path = pdf_remote_path
                db.commit()

            # PDF laden
            pdf_binary = storage.download(invoice.pdf_path)

            # ZUGFeRD-PDF generieren (PDF mit eingebetteter XML)
            zugferd_content = generate_zugferd_pdf(invoice, pdf_binary)

            # ZUGFeRD-Dateiname und remote path
            zugferd_filename = f"{invoice.invoice_number}_zugferd.pdf"
            storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
            remote_path = f"{storage_path}/zugferd/{zugferd_filename}"

            # ZUGFeRD-PDF zu Storage hochladen
            storage.upload(remote_path, zugferd_content)
            invoice.zugferd_path = remote_path
            db.commit()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate ZUGFeRD PDF: {str(e)}"
            )

    # ZUGFeRD-PDF aus Storage herunterladen
    try:
        zugferd_content = storage.download(invoice.zugferd_path)
        filename = f"{invoice.invoice_number}_zugferd.pdf"

        return StreamingResponse(
            BytesIO(zugferd_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download ZUGFeRD PDF: {str(e)}"
        )


@router.post("/{invoice_id}/regenerate-pdf", response_model=schemas.InvoiceResponse)
@require_permissions(["backoffice.invoices.write", "backoffice.*"])
def regenerate_pdf(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
# SEND PER MAIL
# ============================================================================

@router.post("/{invoice_id}/send", status_code=200)
@require_permissions(["backoffice.invoices.write", "backoffice.*"])
def send_invoice_by_email(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
    ctx: RequestContext = Depends()
):
    """
    Rechnung per E-Mail an den Kunden senden.

    - PDF wird generiert (falls nicht vorhanden)
    - E-Mail geht an die Kunden-E-Mail-Adresse
    - Status wird automatisch auf 'sent' gesetzt
    - Audit Log Eintrag wird erstellt
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication

    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")

    # Kunden-E-Mail ermitteln
    customer = invoice.customer
    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invoice has no customer assigned")

    recipient_email = customer.email
    recipient_name = customer.name or customer.company_name or "Kunde"

    if not recipient_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer has no email address")

    # PDF generieren / laden
    storage = get_storage()
    if not invoice.pdf_path or not storage.exists(invoice.pdf_path):
        try:
            pdf_filename = f"{invoice.invoice_number}.pdf"
            storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
            remote_path = f"{storage_path}/{pdf_filename}"
            pdf_content = generate_invoice_pdf(invoice, output_path=None)
            if not pdf_content:
                raise ValueError("PDF generation returned no content")
            storage.upload(remote_path, pdf_content)
            invoice.pdf_path = remote_path
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PDF generation failed: {e}")

    pdf_bytes = storage.download(invoice.pdf_path)
    pdf_filename = f"{invoice.invoice_number}.pdf"

    # Betreff & Typ-Label
    doc_type_labels = {
        "invoice": "Rechnung",
        "quote": "Angebot",
        "credit_note": "Gutschrift",
        "order_confirmation": "Auftragsbestätigung",
    }
    doc_label = doc_type_labels.get(invoice.document_type, "Dokument")
    subject = f"{doc_label} {invoice.invoice_number} – K.I.T. Solutions"

    total_str = f"{float(invoice.total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

    html_body = f"""<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0f1e;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="height:4px;background:linear-gradient(90deg,#FF6B35 0%,#3B82F6 50%,#06B6D4 100%);border-radius:4px 4px 0 0;"></div>
    <div style="background:#0F1629;padding:28px 32px 24px;border-left:1px solid #1E2D4A;border-right:1px solid #1E2D4A;">
      <span style="font-size:22px;font-weight:700;color:#ffffff;">K.I.T.</span>
      <span style="font-size:22px;font-weight:300;color:#FF6B35;"> Solutions</span>
      <p style="margin:4px 0 0;color:#64748b;font-size:13px;letter-spacing:0.05em;text-transform:uppercase;">Buchhaltung</p>
    </div>
    <div style="background:#1E2D4A;padding:32px;border-left:1px solid #263a5a;border-right:1px solid #263a5a;">
      <p style="color:#e2e8f0;font-size:16px;margin:0 0 12px;">Guten Tag {recipient_name},</p>
      <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin:0 0 24px;">
        im Anhang finden Sie Ihre {doc_label} von K.I.T. Solutions.
      </p>
      <div style="background:#0F1629;border:1px solid #263a5a;border-left:4px solid #FF6B35;border-radius:8px;padding:20px 24px;margin:0 0 24px;">
        <table style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;padding-bottom:6px;">{doc_label}</td>
            <td style="color:#FF6B35;font-size:18px;font-weight:700;font-family:'Courier New',monospace;text-align:right;">{invoice.invoice_number}</td>
          </tr>
          <tr>
            <td style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;padding-top:10px;border-top:1px solid #1E2D4A;">Betrag (brutto)</td>
            <td style="color:#e2e8f0;font-size:16px;font-weight:600;text-align:right;padding-top:10px;border-top:1px solid #1E2D4A;">{total_str}</td>
          </tr>
        </table>
      </div>
      <p style="color:#94a3b8;font-size:14px;line-height:1.6;margin:0;">
        Bei Fragen stehen wir Ihnen jederzeit zur Verfügung.
      </p>
    </div>
    <div style="background:#0F1629;padding:20px 32px;border:1px solid #1E2D4A;border-top:none;border-radius:0 0 4px 4px;">
      <p style="margin:0;color:#475569;font-size:12px;line-height:1.8;">
        <span style="color:#FF6B35;font-weight:600;">K.I.T. Solutions</span> &bull;
        <a href="mailto:support@kit-it-koblenz.de" style="color:#3B82F6;text-decoration:none;">support@kit-it-koblenz.de</a>
      </p>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,#06B6D4 0%,#3B82F6 50%,#FF6B35 100%);border-radius:0 0 4px 4px;"></div>
  </div>
</body>
</html>"""

    plain_body = (
        f"Guten Tag {recipient_name},\n\n"
        f"im Anhang finden Sie Ihre {doc_label} {invoice.invoice_number} "
        f"über {total_str} von K.I.T. Solutions.\n\n"
        f"Bei Fragen: support@kit-it-koblenz.de\n\n"
        f"Mit freundlichen Grüßen\nK.I.T. Solutions"
    )

    # Mail zusammenbauen
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
    msg["To"] = recipient_email

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(plain_body, "plain", "utf-8"))
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)

    pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    pdf_attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
    msg.attach(pdf_attachment)

    # SMTP senden
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.SMTP_FROM, [recipient_email], msg.as_bytes())
        logger.info("✉️ Rechnung %s an %s gesendet", invoice.invoice_number, recipient_email)
    except Exception as e:
        logger.error("❌ Mail-Versand fehlgeschlagen: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Mail-Versand fehlgeschlagen: {e}")

    # Status auf 'sent' setzen (nur wenn noch draft)
    if invoice.status == "draft":
        crud.update_invoice_status(db, invoice_id, "sent", user_id=ctx.user_id, ip_address=ctx.ip_address)

    return {"ok": True, "sent_to": recipient_email, "invoice_number": invoice.invoice_number}


# ============================================================================
# DATEV EXPORT
# ============================================================================

@router.get("/datev-export")
@require_permissions(["backoffice.invoices.export", "backoffice.*"])
def export_datev(
    from_date: Optional[date] = Query(None, description="Rechnungsdatum ab (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Rechnungsdatum bis (YYYY-MM-DD)"),
    only_paid: bool = Query(False, description="Nur bezahlte Rechnungen exportieren"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    DATEV EXTF Buchungsstapel Export.

    **Format:** DATEV EXTF Buchungsstapel v700, CP1252, Semikolon-getrennt

    **Kontenrahmen:** SKR03
    - Erlöse 19% MwSt → 8400
    - Erlöse  7% MwSt → 8300
    - Erlöse  0% MwSt → 8100
    - Debitor (Kunde) → 10000

    **Verwendung:** Direkt in DATEV Unternehmen online importierbar.
    Exportierte Datei an Steuerberater weitergeben.

    **Filter:**
    - `from_date` / `to_date`: Datumsbereich
    - `only_paid`: Nur abgeschlossene Buchungen
    """
    from app.modules.backoffice.invoices.datev_export import generate_datev_extf

    csv_bytes = generate_datev_extf(
        db=db,
        from_date=from_date,
        to_date=to_date,
        only_paid=only_paid,
    )

    date_suffix = ""
    if from_date and to_date:
        date_suffix = f"_{from_date.isoformat()}_bis_{to_date.isoformat()}"
    elif from_date:
        date_suffix = f"_ab_{from_date.isoformat()}"

    filename = f"DATEV_Buchungsstapel{date_suffix}_{datetime.now().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv; charset=cp1252",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# ============================================================================
# MAHNWESEN (INVOICE REMINDERS)
# ============================================================================

# Konfiguration der Mahnstufen
REMINDER_DEFAULTS = {
    1: {"fee": 0.00,  "label": "Zahlungserinnerung", "days_extra": 7},
    2: {"fee": 5.00,  "label": "1. Mahnung",          "days_extra": 7},
    3: {"fee": 15.00, "label": "2. Mahnung (Letzte)",  "days_extra": 7},
}


@router.get("/{invoice_id}/reminders", response_model=list[schemas.ReminderResponse])
@require_permissions(["backoffice.invoices.view", "backoffice.*"])
def list_reminders(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Alle Mahnungen einer Rechnung abrufen."""
    from app.modules.backoffice.invoices.models import InvoiceReminder
    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")
    return db.query(InvoiceReminder).filter(InvoiceReminder.invoice_id == invoice_id).order_by(InvoiceReminder.level).all()


@router.post("/{invoice_id}/reminders", response_model=schemas.ReminderResponse, status_code=201)
@require_permissions(["backoffice.invoices.write", "backoffice.*"])
def create_reminder(
    invoice_id: uuid.UUID,
    data: schemas.ReminderCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
    ctx: RequestContext = Depends()
):
    """
    Mahnung erstellen und optional per E-Mail senden.

    **Stufen:**
    - 1 = Zahlungserinnerung (0 € Gebühr)
    - 2 = 1. Mahnung (5 € Gebühr)
    - 3 = 2. Mahnung / Letzte Mahnung (15 € Gebühr)

    **Regeln:**
    - Pro Stufe nur eine Mahnung pro Rechnung
    - Rechnung muss Status sent/overdue haben
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from datetime import timedelta
    from app.modules.backoffice.invoices.models import InvoiceReminder

    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice {invoice_id} not found")

    if invoice.status not in ("sent", "overdue", "partial"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mahnungen nur für Rechnungen mit Status sent/overdue/partial möglich (aktuell: {invoice.status})"
        )

    # Doppelte Mahnstufe verhindern
    existing = db.query(InvoiceReminder).filter(
        InvoiceReminder.invoice_id == invoice_id,
        InvoiceReminder.level == data.level
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Mahnstufe {data.level} für diese Rechnung existiert bereits"
        )

    # Fälligkeit berechnen
    defaults = REMINDER_DEFAULTS[data.level]
    due_date = data.due_date or (
        (invoice.due_date or invoice.issued_date) + timedelta(days=defaults["days_extra"] * data.level)
        if (invoice.due_date or invoice.issued_date) else None
    )

    fee = data.fee if data.fee is not None else defaults["fee"]
    level_label = defaults["label"]

    # Mahnung in DB anlegen
    reminder = InvoiceReminder(
        invoice_id=invoice_id,
        level=data.level,
        fee=fee,
        due_date=due_date,
        notes=data.notes,
    )
    db.add(reminder)
    db.flush()  # ID erzeugen

    # E-Mail senden
    if data.send_email:
        customer = invoice.customer
        recipient_email = customer.email if customer else None
        recipient_name = (customer.name or customer.company_name or "Kunde") if customer else "Kunde"

        if not recipient_email:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kunden-E-Mail-Adresse fehlt – Mahnung kann nicht gesendet werden"
            )

        total_str = f"{float(invoice.total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        fee_str = f"{float(fee):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        due_str = due_date.strftime("%d.%m.%Y") if due_date else "–"
        subject = f"{level_label} – {invoice.invoice_number} – K.I.T. Solutions"

        # Border-Farbe nach Stufe
        level_color = {1: "#06B6D4", 2: "#FF6B35", 3: "#ef4444"}.get(data.level, "#FF6B35")

        if data.level == 1:
            intro = (
                f"wir möchten Sie freundlich daran erinnern, dass die Zahlung für "
                f"Rechnung <strong>{invoice.invoice_number}</strong> noch aussteht."
            )
        elif data.level == 2:
            intro = (
                f"trotz unserer Zahlungserinnerung ist die Zahlung für Rechnung "
                f"<strong>{invoice.invoice_number}</strong> noch nicht bei uns eingegangen."
            )
        else:
            intro = (
                f"leider müssen wir Sie letztmalig an die ausstehende Zahlung für Rechnung "
                f"<strong>{invoice.invoice_number}</strong> erinnern. Bitte beachten Sie, dass "
                f"bei weiterer Nichtbeachtung rechtliche Schritte eingeleitet werden."
            )

        fee_row = ""
        if float(fee) > 0:
            fee_row = f"""
          <tr>
            <td style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;padding-top:10px;border-top:1px solid #1E2D4A;">Mahngebühr</td>
            <td style="color:#ef4444;font-size:14px;font-weight:600;text-align:right;padding-top:10px;border-top:1px solid #1E2D4A;">{fee_str}</td>
          </tr>"""

        html_body = f"""<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0f1e;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="height:4px;background:linear-gradient(90deg,#FF6B35 0%,#3B82F6 50%,#06B6D4 100%);border-radius:4px 4px 0 0;"></div>
    <div style="background:#0F1629;padding:28px 32px 24px;border-left:1px solid #1E2D4A;border-right:1px solid #1E2D4A;">
      <span style="font-size:22px;font-weight:700;color:#ffffff;">K.I.T.</span>
      <span style="font-size:22px;font-weight:300;color:#FF6B35;"> Solutions</span>
      <p style="margin:4px 0 0;color:#64748b;font-size:13px;letter-spacing:0.05em;text-transform:uppercase;">{level_label}</p>
    </div>
    <div style="background:#1E2D4A;padding:32px;border-left:1px solid #263a5a;border-right:1px solid #263a5a;">
      <p style="color:#e2e8f0;font-size:16px;margin:0 0 12px;">Guten Tag {recipient_name},</p>
      <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin:0 0 24px;">{intro}</p>
      <div style="background:#0F1629;border:1px solid #263a5a;border-left:4px solid {level_color};border-radius:8px;padding:20px 24px;margin:0 0 24px;">
        <table style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;padding-bottom:6px;">Rechnungsnummer</td>
            <td style="color:#FF6B35;font-size:18px;font-weight:700;font-family:'Courier New',monospace;text-align:right;">{invoice.invoice_number}</td>
          </tr>
          <tr>
            <td style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;padding-top:10px;border-top:1px solid #1E2D4A;">Offener Betrag</td>
            <td style="color:#e2e8f0;font-size:16px;font-weight:600;text-align:right;padding-top:10px;border-top:1px solid #1E2D4A;">{total_str}</td>
          </tr>{fee_row}
          <tr>
            <td style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;padding-top:10px;border-top:1px solid #1E2D4A;">Bitte zahlen bis</td>
            <td style="color:{level_color};font-size:15px;font-weight:600;text-align:right;padding-top:10px;border-top:1px solid #1E2D4A;">{due_str}</td>
          </tr>
        </table>
      </div>
      <p style="color:#94a3b8;font-size:14px;line-height:1.6;margin:0;">
        Bitte überweisen Sie den Betrag auf unser Konto:<br>
        <strong style="color:#e2e8f0;">IBAN:</strong> <span style="color:#94a3b8;">DE94 1001 1001 2706 4711 70</span> &bull; N26 Bank
      </p>
    </div>
    <div style="background:#0F1629;padding:20px 32px;border:1px solid #1E2D4A;border-top:none;border-radius:0 0 4px 4px;">
      <p style="margin:0;color:#475569;font-size:12px;line-height:1.8;">
        <span style="color:#FF6B35;font-weight:600;">K.I.T. Solutions</span> &bull;
        <a href="mailto:support@kit-it-koblenz.de" style="color:#3B82F6;text-decoration:none;">support@kit-it-koblenz.de</a>
      </p>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,#06B6D4 0%,#3B82F6 50%,#FF6B35 100%);border-radius:0 0 4px 4px;"></div>
  </div>
</body>
</html>"""

        plain_body = (
            f"Guten Tag {recipient_name},\n\n"
            f"{level_label}: Rechnung {invoice.invoice_number}\n"
            f"Offener Betrag: {total_str}\n"
            f"Bitte zahlen bis: {due_str}\n\n"
            f"IBAN: DE94 1001 1001 2706 4711 70 (N26 Bank)\n\n"
            f"Bei Fragen: support@kit-it-koblenz.de\n\nK.I.T. Solutions"
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.sendmail(settings.SMTP_FROM, [recipient_email], msg.as_bytes())

            from datetime import timezone
            reminder.sent_at = datetime.now(timezone.utc)
            logger.info("📬 Mahnstufe %d für %s an %s gesendet", data.level, invoice.invoice_number, recipient_email)
        except Exception as e:
            logger.error("❌ Mahnungs-Mail fehlgeschlagen: %s", e)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Mahnung konnte nicht gesendet werden: {e}"
            )

    # Rechnung auf overdue setzen wenn noch sent
    if invoice.status == "sent":
        crud.update_invoice_status(db, invoice_id, "overdue", user_id=ctx.user_id, ip_address=ctx.ip_address)

    db.commit()
    db.refresh(reminder)
    return reminder


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/bulk/status-update", response_model=schemas.BulkUpdateResponse)
@require_permissions(["backoffice.invoices.approve", "backoffice.*"])
def bulk_update_status(
    data: schemas.BulkStatusUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
            logger.error("❌ Failed to update %s: %s", invoice_id, e)

    return schemas.BulkUpdateResponse(
        success_count=success_count,
        failed_count=len(failed_ids),
        failed_ids=failed_ids
    )


@router.post("/{invoice_id}/validate-xrechnung")
@require_permissions(["backoffice.invoices.view", "backoffice.*"])
def validate_xrechnung_endpoint(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Validiert XRechnung-XML gegen EN16931 Standard.

    **Prüfungen:**
    1. XML Syntax (Well-Formed)
    2. XML Struktur (Pflichtfelder)
    3. Business Rules (Basic)

    **Standards:**
    - EN 16931: Europäische Norm
    - XRechnung 3.0: Deutscher CIUS

    **Returns:**
    ```json
    {
        "valid": true,
        "syntax_check": {...},
        "structure_check": {...},
        "errors": [],
        "warnings": [],
        "summary": "✅ XRechnung validation passed"
    }
    ```
    """
    from app.modules.backoffice.invoices.xrechnung_validator import validate_xrechnung

    invoice = crud.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    storage = get_storage()

    # XRechnung XML generieren falls nicht vorhanden
    if not invoice.xml_path or not storage.exists(invoice.xml_path):
        from app.modules.backoffice.invoices.xrechnung_generator import generate_xrechnung_xml

        xml_content = generate_xrechnung_xml(invoice)

        # Speichern
        filename = f"{invoice.invoice_number}_xrechnung.xml"
        xml_path = f"invoices/xrechnung/{invoice.invoice_number}/{filename}"
        storage.upload(xml_path, xml_content)

        invoice.xml_path = xml_path
        db.commit()
    else:
        # XML aus Storage laden
        xml_content = storage.download(invoice.xml_path)

    # Validierung durchführen
    validation_result = validate_xrechnung(xml_content)

    return {
        "invoice_id": str(invoice_id),
        "invoice_number": invoice.invoice_number,
        "xml_path": invoice.xml_path,
        **validation_result
    }


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/{invoice_id}/payments", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["backoffice.invoices.write", "backoffice.*"])
def add_payment(
    invoice_id: uuid.UUID,
    data: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
@require_permissions(["backoffice.invoices.view", "backoffice.*"])
def list_invoice_payments(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
@require_permissions(["backoffice.invoices.view", "backoffice.*"])
def get_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
@require_permissions(["backoffice.invoices.write", "backoffice.*"])
def update_payment(
    payment_id: uuid.UUID,
    data: schemas.PaymentUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
@require_permissions(["backoffice.invoices.delete", "backoffice.*"])
def delete_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
# RETENTION POLICY (GoBD § 147 AO)
# ============================================================================

@router.get("/retention/report")
@require_permissions(["backoffice.invoices.view", "backoffice.*"])
def get_retention_report_endpoint(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Retention Policy Report.

    Zeigt Statistiken über soft-deleted Invoices und Retention Status.

    **GoBD Compliance:**
    - § 147 AO: 10 Jahre Aufbewahrungspflicht
    - § 257 HGB: 10 Jahre für Handelsbriefe
    - Frist beginnt mit Schluss des Kalenderjahrs

    **Returns:**
    - Retention-Deadline
    - Anzahl soft-deleted Invoices
    - Anzahl eligible für Hard-Delete
    - Liste aller eligible Invoices
    """
    from app.modules.backoffice.invoices.retention import get_retention_report

    report = get_retention_report(db)
    return report


@router.post("/retention/cleanup")
@require_permissions(["backoffice.invoices.delete", "backoffice.*"])
def execute_retention_cleanup_endpoint(
    dry_run: bool = Query(default=True, description="Nur simulieren (kein echtes Löschen)"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Führt Retention Policy Cleanup aus.

    Löscht alle Invoices die älter als 10 Jahre sind (Hard-Delete).

    **WARNUNG:**
    Dies ist IRREVERSIBEL! Invoices werden permanent gelöscht.

    **Parameter:**
    - dry_run=true: Simulation (kein echtes Löschen) - EMPFOHLEN zum Testen!
    - dry_run=false: Echtes Löschen (VORSICHT!)

    **GoBD Compliance:**
    - § 147 AO: Nach 10 Jahren dürfen Invoices gelöscht werden
    - Audit Log wird erstellt vor Löschung

    **Returns:**
    - Statistiken über gelöschte Invoices
    """
    from app.modules.backoffice.invoices.retention import hard_delete_expired_invoices

    stats = hard_delete_expired_invoices(db, dry_run=dry_run)

    return {
        "success": stats["failed"] == 0,
        "stats": stats,
        "warning": "DRY RUN - Keine echten Änderungen" if dry_run else "ECHTES LÖSCHEN durchgeführt!"
    }


