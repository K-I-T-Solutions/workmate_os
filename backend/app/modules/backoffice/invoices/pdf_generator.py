# app/modules/backoffice/invoices/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

import os
from pathlib import Path
from decimal import Decimal

from app.core.config import settings

ASSETS_DIR = settings.ASSETS_DIR

# ── Rebrand 2026 ────────────────────────────────────────────────────────────
ORANGE   = colors.HexColor("#FF6B35")
CYAN     = colors.HexColor("#06B6D4")
NAVY     = colors.HexColor("#0F1629")
GREY_LIGHT = colors.HexColor("#F8F9FA")
GREY_MID   = colors.HexColor("#E9ECEF")
GREY_TEXT  = colors.HexColor("#6C757D")
GREEN_PAID = colors.HexColor("#22C55E")

DOCUMENT_TYPES = {
    "invoice": {
        "title": "RECHNUNG",
        "accent": ORANGE,
        "badge": None,
        "terms_default": "Zahlbar innerhalb von 14 Tagen ohne Abzug.",
    },
    "quote": {
        "title": "ANGEBOT",
        "accent": CYAN,
        "badge": None,
        "terms_default": "Dieses Angebot ist 14 Tage gültig.",
    },
    "credit_note": {
        "title": "GUTSCHRIFT",
        "accent": GREEN_PAID,
        "badge": None,
        "terms_default": "Die Gutschrift wird mit offenen Posten verrechnet.",
    },
    "order_confirmation": {
        "title": "AUFTRAGSBESTÄTIGUNG",
        "accent": CYAN,
        "badge": None,
        "terms_default": "Bitte prüfen Sie alle Angaben sorgfältig.",
    },
}

COMPANY_NAME      = "K.I.T. Solutions"
COMPANY_SUBTITLE  = "Kuhrau InformationsTechnik"
COMPANY_OWNER     = "Joshua Phu Kuhrau"
COMPANY_STREET    = "Dietzstr. 1"
COMPANY_ZIP_CITY  = "56073 Koblenz"
COMPANY_STATE     = "Rheinland-Pfalz"
COMPANY_EMAIL     = "joshua@kit-it-koblenz.de"
COMPANY_WEBSITE   = "kit-it-koblenz.de"
COMPANY_PHONE     = "0162 2654262"
COMPANY_TAGLINE   = "Business IT  •  Event Tech  •  Custom Software"
COMPANY_FOOTER_TAGLINE = "Miteinander statt Führend."
COMPANY_UST_HINWEIS = "Kleinunternehmer gem. § 19 UStG – Es wird keine Umsatzsteuer berechnet."

BANK_IBAN = "DE94100110012706471170"
BANK_BIC  = "NTSBDEB1XX"
BANK_NAME = "N26 Bank AG"


def format_eur(value) -> str:
    if value is None:
        return "0,00 EUR"
    if isinstance(value, Decimal):
        value = float(value)
    s = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{s} EUR"


def format_customer_address(customer) -> list[str]:
    if not customer:
        return ["Unbekannter Kunde"]
    lines = []
    if getattr(customer, "name", None):
        lines.append(customer.name)
    if getattr(customer, "street", None):
        lines.append(customer.street)
    zip_city = f"{getattr(customer, 'zip_code', '') or ''} {getattr(customer, 'city', '') or ''}".strip()
    if zip_city:
        lines.append(zip_city)
    return lines


def build_epc_qr_string(amount, invoice_number: str) -> str:
    eur = float(amount) if isinstance(amount, Decimal) else float(amount)
    return "\n".join([
        "BCD", "001", "1", "SCT",
        BANK_BIC, COMPANY_NAME, BANK_IBAN,
        f"EUR{eur:.2f}", "", f"Rechnung {invoice_number}", "",
    ])


def draw_qr_code(c, x, y, size_mm, data):
    qr_code = qr.QrCodeWidget(data)
    b = qr_code.getBounds()
    size = size_mm * mm
    d = Drawing(size, size)
    d.add(qr_code)
    d.scale(size / (b[2] - b[0]), size / (b[3] - b[1]))
    renderPDF.draw(d, c, x, y)


