# app/modules/backoffice/invoices/pdf_generator.py
#
# K.I.T. Solutions – PDF Generator
# Spec: 3_Assets/Rebrand 2026/files/KIT_Solutions_PDFGenerator_DesignSpec.md
# Fonts: built-in Helvetica/Courier (no TTF required)
# Logo: ASSETS_DIR/kit_logo.png (fallback: KIT_IT_GREY_NO_BACKGROUND.png)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

import os
from io import BytesIO
from pathlib import Path
from decimal import Decimal

from app.core.settings.config import settings

ASSETS_DIR = settings.ASSETS_DIR

# =====================================================================
# LAYOUT
# =====================================================================
PAGE_W, PAGE_H = A4          # 595.28 x 841.89 pt
MARGIN_L  = 18 * mm
MARGIN_R  = 18 * mm
MARGIN_B  = 14 * mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R   # ≈ 493 pt
HEADER_H  = 72               # pt  (orange line at PAGE_H - HEADER_H)
FOOTER_H  = 32               # pt  (blue line at FOOTER_H + 18)
CONTENT_START = PAGE_H - HEADER_H - 14    # first usable Y ≈ 756 pt
MIN_Y     = FOOTER_H + 18 + 12            # lowest usable Y (above footer)

# =====================================================================
# BRAND COLORS
# =====================================================================
NAVY  = HexColor("#0F1629")
DARK2 = HexColor("#1E2D4A")
ORANGE= HexColor("#FF6B35")
BLUE  = HexColor("#3B82F6")
CYAN  = HexColor("#06B6D4")
WHITE = HexColor("#FFFFFF")
LGRAY = HexColor("#F5F7FA")
MGRAY = HexColor("#94A3B8")
DGRAY = HexColor("#374151")
EGRAY = HexColor("#E5E7EB")
GREEN = HexColor("#22C55E")
RED   = HexColor("#EF4444")

# =====================================================================
# TYPOGRAPHY  (ReportLab built-ins — no installation required)
# =====================================================================
FONT_BODY   = "Helvetica"
FONT_BOLD   = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"
FONT_MONO   = "Courier"
FONT_MONO_B = "Courier-Bold"

# =====================================================================
# COMPANY DATA
# =====================================================================
COMPANY_NAME    = "K.I.T. Solutions"
COMPANY_OWNER   = "Joshua Phu Kuhrau"
COMPANY_STREET  = "Dietzstr. 1"
COMPANY_CITY    = "56073 Koblenz"
COMPANY_STATE   = "Rheinland-Pfalz"
COMPANY_EMAIL   = "joshua@kit-it-koblenz.de"
COMPANY_PHONE   = "0162 2654262"
COMPANY_WEB     = "kit-it-koblenz.de"
COMPANY_TAGLINE = "Kuhrau InformationsTechnik"
COMPANY_SLOGAN  = "Miteinander statt Führend."

BANK_IBAN = "DE94100110012706471170"
BANK_BIC  = "NTSBDEB1XX"
BANK_NAME = "N26 Bank AG"

# =====================================================================
# DOCUMENT TYPES
# =====================================================================
DOCUMENT_TYPES = {
    "invoice": {
        "title":         "RECHNUNG",
        "terms_default": "Zahlbar innerhalb von 14 Tagen nach Rechnungsdatum.",
    },
    "quote": {
        "title":         "ANGEBOT",
        "terms_default": "Dieses Angebot ist 14 Tage gültig.",
    },
    "credit_note": {
        "title":         "GUTSCHRIFT",
        "terms_default": "Die Gutschrift wird mit offenen Posten verrechnet.",
    },
    "order_confirmation": {
        "title":         "AUFTRAGSBESTÄTIGUNG",
        "terms_default": "Bitte prüfen Sie alle Angaben sorgfältig.",
    },
}

