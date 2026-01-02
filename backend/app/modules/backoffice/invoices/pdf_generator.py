# app/modules/backoffice/invoices/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

import os
from pathlib import Path
from decimal import Decimal

from app.core.settings.config import settings

ASSETS_DIR = settings.ASSETS_DIR

# =====================================================================
# DOKUMENTTYPEN → Titel, Farben, Default Terms
# =====================================================================

DOCUMENT_TYPES = {
    "invoice": {
        "title": "RECHNUNG",
        "color": "#ff9100",
        "terms_default": "Zahlbar innerhalb von 14 Tagen nach Rechnungsdatum.",
    },
    "quote": {
        "title": "ANGEBOT",
        "color": "#008cff",
        "terms_default": "Dieses Angebot ist 14 Tage gültig.",
    },
    "credit_note": {
        "title": "GUTSCHRIFT",
        "color": "#5dcc5d",
        "terms_default": "Die Gutschrift wird mit offenen Posten verrechnet.",
    },
    "order_confirmation": {
        "title": "AUFTRAGSBESTÄTIGUNG",
        "color": "#9933ff",
        "terms_default": "Bitte prüfen Sie alle Angaben sorgfältig.",
    },
}

# Feste Stammdaten für Footer & SEPA-QR
COMPANY_NAME = "K.I.T. Solutions"
COMPANY_OWNER = "Joshua Phu Kuhrau"
COMPANY_STREET = "Dietzstr. 1"
COMPANY_ZIP_CITY = "56073 Koblenz"
COMPANY_COUNTRY = "Germany"
COMPANY_EMAIL = "info@kit-it-koblenz.de"
COMPANY_WEBSITE = "https://kit-it-koblenz.de"
COMPANY_PHONE = "Tel. 0162 / 2654262"

BANK_IBAN = "DE94100110012706471170"
BANK_BIC = "NTSBDEB1XX"
BANK_NAME = "N26 Bank AG"

# =====================================================================
# HELFER
# =====================================================================

def format_eur(value) -> str:
    """
    Formatiert Zahlen nach deutschem Firmenkunden-Schema:
    1234.5 -> '1.234,50 €'
    """
    if value is None:
        return "0,00 €"
    if isinstance(value, Decimal):
        value = float(value)

    # 1,234.50 -> 1.234,50
    s = f"{value:,.2f}"
    # US-Format: 1,234.50  ->  deutsch: 1.234,50
    s = s.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{s} €"


def draw_logo_watermark(c: canvas.Canvas, width, height):
    """
    Zeichnet ein halbtransparentes Logo als Wasserzeichen diagonal über die Seite.
    Wird nur verwendet, wenn das Logo existiert.
    """
    logo_path = Path(ASSETS_DIR) / "KIT_IT_GREY_NO_BACKGROUND.png"
    if not logo_path.exists():
        return

    try:
        c.saveState()
        # Mitte der Seite
        c.translate(width / 2, height / 2)
        # Diagonal drehen
        c.rotate(45)
        # Transparenz
        try:
            c.setFillAlpha(0.10)
        except Exception:
            # Wenn Alpha im Backend nicht verfügbar ist, einfach normal zeichnen
            pass

        # Bild relativ zur Mitte zeichnen
        watermark_width = 120 * mm
        c.drawImage(
            str(logo_path),
            -watermark_width / 2,
            -watermark_width / 2,
            width=watermark_width,
            preserveAspectRatio=True,
            mask="auto",
        )
        c.restoreState()
    except Exception:
        # Wasserzeichen ist nice-to-have; Fehler sollen das PDF nicht killen
        c.restoreState()


def build_epc_qr_string(amount: Decimal, invoice_number: str) -> str:
    """
    Baut den EPC-QR-String für SEPA-Zahlungen.
    Siehe: EPC069-12 (vereinfachte Variante).
    """
    eur_amount = float(amount) if isinstance(amount, Decimal) else amount
    amount_str = f"{eur_amount:.2f}"

    # Zeilen: BCD-Header, Version, Service Tag, Charakter-Set,
    #         Transfer Type, BIC, Name, IBAN, Betrag, Purpose, Verwendungszweck, leer
    lines = [
        "BCD",
        "001",
        "1",
        "SCT",
        BANK_BIC,
        COMPANY_NAME,
        BANK_IBAN,
        f"EUR{amount_str}",
        "",
        f"Rechnung {invoice_number}",
        "",
    ]
    return "\n".join(lines)


