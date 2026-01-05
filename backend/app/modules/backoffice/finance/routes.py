# app/modules/backoffice/finance/router.py
from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, UploadFile, File
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.settings.config import settings
from app.core.errors import ErrorCode, get_error_detail
from .models import ExpenseCategory, ReconciliationStatus
from .schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseRead,
    ExpenseListResponse,
    ExpenseKpiResponse,
    BankAccountCreate,
    BankAccountUpdate,
    BankAccountRead,
    BankAccountListResponse,
    BankTransactionCreate,
    BankTransactionUpdate,
    BankTransactionRead,
    BankTransactionListResponse,
    ReconcileRequest,
    CsvImportRequest,
    CsvImportResponse,
    FinTsSyncRequest,
    FinTsSyncResponse,
    FinTsAccountSyncResponse,
    FinTsBalanceRequest,
    FinTsBalanceResponse,
)
from .psd2_integration import (
    PSD2Credentials,
    PSD2ConsentRequest,
    PSD2ConsentResponse,
    PSD2TokenRequest,
    PSD2TokenResponse,
    initiate_consent,
    request_application_access_token,
    exchange_authorization_code,
    get_accounts as psd2_get_accounts,
    get_transactions as psd2_get_transactions,
    convert_psd2_account_to_bank_account,
    convert_psd2_transaction_to_bank_transaction,
)
from .crud import (
    create_expense,
    get_expense,
    list_expenses,
    update_expense,
    delete_expense,
    get_expense_kpis,
    create_bank_account,
    get_bank_account,
    list_bank_accounts,
    update_bank_account,
    delete_bank_account,
    create_bank_transaction,
    get_bank_transaction,
    list_bank_transactions,
    update_bank_transaction,
    delete_bank_transaction,
    reconcile_transaction,
    unreconcile_transaction,
)
from .reconciliation import (
    auto_reconcile_transaction,
    auto_reconcile_all_unmatched,
    get_reconciliation_suggestions,
)

router = APIRouter(
    prefix="/backoffice/finance",
    tags=["Backoffice Finance"],
)


# ---------------------------
# CRUD: Expenses
# ---------------------------

