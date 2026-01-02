# app/modules/backoffice/finance/router.py
from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
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
            detail="Expense not found",
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
            detail="Expense not found",
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
        raise HTTPException(404, "Expense not found") #✔️ KORREKT
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
            detail="Bank account not found",
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
            detail="Bank account not found",
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
            detail="Bank account not found"
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
            detail="Bank account not found",
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
            detail="Transaction not found",
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
            detail="Transaction not found",
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
            detail="Transaction not found"
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
            detail="Transaction not found",
        )

    if not payload.payment_id and not payload.expense_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either payment_id or expense_id must be provided",
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
            detail="Transaction not found",
        )

    unreconciled = unreconcile_transaction(db, transaction)
    return unreconciled