def draw_qr_code(c: canvas.Canvas, x: float, y: float, size_mm: float, data: str):
    """Zeichnet einen QR-Code an Position (x, y) mit gegebener Datenbasis."""
    qr_code = qr.QrCodeWidget(data)
    bounds = qr_code.getBounds()
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    size = size_mm * mm

    d = Drawing(size, size)
    d.add(qr_code)
    d.scale(size / w, size / h)
    renderPDF.draw(d, c, x, y)


def format_customer_address(customer) -> list[str]:
    """
    Baut eine saubere Adress-Blockliste für den Kunden.
    """
    lines = []
    if not customer:
        return ["Unbekannter Kunde"]

    if getattr(customer, "name", None):
        lines.append(customer.name)

    street = getattr(customer, "street", None) or ""
    zip_code = getattr(customer, "zip_code", None) or ""
    city = getattr(customer, "city", None) or ""
    country = getattr(customer, "country", None) or ""

    if street:
        lines.append(street)

    zip_city = f"{zip_code} {city}".strip()
    if zip_city:
        lines.append(zip_city)

    if country and country not in lines:
        lines.append(country)

    return lines


def draw_footer(c: canvas.Canvas, width: float, margin: float, accent_color, page_num: int = None, total_pages: int = None):
    """
    Zeichnet den 3-Spalten-Footer mit Firmendaten.
    """
    footer_y = 35 * mm   # etwas tiefer, wirkt ruhiger

    # Divider
    c.setStrokeColor(accent_color)
    c.setLineWidth(1)
    c.line(margin, footer_y + 20, width - margin, footer_y + 20)

    # Schrift
    c.setFont("Roboto", 8)
    c.setFillColor(colors.black)

    # Grid
    usable_width = width - 2 * margin
    col_width = usable_width / 3

    left_x  = margin
    mid_x   = margin + col_width
    right_x = margin + 2 * col_width

    # Zeilenabstände (perfekt für 8pt Roboto)
    line_step = 12
    line1 = 0
    line2 = line_step
    line3 = line_step * 2
    line4 = line_step * 3

    # -------------------------------
    # SPALTE 1: ANSCHRIFT
    # -------------------------------
    c.drawString(left_x, footer_y,                 COMPANY_NAME)
    c.drawString(left_x, footer_y - line2,         f"Inhaber: {COMPANY_OWNER}")
    c.drawString(left_x, footer_y - line3,         COMPANY_STREET)
    c.drawString(left_x, footer_y - line4,         COMPANY_ZIP_CITY)

    # -------------------------------
    # SPALTE 2: KONTAKT
    # -------------------------------
    c.drawString(mid_x, footer_y,                  "Kontakt")
    c.drawString(mid_x, footer_y - line2,          COMPANY_EMAIL)
    c.drawString(mid_x, footer_y - line3,          COMPANY_WEBSITE.replace("https://", ""))
    c.drawString(mid_x, footer_y - line4,          COMPANY_PHONE)

    # -------------------------------
    # SPALTE 3: BANK
    # -------------------------------
    c.drawString(right_x, footer_y,                "Bankverbindung")
    c.drawString(right_x, footer_y - line2,        f"IBAN: {BANK_IBAN}")
    c.drawString(right_x, footer_y - line3,        f"BIC: {BANK_BIC}")
    c.drawString(right_x, footer_y - line4,        BANK_NAME)

    # -------------------------------
    # SEITENZAHL (zentriert unter dem Footer)
    # -------------------------------
    if page_num is not None and total_pages is not None:
        c.setFont("Roboto", 8)
        c.setFillColor(colors.grey)
        page_text = f"Seite {page_num} von {total_pages}"
        text_width = c.stringWidth(page_text, "Roboto", 8)
        c.drawString((width - text_width) / 2, footer_y - line4 - 8, page_text)
        c.setFillColor(colors.black)


# =====================================================================
# GENERATOR
# =====================================================================

