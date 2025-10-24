# app/modules/backoffice/invoices/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
from pathlib import Path
from decimal import Decimal
from app.core.config import settings
from jinja2 import Template
import markdown2
import re
from html import unescape


ASSETS_DIR = settings.ASSETS_DIR


# ========================================
# PDF GENERATOR
# ========================================

def generate_invoice_pdf(invoice, output_path: str):
    """
    Generiert ein modernes K.I.T. Solutions Rechnungs-PDF mit Branding, Tabelle und Footer.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 20 * mm

    # === Header ===
    assets_dir = Path(ASSETS_DIR)
    logo_path = assets_dir / "KIT_IT_GREY_NO_BACKGROUND.png"
    logo_path = str(logo_path)

    if os.path.exists(logo_path):
        c.drawImage(logo_path, margin, height - 45 * mm, width=40 * mm, preserveAspectRatio=True, mask='auto')

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - margin, height - 20 * mm, "K.I.T. Solutions")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, height - 25 * mm, "Dietzstr. 1 · 56073 Koblenz")
    c.drawRightString(width - margin, height - 30 * mm, "info@kit-it-koblenz.de · kit-it-koblenz.de")
    c.drawRightString(width - margin, height - 35 * mm, "Tel. 0162 / 2654262")

    # === Title ===
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#ff9100"))
    c.drawString(margin, height - 55 * mm, "RECHNUNG")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(margin, height - 65 * mm, f"Rechnungsnummer: {invoice.invoice_number}")
    c.drawString(margin, height - 72 * mm, f"Rechnungsdatum: {invoice.issued_date}")
    c.drawString(margin, height - 79 * mm, f"Fällig bis: {invoice.due_date or '–'}")

    # === Customer Block ===
    y = height - 95 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, f"{invoice.customer.name}")
    c.setFont("Helvetica", 9)
    c.drawString(margin, y - 5 * mm, f"{invoice.customer.street or ''}")
    c.drawString(margin, y - 10 * mm, f"{invoice.customer.zip_code or ''} {invoice.customer.city or ''}")
    c.drawString(margin, y - 15 * mm, f"{invoice.customer.country or ''}")

    # === Table ===
    y_table_start = y - 35 * mm
    data = [["Pos", "Beschreibung", "Menge", "Einheit", "Einzelpreis", "Gesamt"]]

    if invoice.line_items:
        for i, item in enumerate(invoice.line_items, start=1):
            total = (Decimal(item.quantity) * Decimal(item.unit_price)) * (
                Decimal(1) - Decimal(item.discount_percent) / 100
            )
            data.append([
                str(i),
                item.description,
                f"{item.quantity:.2f}",
                item.unit,
                f"{item.unit_price:.2f} €",
                f"{total:.2f} €"
            ])
    else:
        data.append(["-", "Keine Positionen vorhanden", "", "", "", ""])

    table = Table(data, colWidths=[15*mm, 65*mm, 20*mm, 25*mm, 30*mm, 30*mm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#ff9100")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, margin, y_table_start)

    # === Totals ===
    y_totals = y_table_start - (len(data) * 8 * mm) - 10
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - margin - 60, y_totals, "Zwischensumme:")
    c.drawRightString(width - margin, y_totals, f"{invoice.subtotal:.2f} €")

    c.drawRightString(width - margin - 60, y_totals - 6 * mm, "MwSt:")
    c.drawRightString(width - margin, y_totals - 6 * mm, f"{invoice.tax_amount:.2f} €")

    c.drawRightString(width - margin - 60, y_totals - 12 * mm, "Gesamtbetrag:")
    c.setFillColor(colors.HexColor("#ff9100"))
    c.drawRightString(width - margin, y_totals - 12 * mm, f"{invoice.total:.2f} €")
    c.setFillColor(colors.black)

    # === Footer (aus Markdown-Template) ===
    footer_text = render_footer(invoice)
    c.setFont("Helvetica", 8)
    text_object = c.beginText(margin, 25 * mm)

    for line in footer_text.splitlines():
        if line.strip() == "":
            text_object.moveCursor(0, -6)  # Leerzeile = Abstand
        else:
            text_object.textLine(line)
    c.drawText(text_object)

    # === Abschluss ===
    c.showPage()
    c.save()


# ========================================
# FOOTER RENDERING
# ========================================

def render_footer(invoice, template_path: str = "./app/modules/backoffice/invoices/templates/footer_default.md") -> str:
    """
    Rendert den Footer (Markdown + Jinja2) zu Plaintext für PDF-Ausgabe.
    """
    if not os.path.exists(template_path):
        return "K.I.T. Solutions – Kleingewerbe nach §19 UStG – keine Umsatzsteuer ausgewiesen."

    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()

    # Template dynamisch rendern
    rendered_md = Template(template_str).render(
        invoice=invoice,
        terms=invoice.terms or "Zahlbar innerhalb von 14 Tagen.",
        customer_name=invoice.customer.name if invoice.customer else "Unbekannter Kunde",
        invoice_number=invoice.invoice_number,
        total=f"{invoice.total:.2f} €",
    )

    # --- Markdown → HTML → Plaintext ---
    html = markdown2.markdown(rendered_md)
    text = re.sub(r"<[^>]+>", "", html)  # HTML-Tags entfernen
    text = unescape(text)  # HTML-Entities (&uuml; → ü)
    text = text.strip().replace("\n\n", "\n")  # Leerzeilen bereinigen

    return text