@router.post(
    "/expenses",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_endpoint(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
) -> ExpenseRead:
    expense = create_expense(db, payload)
    return expense


@router.get(
    "/expenses",
    response_model=ExpenseListResponse,
)
def list_expenses_endpoint(
    db: Session = Depends(get_db),
    title: Optional[str] =Query(default=None),
    category: Optional[ExpenseCategory] = Query(default=None),
    project_id: Optional[uuid.UUID] = Query(default=None),
    invoice_id: Optional[uuid.UUID] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> ExpenseListResponse:
    items, total = list_expenses(
        db,
        title=title,
        category=category,
        project_id=project_id,
        invoice_id=invoice_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    # Convert ORM Expense instances to Pydantic ExpenseRead models to satisfy static typing
    items_read = [ExpenseRead.from_orm(item) for item in items]
    return ExpenseListResponse(items=items_read, total=total)


@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseRead,
)
def get_expense_endpoint(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ExpenseRead:
    expense = get_expense(db, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.EXPENSE_NOT_FOUND),
        )
    return expense


@router.patch(
    "/expenses/{expense_id}",
    response_model=ExpenseRead,
)
def update_expense_endpoint(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
) -> ExpenseRead:
    expense = get_expense(db, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.EXPENSE_NOT_FOUND),
        )
    updated = update_expense(db, expense, payload)
    return updated


@router.delete(
    "/expenses/{expense_id}",
    status_code=204,
)
def delete_expense_endpoint(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    expense = get_expense(db,expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.EXPENSE_NOT_FOUND),
        )
    delete_expense(db, expense)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#---------------------------
# KPIs
# ---------------------------

@router.get(
    "/kpis/expenses",
    response_model=ExpenseKpiResponse,
)
def get_expense_kpis_endpoint(
    db: Session = Depends(get_db),
    title: Optional[str]= Query(default=None),
    category: Optional[ExpenseCategory] = Query(default=None),
    project_id: Optional[uuid.UUID] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
) -> ExpenseKpiResponse:
    """
    Einfache Finance-KPIs für v0.1:
    - Gesamtsumme aller Ausgaben
    - Summe pro Kategorie
    """
    return get_expense_kpis(
        db,
        title= title,
        category=category,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )


# ============================================================================
# BANKING - BANK ACCOUNTS
# ============================================================================

@router.post(
    "/bank-accounts",
    response_model=BankAccountRead,
    status_code=status.HTTP_201_CREATED,
)
def create_bank_account_endpoint(
    payload: BankAccountCreate,
    db: Session = Depends(get_db),
) -> BankAccountRead:
    """Erstellt ein neues Bankkonto."""
    account = create_bank_account(db, payload)
    return account


@router.get(
    "/bank-accounts",
    response_model=BankAccountListResponse,
)
def list_bank_accounts_endpoint(
    db: Session = Depends(get_db),
    is_active: Optional[bool] = Query(default=None, description="Filter nach aktiv/inaktiv"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> BankAccountListResponse:
    """Liste aller Bankkonten."""
    items, total = list_bank_accounts(
        db,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    items_read = [BankAccountRead.from_orm(item) for item in items]
    return BankAccountListResponse(items=items_read, total=total)


@router.get(
    "/bank-accounts/{account_id}",
    response_model=BankAccountRead,
)
def get_bank_account_endpoint(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> BankAccountRead:
    """Einzelnes Bankkonto abrufen."""
    account = get_bank_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
        )
    return account


@router.patch(
    "/bank-accounts/{account_id}",
    response_model=BankAccountRead,
)
def update_bank_account_endpoint(
    account_id: uuid.UUID,
    payload: BankAccountUpdate,
    db: Session = Depends(get_db),
) -> BankAccountRead:
    """Bankkonto aktualisieren."""
    account = get_bank_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
        )
    updated = update_bank_account(db, account, payload)
    return updated


@router.delete(
    "/bank-accounts/{account_id}",
    status_code=204,
)
def delete_bank_account_endpoint(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Bankkonto löschen (CASCADE löscht auch Transaktionen)."""
    account = get_bank_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
        )
    delete_bank_account(db, account)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# BANKING - TRANSACTIONS
# ============================================================================

@router.post(
    "/bank-transactions",
    response_model=BankTransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_bank_transaction_endpoint(
    payload: BankTransactionCreate,
    db: Session = Depends(get_db),
) -> BankTransactionRead:
    """
    Erstellt eine neue Banktransaktion.

    **Automatisch:**
    - Aktualisiert den Kontostand (balance += amount)
    """
    # Validate account exists
    account = get_bank_account(db, payload.account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
        )

    transaction = create_bank_transaction(db, payload)
    return transaction


@router.get(
    "/bank-transactions",
    response_model=BankTransactionListResponse,
)
def list_bank_transactions_endpoint(
    db: Session = Depends(get_db),
    account_id: Optional[uuid.UUID] = Query(default=None, description="Filter nach Bankkonto"),
    reconciliation_status: Optional[ReconciliationStatus] = Query(default=None, description="Filter nach Abgleichsstatus"),
    from_date: Optional[date] = Query(default=None, description="Von Datum"),
    to_date: Optional[date] = Query(default=None, description="Bis Datum"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> BankTransactionListResponse:
    """
    Liste aller Transaktionen mit Filtern.

    **Filter:**
    - account_id: Nur Transaktionen eines bestimmten Kontos
    - reconciliation_status: unmatched, matched, confirmed, ignored
    - from_date / to_date: Zeitraum
    """
    items, total = list_bank_transactions(
        db,
        account_id=account_id,
        reconciliation_status=reconciliation_status,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    items_read = [BankTransactionRead.from_orm(item) for item in items]
    return BankTransactionListResponse(items=items_read, total=total)


@router.get(
    "/bank-transactions/{transaction_id}",
    response_model=BankTransactionRead,
)
def get_bank_transaction_endpoint(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> BankTransactionRead:
    """Einzelne Transaktion abrufen."""
    transaction = get_bank_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.TRANSACTION_NOT_FOUND),
        )
    return transaction


@router.patch(
    "/bank-transactions/{transaction_id}",
    response_model=BankTransactionRead,
)
def update_bank_transaction_endpoint(
    transaction_id: uuid.UUID,
    payload: BankTransactionUpdate,
    db: Session = Depends(get_db),
) -> BankTransactionRead:
    """Transaktion aktualisieren."""
    transaction = get_bank_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.TRANSACTION_NOT_FOUND),
        )
    updated = update_bank_transaction(db, transaction, payload)
    return updated


@router.delete(
    "/bank-transactions/{transaction_id}",
    status_code=204,
)
def delete_bank_transaction_endpoint(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Transaktion löschen.

    **Automatisch:**
    - Korrigiert den Kontostand (balance -= amount)
    """
    transaction = get_bank_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.TRANSACTION_NOT_FOUND),
        )
    delete_bank_transaction(db, transaction)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# BANKING - RECONCILIATION
# ============================================================================

@router.post(
    "/bank-transactions/{transaction_id}/reconcile",
    response_model=BankTransactionRead,
)
def reconcile_transaction_endpoint(
    transaction_id: uuid.UUID,
    payload: ReconcileRequest,
    db: Session = Depends(get_db),
) -> BankTransactionRead:
    """
    Gleicht eine Transaktion manuell mit einer Zahlung oder Ausgabe ab.

    **Request Body:**
    - payment_id: Invoice Payment ID (optional)
    - expense_id: Expense ID (optional)
    - reconciliation_note: Notiz (optional)

    **Mindestens payment_id ODER expense_id muss angegeben werden.**
    """
    transaction = get_bank_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.TRANSACTION_NOT_FOUND),
        )

    if not payload.payment_id and not payload.expense_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.TRANSACTION_LINK_INVALID),
        )

    # TODO: Add user_id from auth context
    reconciled = reconcile_transaction(
        db,
        transaction,
        payment_id=payload.payment_id,
        expense_id=payload.expense_id,
        reconciliation_note=payload.reconciliation_note,
        user_id=None,  # TODO: Get from request context
    )
    return reconciled


