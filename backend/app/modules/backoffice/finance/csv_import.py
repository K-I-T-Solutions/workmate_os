"""
CSV-Import für Banktransaktionen

Unterstützt gängige deutsche Bank-Formate:
- N26
- Sparkasse
- Volksbank
- Deutsche Bank
- Commerzbank
- ING DiBa
"""
import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy.orm import Session

from .models import BankTransaction, BankAccount, TransactionType
from .schemas import BankTransactionCreate


# ============================================================================
# CSV FORMAT DETECTION
# ============================================================================

class BankFormat(str, Enum):
    """Unterstützte Bank-CSV-Formate."""
    N26 = "n26"
    SPARKASSE = "sparkasse"
    VOLKSBANK = "volksbank"
    DEUTSCHE_BANK = "deutsche_bank"
    COMMERZBANK = "commerzbank"
    ING = "ing"
    GENERIC = "generic"


# ============================================================================
# FIELD MAPPINGS
# ============================================================================

FIELD_MAPPINGS = {
    BankFormat.N26: {
        "date": ["Date", "Datum", "Buchungstag"],
        "amount": ["Amount (EUR)", "Betrag", "Amount"],
        "counterparty": ["Payee", "Empfänger", "Counterparty"],
        "purpose": ["Payment Reference", "Verwendungszweck", "Reference"],
        "reference": ["Transaction ID", "Transaktions-ID", "ID"],
    },
    BankFormat.SPARKASSE: {
        "date": ["Buchungstag", "Valutadatum"],
        "amount": ["Betrag", "Umsatz"],
        "counterparty": ["Beguenstigter/Zahlungspflichtiger", "Empfänger/Auftraggeber"],
        "purpose": ["Verwendungszweck", "Buchungstext"],
        "reference": ["Mandatsreferenz", "Referenz"],
        "iban": ["Kontonummer/IBAN", "IBAN"],
    },
    BankFormat.GENERIC: {
        "date": ["Date", "Datum", "Buchungstag", "Valutadatum", "Transaction Date"],
        "amount": ["Amount", "Betrag", "Umsatz"],
        "counterparty": ["Counterparty", "Empfänger", "Zahlungspartner", "Name"],
        "purpose": ["Purpose", "Verwendungszweck", "Reference", "Description"],
        "reference": ["Reference", "Referenz", "Transaction ID", "ID"],
        "iban": ["IBAN", "Kontonummer"],
    },
}


def detect_bank_format(headers: List[str]) -> BankFormat:
    """
    Erkennt Bank-Format anhand der CSV-Header.

    Returns:
        BankFormat enum value
    """
    headers_lower = [h.lower() for h in headers]

    # N26 detection
    if any("n26" in h for h in headers_lower) or "payee" in headers_lower:
        return BankFormat.N26

    # Sparkasse detection
    if any("buchungstag" in h for h in headers_lower) and any("beguenstigter" in h for h in headers_lower):
        return BankFormat.SPARKASSE

    # Volksbank detection
    if any("volksbank" in h for h in headers_lower):
        return BankFormat.VOLKSBANK

    # Deutsche Bank detection
    if any("deutsche bank" in h for h in headers_lower):
        return BankFormat.DEUTSCHE_BANK

    # Commerzbank detection
    if any("commerzbank" in h for h in headers_lower):
        return BankFormat.COMMERZBANK

    # ING detection
    if any("ing" in h for h in headers_lower) or any("diba" in h for h in headers_lower):
        return BankFormat.ING

    # Default to generic
    return BankFormat.GENERIC


def find_column(headers: List[str], field_names: List[str]) -> Optional[str]:
    """
    Findet die passende Spalte für ein Feld.

    Args:
        headers: CSV Header
        field_names: Liste möglicher Feldnamen

    Returns:
        Header-Name oder None
    """
    headers_lower = {h.lower(): h for h in headers}

    for field_name in field_names:
        field_lower = field_name.lower()
        if field_lower in headers_lower:
            return headers_lower[field_lower]

    return None


# ============================================================================
# DATE PARSING
# ============================================================================

