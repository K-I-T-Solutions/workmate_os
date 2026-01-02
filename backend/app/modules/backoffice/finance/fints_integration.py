"""
FinTS/HBCI Integration für automatischen Transaktions-Import

Unterstützt direkten Zugriff auf deutsche Bankkonten via FinTS-Protokoll.

**Wichtig:**
- Erfordert Bank-Credentials (Bankleitzahl, Benutzer-ID, PIN/TAN)
- Nur für deutsche Banken mit FinTS-Support
- PSD2-konform mit starker Kundenauthentifizierung (SCA)

**Sicherheit:**
- Credentials NIE in Datenbank speichern (nur verschlüsselt/temporär)
- PIN/TAN nur für Session-Dauer im Memory
- HTTPS required für alle Anfragen
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import logging

from sqlalchemy.orm import Session

from .models import BankAccount, TransactionType
from .schemas import BankTransactionCreate

logger = logging.getLogger(__name__)


# ============================================================================
# FINTS CONNECTION
# ============================================================================

def create_fints_client(
    blz: str,
    login: str,
    pin: str,
    endpoint: Optional[str] = None,
):
    """
    Erstellt FinTS-Client für Bankverbindung.

    Args:
        blz: Bankleitzahl (8-stellig)
        login: Benutzerkennung / Online-Banking-ID
        pin: PIN für Online-Banking
        endpoint: Optional - FinTS-Server-URL (automatisch ermittelt wenn None)

    Returns:
        FinTSClient instance

    Raises:
        FinTSConnectionError: Bei Verbindungsproblemen
        FinTSAuthError: Bei falschen Credentials
    """
    try:
        from fints.client import FinTS3PinTanClient

        client = FinTS3PinTanClient(
            blz=blz,
            user=login,
            pin=pin,
            endpoint=endpoint,
        )

        return client

    except ImportError:
        raise Exception(
            "FinTS Library nicht installiert. Bitte installieren: pip install fints mt940"
        )
    except Exception as e:
        logger.error(f"FinTS Connection Error: {str(e)}")
        raise


# ============================================================================
# ACCOUNT SYNC
# ============================================================================

def sync_fints_accounts(
    db: Session,
    blz: str,
    login: str,
    pin: str,
    create_missing: bool = True,
) -> Dict[str, Any]:
    """
    Synchronisiert Bankkonten via FinTS.

    Ruft alle SEPAAccount-Objekte ab und erstellt fehlende BankAccount-Einträge.

    Args:
        db: Database Session
        blz: Bankleitzahl
        login: Benutzerkennung
        pin: PIN
        create_missing: Erstelle fehlende Konten automatisch

    Returns:
        Dict mit Sync-Statistiken
    """
    stats = {
        "total_accounts": 0,
        "existing": 0,
        "created": 0,
        "errors": []
    }

    try:
        client = create_fints_client(blz, login, pin)

        # Get accounts
        accounts = client.get_sepa_accounts()

        for account in accounts:
            stats["total_accounts"] += 1

            # Check if account exists
            existing = db.query(BankAccount).filter(
                BankAccount.iban == account.iban
            ).first()

            if existing:
                stats["existing"] += 1
                continue

            if create_missing:
                from .crud import create_bank_account
                from .schemas import BankAccountCreate

                # Create account
                account_data = BankAccountCreate(
                    account_name=f"{account.bank_name or 'Bank'} - {account.iban[-4:]}",
                    account_type="checking",  # Default
                    iban=account.iban,
                    bic=account.bic or None,
                    bank_name=account.bank_name,
                    account_holder=account.owner_name.join(", ") if isinstance(account.owner_name, list) else account.owner_name,
                    balance=Decimal("0.00"),  # Will be updated via transaction import
                    is_active=True,
                )

                create_bank_account(db, account_data)
                stats["created"] += 1

        return stats

    except Exception as e:
        stats["errors"].append(str(e))
        return stats


# ============================================================================
# TRANSACTION SYNC
# ============================================================================

def convert_fints_transaction_type(mt940_type: str) -> TransactionType:
    """
    Konvertiert MT940-Transaktionstyp zu unserem TransactionType.

    MT940 Codes:
    - NTRF: Überweisung
    - NMSC: Sonstige
    - NDDT: Lastschrift
    - NSTO: Standing Order
    - etc.
    """
    type_mapping = {
        "NTRF": TransactionType.TRANSFER,
        "NMSC": TransactionType.EXPENSE,
        "NDDT": TransactionType.EXPENSE,
        "NSTO": TransactionType.EXPENSE,
        "NCHG": TransactionType.FEE,
        "NINT": TransactionType.INTEREST,
    }

    return type_mapping.get(mt940_type, TransactionType.EXPENSE)


def sync_fints_transactions(
    db: Session,
    account_id: str,
    blz: str,
    login: str,
    pin: str,
    sepa_account_iban: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip_duplicates: bool = True,
    auto_reconcile: bool = True,
) -> Dict[str, Any]:
    """
    Importiert Transaktionen via FinTS für ein Konto.

    Args:
        db: Database Session
        account_id: BankAccount ID
        blz: Bankleitzahl
        login: Benutzerkennung
        pin: PIN
        sepa_account_iban: IBAN des Kontos
        from_date: Startdatum (default: vor 90 Tagen)
        to_date: Enddatum (default: heute)
        skip_duplicates: Überspringe Duplikate (via reference)
        auto_reconcile: Automatische Reconciliation

    Returns:
        Dict mit Import-Statistiken
    """
    from .crud import create_bank_transaction, get_bank_account
    from .reconciliation import auto_reconcile_transaction
    from .models import BankTransaction

    stats = {
        "total": 0,
        "imported": 0,
        "skipped": 0,
        "reconciled": 0,
        "errors": []
    }

    try:
        # Verify account exists
        account = get_bank_account(db, account_id)
        if not account:
            stats["errors"].append("Bank account not found")
            return stats

        if account.iban != sepa_account_iban:
            stats["errors"].append("IBAN mismatch")
            return stats

        # Default date range: last 90 days
        if not from_date:
            from_date = date.today() - timedelta(days=90)
        if not to_date:
            to_date = date.today()

        # Create FinTS client
        client = create_fints_client(blz, login, pin)

        # Get account
        accounts = client.get_sepa_accounts()
        sepa_account = None
        for acc in accounts:
            if acc.iban == sepa_account_iban:
                sepa_account = acc
                break

        if not sepa_account:
            stats["errors"].append(f"SEPA account with IBAN {sepa_account_iban} not found")
            return stats

        # Get transactions
        transactions = client.get_transactions(
            sepa_account,
            start_date=from_date,
            end_date=to_date,
        )

        for transaction in transactions:
            stats["total"] += 1

            try:
                # Parse transaction data
                data = transaction.data

                # Extract reference (unique identifier)
                reference = (
                    data.get("end_to_end_reference") or
                    data.get("transaction_reference") or
                    data.get("reference") or
                    None
                )

                # Check for duplicate
                if skip_duplicates and reference:
                    existing = db.query(BankTransaction).filter(
                        BankTransaction.reference == reference
                    ).first()

                    if existing:
                        stats["skipped"] += 1
                        continue

                # Extract amount
                amount = Decimal(str(data["amount"].amount))

                # Detect transaction type
                transaction_type = convert_fints_transaction_type(
                    data.get("transaction_code", "NMSC")
                )

                # If amount is negative, it's an expense
                if amount < 0:
                    transaction_type = TransactionType.EXPENSE
                elif amount > 0:
                    transaction_type = TransactionType.INCOME

                # Create transaction
                transaction_data = BankTransactionCreate(
                    account_id=account_id,
                    transaction_date=data["date"],
                    value_date=data.get("entry_date", data["date"]),
                    amount=amount,
                    transaction_type=transaction_type,
                    counterparty_name=data.get("applicant_name", "")[:255],
                    counterparty_iban=data.get("applicant_iban", "")[:34] if data.get("applicant_iban") else None,
                    purpose=data.get("purpose", ""),
                    reference=reference[:255] if reference else None,
                )

                # Import transaction
                new_transaction = create_bank_transaction(db, transaction_data)
                stats["imported"] += 1

                # Auto-reconcile
                if auto_reconcile:
                    success = auto_reconcile_transaction(db, new_transaction)
                    if success:
                        stats["reconciled"] += 1

            except Exception as e:
                stats["errors"].append(f"Transaction import error: {str(e)}")

        return stats

    except Exception as e:
        stats["errors"].append(f"FinTS sync error: {str(e)}")
        return stats


# ============================================================================
# BALANCE CHECK
# ============================================================================

def get_fints_balance(
    blz: str,
    login: str,
    pin: str,
    sepa_account_iban: str,
) -> Optional[Decimal]:
    """
    Ruft aktuellen Kontostand via FinTS ab.

    Args:
        blz: Bankleitzahl
        login: Benutzerkennung
        pin: PIN
        sepa_account_iban: IBAN

    Returns:
        Balance als Decimal oder None bei Fehler
    """
    try:
        client = create_fints_client(blz, login, pin)

        accounts = client.get_sepa_accounts()
        for account in accounts:
            if account.iban == sepa_account_iban:
                # Get balance
                balance = client.get_balance(account)
                return Decimal(str(balance.amount))

        return None

    except Exception as e:
        logger.error(f"FinTS Balance Error: {str(e)}")
        return None


# ============================================================================
# TAN HANDLING (für PSD2/SCA)
# ============================================================================

def request_tan(
    blz: str,
    login: str,
    pin: str,
    sepa_account_iban: str,
    tan_medium: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fordert TAN an (für Transaktionsabruf mit starker Authentifizierung).

    **Hinweis:**
    Viele Banken unterstützen FinTS 3.0 mit PIN-only für Kontoinformationen.
    TAN ist nur für SEPA-Überweisungen erforderlich.

    Args:
        blz: Bankleitzahl
        login: Benutzerkennung
        pin: PIN
        sepa_account_iban: IBAN
        tan_medium: Optional - TAN-Medium (SMS, pushTAN, etc.)

    Returns:
        Dict mit TAN-Request-Informationen
    """
    try:
        client = create_fints_client(blz, login, pin)

        # Get TAN mechanisms
        tan_mechanisms = client.get_tan_mechanisms()

        return {
            "success": True,
            "tan_mechanisms": [
                {
                    "id": mech.security_function,
                    "name": mech.name,
                }
                for mech in tan_mechanisms
            ],
            "message": "TAN-Mechanismen abgerufen. Wähle Mechanismus für TAN-Anforderung."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