@router.post(
    "/bank-transactions/{transaction_id}/unreconcile",
    response_model=BankTransactionRead,
)
def unreconcile_transaction_endpoint(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> BankTransactionRead:
    """
    Entfernt den Abgleich einer Transaktion.

    **Setzt zurück:**
    - matched_payment_id = NULL
    - matched_expense_id = NULL
    - reconciliation_status = 'unmatched'
    """
    transaction = get_bank_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.TRANSACTION_NOT_FOUND),
        )

    unreconciled = unreconcile_transaction(db, transaction)
    return unreconciled


# ============================================================================
# BANKING - AUTOMATIC RECONCILIATION
# ============================================================================

@router.post(
    "/bank-transactions/{transaction_id}/auto-reconcile",
    response_model=BankTransactionRead,
)
def auto_reconcile_single_transaction_endpoint(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> BankTransactionRead:
    """
    Versucht eine einzelne Transaktion automatisch abzugleichen.

    **Algorithmus:**
    1. Suche nach Rechnungsnummer im Verwendungszweck
    2. Vergleiche Betrag (mit ±1 EUR Toleranz)
    3. Berechne Confidence Score
    4. Auto-Match wenn Confidence > 90%

    **Automatisch:**
    - Erstellt Payment wenn noch keins existiert
    - Setzt reconciliation_status = 'matched'
    - Füllt matched_payment_id
    """
    transaction = get_bank_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.TRANSACTION_NOT_FOUND),
        )

    success = auto_reconcile_transaction(db, transaction)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.TRANSACTION_NO_MATCH),
        )

    # Refresh to get updated data
    db.refresh(transaction)
    return transaction