STATUS_COLORS = {
    "offen":        ORANGE,
    "open":         ORANGE,
    "paid":         GREEN,
    "bezahlt":      GREEN,
    "overdue":      RED,
    "ueberfaellig": RED,
    "draft":        MGRAY,
    "storniert":    MGRAY,
    "cancelled":    MGRAY,
}

# =====================================================================
# POSITIONS TABLE  – column layout
# =====================================================================
_COLS = [
    ("pos",         30),
    ("description", 218),
    ("qty",         42),
    ("unit",        43),
    ("unit_price",  72),
    ("total_price", 88),
]
_COL_HEADERS = ["Pos.", "Beschreibung", "Menge", "Einheit", "EP (EUR)", "GP (EUR)"]
_COL_ALIGNS  = ["center", "left", "right", "left", "right", "right"]

TABLE_HDR_H = 22   # pt – header row
ROW_H_MIN   = 26   # pt – minimum data row

def _row_h(desc: str) -> float:
    lines = str(desc or "").split("\n")
    return max(ROW_H_MIN, len(lines) * 12 + 8)


# =====================================================================
# HELPERS
# =====================================================================

def format_eur(value) -> str:
    if value is None:
        return "0,00 €"
    if isinstance(value, Decimal):
        value = float(value)
    s = f"{value:,.2f}"
    s = s.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{s} €"


def format_customer_address(customer) -> list[str]:
    if not customer:
        return ["Unbekannter Kunde"]
    lines = []
    if getattr(customer, "name", None):
        lines.append(customer.name)
    street   = getattr(customer, "street",   None) or ""
    zip_code = getattr(customer, "zip_code", None) or ""
    city     = getattr(customer, "city",     None) or ""
    country  = getattr(customer, "country",  None) or ""
    if street:
        lines.append(street)
    zip_city = f"{zip_code} {city}".strip()
    if zip_city:
        lines.append(zip_city)
    if country and country.upper() not in ("GERMANY", "DE", "DEUTSCHLAND"):
        lines.append(country)
    return lines


def build_epc_qr_string(amount, invoice_number: str) -> str:
    eur = float(amount) if isinstance(amount, Decimal) else float(amount)
    return "\n".join([
        "BCD", "001", "1", "SCT",
        BANK_BIC, COMPANY_NAME, BANK_IBAN,
        f"EUR{eur:.2f}", "", f"Rechnung {invoice_number}", "",
    ])


def draw_qr_code(c: canvas.Canvas, x: float, y: float, size_mm: float, data: str):
    qr_widget = qr.QrCodeWidget(data)
    bounds = qr_widget.getBounds()
    bw = bounds[2] - bounds[0]
    bh = bounds[3] - bounds[1]
    size = size_mm * mm
    d = Drawing(size, size)
    d.add(qr_widget)
    d.scale(size / bw, size / bh)
    renderPDF.draw(d, c, x, y)


def _resolve_logo() -> str | None:
    """Returns path to the best available logo PNG, or None."""
    for name in ("kit_logo.png", "KIT_IT_GREY_NO_BACKGROUND.png"):
        p = Path(ASSETS_DIR) / name
        if p.exists():
            return str(p)
    return None


# =====================================================================
# WATERMARK
# =====================================================================

def draw_logo_watermark(c: canvas.Canvas):
    logo_path = Path(ASSETS_DIR) / "KIT_IT_GREY_NO_BACKGROUND.png"
    if not logo_path.exists():
        return
    try:
        from PIL import Image as PILImage
        img = PILImage.open(str(logo_path)).convert("RGBA")
        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * 0.12))
        img.putalpha(a)
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        size = 90 * mm
        c.saveState()
        c.translate(5 * mm, PAGE_H - 5 * mm)
        c.rotate(30)
        c.drawImage(ImageReader(buf), 0, -size, width=size, height=size,
                    preserveAspectRatio=True, mask="auto")
        c.restoreState()
    except Exception:
        pass


# =====================================================================
# HEADER
# =====================================================================