def parse_date(date_str: str) -> Optional[date]:
    """
    Parst verschiedene Datumsformate.

    Unterstützt:
    - YYYY-MM-DD (ISO)
    - DD.MM.YYYY (Deutsch)
    - DD/MM/YYYY
    - MM/DD/YYYY (US)
    """
    if not date_str or date_str.strip() == "":
        return None

    date_str = date_str.strip()

    formats = [
        "%Y-%m-%d",      # 2026-01-02
        "%d.%m.%Y",      # 02.01.2026
        "%d/%m/%Y",      # 02/01/2026
        "%m/%d/%Y",      # 01/02/2026 (US)
        "%Y/%m/%d",      # 2026/01/02
        "%d-%m-%Y",      # 02-01-2026
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


# ============================================================================
# AMOUNT PARSING
# ============================================================================

def parse_amount(amount_str: str) -> Optional[Decimal]:
    """
    Parst Beträge mit verschiedenen Formaten.

    Unterstützt:
    - 1234.56 (Punkt als Dezimaltrennzeichen)
    - 1234,56 (Komma als Dezimaltrennzeichen)
    - 1.234,56 (Deutsch mit Tausendertrennzeichen)
    - 1,234.56 (US mit Tausendertrennzeichen)
    - -1234.56 (Negativ)
    """
    if not amount_str or amount_str.strip() == "":
        return None

    amount_str = amount_str.strip()

    # Remove currency symbols
    amount_str = amount_str.replace("€", "").replace("EUR", "").replace("$", "").replace("USD", "")
    amount_str = amount_str.strip()

    # Handle German format: 1.234,56 -> 1234.56
    if "," in amount_str and "." in amount_str:
        # Determine which is decimal separator (last occurrence)
        if amount_str.rfind(",") > amount_str.rfind("."):
            # German format: 1.234,56
            amount_str = amount_str.replace(".", "").replace(",", ".")
        else:
            # US format: 1,234.56
            amount_str = amount_str.replace(",", "")
    elif "," in amount_str:
        # Only comma: assume German decimal separator
        amount_str = amount_str.replace(",", ".")

    # Remove remaining spaces
    amount_str = amount_str.replace(" ", "")

    try:
        return Decimal(amount_str)
    except (InvalidOperation, ValueError):
        return None


# ============================================================================
# TRANSACTION TYPE DETECTION
# ============================================================================

def detect_transaction_type(amount: Decimal, purpose: Optional[str] = None) -> TransactionType:
    """
    Erkennt Transaktionstyp anhand von Betrag und Verwendungszweck.

    Args:
        amount: Betrag (positiv=Eingang, negativ=Ausgang)
        purpose: Optional Verwendungszweck für bessere Klassifizierung

    Returns:
        TransactionType enum
    """
    if purpose:
        purpose_lower = purpose.lower()

        # Fee detection
        if any(keyword in purpose_lower for keyword in ["gebühr", "fee", "commission", "provision"]):
            return TransactionType.FEE

        # Interest detection
        if any(keyword in purpose_lower for keyword in ["zinsen", "interest", "zins"]):
            return TransactionType.INTEREST

        # Transfer detection
        if any(keyword in purpose_lower for keyword in ["überweisung", "transfer", "umbuchung"]):
            return TransactionType.TRANSFER

    # Default: income or expense based on amount
    return TransactionType.INCOME if amount > 0 else TransactionType.EXPENSE


# ============================================================================
# CSV PARSING
# ============================================================================

def parse_csv_file(
    csv_content: str,
    account_id: str,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Parst CSV-Datei und extrahiert Transaktionen.

    Args:
        csv_content: CSV-Dateiinhalt als String
        account_id: Bank Account ID
        delimiter: CSV-Trennzeichen (default: ",")
        encoding: Encoding (default: "utf-8")

    Returns:
        Dict mit parsed transactions und Statistiken
    """
    transactions = []
    errors = []

    try:
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file, delimiter=delimiter)

        # Get headers
        headers = reader.fieldnames or []
        if not headers:
            return {
                "success": False,
                "error": "Keine Header gefunden in CSV-Datei",
                "transactions": [],
                "errors": []
            }

        # Detect bank format
        bank_format = detect_bank_format(headers)
        field_mapping = FIELD_MAPPINGS.get(bank_format, FIELD_MAPPINGS[BankFormat.GENERIC])

        # Find column mappings
        date_col = find_column(headers, field_mapping["date"])
        amount_col = find_column(headers, field_mapping["amount"])
        counterparty_col = find_column(headers, field_mapping["counterparty"])
        purpose_col = find_column(headers, field_mapping["purpose"])
        reference_col = find_column(headers, field_mapping.get("reference", []))
        iban_col = find_column(headers, field_mapping.get("iban", []))

        if not date_col or not amount_col:
            return {
                "success": False,
                "error": f"Pflichtfelder nicht gefunden. Erkanntes Format: {bank_format}. Benötigt: Datum und Betrag",
                "transactions": [],
                "errors": []
            }

        # Parse rows
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (1=header)
            try:
                # Parse date
                transaction_date = parse_date(row.get(date_col, ""))
                if not transaction_date:
                    errors.append(f"Zeile {row_num}: Ungültiges Datum '{row.get(date_col)}'")
                    continue

                # Parse amount
                amount = parse_amount(row.get(amount_col, ""))
                if amount is None:
                    errors.append(f"Zeile {row_num}: Ungültiger Betrag '{row.get(amount_col)}'")
                    continue

                # Extract other fields
                counterparty_name = row.get(counterparty_col, "").strip() if counterparty_col else None
                purpose = row.get(purpose_col, "").strip() if purpose_col else None
                reference = row.get(reference_col, "").strip() if reference_col else None
                counterparty_iban = row.get(iban_col, "").strip() if iban_col else None

                # Detect transaction type
                transaction_type = detect_transaction_type(amount, purpose)

                # Create transaction data
                transaction = BankTransactionCreate(
                    account_id=account_id,
                    transaction_date=transaction_date,
                    value_date=transaction_date,  # Use same date if not provided
                    amount=amount,
                    transaction_type=transaction_type,
                    counterparty_name=counterparty_name[:255] if counterparty_name else None,
                    counterparty_iban=counterparty_iban[:34] if counterparty_iban else None,
                    purpose=purpose,
                    reference=reference[:255] if reference else None,
                )

                transactions.append(transaction)

            except Exception as e:
                errors.append(f"Zeile {row_num}: {str(e)}")

        return {
            "success": True,
            "bank_format": bank_format,
            "transactions": transactions,
            "total": len(transactions),
            "errors": errors,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Fehler beim Parsen der CSV-Datei: {str(e)}",
            "transactions": [],
            "errors": []
        }


# ============================================================================
# BULK IMPORT
# ============================================================================

def import_transactions(
    db: Session,
    transactions: List[BankTransactionCreate],
    skip_duplicates: bool = True,
    auto_reconcile: bool = True,
) -> Dict[str, Any]:
    """
    Importiert Transaktionen in die Datenbank.

    Args:
        db: Database Session
        transactions: Liste von BankTransactionCreate
        skip_duplicates: Überspringe Duplikate (basierend auf reference)
        auto_reconcile: Führe automatische Reconciliation nach Import durch

    Returns:
        Dict mit Import-Statistiken
    """
    from .crud import create_bank_transaction, get_bank_account
    from .reconciliation import auto_reconcile_transaction

    stats = {
        "total": len(transactions),
        "imported": 0,
        "skipped": 0,
        "reconciled": 0,
        "errors": []
    }

    for transaction_data in transactions:
        try:
            # Check for duplicate (by reference)
            if skip_duplicates and transaction_data.reference:
                existing = db.query(BankTransaction).filter(
                    BankTransaction.reference == transaction_data.reference
                ).first()

                if existing:
                    stats["skipped"] += 1
                    continue

            # Import transaction
            transaction = create_bank_transaction(db, transaction_data)
            stats["imported"] += 1

            # Auto-reconcile if enabled
            if auto_reconcile:
                success = auto_reconcile_transaction(db, transaction)
                if success:
                    stats["reconciled"] += 1

        except Exception as e:
            stats["errors"].append(f"Import-Fehler: {str(e)}")

    return stats