@router.post(
    "/bank-transactions/auto-reconcile-all",
)
def auto_reconcile_all_transactions_endpoint(
    account_id: Optional[uuid.UUID] = Query(default=None, description="Optional: Nur für bestimmtes Konto"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Gleicht alle unmatched Transaktionen automatisch ab.

    **Filter:**
    - account_id: Optional - nur für bestimmtes Bankkonto

    **Returns:**
    ```json
    {
        "total": 10,
        "matched": 7,
        "failed": 3,
        "details": [
            {
                "transaction_id": "...",
                "amount": 1234.56,
                "status": "matched"
            },
            {
                "transaction_id": "...",
                "amount": 999.99,
                "status": "failed",
                "reason": "low_confidence_75%"
            }
        ]
    }
    ```
    """
    # Validate account exists if provided
    if account_id:
        account = get_bank_account(db, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
            )

    stats = auto_reconcile_all_unmatched(db, str(account_id) if account_id else None)
    return stats


@router.get(
    "/bank-transactions/{transaction_id}/suggestions",
)
def get_reconciliation_suggestions_endpoint(
    transaction_id: uuid.UUID,
    limit: int = Query(5, ge=1, le=20, description="Anzahl der Vorschläge"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Gibt Reconciliation-Vorschläge für manuelle Überprüfung.

    **Nutzen:**
    - Für UI: Liste von möglichen Matches mit Confidence
    - User kann besten Match manuell auswählen

    **Returns:**
    ```json
    {
        "transaction_id": "...",
        "suggestions": [
            {
                "invoice_id": "...",
                "invoice_number": "RE-2026-0001",
                "invoice_total": 1234.56,
                "invoice_status": "sent",
                "payment_id": "...",
                "payment_amount": 1234.56,
                "confidence": 0.95,
                "confidence_percent": "95%",
                "auto_match": true
            }
        ]
    }
    ```
    """
    transaction = get_bank_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.TRANSACTION_NOT_FOUND),
        )

    suggestions = get_reconciliation_suggestions(db, transaction, limit)

    return {
        "transaction_id": str(transaction_id),
        "transaction_amount": float(transaction.amount),
        "transaction_purpose": transaction.purpose,
        "suggestions": suggestions,
    }


# ============================================================================
# BANKING - CSV IMPORT
# ============================================================================

@router.post(
    "/bank-transactions/import-csv",
    response_model=CsvImportResponse,
)
async def import_csv_transactions_endpoint(
    file: UploadFile = File(..., description="CSV-Datei mit Transaktionen"),
    account_id: uuid.UUID = Query(..., description="Ziel-Bankkonto"),
    delimiter: str = Query(",", max_length=1, description="CSV-Trennzeichen"),
    skip_duplicates: bool = Query(True, description="Duplikate überspringen"),
    auto_reconcile: bool = Query(True, description="Automatische Reconciliation"),
    db: Session = Depends(get_db),
) -> CsvImportResponse:
    """
    Importiert Banktransaktionen aus CSV-Datei.

    **Unterstützte Bank-Formate:**
    - N26
    - Sparkasse
    - Volksbank
    - Deutsche Bank
    - Commerzbank
    - ING DiBa
    - Generic (automatische Erkennung)

    **CSV-Anforderungen:**
    - Header-Zeile erforderlich
    - Pflichtfelder: Datum, Betrag
    - Optionale Felder: Empfänger, Verwendungszweck, Referenz, IBAN

    **Features:**
    - Automatische Format-Erkennung
    - Duplikat-Erkennung (via reference)
    - Automatische Reconciliation nach Import
    - Balance-Update des Kontos

    **Delimiter:**
    - `,` (Komma) - Standard
    - `;` (Semikolon) - Deutsch
    - `\\t` (Tab)

    **Returns:**
    ```json
    {
        "success": true,
        "bank_format": "n26",
        "total": 100,
        "imported": 95,
        "skipped": 5,
        "reconciled": 80,
        "errors": []
    }
    ```
    """
    from .csv_import import parse_csv_file, import_transactions

    # Validate account exists
    account = get_bank_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
        )

    # Validate file type
    if not file.filename or not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.CSV_INVALID_FORMAT),
        )

    try:
        # Read file content
        content = await file.read()

        # Try different encodings
        csv_content = None
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                csv_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if csv_content is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_error_detail(ErrorCode.CSV_ENCODING_ERROR),
            )

        # Parse CSV
        parse_result = parse_csv_file(
            csv_content=csv_content,
            account_id=str(account_id),
            delimiter=delimiter,
        )

        if not parse_result["success"]:
            return CsvImportResponse(
                success=False,
                bank_format=None,
                total=0,
                imported=0,
                skipped=0,
                reconciled=0,
                errors=[parse_result.get("error", "Unknown error")],
            )

        # Import transactions
        import_stats = import_transactions(
            db=db,
            transactions=parse_result["transactions"],
            skip_duplicates=skip_duplicates,
            auto_reconcile=auto_reconcile,
        )

        return CsvImportResponse(
            success=True,
            bank_format=parse_result.get("bank_format"),
            total=import_stats["total"],
            imported=import_stats["imported"],
            skipped=import_stats["skipped"],
            reconciled=import_stats["reconciled"],
            errors=import_stats["errors"] + parse_result.get("errors", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.CSV_IMPORT_FAILED, error=str(e)),
        )