def draw_header(c: canvas.Canvas, logo_path: str | None):
    # Logo
    if logo_path:
        try:
            c.drawImage(logo_path, MARGIN_L, PAGE_H - HEADER_H + 9,
                        width=54, height=54,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # Company name – Courier Bold, Navy
    c.setFillColor(NAVY)
    c.setFont(FONT_MONO_B, 18)
    c.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 22, "K.I.T. SOLUTIONS")

    # Subtitle – Orange
    c.setFillColor(ORANGE)
    c.setFont(FONT_ITALIC, 10)
    c.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 35, COMPANY_TAGLINE)

    # Contact line
    c.setFillColor(MGRAY)
    c.setFont(FONT_BODY, 9)
    c.drawRightString(
        PAGE_W - MARGIN_R, PAGE_H - 48,
        f"{COMPANY_EMAIL}  \u2022  {COMPANY_PHONE}  \u2022  {COMPANY_WEB}",
    )

    # Address line
    c.drawRightString(
        PAGE_W - MARGIN_R, PAGE_H - 60,
        f"{COMPANY_STREET}  \u2022  {COMPANY_CITY}  \u2022  {COMPANY_STATE}",
    )

    # Orange divider
    c.setStrokeColor(ORANGE)
    c.setLineWidth(3)
    c.line(0, PAGE_H - HEADER_H, PAGE_W, PAGE_H - HEADER_H)


# =====================================================================
# FOOTER
# =====================================================================

def draw_footer(c: canvas.Canvas, page_num: int, total_pages: int):
    footer_line_y = FOOTER_H + 18

    # Blue divider
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.5)
    c.line(MARGIN_L, footer_line_y, PAGE_W - MARGIN_R, footer_line_y)

    c.setFont(FONT_BODY, 8)
    c.setFillColor(MGRAY)

    # Left: tagline
    c.drawString(
        MARGIN_L, FOOTER_H + 8,
        f"{COMPANY_NAME}  \u2022  {COMPANY_SLOGAN}"
        "  \u2022  Business IT \u2022 Event Tech \u2022 Custom Software",
    )

    # Right: page number
    c.drawRightString(PAGE_W - MARGIN_R, FOOTER_H + 8,
                      f"Seite {page_num} / {total_pages}")

    # Steuerhinweis only on last page
    if page_num == total_pages:
        c.setFont(FONT_BODY, 7)
        c.drawString(
            MARGIN_L, FOOTER_H - 4,
            "Kleinunternehmer gem. \u00a7 19 UStG \u2013 "
            "Es wird keine Umsatzsteuer berechnet.",
        )


# =====================================================================
# STATUS BADGE
# =====================================================================

def draw_status_badge(c: canvas.Canvas, status: str, x: float, y: float):
    color = STATUS_COLORS.get(status.lower(), MGRAY)
    bw, bh = 65, 16
    c.setFillColor(color)
    c.roundRect(x, y, bw, bh, 3, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 7.5)
    c.drawCentredString(x + bw / 2, y + 5, status.upper())


# =====================================================================
# POSITIONS TABLE  (canvas-based, no Platypus Table)
# =====================================================================

def _draw_table_header_row(c: canvas.Canvas, x: float, y: float):
    c.setFillColor(NAVY)
    c.rect(x, y - TABLE_HDR_H, CONTENT_W, TABLE_HDR_H, fill=1, stroke=0)
    cx = x
    for i, (_, col_w) in enumerate(_COLS):
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(WHITE)
        text = _COL_HEADERS[i]
        mid_y = y - TABLE_HDR_H + 7
        if _COL_ALIGNS[i] == "right":
            c.drawRightString(cx + col_w - 4, mid_y, text)
        elif _COL_ALIGNS[i] == "center":
            c.drawCentredString(cx + col_w / 2, mid_y, text)
        else:
            c.drawString(cx + 4, mid_y, text)
        cx += col_w
    return y - TABLE_HDR_H


