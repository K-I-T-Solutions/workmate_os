"""
DATEV EXTF Export (Buchungsstapel)
------------------------------------
Exportiert Rechnungen im DATEV-EXTF-Format (External Format),
kompatibel mit DATEV Unternehmen online und DATEV Kanzlei-Rechnungswesen.

Standard: DATEV EXTF Buchungsstapel, Version 700
Kontenrahmen: SKR03 (Standard für Freiberufler/Dienstleister)

Kontenzuordnung SKR03:
  Erlöse 19% MwSt  → 8400
  Erlöse  7% MwSt  → 8300
  Erlöse  0% MwSt  → 8100
  Kunden-Sachkonto → 10000 (pauschaler Debitorenbereich)
"""
import csv
from datetime import date, datetime
from io import BytesIO, StringIO
from typing import Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.backoffice.invoices import models


# SKR03 Erlöskonten nach MwSt-Satz
_TAX_ACCOUNTS = {
    19: "8400",
    7:  "8300",
    0:  "8100",
}
_DEFAULT_REVENUE_ACCOUNT = "8400"

# Kunden-Debitorenkonto (pauschales Sammelkonto)
_DEBITOR_ACCOUNT = "10000"

# DATEV EXTF: Trennzeichen ist Semikolon, Encoding: CP1252
_DATEV_ENCODING = "cp1252"
_DATEV_DELIMITER = ";"


def _datev_amount(value: Decimal) -> str:
    """Betrag als DATEV-Format: Komma als Dezimaltrenner, kein Tausender."""
    return str(value.quantize(Decimal("0.01"))).replace(".", ",")


def _datev_date(d: Optional[date]) -> str:
    """Datum als DDMM (DATEV Belegdatum-Format)."""
    if not d:
        return ""
    return d.strftime("%d%m")


def _datev_date_full(d: Optional[date]) -> str:
    """Datum als TTMMJJJJ für den EXTF-Header."""
    if not d:
        return ""
    return d.strftime("%d%m%Y")


def _invoice_number_short(invoice_number: str) -> str:
    """Kürzt Rechnungsnummer auf max. 12 Zeichen (DATEV Belegfeld1-Limit)."""
    return invoice_number[:12]


def _determine_revenue_account(invoice: models.Invoice) -> str:
    """
    Erlöskonto aus dem dominanten MwSt-Satz der Rechnungspositionen bestimmen.
    Nimmt den häufigsten Steuersatz.
    """
    if not invoice.line_items:
        return _DEFAULT_REVENUE_ACCOUNT

    tax_totals: dict[int, Decimal] = {}
    for item in invoice.line_items:
        rate = int(item.tax_rate)
        tax_totals[rate] = tax_totals.get(rate, Decimal("0")) + item.subtotal_after_discount

    dominant_rate = max(tax_totals, key=lambda r: tax_totals[r])
    return _TAX_ACCOUNTS.get(dominant_rate, _DEFAULT_REVENUE_ACCOUNT)


