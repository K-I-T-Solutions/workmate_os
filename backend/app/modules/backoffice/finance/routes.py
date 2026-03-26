# app/modules/backoffice/finance/router.py
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, UploadFile, File
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
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
    N8nWebhookPayload,
    N8nWebhookResponse,
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
@require_permissions(["backoffice.finance.write", "backoffice.*"])
def create_expense_endpoint(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> ExpenseRead:
    expense = create_expense(db, payload)
    return expense


@router.get(
    "/expenses",
    response_model=ExpenseListResponse,
)
@require_permissions(["backoffice.finance.view", "backoffice.*"])
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
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.view", "backoffice.*"])
def get_expense_endpoint(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.write", "backoffice.*"])
def update_expense_endpoint(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.delete", "backoffice.*"])
def delete_expense_endpoint(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.view", "backoffice.*"])
def get_expense_kpis_endpoint(
    db: Session = Depends(get_db),
    title: Optional[str]= Query(default=None),
    category: Optional[ExpenseCategory] = Query(default=None),
    project_id: Optional[uuid.UUID] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.banking", "backoffice.*"])
def create_bank_account_endpoint(
    payload: BankAccountCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> BankAccountRead:
    """Erstellt ein neues Bankkonto."""
    account = create_bank_account(db, payload)
    return account


@router.get(
    "/bank-accounts",
    response_model=BankAccountListResponse,
)
@require_permissions(["backoffice.finance.view", "backoffice.*"])
def list_bank_accounts_endpoint(
    db: Session = Depends(get_db),
    is_active: Optional[bool] = Query(default=None, description="Filter nach aktiv/inaktiv"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.view", "backoffice.*"])
def get_bank_account_endpoint(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.banking", "backoffice.*"])
def update_bank_account_endpoint(
    account_id: uuid.UUID,
    payload: BankAccountUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
# N8N WEBHOOK – Kontoauszüge importieren
# ============================================================================

@router.post(
    "/bank-transactions/n8n-webhook",
    response_model=N8nWebhookResponse,
    summary="n8n Webhook: Banktransaktionen importieren",
)
def n8n_webhook_endpoint(
    payload: N8nWebhookPayload,
    db: Session = Depends(get_db),
) -> N8nWebhookResponse:
    """
    Nimmt Banktransaktionen von n8n entgegen und importiert sie.

    n8n holt Kontoauszüge (z.B. via FinTS-Node oder Bank-API) und
    schickt die Daten normalisiert an diesen Endpoint.

    **Beispiel n8n-Payload:**
    ```json
    {
      "account_id": "uuid-des-bankkontos",
      "transactions": [
        {
          "date": "2026-03-21",
          "amount": -49.90,
          "purpose": "Rechnung #2026-001",
          "counterpart_name": "Musterfirma GmbH",
          "counterpart_iban": "DE89370400440532013000",
          "reference": "eindeutige-referenz-123"
        }
      ],
      "skip_duplicates": true,
      "auto_reconcile": true
    }
    ```
    """
    from .csv_import import import_transactions

    account = get_bank_account(db, payload.account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
        )

    transactions = [
        {
            "account_id": str(payload.account_id),
            "date": txn.date,
            "amount": txn.amount,
            "purpose": txn.purpose,
            "counterpart_name": txn.counterpart_name,
            "counterpart_iban": txn.counterpart_iban,
            "reference": txn.reference,
            "transaction_type": "credit" if txn.amount >= 0 else "debit",
        }
        for txn in payload.transactions
    ]

    stats = import_transactions(
        db=db,
        transactions=transactions,
        skip_duplicates=payload.skip_duplicates,
        auto_reconcile=payload.auto_reconcile,
    )

    return N8nWebhookResponse(
        success=True,
        total=stats["total"],
        imported=stats["imported"],
        skipped=stats["skipped"],
        reconciled=stats["reconciled"],
        errors=stats["errors"],
    )