def _draw_data_row(c: canvas.Canvas, x: float, y: float, pos: dict, row_idx: int):
    desc  = str(pos.get("description", ""))
    row_h = _row_h(desc)

    # Zebra
    if row_idx % 2 == 0:
        c.setFillColor(LGRAY)
        c.rect(x, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)

    # Divider
    c.setStrokeColor(EGRAY)
    c.setLineWidth(0.5)
    c.line(x, y - row_h, x + CONTENT_W, y - row_h)

    cells = [
        str(pos.get("pos", row_idx + 1)),
        desc,
        f"{pos.get('qty', 0):.2f}".replace(".", ","),
        pos.get("unit", "Stk."),
        f"{pos.get('unit_price', 0):.2f}".replace(".", ","),
        f"{pos.get('total_price', 0):.2f}".replace(".", ","),
    ]

    # Vertikale Mitte der Zeile (Baseline für 9pt ≈ Mitte - 3)
    cell_mid_y = y - row_h / 2 - 3

    cx = x
    for i, (col_key, col_w) in enumerate(_COLS):
        c.setFillColor(DGRAY)
        cell_text = cells[i]

        if col_key == "description":
            desc_lines = cell_text.split("\n")
            line_h = 11
            block_h = len(desc_lines) * line_h
            # Block vertikal mittig in der Zeile
            start_y = y - (row_h - block_h) / 2 - 3
            for li, line in enumerate(desc_lines):
                line_y = start_y - li * line_h
                if li == 0:
                    c.setFont(FONT_BOLD, 9)
                    c.setFillColor(DGRAY)
                else:
                    c.setFont(FONT_BODY, 8.5)
                    c.setFillColor(MGRAY)
                c.drawString(cx + 4, line_y, line)
        elif _COL_ALIGNS[i] == "right":
            c.setFont(FONT_BODY, 9)
            c.drawRightString(cx + col_w - 4, cell_mid_y, cell_text)
        elif _COL_ALIGNS[i] == "center":
            c.setFont(FONT_BODY, 9)
            c.drawCentredString(cx + col_w / 2, cell_mid_y, cell_text)
        else:
            c.setFont(FONT_BODY, 9)
            c.drawString(cx + 4, cell_mid_y, cell_text)
        cx += col_w

    return y - row_h


def _draw_summary_rows(c: canvas.Canvas, x: float, y: float,
                       subtotal: float, tax_amt: float, total: float) -> float:
    y -= 4  # small gap after last data row

    rows = [
        ("Nettobetrag:",                      f"{subtotal:.2f} EUR".replace(".", ",")),
        ("zzgl. 0 % USt. (\u00a7 19 UStG):", f"{tax_amt:.2f} EUR".replace(".", ",")),
        ("GESAMT:",                            f"{total:.2f} EUR".replace(".", ",")),
    ]
    for i, (label, value) in enumerate(rows):
        is_total = (i == len(rows) - 1)
        sh = 24 if is_total else 20
        bg = DARK2 if is_total else (LGRAY if i % 2 == 0 else WHITE)
        c.setFillColor(bg)
        c.rect(x, y - sh, CONTENT_W, sh, fill=1, stroke=0)

        lbl_x = x + CONTENT_W - _COLS[-1][1] - 4
        val_x = x + CONTENT_W - 4

        c.setFont(FONT_BOLD if is_total else FONT_BODY, 9)
        c.setFillColor(CYAN if is_total else MGRAY)
        c.drawRightString(lbl_x, y - sh + 7, label)

        c.setFont(FONT_BOLD if is_total else FONT_BODY, 10 if is_total else 9)
        c.setFillColor(CYAN if is_total else DGRAY)
        c.drawRightString(val_x, y - sh + 7, value)

        y -= sh
    return y


# =====================================================================
# PAYMENT INFO BLOCK
# =====================================================================