def generate_invoice_pdf(invoice, output_path: str = None) -> bytes | None:
    """
    Universeller PDF-Generator für:
    - Rechnung
    - Angebot
    - Gutschrift
    - Auftragsbestätigung
    inkl.:
    - Logo-Wasserzeichen
    - dynamischer Farb- & Titelwahl
    - Summenblock mit doppelt unterstrichenem Gesamtbetrag
    - Terms / Zahlungsbedingungen
    - 3-Spalten-Footer
    - SEPA-EPC-QR (und optional Payment-URL-QR)

    Args:
        invoice: Invoice object
        output_path: Optional file path. If None, returns PDF as bytes.

    Returns:
        If output_path is None: PDF content as bytes
        If output_path is provided: None (saves to file)
    """
    from io import BytesIO
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Register Roboto fonts
    # Use absolute path to ensure fonts are found
    fonts_dir = Path("/app/app/assets/fonts")
    pdfmetrics.registerFont(TTFont('Roboto', str(fonts_dir / "Roboto-Regular.ttf")))
    pdfmetrics.registerFont(TTFont('Roboto-Bold', str(fonts_dir / "Roboto-Bold.ttf")))
    pdfmetrics.registerFont(TTFont('Roboto-Italic', str(fonts_dir / "Roboto-Italic.ttf")))
    pdfmetrics.registerFont(TTFont('Roboto-BoldItalic', str(fonts_dir / "Roboto-BoldItalic.ttf")))

    # Create BytesIO buffer if no output path
    if output_path is None:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 20 * mm

    # ---------------------------------------------------------
    # Dokumenttyp & Farbe
    # ---------------------------------------------------------
    doc_type = getattr(invoice, "document_type", "invoice")
    cfg = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["invoice"])
    accent_color = colors.HexColor(cfg["color"])

    # Seitenzahl-Tracking
    current_page = 1

    # ---------------------------------------------------------
    # Wasserzeichen (Logo)
    # ---------------------------------------------------------
    draw_logo_watermark(c, width, height)

    # ---------------------------------------------------------
    # HEADER (Logo oben links, Firmendaten oben rechts)
    # ---------------------------------------------------------
    logo_path = Path(ASSETS_DIR) / "KIT_IT_GREY_NO_BACKGROUND.png"
    if logo_path.exists():
        c.drawImage(
            str(logo_path),
            margin,
            height - 45 * mm,
            width=40 * mm,
            preserveAspectRatio=True,
            mask="auto",
        )

    c.setFont("Roboto-Bold", 14)
    c.drawRightString(width - margin, height - 20 * mm, COMPANY_NAME)

    c.setFont("Roboto", 9)
    c.drawRightString(
        width - margin,
        height - 26 * mm,
        f"Inhaber: {COMPANY_OWNER}",
    )
    c.drawRightString(
        width - margin,
        height - 31 * mm,
        f"{COMPANY_STREET} · {COMPANY_ZIP_CITY}",
    )
    c.drawRightString(
        width - margin,
        height - 36 * mm,
        f"{COMPANY_EMAIL} · kit-it-koblenz.de",
    )
    c.drawRightString(
        width - margin,
        height - 41 * mm,
        COMPANY_PHONE,
    )

    # ---------------------------------------------------------
    # TITELBLOCK (Dokumenttyp, Nummer, Datum, Fälligkeit)
    # ---------------------------------------------------------
    c.setFont("Roboto-Bold", 18)
    c.setFillColor(accent_color)
    c.drawString(margin, height - 55 * mm, cfg["title"])

    c.setFillColor(colors.black)
    c.setFont("Roboto-Bold", 10)
    c.drawString(margin, height - 65 * mm, f"Nummer: {invoice.invoice_number}")
    c.drawString(margin, height - 72 * mm, f"Datum: {invoice.issued_date}")
    if doc_type == "invoice":
        c.drawString(
            margin,
            height - 79 * mm,
            f"Fällig bis: {getattr(invoice, 'due_date', None) or '—'}",
        )
    elif doc_type == "quote":
        c.drawString(
            margin,
            height - 79 * mm,
            "Dieses Angebot ist 14 Tage gültig.",
        )

    # ---------------------------------------------------------
    # KUNDENBLOCK
    # ---------------------------------------------------------
    y = height - 95 * mm
    c.setFont("Roboto-Bold", 11)

    address_lines = format_customer_address(getattr(invoice, "customer", None))
    for i, line in enumerate(address_lines):
        if i == 0:
            c.drawString(margin, y, line)
        else:
            c.setFont("Roboto", 9)
            c.drawString(margin, y - 5 * mm * i, line)

    # ---------------------------------------------------------
    # OPTIONALE HINWEISBOX (oberhalb der Tabelle)
    # Verwendet invoice.notes, falls vorhanden
    # ---------------------------------------------------------
    notes = getattr(invoice, "notes", None)
    y_table_top = y - 35 * mm

    if notes:
        box_height = 15 * mm
        box_y = y_table_top
        c.setStrokeColor(accent_color)
        c.setFillColor(colors.white)
        c.setLineWidth(0.5)
        c.roundRect(margin, box_y - box_height, width - 2 * margin, box_height, 3 * mm)

        c.setFont("Roboto-Bold", 9)
        c.setFillColor(accent_color)
        c.drawString(margin + 3 * mm, box_y - 5, "Hinweis")
        c.setFillColor(colors.black)
        c.setFont("Roboto", 8)

        text_obj = c.beginText(margin + 3 * mm, box_y - 10)
        text_obj.setLeading(10)
        for line in notes.split("\n"):
            text_obj.textLine(line)
        c.drawText(text_obj)

        y_table_top = box_y - box_height - 5 * mm

    # ---------------------------------------------------------
    # POSITIONSTABELLE
    # ---------------------------------------------------------
    # Styles für Tabellen-Inhalte
    desc_style = ParagraphStyle(
        'Description',
        fontName='Roboto',
        fontSize=9,
        leading=11,
        alignment=0,  # LEFT
    )

    bold_style = ParagraphStyle(
        'Bold',
        fontName='Roboto-Bold',
        fontSize=9,
        leading=11,
        alignment=1,  # CENTER
    )

    data = [["Pos", "Beschreibung", "Menge", "Einheit", "Einzelpreis", "Gesamt"]]

    if getattr(invoice, "line_items", None):
        for idx, item in enumerate(invoice.line_items, start=1):
            total = item.total if hasattr(item, "total") else (
                (item.quantity * item.unit_price) * (1 - item.discount_percent / 100)
            )
            # Beschreibung als Paragraph für automatischen Umbruch
            desc_paragraph = Paragraph(item.description or "", desc_style)

            # Position, Menge und Gesamt fett
            pos_paragraph = Paragraph(str(idx), bold_style)
            qty_paragraph = Paragraph(f"{item.quantity:.2f}", bold_style)
            total_paragraph = Paragraph(format_eur(total), bold_style)

            data.append(
                [
                    pos_paragraph,
                    desc_paragraph,
                    qty_paragraph,
                    item.unit,
                    format_eur(item.unit_price),
                    total_paragraph,
                ]
            )
    else:
        data.append(["-", "Keine Positionen vorhanden", "", "", "", ""])

    table = Table(
        data,
        colWidths=[15 * mm, 65 * mm, 22 * mm, 22 * mm, 28 * mm, 28 * mm],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), accent_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Roboto-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 1), (-1, -1), "Roboto"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),  # Nur Beschreibung linksbündig
                ("ALIGN", (0, 0), (0, -1), "CENTER"),  # Pos zentriert
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),  # Menge, Einheit, Einzelpreis, Gesamt zentriert
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.whitesmoke, colors.Color(0.97, 0.97, 0.97)]),
                ("LEFTPADDING", (0, 1), (-1, -1), 4),
                ("RIGHTPADDING", (0, 1), (-1, -1), 4),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
            ]
        )
    )

    avail_width = width - 2 * margin
    table_w, table_h = table.wrap(avail_width, height)

    # Berechne verfügbaren Platz auf aktueller Seite
    footer_line_y = 55 * mm  # Footer blue line position
    summen_height = 25 * mm  # Platz für Summenblock
    min_y_above_footer = footer_line_y + 15 * mm  # Sicherheitsabstand

    # Verfügbare Höhe für Tabelle auf aktueller Seite
    available_height = y_table_top - min_y_above_footer - summen_height

    # ======================================================================
    # BERECHNE TOTAL PAGES (für Seitenzahlen im Footer)
    # ======================================================================
    total_pages = current_page  # Start mit aktueller Seite (1)

    # Prüfe ob Tabelle gesplittet werden muss
    if table_h > available_height:
        split_tables_preview = table.split(avail_width, available_height)
        if len(split_tables_preview) > 1:
            total_pages += len(split_tables_preview) - 1  # Zusätzliche Seiten für Tabellen-Teile

    # Prüfe ob Terms auf neue Seite müssen
    terms = getattr(invoice, "terms", None) or cfg["terms_default"]
    terms_lines = len(terms.split("\n"))
    terms_height_calc = (terms_lines * 11) + 5 * mm
    contact_height = 11
    total_content_height = terms_height_calc + contact_height + 5 * mm

    # Simuliere y_totals Position
    if table_h > available_height:
        # Tabelle wird gesplittet, y_totals ist auf letzter Tabellenseite
        # Nimm Höhe der letzten Tabelle
        if len(split_tables_preview) > 1:
            last_table = split_tables_preview[-1]
            last_table_w, last_table_h = last_table.wrap(avail_width, height)
            simulated_table_y = height - 40 * mm - last_table_h
            simulated_y_totals = simulated_table_y - 10 * mm
        else:
            simulated_y_totals = height - 40 * mm - table_h - 10 * mm
    else:
        # Tabelle passt auf Seite 1
        simulated_y_totals = y_table_top - table_h - 10 * mm

    simulated_terms_title_y = simulated_y_totals - 20 * mm
    footer_line_y_check = 55 * mm
    min_safe_y = footer_line_y_check + 10 * mm

    if (simulated_terms_title_y - total_content_height) < min_safe_y:
        total_pages += 1  # Terms brauchen eine neue Seite

    # ======================================================================
    # ENDE TOTAL PAGES BERECHNUNG
    # ======================================================================

    # Versuche Tabelle zu splitten wenn nötig
    if table_h > available_height:
        # Tabelle splitten
        split_tables = table.split(avail_width, available_height)

        if len(split_tables) > 1:
            # Erster Teil auf aktuelle Seite
            first_table = split_tables[0]
            first_table_w, first_table_h = first_table.wrap(avail_width, available_height)
            table_y = y_table_top - first_table_h
            first_table.drawOn(c, margin, table_y)

            # Hinweis "Fortsetzung auf Seite 2"
            c.setFont("Roboto-Italic", 9)
            c.setFillColor(accent_color)
            continuation_y = table_y - 5 * mm
            c.drawRightString(width - margin, continuation_y, "Fortsetzung auf Seite 2 →")
            c.setFillColor(colors.black)

            # Footer auf Seite 1
            draw_footer(c, width, margin, accent_color, current_page, total_pages)

            # Neue Seite für Rest der Tabelle
            c.showPage()
            current_page += 1
            draw_logo_watermark(c, width, height)

            # Hinweis "Fortsetzung von Seite 1" oben auf Seite 2
            c.setFont("Roboto-Italic", 9)
            c.setFillColor(accent_color)
            c.drawString(margin, height - 30 * mm, "← Fortsetzung von Seite 1")
            c.setFillColor(colors.black)

            # Restliche Tabellen-Teile auf neue Seiten
            current_y = height - 40 * mm
            for remaining_table in split_tables[1:]:
                rem_w, rem_h = remaining_table.wrap(avail_width, height)

                # Prüfe ob auf aktuelle Seite passt
                if current_y - rem_h < (footer_line_y + summen_height + 15 * mm):
                    # Footer zeichnen
                    draw_footer(c, width, margin, accent_color, current_page, total_pages)
                    # Neue Seite
                    c.showPage()
                    current_page += 1
                    draw_logo_watermark(c, width, height)
                    current_y = height - 40 * mm

                table_y = current_y - rem_h
                remaining_table.drawOn(c, margin, table_y)
                current_y = table_y

            # y_totals auf letzter Position nach letztem Tabellenteil
            y_totals = table_y - 10 * mm
        else:
            # Tabelle passt nicht mal gesplittet auf eine Seite - komplett auf neue Seite
            draw_footer(c, width, margin, accent_color, current_page, total_pages)
            c.showPage()
            current_page += 1
            draw_logo_watermark(c, width, height)
            table_y = height - 40 * mm - table_h
            table.drawOn(c, margin, table_y)
            y_totals = table_y - 10 * mm
    else:
        # Tabelle passt komplett auf aktuelle Seite
        table_y = y_table_top - table_h
        table.drawOn(c, margin, table_y)
        y_totals = table_y - 10 * mm

    # ---------------------------------------------------------
    # SUMMENBLOCK (mit doppelt unterstrichenem Gesamtbetrag)
    # ---------------------------------------------------------
    y_totals = table_y - 10 * mm

    c.setFont("Roboto-Bold", 10)
    c.setFillColor(colors.black)

    c.drawRightString(width - margin - 60, y_totals, "Zwischensumme:")
    c.drawRightString(width - margin, y_totals, format_eur(invoice.subtotal))

    c.drawRightString(width - margin - 60, y_totals - 6 * mm, "MwSt:")
    c.drawRightString(width - margin, y_totals - 6 * mm, format_eur(invoice.tax_amount))

    total_y = y_totals - 12 * mm
    c.setFillColor(accent_color)
    c.drawRightString(width - margin - 60, total_y, "Gesamtbetrag:")
    c.drawRightString(width - margin, total_y, format_eur(invoice.total))
    c.setFillColor(colors.black)

    # Doppelte Unterstreichung unter dem Gesamtbetrag
    line_left = width - margin - 60
    line_right = width - margin
    c.setLineWidth(0.7)
    c.setStrokeColor(accent_color)
    c.line(line_left, total_y - 2, line_right, total_y - 2)
    c.line(line_left, total_y - 4, line_right, total_y - 4)

    # ---------------------------------------------------------
    # QR-CODES (SEPA & optional Payment-URL) - auf Seite 1 bei Totals
    # ---------------------------------------------------------
    qr_size = 30  # mm
    qr_y = y_totals - 60 * mm  # Position unterhalb der Totals

    # SEPA-EPC-QR nur bei Rechnungen & positive Beträge
    if doc_type == "invoice" and float(invoice.total) > 0:
        epc_data = build_epc_qr_string(invoice.total, invoice.invoice_number)
        qr_x = width - margin - qr_size * mm
        draw_qr_code(c, qr_x, qr_y, qr_size, epc_data)
        c.setFont("Roboto", 7)
        c.drawRightString(
            width - margin,
            qr_y - 3,
            "SEPA-Überweisung per Scan",
        )

    # Optional: Payment-URL-QR (z.B. Stripe-Link), falls verfügbar
    payment_url = getattr(invoice, "payment_url", None)
    if payment_url:
        qr2_x = width - margin - 2 * qr_size * mm - 5 * mm
        draw_qr_code(c, qr2_x, qr_y, qr_size, payment_url)
        c.setFont("Roboto", 7)
        c.drawString(
            qr2_x,
            qr_y - 3,
            "Online-Zahlung",
        )

    # ---------------------------------------------------------
    # TERMS / ZAHLUNGSBEDINGUNGEN
    # ---------------------------------------------------------
    terms = getattr(invoice, "terms", None) or cfg["terms_default"]

    # Calculate space needed for Terms + Rückfragen
    terms_lines = len(terms.split("\n"))
    terms_height = (terms_lines * 11) + 5 * mm  # 11 = leading, 5mm = space after title
    contact_height = 11  # Rückfragen line height
    total_content_height = terms_height + contact_height + 5 * mm  # 5mm = title "Zahlungsbedingungen:"

    # Footer blue line is at 55mm from bottom (footer_y + 20)
    footer_line_y = 55 * mm
    min_safe_y = footer_line_y + 10 * mm  # 10mm safety margin above footer line

    # Calculate initial position
    terms_title_y = y_totals - 20 * mm

    # Check if content would overlap with footer
    if (terms_title_y - total_content_height) < min_safe_y:
        # Draw footer on current page first
        draw_footer(c, width, margin, accent_color, current_page, total_pages)

        # Start new page for Terms + Rückfragen
        c.showPage()
        current_page += 1
        # Redraw watermark on new page
        draw_logo_watermark(c, width, height)
        # Position Terms at top of new page
        terms_title_y = height - 40 * mm

    c.setFont("Roboto", 9)
    c.drawString(margin, terms_title_y, "Zahlungsbedingungen:")

    text_obj = c.beginText(margin, terms_title_y - 5 * mm)
    text_obj.setLeading(11)
    for line in terms.split("\n"):
        text_obj.textLine(line)

    c.drawText(text_obj)

    # Rückfragen-Hinweis mit fettem Namen
    responsible = getattr(invoice, "responsible_person", None)
    if not responsible:
        # Fallback: Nur den Namen des Inhabers verwenden
        responsible = COMPANY_OWNER

    # Berechne Y-Position nach den Terms
    contact_y = terms_title_y - 5 * mm - (len(terms.split("\n")) * 11) - 11  # 11 = leading

    # Zeichne Text in zwei Teilen: normaler Text + fetter Name
    c.setFont("Roboto", 9)
    text_before = "Bei Rückfragen wenden Sie sich bitte an: "
    text_width = c.stringWidth(text_before, "Roboto", 9)
    c.drawString(margin, contact_y, text_before)

    c.setFont("Roboto-Bold", 9)
    c.drawString(margin + text_width, contact_y, responsible)

    # ---------------------------------------------------------
    # FOOTER (3 Spalten) – Clean & Stable Version
    # ---------------------------------------------------------
    draw_footer(c, width, margin, accent_color, current_page, total_pages)

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------
    c.showPage()
    c.save()

    # Return bytes if no output path
    if output_path is None:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    return None