# ============================================================================
# BANKING - FINTS/HBCI INTEGRATION
# ============================================================================

@router.post(
    "/fints/sync-transactions",
    response_model=FinTsSyncResponse,
)
def sync_fints_transactions_endpoint(
    payload: FinTsSyncRequest,
    db: Session = Depends(get_db),
) -> FinTsSyncResponse:
    """
    Importiert Transaktionen direkt von Bank via FinTS/HBCI.

    **Unterstützt:**
    - Alle deutschen Banken mit FinTS 3.0+ Support
    - PIN/TAN-Verfahren
    - PSD2-konform

    **Sicherheit:**
    - Credentials werden NICHT in DB gespeichert
    - PIN nur temporär im Memory
    - HTTPS erforderlich

    **Anforderungen:**
    - Online-Banking aktiviert
    - FinTS/HBCI freigeschaltet
    - PIN/TAN verfügbar

    **Zeitraum:**
    - Default: Letzte 90 Tage
    - Max: Abhängig von Bank (meist 90-180 Tage)

    **Features:**
    - Automatische Duplikat-Erkennung
    - Automatische Reconciliation
    - Balance-Update

    Returns:
        FinTsSyncResponse mit Import-Statistiken
    """
    from .fints_integration import sync_fints_transactions

    # Validate account
    account = get_bank_account(db, payload.account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
        )

    if not account.iban:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NO_IBAN),
        )

    try:
        stats = sync_fints_transactions(
            db=db,
            account_id=str(payload.account_id),
            blz=payload.credentials.blz,
            login=payload.credentials.login,
            pin=payload.credentials.pin,
            sepa_account_iban=account.iban,
            from_date=payload.from_date,
            to_date=payload.to_date,
            skip_duplicates=payload.skip_duplicates,
            auto_reconcile=payload.auto_reconcile,
        )

        return FinTsSyncResponse(
            success=len(stats["errors"]) == 0,
            total=stats["total"],
            imported=stats["imported"],
            skipped=stats["skipped"],
            reconciled=stats["reconciled"],
            errors=stats["errors"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.FINTS_SYNC_FAILED, error=str(e)),
        )


@router.post(
    "/fints/sync-accounts",
    response_model=FinTsAccountSyncResponse,
)
def sync_fints_accounts_endpoint(
    blz: str = Query(..., min_length=8, max_length=8, description="Bankleitzahl"),
    login: str = Query(..., description="Online-Banking Login"),
    pin: str = Query(..., description="PIN"),
    create_missing: bool = Query(True, description="Fehlende Konten erstellen"),
    db: Session = Depends(get_db),
) -> FinTsAccountSyncResponse:
    """
    Synchronisiert Bankkonten via FinTS.

    Ruft alle verfügbaren SEPA-Konten ab und erstellt fehlende
    BankAccount-Einträge automatisch.

    **Use Case:**
    - Initiales Setup: Alle Konten importieren
    - Regelmäßige Sync: Neue Konten erkennen

    **Hinweis:**
    Credentials werden als Query-Parameter übergeben (nicht in DB gespeichert).
    In Produktion: HTTPS erforderlich!

    Returns:
        Statistiken über gefundene/erstellte Konten
    """
    from .fints_integration import sync_fints_accounts

    try:
        stats = sync_fints_accounts(
            db=db,
            blz=blz,
            login=login,
            pin=pin,
            create_missing=create_missing,
        )

        return FinTsAccountSyncResponse(
            success=len(stats["errors"]) == 0,
            total_accounts=stats["total_accounts"],
            existing=stats["existing"],
            created=stats["created"],
            errors=stats["errors"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.FINTS_SYNC_FAILED, error=str(e)),
        )


