# app/modules/backoffice/invoices/crud.py
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal
from app.modules.backoffice.invoices import models, schemas
from app.modules.backoffice.invoices.pdf_generator import generate_invoice_pdf
from app.modules.documents.models import Document
import os
import uuid

def get_invoices(db: Session):
    return db.query(models.Invoice).all()


def get_invoice(db: Session, invoice_id: str):
    """
    Holt eine Rechnung inkl. zugehöriger Line Items und Customer-Daten.
    """
    return (
        db.query(models.Invoice)
        .options(
            joinedload(models.Invoice.customer),
            joinedload(models.Invoice.line_items)
        )
        .filter(models.Invoice.id == invoice_id)
        .first()
    )


def create_invoice(db: Session, data: schemas.InvoiceCreate):
    invoice = models.Invoice(
        **data.model_dump(exclude={"line_items"}),
        subtotal=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total=Decimal("0.00"),
    )
    db.add(invoice)
    db.flush()  # ID generiert

    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")

    # --- 2️⃣ Line Items ---
    if data.line_items:
        for pos, item_data in enumerate(data.line_items, start=1):
            item = models.InvoiceLineItem(
                invoice_id=invoice.id,
                position=pos,
                **item_data.model_dump(exclude={"position"}),
            )
            subtotal += getattr(item, "subtotal_after_discount", Decimal("0.00"))
            tax_total += getattr(item, "tax_amount", Decimal("0.00"))
            db.add(item)
    print("DEBUG Invoice ID:", invoice.id)
    print("Alle IDs:", [x.id for x in db.query(models.Invoice).all()])

    # --- 3️⃣ Summen ---
    invoice.subtotal = subtotal
    invoice.tax_amount = tax_total
    invoice.total = subtotal + tax_total
    db.commit()
    db.refresh(invoice)

    # --- 4️⃣ Invoice neu laden (mit Joinedload) ---
    invoice_db = (
        db.query(models.Invoice)
        .options(
            joinedload(models.Invoice.customer),
            joinedload(models.Invoice.line_items)
        )
        .filter(models.Invoice.id == invoice.id)
        .first()
    )

    if not invoice_db:
        print(f"❌ Fehler: Invoice {invoice.id} konnte nach Commit nicht geladen werden.")
        return None

    invoice = invoice_db

    # --- 5️⃣ PDF erzeugen ---
    pdf_dir = "/root/workmate_os_uploads/invoices"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{invoice.invoice_number or 'unbekannt'}.pdf")

    try:
        generate_invoice_pdf(invoice, pdf_path)
        invoice.pdf_path = pdf_path
    except Exception as e:
        print(f"❌ Fehler beim PDF-Rendern: {e}")

    # --- 6️⃣ Dokument registrieren ---
    if os.path.exists(pdf_path):
        doc = Document(
            id=uuid.uuid4(),
            title=f"Rechnung {invoice.invoice_number or 'Unbekannt'}",
            file_path=pdf_path,
            type="pdf",
            category="Rechnungen",
            owner_id=None,
            linked_module="invoices",
            checksum=None,
            is_confidential=False,
        )
        db.add(doc)
    else:
        print("⚠️ Kein PDF gefunden, Dokument nicht angelegt.")

    db.commit()
    db.refresh(invoice)
    return (
        db.query(models.Invoice)
        .options(joinedload(models.Invoice.line_items))
        .filter(models.Invoice.id == invoice.id)
        .first()
    )


def update_invoice(db: Session, invoice_id: str, data: schemas.InvoiceUpdate):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(invoice, key, value)

    db.commit()
    db.refresh(invoice)
    return invoice


def delete_invoice(db: Session, invoice_id: str):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return False
    db.delete(invoice)
    db.commit()
    return True