def draw_payment_info(c: canvas.Canvas, y: float, invoice_number: str) -> float:
    block_h = 72  # 4 Zeilen à 11pt + Titel (14pt) + Padding
    c.setFillColor(DARK2)
    c.rect(MARGIN_L, y - block_h, CONTENT_W, block_h, fill=1, stroke=0)
    # Cyan left accent
    c.setFillColor(CYAN)
    c.rect(MARGIN_L, y - block_h, 3, block_h, fill=1, stroke=0)

    c.setFont(FONT_BOLD, 9)
    c.setFillColor(CYAN)
    c.drawString(MARGIN_L + 10, y - 14, "Zahlungsinformationen")

    fields = [
        ("IBAN:",       BANK_IBAN),
        ("BIC:",        BANK_BIC),
        ("Bank:",       BANK_NAME),
        ("Verwendung:", f"Rechnung {invoice_number}"),
    ]
    for i, (label, value) in enumerate(fields):
        row_y = y - 28 - i * 11
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(MGRAY)
        c.drawString(MARGIN_L + 10, row_y, label)
        c.setFont(FONT_BODY, 8)
        c.setFillColor(WHITE)
        c.drawString(MARGIN_L + 68, row_y, value)

    return y - block_h - 8


# =====================================================================
# GENERATOR
# =====================================================================