@router.post(
    "/fints/check-balance",
    response_model=FinTsBalanceResponse,
)
def check_fints_balance_endpoint(
    payload: FinTsBalanceRequest,
    db: Session = Depends(get_db),
) -> FinTsBalanceResponse:
    """
    Prüft aktuellen Kontostand via FinTS.

    **Use Case:**
    - Balance-Verifikation gegen FinTS
    - Abgleich mit gespeichertem Balance

    **Hinweis:**
    Viele Banken erlauben max. 1-2 Balance-Abfragen pro Minute.

    Returns:
        Aktueller Kontostand
    """
    from .fints_integration import get_fints_balance

    try:
        balance = get_fints_balance(
            blz=payload.credentials.blz,
            login=payload.credentials.login,
            pin=payload.credentials.pin,
            sepa_account_iban=payload.iban,
        )

        if balance is None:
            return FinTsBalanceResponse(
                success=False,
                balance=None,
                iban=payload.iban,
                error="Kontostand konnte nicht abgerufen werden",
            )

        return FinTsBalanceResponse(
            success=True,
            balance=balance,
            iban=payload.iban,
            error=None,
        )

    except Exception as e:
        return FinTsBalanceResponse(
            success=False,
            balance=None,
            iban=payload.iban,
            error=str(e),
        )


# ============================================================================
# PSD2 OPEN BANKING API (ING)
# ============================================================================

@router.post("/psd2/consent/initiate", response_model=PSD2ConsentResponse)
def initiate_psd2_consent(
    payload: PSD2ConsentRequest,
    db: Session = Depends(get_db),
):
    """
    Initiiert PSD2 OAuth2 Consent Flow.

    **Flow:**
    1. Client ruft diesen Endpoint auf
    2. Endpoint gibt authorization_url zurück
    3. Client redirectet User zu authorization_url
    4. User gibt Consent in ING App
    5. ING redirectet zurück zu redirect_uri mit authorization_code
    6. Client ruft /psd2/consent/callback mit authorization_code auf

    **Hinweis:**
    - Erfordert mTLS-Zertifikate (QWAC/QSealC)
    - redirect_uri muss mit registrierter URI übereinstimmen

    **Beispiel redirect_uri:**
    - https://workmateOS.example.com/banking/callback
    - http://localhost:5173/banking/callback (für Dev)
    """
    try:
        credentials = PSD2Credentials(
            client_id=payload.client_id,
            environment=settings.PSD2_ENVIRONMENT,
        )

        consent_response = initiate_consent(
            credentials=credentials,
            redirect_uri=payload.redirect_uri,
            scope=payload.scope,
        )

        return consent_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


@router.post("/psd2/consent/callback", response_model=PSD2TokenResponse)
def psd2_consent_callback(
    payload: PSD2TokenRequest,
    db: Session = Depends(get_db),
):
    """
    Callback nach User-Consent.

    Tauscht authorization_code gegen customer access_token.

    **ING mTLS Flow:**
    1. Request Application Access Token (mTLS-only)
    2. Exchange authorization code with this token
    3. Return Customer Access Token

    **Parameter:**
    - client_id: ING Client ID
    - authorization_code: Code aus ING Redirect

    **Returns:**
    - access_token: Customer Access Token (gültig 15 min)
    - refresh_token: Für Token-Refresh (gültig 30 Tage)

    **Hinweis:**
    - access_token muss sicher gespeichert werden
    - Token ist personenbezogen
    """
    try:
        credentials = PSD2Credentials(
            client_id=payload.client_id,
            environment=settings.PSD2_ENVIRONMENT,
        )

        # Step 1: Get Application Access Token via mTLS
        app_token_response = request_application_access_token(credentials)
        app_access_token = app_token_response["access_token"]

        # Step 2: Exchange authorization code
        token_response = exchange_authorization_code(
            credentials=credentials,
            authorization_code=payload.authorization_code,
            application_access_token=app_access_token,
        )

        return token_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