def generate_datev_extf(
    db: Session,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    only_paid: bool = False,
) -> bytes:
    """
    Generiert DATEV EXTF Buchungsstapel als CSV-Bytes (CP1252).

    Args:
        db: SQLAlchemy Session
        from_date: Filter: Rechnungsdatum ab
        to_date: Filter: Rechnungsdatum bis
        only_paid: Nur bezahlte Rechnungen exportieren

    Returns:
        bytes im DATEV EXTF Format (CP1252 kodiert)

    Format:
        Zeile 1: EXTF-Header (Metadaten)
        Zeile 2: Spaltenüberschriften
        Zeile 3+: Buchungszeilen
    """
    # Rechnungen laden
    query = db.query(models.Invoice).filter(
        models.Invoice.deleted_at.is_(None),
        models.Invoice.document_type == "invoice",
    )

    if from_date:
        query = query.filter(models.Invoice.issued_date >= from_date)
    if to_date:
        query = query.filter(models.Invoice.issued_date <= to_date)
    if only_paid:
        query = query.filter(models.Invoice.status.in_(["paid", "partial"]))
    else:
        # Nur fertige Rechnungen (nicht Entwürfe/stornierte)
        query = query.filter(models.Invoice.status.in_(["sent", "paid", "partial", "overdue"]))

    invoices = query.order_by(models.Invoice.issued_date).all()

    # Datumsbereich für Header
    header_from = from_date or (invoices[0].issued_date if invoices else date.today())
    header_to = to_date or (invoices[-1].issued_date if invoices else date.today())
    now_str = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:17] + "000"

    output = StringIO()

    # -------------------------------------------------------------------------
    # Zeile 1: EXTF-Header
    # Felder: Kennzeichen;Versionsnummer;Datenkategorie;Formatname;Formatversion;
    #         Erzeugt_am;Importiert;"";Herkunft;Exportiert_von;"";"";
    #         Sachkontonummernlänge;Datum_von;Datum_bis;Währungskennzeichen;
    #         "derivativer_Buchungstyp";"SKR";"BranchenloesungId";"";"";""
    # -------------------------------------------------------------------------
    header_line = _DATEV_DELIMITER.join([
        '"EXTF"',
        "700",
        "21",
        '"Buchungsstapel"',
        "4",
        now_str,
        '""',
        '""',
        '""',
        '""',
        '""',
        "4",                              # Sachkontonummernlänge
        _datev_date_full(header_from),
        _datev_date_full(header_to),
        '""',
        '""',
        '""',
        '""',
        '""',
        '""',
        '""',
        '""',
        '""',
    ])
    output.write(header_line + "\r\n")

    # -------------------------------------------------------------------------
    # Zeile 2: Spaltenüberschriften (DATEV Pflichtformat)
    # -------------------------------------------------------------------------
    column_headers = [
        "Umsatz (ohne Soll/Haben-Kz)",
        "Soll/Haben-Kennzeichen",
        "WKZ Umsatz",
        "Kurs",
        "Basis-Umsatz",
        "WKZ Basis-Umsatz",
        "Konto",
        "Gegenkonto (ohne BU-Schlüssel)",
        "BU-Schlüssel",
        "Belegdatum",
        "Belegfeld 1",
        "Belegfeld 2",
        "Skonto",
        "Buchungstext",
        "Postensperre",
        "Diverse Adressnummer",
        "Geschäftspartnerbank",
        "Sachverhalt",
        "Zinssperre",
        "Beleglink",
        "Beleginfo - Art 1",
        "Beleginfo - Inhalt 1",
        "Beleginfo - Art 2",
        "Beleginfo - Inhalt 2",
        "Beleginfo - Art 3",
        "Beleginfo - Inhalt 3",
    ]
    output.write(_DATEV_DELIMITER.join(column_headers) + "\r\n")

    # -------------------------------------------------------------------------
    # Datenzeilen: eine Zeile pro Rechnung
    # -------------------------------------------------------------------------
    for invoice in invoices:
        revenue_account = _determine_revenue_account(invoice)

        customer_name = ""
        if invoice.customer:
            customer_name = (invoice.customer.name or invoice.customer.company_name or "")[:60]

        row = [
            _datev_amount(invoice.total),   # Umsatz brutto
            "S",                             # Soll (Forderung gegenüber Kunde)
            "EUR",                           # Währung
            "",                              # Kurs (leer bei EUR)
            "",                              # Basis-Umsatz
            "",                              # WKZ Basis
            _DEBITOR_ACCOUNT,                # Konto (Debitor)
            revenue_account,                 # Gegenkonto (Erlöskonto)
            "",                              # BU-Schlüssel (Steuerautomatik)
            _datev_date(invoice.issued_date),
            _invoice_number_short(invoice.invoice_number),
            "",                              # Belegfeld 2
            "",                              # Skonto
            customer_name,                   # Buchungstext
            "",                              # Postensperre
            "",                              # Diverse Adressnummer
            "",                              # Geschäftspartnerbank
            "",                              # Sachverhalt
            "",                              # Zinssperre
            "",                              # Beleglink
            "Rechnungsnummer",               # Beleginfo Art 1
            invoice.invoice_number,          # Beleginfo Inhalt 1
            "Nettobetrag",                   # Beleginfo Art 2
            _datev_amount(invoice.subtotal), # Beleginfo Inhalt 2
            "MwSt",                          # Beleginfo Art 3
            _datev_amount(invoice.tax_amount),  # Beleginfo Inhalt 3
        ]

        output.write(_DATEV_DELIMITER.join(row) + "\r\n")

    return output.getvalue().encode(_DATEV_ENCODING, errors="replace")