def generate_invoice_pdf(invoice, output_path: str = None) -> bytes | None:
    """
    Universeller PDF-Generator für Rechnung, Angebot, Gutschrift,
    Auftragsbestätigung.

    Args:
        invoice:     Invoice-Objekt aus WorkmateOS
        output_path: Optional. Wenn None → PDF als bytes zurückgeben.
    Returns:
        bytes wenn output_path=None, sonst None (Datei geschrieben).
    """
    # --- Setup ---
    doc_type = getattr(invoice, "document_type", "invoice")
    cfg      = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["invoice"])
    logo     = _resolve_logo()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        target = output_path
    else:
        target = BytesIO()

    # --- Positionen normalisieren ---
    raw_items = getattr(invoice, "line_items", None) or []
    positions: list[dict] = []
    for idx, item in enumerate(raw_items, start=1):
        if hasattr(item, "total") and item.total is not None:
            total = float(item.total)
        else:
            discount = getattr(item, "discount_percent", 0) or 0
            total = float(item.quantity) * float(item.unit_price) * (1 - discount / 100)
        positions.append({
            "pos":         idx,
            "description": item.description or "",
            "qty":         float(item.quantity),
            "unit":        getattr(item, "unit", "Stk."),
            "unit_price":  float(item.unit_price),
            "total_price": total,
        })
    if not positions:
        positions = [{
            "pos": "-", "description": "Keine Positionen vorhanden",
            "qty": 0, "unit": "", "unit_price": 0.0, "total_price": 0.0,
        }]

    subtotal  = sum(p["total_price"] for p in positions)
    tax_amt   = 0.0   # Kleinunternehmer
    inv_total = subtotal + tax_amt

    # Für Summenzeilen (aus invoice-Objekt falls vorhanden, sonst berechnet)
    sub_display   = float(getattr(invoice, "subtotal",   subtotal))
    tax_display   = float(getattr(invoice, "tax_amount", 0.0))
    total_display = float(getattr(invoice, "total",      inv_total))

    inv_number = getattr(invoice, "invoice_number", "—") or "—"
    status     = getattr(invoice, "status", None)
    terms_raw  = getattr(invoice, "terms", None) or cfg["terms_default"]
    notes      = getattr(invoice, "notes", None)
    responsible = getattr(invoice, "responsible_person", None) or COMPANY_OWNER

    # --- Höhen für Seitenzahl-Schätzung ---
    # Seite 1 Content-Bereich: CONTENT_START → MIN_Y
    # Fester Block oben: Absender + Empfänger + Meta + Titel + Betreff ≈ 170 pt
    FIXED_TOP = 170
    avail_p1  = CONTENT_START - FIXED_TOP - MIN_Y  # Platz für Tabelle auf S.1

    tbl_h = TABLE_HDR_H
    for p in positions:
        tbl_h += _row_h(p["description"])
    tbl_h += 4 + 20 + 20 + 24   # gap + 3 summary rows

    payment_h = 64 if doc_type == "invoice" else 0
    qr_h      = 35 if doc_type == "invoice" and total_display > 0 else 0
    terms_h   = len(terms_raw.split("\n")) * 11 + 40

    # Grobe Seitenzahl-Schätzung (für Footer-Text; max 1 Fehler ist ok)
    overflow  = max(0, tbl_h - avail_p1)
    avail_p2  = CONTENT_START - MIN_Y
    extra_pages = 0
    if overflow > 0:
        extra_pages = 1
        remaining_h = overflow - avail_p2
        if remaining_h > 0:
            extra_pages += int(remaining_h / avail_p2) + 1

    tail_h = payment_h + qr_h + terms_h
    tail_on_last = avail_p2 - max(0, tbl_h - avail_p1 - extra_pages * avail_p2)
    if tail_on_last < tail_h:
        extra_pages += 1

    total_pages = 1 + extra_pages

    # --- Canvas ---
    c = canvas.Canvas(target, pagesize=A4)
    current_page = [1]   # list for nonlocal mutation

    def start_page(first=False):
        draw_header(c, logo)

    def finish_page():
        draw_footer(c, current_page[0], total_pages)
        c.showPage()
        current_page[0] += 1

    def next_page():
        finish_page()
        start_page()

    # ===== SEITE 1 =====
    start_page(first=True)

    # Absender-Zeile (DIN 5008)
    y = CONTENT_START
    c.setFont(FONT_BODY, 7)
    c.setFillColor(MGRAY)
    c.line(MARGIN_L, y - 2, MARGIN_L + 85 * mm, y - 2)
    c.drawString(
        MARGIN_L, y - 14,
        f"{COMPANY_NAME}  \u2022  {COMPANY_STREET}  \u2022  {COMPANY_CITY}",
    )

    # Empfänger-Block
    RECIPIENT_Y = y - 32
    address_lines = format_customer_address(getattr(invoice, "customer", None))
    for i, line in enumerate(address_lines):
        c.setFont(FONT_BOLD if i == 0 else FONT_BODY, 10 if i == 0 else 9)
        c.setFillColor(NAVY if i == 0 else DGRAY)
        c.drawString(MARGIN_L, RECIPIENT_Y - i * 15, line)

    # Meta-Block (rechts)
    META_X = MARGIN_L + CONTENT_W * 0.55
    META_Y = RECIPIENT_Y
    title_key = "Angebotsnummer:" if doc_type == "quote" else "Rechnungsnummer:"
    meta_fields = [
        (title_key, inv_number),
        ("Datum:",  str(getattr(invoice, "issued_date", "—"))),
    ]
    if doc_type == "quote":
        meta_fields.append(("Gültig bis:", "14 Tage ab Datum"))
    elif doc_type == "invoice":
        meta_fields.append(("Fällig bis:", str(getattr(invoice, "due_date", "—"))))

    META_VALUE_X = META_X + 115  # Offset breit genug für "Rechnungsnummer:"
    for i, (label, value) in enumerate(meta_fields):
        row_y = META_Y - i * 16
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(MGRAY)
        c.drawString(META_X, row_y, label)
        c.setFont(FONT_BODY, 9)
        c.setFillColor(NAVY)
        c.drawString(META_VALUE_X, row_y, value or "—")

    # Status-Badge (nur Rechnung) – 2 Zeilen unter letztem Meta-Eintrag
    if doc_type == "invoice" and status:
        badge_y = META_Y - len(meta_fields) * 16 - 20
        draw_status_badge(c, status, META_X, badge_y)

    # Titel
    TITLE_Y = RECIPIENT_Y - 90
    c.setFont(FONT_MONO_B, 22)
    c.setFillColor(NAVY)
    c.drawString(MARGIN_L, TITLE_Y, cfg["title"])

    # Betreff-Box mit orangem Akzentbalken
    subject = notes or (
        "Rechnung für erbrachte Leistungen" if doc_type == "invoice"
        else "Angebot für geplante Leistungen"
    )
    SUBJECT_Y = TITLE_Y - 32
    c.setFillColor(ORANGE)
    c.rect(MARGIN_L, SUBJECT_Y - 2, 3, 18, fill=1, stroke=0)
    c.setFont(FONT_BOLD, 10)
    c.setFillColor(NAVY)
    c.drawString(MARGIN_L + 8, SUBJECT_Y + 3, f"Betreff: {subject}")

    # ===== POSITIONEN-TABELLE mit Seitenumbruch =====
    TABLE_Y = SUBJECT_Y - 22
    x = MARGIN_L

    # Tabellen-Header
    y = _draw_table_header_row(c, x, TABLE_Y)

    for row_idx, pos in enumerate(positions):
        rh = _row_h(pos["description"])
        # Platz prüfen: brauchen Zeile + Summen + Mindestpuffer
        sum_h = 4 + 20 + 20 + 24  # summary rows
        if y - rh - sum_h < MIN_Y + 20:
            # Fortsetzungshinweis
            c.setFont(FONT_ITALIC, 8)
            c.setFillColor(ORANGE)
            c.drawRightString(PAGE_W - MARGIN_R, y - 4,
                              "Fortsetzung auf nächster Seite \u2192")
            next_page()
            y = CONTENT_START - 6
            y = _draw_table_header_row(c, x, y)

        y = _draw_data_row(c, x, y, pos, row_idx)

    # Summen-Block
    y = _draw_summary_rows(c, x, y, sub_display, tax_display, total_display)

    # ===== ZAHLUNGSINFO + QR (nur Rechnung) =====
    if doc_type == "invoice":
        y -= 12
        # Neue Seite wenn zu wenig Platz
        if y - payment_h - qr_h < MIN_Y:
            next_page()
            y = CONTENT_START - 6

        y = draw_payment_info(c, y, inv_number)

        # SEPA-QR
        if total_display > 0:
            qr_size = 28  # mm
            qr_y = y - qr_size * mm
            if qr_y > MIN_Y:
                epc = build_epc_qr_string(total_display, inv_number)
                qr_x = PAGE_W - MARGIN_R - qr_size * mm
                draw_qr_code(c, qr_x, qr_y, qr_size, epc)
                c.setFont(FONT_BODY, 7)
                c.setFillColor(MGRAY)
                c.drawRightString(PAGE_W - MARGIN_R, qr_y - 3,
                                  "SEPA-Überweisung per Scan")
                y = qr_y - 6

    # ===== TERMS =====
    terms_lines = terms_raw.split("\n")
    terms_needed = len(terms_lines) * 11 + 42
    y -= 16

    if y - terms_needed < MIN_Y:
        next_page()
        y = CONTENT_START - 16

    # Terms-Überschrift
    c.setFont(FONT_BOLD, 9)
    c.setFillColor(NAVY)
    c.drawString(MARGIN_L, y, "Zahlungsbedingungen")
    c.setFillColor(ORANGE)
    c.rect(MARGIN_L, y - 2, CONTENT_W, 1.5, fill=1, stroke=0)
    y -= 12

    c.setFont(FONT_BODY, 9)
    c.setFillColor(DGRAY)
    for line in terms_lines:
        c.drawString(MARGIN_L, y, line)
        y -= 11

    # Rückfragen-Hinweis
    y -= 8
    prefix = "Bei Rückfragen: "
    c.setFont(FONT_BODY, 9)
    c.setFillColor(DGRAY)
    tw = c.stringWidth(prefix, FONT_BODY, 9)
    c.drawString(MARGIN_L, y, prefix)
    c.setFont(FONT_BOLD, 9)
    c.drawString(MARGIN_L + tw, y, responsible)

    # ===== FINAL FOOTER + SAVE =====
    finish_page()
    c.save()

    if output_path is None:
        pdf_bytes = target.getvalue()
        target.close()
        return pdf_bytes

    return None