@router.post("/psd2/accounts/sync")
def sync_psd2_accounts(
    client_id: str,
    access_token: str,
    create_missing: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    """
    Synct Konten von ING PSD2 API.

    **Prerequisite:**
    - User muss Consent gegeben haben (/psd2/consent/initiate)
    - access_token muss valid sein

    **Parameter:**
    - client_id: ING Client ID
    - access_token: OAuth2 Access Token
    - create_missing: Neue Konten automatisch anlegen?

    **Returns:**
    - Liste der synchronisierten Konten
    - Neu erstellte Konten werden markiert
    """
    try:
        credentials = PSD2Credentials(
            client_id=client_id,
            environment=settings.PSD2_ENVIRONMENT,
        )

        # Get accounts from PSD2 API
        psd2_accounts = psd2_get_accounts(
            credentials=credentials,
            access_token=access_token,
        )

        synced_accounts = []

        for psd2_account in psd2_accounts:
            # Check if account exists
            existing_account = None
            if psd2_account.iban:
                from sqlalchemy import select
                from .models import BankAccount
                stmt = select(BankAccount).where(BankAccount.iban == psd2_account.iban)
                existing_account = db.scalars(stmt).first()

            if existing_account:
                # Update existing account
                account_data = convert_psd2_account_to_bank_account(psd2_account)
                for key, value in account_data.items():
                    if key not in ["id", "created_at", "updated_at"]:
                        setattr(existing_account, key, value)
                db.commit()
                db.refresh(existing_account)

                synced_accounts.append({
                    "account": BankAccountRead.model_validate(existing_account),
                    "created": False,
                })

            elif create_missing:
                # Create new account
                account_data = convert_psd2_account_to_bank_account(psd2_account)
                new_account = create_bank_account(
                    db,
                    BankAccountCreate(**account_data)
                )

                synced_accounts.append({
                    "account": new_account,
                    "created": True,
                })

        return {
            "success": True,
            "accounts_synced": len(synced_accounts),
            "accounts": synced_accounts,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


@router.post("/psd2/transactions/sync")
def sync_psd2_transactions(
    client_id: str,
    access_token: str,
    account_id: uuid.UUID,
    psd2_account_id: str,
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    skip_duplicates: bool = Query(default=True),
    auto_reconcile: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    """
    Synct Transaktionen von ING PSD2 API.

    **Prerequisite:**
    - User muss Consent gegeben haben
    - access_token muss valid sein
    - account_id muss existieren (WorkmateOS BankAccount)
    - psd2_account_id ist der ING resource_id

    **Parameter:**
    - client_id: ING Client ID
    - access_token: OAuth2 Access Token
    - account_id: WorkmateOS BankAccount UUID
    - psd2_account_id: ING Account Resource ID
    - date_from: Start-Datum (YYYY-MM-DD)
    - date_to: End-Datum (YYYY-MM-DD)
    - skip_duplicates: Duplikate überspringen?
    - auto_reconcile: Automatisches Reconciliation?

    **Returns:**
    - Anzahl importierter Transaktionen
    - Anzahl übersprungener Duplikate
    - Anzahl auto-reconciled Transaktionen
    """
    try:
        credentials = PSD2Credentials(
            client_id=client_id,
            environment=settings.PSD2_ENVIRONMENT,
        )

        # Get transactions from PSD2 API
        psd2_transactions = psd2_get_transactions(
            credentials=credentials,
            access_token=access_token,
            account_id=psd2_account_id,
            date_from=date_from,
            date_to=date_to,
        )

        imported_count = 0
        skipped_count = 0
        reconciled_count = 0

        for psd2_txn in psd2_transactions:
            # Check for duplicates
            if skip_duplicates:
                from sqlalchemy import select
                from .models import BankTransaction
                stmt = select(BankTransaction).where(
                    BankTransaction.reference == psd2_txn.transaction_id
                )
                existing_txn = db.scalars(stmt).first()

                if existing_txn:
                    skipped_count += 1
                    continue

            # Convert and create transaction
            txn_data = convert_psd2_transaction_to_bank_transaction(
                psd2_txn,
                account_id=account_id
            )

            new_txn = create_bank_transaction(
                db,
                BankTransactionCreate(**txn_data)
            )
            imported_count += 1

            # Auto-reconciliation
            if auto_reconcile:
                try:
                    result = auto_reconcile_transaction(db, new_txn.id)
                    if result["reconciled"]:
                        reconciled_count += 1
                except Exception as reconcile_error:
                    # Reconciliation failure should not stop import
                    pass

        return {
            "success": True,
            "imported": imported_count,
            "skipped": skipped_count,
            "auto_reconciled": reconciled_count,
            "total_fetched": len(psd2_transactions),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


# ============================================================================
# SEVDESK INTEGRATION
# ============================================================================

from .sevdesk_router import router as sevdesk_router

router.include_router(sevdesk_router)


# ============================================================================
# STRIPE PAYMENT INTEGRATION
# ============================================================================

from .stripe_router import router as stripe_router

router.include_router(stripe_router)

