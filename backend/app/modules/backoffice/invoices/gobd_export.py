"""
GoBD Export-Funktion für Betriebsprüfungen

Exportiert alle buchhalterischen Daten gemäß GoBD-Anforderungen:
- Unveränderbarkeit
- Vollständigkeit
- Nachvollziehbarkeit
- Maschinenlesbarkeit
"""
import csv
import json
import zipfile
from io import BytesIO, StringIO
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.modules.backoffice.invoices import models


def generate_gobd_export(
    db: Session,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> BytesIO:
    """
    Generiert GoBD-konformen Export als ZIP-Archiv.
    
    Enthält:
    - invoices.csv (alle Rechnungen inkl. gelöschte)
    - invoice_line_items.csv
    - payments.csv
    - audit_logs.csv
    - metadata.json
    
    Args:
        db: Database Session
        from_date: Optional Start-Datum für Filter
        to_date: Optional End-Datum für Filter
        
    Returns:
        BytesIO mit ZIP-Archiv
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Metadata
        metadata = {
            "export_date": datetime.utcnow().isoformat(),
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None,
            "format": "CSV",
            "encoding": "UTF-8",
            "compliance": "GoBD",
            "generator": "WorkmateOS Invoice Module"
        }
        zip_file.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        # 2. Invoices (inkl. soft-deleted)
        invoices_csv = _export_invoices_csv(db, from_date, to_date)
        zip_file.writestr("invoices.csv", invoices_csv)
        
        # 3. Invoice Line Items
        line_items_csv = _export_line_items_csv(db, from_date, to_date)
        zip_file.writestr("invoice_line_items.csv", line_items_csv)
        
        # 4. Payments
        payments_csv = _export_payments_csv(db, from_date, to_date)
        zip_file.writestr("payments.csv", payments_csv)
        
        # 5. Audit Logs
        audit_logs_csv = _export_audit_logs_csv(db, from_date, to_date)
        zip_file.writestr("audit_logs.csv", audit_logs_csv)
        
        # 6. README
        readme = _generate_readme()
        zip_file.writestr("README.txt", readme)
    
    zip_buffer.seek(0)
    return zip_buffer


def _export_invoices_csv(db: Session, from_date: Optional[datetime], to_date: Optional[datetime]) -> str:
    """Exportiert Invoices als CSV."""
    query = db.query(models.Invoice)
    
    # WICHTIG: Inkludiert soft-deleted Invoices für GoBD
    # (nicht filtern nach deleted_at)
    
    if from_date:
        query = query.filter(models.Invoice.created_at >= from_date)
    if to_date:
        query = query.filter(models.Invoice.created_at <= to_date)
    
    invoices = query.order_by(models.Invoice.created_at).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'id', 'invoice_number', 'customer_id', 'project_id',
        'status', 'document_type', 'issued_date', 'due_date',
        'subtotal', 'tax_amount', 'total',
        'notes', 'terms', 'pdf_path',
        'created_at', 'updated_at', 'deleted_at'
    ])
    
    # Data
    for inv in invoices:
        writer.writerow([
            str(inv.id),
            inv.invoice_number,
            str(inv.customer_id) if inv.customer_id else '',
            str(inv.project_id) if inv.project_id else '',
            inv.status,
            inv.document_type,
            inv.issued_date.isoformat() if inv.issued_date else '',
            inv.due_date.isoformat() if inv.due_date else '',
            str(inv.subtotal),
            str(inv.tax_amount),
            str(inv.total),
            inv.notes or '',
            inv.terms or '',
            inv.pdf_path or '',
            inv.created_at.isoformat() if inv.created_at else '',
            inv.updated_at.isoformat() if inv.updated_at else '',
            inv.deleted_at.isoformat() if inv.deleted_at else ''
        ])
    
    return output.getvalue()


def _export_line_items_csv(db: Session, from_date: Optional[datetime], to_date: Optional[datetime]) -> str:
    """Exportiert Invoice Line Items als CSV."""
    query = db.query(models.InvoiceLineItem).join(models.Invoice)
    
    if from_date:
        query = query.filter(models.Invoice.created_at >= from_date)
    if to_date:
        query = query.filter(models.Invoice.created_at <= to_date)
    
    items = query.order_by(models.Invoice.created_at, models.InvoiceLineItem.position).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'id', 'invoice_id', 'position', 'description',
        'quantity', 'unit', 'unit_price', 'tax_rate', 'discount_percent',
        'subtotal', 'discount_amount', 'subtotal_after_discount', 'tax_amount', 'total',
        'created_at', 'updated_at', 'deleted_at'
    ])
    
    # Data
    for item in items:
        writer.writerow([
            str(item.id),
            str(item.invoice_id),
            item.position,
            item.description,
            str(item.quantity),
            item.unit,
            str(item.unit_price),
            str(item.tax_rate),
            str(item.discount_percent),
            str(item.subtotal),
            str(item.discount_amount),
            str(item.subtotal_after_discount),
            str(item.tax_amount),
            str(item.total),
            getattr(item, 'created_at', None).isoformat() if getattr(item, 'created_at', None) else '',
            getattr(item, 'updated_at', None).isoformat() if getattr(item, 'updated_at', None) else '',
            getattr(item, 'deleted_at', None).isoformat() if getattr(item, 'deleted_at', None) else ''
        ])
    
    return output.getvalue()


def _export_payments_csv(db: Session, from_date: Optional[datetime], to_date: Optional[datetime]) -> str:
    """Exportiert Payments als CSV."""
    query = db.query(models.Payment).join(models.Invoice)
    
    if from_date:
        query = query.filter(models.Payment.payment_date >= from_date)
    if to_date:
        query = query.filter(models.Payment.payment_date <= to_date)
    
    payments = query.order_by(models.Payment.payment_date).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'id', 'invoice_id', 'amount', 'payment_date',
        'method', 'reference', 'note',
        'created_at', 'updated_at', 'deleted_at'
    ])
    
    # Data
    for payment in payments:
        writer.writerow([
            str(payment.id),
            str(payment.invoice_id),
            str(payment.amount),
            payment.payment_date.isoformat() if payment.payment_date else '',
            payment.method or '',
            payment.reference or '',
            payment.note or '',
            getattr(payment, 'created_at', None).isoformat() if getattr(payment, 'created_at', None) else '',
            getattr(payment, 'updated_at', None).isoformat() if getattr(payment, 'updated_at', None) else '',
            getattr(payment, 'deleted_at', None).isoformat() if getattr(payment, 'deleted_at', None) else ''
        ])
    
    return output.getvalue()


def _export_audit_logs_csv(db: Session, from_date: Optional[datetime], to_date: Optional[datetime]) -> str:
    """Exportiert Audit Logs als CSV."""
    query = db.query(models.AuditLog).filter(
        models.AuditLog.entity_type.in_(['Invoice', 'InvoiceLineItem', 'Payment'])
    )
    
    if from_date:
        query = query.filter(models.AuditLog.timestamp >= from_date)
    if to_date:
        query = query.filter(models.AuditLog.timestamp <= to_date)
    
    logs = query.order_by(models.AuditLog.timestamp).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'id', 'entity_type', 'entity_id', 'action',
        'old_values', 'new_values', 'user_id', 'ip_address', 'timestamp'
    ])
    
    # Data
    for log in logs:
        writer.writerow([
            str(log.id),
            log.entity_type,
            str(log.entity_id),
            log.action,
            json.dumps(log.old_values) if log.old_values else '',
            json.dumps(log.new_values) if log.new_values else '',
            log.user_id or '',
            log.ip_address or '',
            log.timestamp.isoformat() if log.timestamp else ''
        ])
    
    return output.getvalue()


def _generate_readme() -> str:
    """Generiert README für GoBD Export."""
    return """GoBD Export - WorkmateOS Invoice Module
==========================================

Dieses Archiv enthält einen vollständigen Export aller buchhalterischen Daten
gemäß den Anforderungen der GoBD (Grundsätze zur ordnungsmäßigen Führung und
Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form
sowie zum Datenzugriff).

Inhalt:
-------
- metadata.json         : Export-Metadaten (Datum, Filter, Format)
- invoices.csv          : Alle Rechnungen (inkl. stornierte/gelöschte)
- invoice_line_items.csv: Alle Rechnungspositionen
- payments.csv          : Alle Zahlungseingänge
- audit_logs.csv        : Vollständiger Audit Trail (Änderungshistorie)

Format:
-------
- Encoding: UTF-8
- Delimiter: , (Komma)
- Quote: " (Anführungszeichen)
- Line Ending: CRLF

GoBD-Konformität:
-----------------
✓ Vollständigkeit: Alle Transaktionen inkl. gelöschter Einträge
✓ Nachvollziehbarkeit: Audit Trail mit allen Änderungen
✓ Unveränderbarkeit: Zeitstempel und User-Tracking
✓ Maschinenlesbarkeit: Strukturiertes CSV-Format

Aufbewahrungspflicht:
--------------------
Nach § 257 HGB und § 147 AO müssen diese Daten 10 Jahre aufbewahrt werden.

Generiert von: WorkmateOS Invoice Module
Export-Datum: Siehe metadata.json
"""