def draw_badge(c, x, y, text, bg_color, text_color=colors.white, font_size=8):
    w = len(text) * font_size * 0.65 + 8
    h = font_size + 6
    c.setFillColor(bg_color)
    c.roundRect(x, y, w, h, 2, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", font_size)
    c.drawCentredString(x + w / 2, y + 4, text)
    return w


# ── MAIN GENERATOR ──────────────────────────────────────────────────────────

def generate_invoice_pdf(invoice, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    W, H = A4
    margin = 20 * mm

    doc_type = getattr(invoice, "document_type", "invoice")
    cfg = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["invoice"])
    accent = cfg["accent"]

    # ── HEADER ──────────────────────────────────────────────────────────────
    # Logo icon oben rechts (ohne Schriftzug)
    logo_icon = Path(ASSETS_DIR) / "KIT_Solutions_logo_ohne_name.png"
    if not logo_icon.exists():
        logo_icon = Path(ASSETS_DIR) / "kit_logo.png"

    header_top = H - 18 * mm

    if logo_icon.exists():
        icon_w = 14 * mm
        c.drawImage(
            str(logo_icon), W - margin - icon_w, header_top - 14 * mm,
            width=icon_w, preserveAspectRatio=True, mask="auto",
        )
        text_right = W - margin - icon_w - 3 * mm
    else:
        text_right = W - margin

    # Firmenname groß
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(NAVY)
    c.drawRightString(text_right, header_top, "K.I.T.  SOLUTIONS")

    # Untertitel kursiv orange
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(ORANGE)
    c.drawRightString(text_right, header_top - 6 * mm, COMPANY_SUBTITLE)

    # Kontaktzeile
    c.setFont("Helvetica", 8)
    c.setFillColor(NAVY)
    contact_line = f"{COMPANY_EMAIL}  •  {COMPANY_PHONE}  •  {COMPANY_WEBSITE}"
    c.drawRightString(text_right, header_top - 11 * mm, contact_line)
    addr_line = f"{COMPANY_STREET}  •  {COMPANY_ZIP_CITY}  •  {COMPANY_STATE}"
    c.drawRightString(text_right, header_top - 15 * mm, addr_line)

    # Trennlinie (orange + cyan zweifarbig)
    sep_y = H - 38 * mm
    c.setLineWidth(2)
    c.setStrokeColor(ORANGE)
    c.line(margin, sep_y, margin + (W - 2 * margin) * 0.45, sep_y)
    c.setStrokeColor(CYAN)
    c.line(margin + (W - 2 * margin) * 0.45, sep_y, W - margin, sep_y)

    # ── RÜCKSENDEADRESSE (kleine Zeile über Kundenadresse) ──────────────────
    retaddr_y = H - 46 * mm
    c.setFont("Helvetica", 7)
    c.setFillColor(GREY_TEXT)
    c.drawString(margin, retaddr_y, f"{COMPANY_NAME}  •  {COMPANY_STREET}  •  {COMPANY_ZIP_CITY}")

    # ── KUNDENADRESSE (links) ────────────────────────────────────────────────
    addr_start_y = retaddr_y - 5 * mm
    addr_lines = format_customer_address(getattr(invoice, "customer", None))
    c.setFillColor(NAVY)
    for i, line in enumerate(addr_lines):
        if i == 0:
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 9)
        c.drawString(margin, addr_start_y - i * 5 * mm, line)

    # ── RECHNUNGSMETA (rechts, als Key-Value-Block) ──────────────────────────
    meta_x_label = W / 2 + 10 * mm
    meta_x_value = W - margin
    meta_y = retaddr_y - 2 * mm
    meta_line_h = 5.5 * mm

    meta = [
        ("Rechnungsnummer:", str(invoice.invoice_number)),
        ("Datum:", str(invoice.issued_date)),
    ]
    if doc_type == "invoice":
        meta.append(("Fällig bis:", str(getattr(invoice, "due_date", None) or "—")))
    elif doc_type == "quote":
        meta.append(("Gültig bis:", "14 Tage"))

    for i, (label, value) in enumerate(meta):
        y = meta_y - i * meta_line_h
        c.setFont("Helvetica", 8)
        c.setFillColor(GREY_TEXT)
        c.drawString(meta_x_label, y, label)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(NAVY)
        c.drawRightString(meta_x_value, y, value)

    # ── STATUS-BADGE ─────────────────────────────────────────────────────────
    inv_status = getattr(invoice, "status", None)
    badge_y = meta_y - len(meta) * meta_line_h - 3 * mm
    status_colors = {
        "paid": (GREEN_PAID, "PAID"),
        "sent": (CYAN, "VERSENDET"),
        "overdue": (colors.red, "ÜBERFÄLLIG"),
        "draft": (GREY_TEXT, "ENTWURF"),
        "cancelled": (colors.HexColor("#9CA3AF"), "STORNIERT"),
    }
    if inv_status in status_colors:
        bg, label = status_colors[inv_status]
        draw_badge(c, meta_x_label, badge_y, label, bg)

    # ── DOKUMENT-TITEL ───────────────────────────────────────────────────────
    title_y = addr_start_y - len(addr_lines) * 5 * mm - 12 * mm
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(NAVY)
    c.drawString(margin, title_y, cfg["title"])

    # ── BETREFF-ZEILE ────────────────────────────────────────────────────────
    subject = getattr(invoice, "notes", None)
    subj_y = title_y - 10 * mm
    if subject:
        c.setFillColor(accent)
        c.rect(margin, subj_y - 1, 2.5, 12, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin + 5, subj_y + 2, f"Betreff: {subject[:80]}")
        subj_y -= 8 * mm
    else:
        # Kleiner Abstand
        subj_y -= 3 * mm

    # ── POSITIONSTABELLE ─────────────────────────────────────────────────────
    table_data = [["Pos.", "Beschreibung", "Menge", "Einheit", "EP (EUR)", "GP (EUR)"]]

    if getattr(invoice, "line_items", None):
        for idx, item in enumerate(invoice.line_items, 1):
            total = item.total if hasattr(item, "total") else (
                float(item.quantity) * float(item.unit_price) * (1 - float(getattr(item, "discount_percent", 0)) / 100)
            )
            table_data.append([
                str(idx),
                item.description,
                f"{float(item.quantity):.2f}",
                item.unit,
                f"{float(item.unit_price):,.2f}".replace(",", "_").replace(".", ",").replace("_", "."),
                f"{float(total):,.2f}".replace(",", "_").replace(".", ",").replace("_", "."),
            ])
    else:
        table_data.append(["-", "Keine Positionen vorhanden", "", "", "", ""])

    # Summenzeilen
    table_data.append(["", "", "", "", "Nettobetrag:", format_eur(invoice.subtotal)])
    tax_rate = getattr(invoice, "tax_rate", 0) or 0
    table_data.append(["", "", "", "", f"zzgl. {int(tax_rate)} % USt. (§ 19 UStG):", format_eur(invoice.tax_amount)])
    table_data.append(["", "", "", "", "GESAMT:", format_eur(invoice.total)])

    n_items = len(table_data) - 3  # ohne Summenzeilen
    col_w = [12*mm, 68*mm, 18*mm, 20*mm, 30*mm, 27*mm]

    style = [
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),   NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0),   colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),   "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),   8),
        ("TOPPADDING",    (0, 0), (-1, 0),   5),
        ("BOTTOMPADDING", (0, 0), (-1, 0),   5),
        ("ALIGN",         (0, 0), (-1, 0),   "CENTER"),
        # Datenzeilen
        ("FONTNAME",      (0, 1), (-1, n_items), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, n_items), 8.5),
        ("ALIGN",         (2, 1), (-1, n_items), "RIGHT"),
        ("TOPPADDING",    (0, 1), (-1, n_items), 4),
        ("BOTTOMPADDING", (0, 1), (-1, n_items), 4),
        ("ROWBACKGROUNDS",(0, 1), (-1, n_items), [colors.white, GREY_LIGHT]),
        ("GRID",          (0, 0), (-1, n_items), 0.25, GREY_MID),
        # Summen Netto + USt (grau, kein Rand links)
        ("SPAN",          (0, n_items+1), (3, n_items+1), ),
        ("SPAN",          (0, n_items+2), (3, n_items+2), ),
        ("FONTNAME",      (0, n_items+1), (-1, n_items+2), "Helvetica"),
        ("FONTSIZE",      (0, n_items+1), (-1, n_items+2), 8),
        ("TEXTCOLOR",     (4, n_items+1), (4, n_items+2), GREY_TEXT),
        ("ALIGN",         (4, n_items+1), (-1, n_items+2), "RIGHT"),
        ("TOPPADDING",    (0, n_items+1), (-1, n_items+2), 3),
        ("BOTTOMPADDING", (0, n_items+1), (-1, n_items+2), 3),
        ("LINEABOVE",     (0, n_items+1), (-1, n_items+1), 0.5, GREY_MID),
        # GESAMT-Zeile (dunkel)
        ("BACKGROUND",    (0, -1), (-1, -1), NAVY),
        ("TEXTCOLOR",     (4, -1), (-1, -1), colors.white),
        ("FONTNAME",      (4, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (4, -1), (-1, -1), 9),
        ("ALIGN",         (4, -1), (-1, -1), "RIGHT"),
        ("TOPPADDING",    (0, -1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 5),
    ]

    tbl = Table(table_data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle(style))

    avail_w = W - 2 * margin
    _, tbl_h = tbl.wrap(avail_w, H)
    tbl_y = subj_y - tbl_h - 3 * mm
    tbl.drawOn(c, margin, tbl_y)

    # ── ZAHLUNGSINFORMATIONEN BOX ─────────────────────────────────────────────
    box_y = tbl_y - 35 * mm
    box_h = 28 * mm
    box_w = W - 2 * margin

    c.setFillColor(NAVY)
    c.roundRect(margin, box_y, box_w, box_h, 3, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(CYAN)
    c.drawString(margin + 5 * mm, box_y + box_h - 7 * mm, "Zahlungsinformationen")

    fields = [
        ("IBAN:",        BANK_IBAN),
        ("BIC:",         BANK_BIC),
        ("Bank:",        BANK_NAME),
        ("Verwendung:",  f"Rechnung {invoice.invoice_number}"),
    ]
    for i, (k, v) in enumerate(fields):
        fy = box_y + box_h - 12 * mm - i * 4.5 * mm
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(CYAN)
        c.drawString(margin + 5 * mm, fy, k)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(colors.white)
        c.drawString(margin + 28 * mm, fy, v)

    # ── QR-CODE ──────────────────────────────────────────────────────────────
    if doc_type == "invoice" and float(invoice.total) > 0:
        qr_size = 28
        qr_x = W - margin - qr_size * mm
        qr_y_pos = box_y - qr_size * mm - 3 * mm
        draw_qr_code(c, qr_x, qr_y_pos, qr_size, build_epc_qr_string(invoice.total, invoice.invoice_number))
        c.setFont("Helvetica", 7)
        c.setFillColor(GREY_TEXT)
        c.drawRightString(W - margin, qr_y_pos - 3, "SEPA-Überweisung per Scan")

    # ── ZAHLUNGSBEDINGUNGEN ───────────────────────────────────────────────────
    terms = getattr(invoice, "terms", None) or cfg["terms_default"]
    terms_y = box_y - 8 * mm

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(NAVY)
    c.drawString(margin, terms_y, "Zahlungsbedingungen")
    c.setLineWidth(0.5)
    c.setStrokeColor(ORANGE)
    c.line(margin, terms_y - 1.5, margin + 55 * mm, terms_y - 1.5)

    c.setFont("Helvetica", 8)
    c.setFillColor(NAVY)
    t = c.beginText(margin, terms_y - 6 * mm)
    t.setLeading(11)
    for line in terms.split("\n"):
        t.textLine(line)
    responsible = getattr(invoice, "responsible_person", None) or COMPANY_OWNER
    t.textLine("")
    t.textLine(f"Bei Rückfragen: ")
    c.drawText(t)
    # "Name" fett
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 22 * mm, terms_y - 6 * mm - 2 * 11 - 11, responsible)

    # ── FOOTER ───────────────────────────────────────────────────────────────
    footer_y = 18 * mm
    c.setStrokeColor(GREY_MID)
    c.setLineWidth(0.5)
    c.line(margin, footer_y + 10, W - margin, footer_y + 10)

    c.setFont("Helvetica", 7)
    c.setFillColor(GREY_TEXT)
    footer_left = f"{COMPANY_NAME}  •  {COMPANY_FOOTER_TAGLINE}  •  {COMPANY_TAGLINE}"
    c.drawString(margin, footer_y + 3, footer_left)
    c.drawRightString(W - margin, footer_y + 3, "Seite 1 / 1")
    c.drawString(margin, footer_y - 4, COMPANY_UST_HINWEIS)

    c.showPage()
    c.save()
