# app/modules/backoffice/finance/routes.py
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from .models import ExpenseCategory, BankAccount, BankTransaction
from .schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseRead,
    ExpenseListResponse,
    ExpenseKpiResponse,
    BankAccountResponse,
    BankTransactionResponse,
)
from .crud import (
    create_expense,
    get_expense,
    list_expenses,
    update_expense,
    delete_expense,
    get_expense_kpis,
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
@require_permissions(["backoffice.finance.write"])
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
@require_permissions(["backoffice.finance.read"])
def list_expenses_endpoint(
    db: Session = Depends(get_db),
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
@require_permissions(["backoffice.finance.read"])
def get_expense_endpoint(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.write"])
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
            detail="Expense not found",
        )
    updated = update_expense(db, expense, payload)
    return updated


@router.delete(
    "/expenses/{expense_id}",
    status_code=204,
)
@require_permissions(["backoffice.finance.delete"])
def delete_expense_endpoint(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.finance.read"])
def get_expense_kpis_endpoint(
    db: Session = Depends(get_db),
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
        category=category,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )


# ---------------------------
# Bank Accounts
# ---------------------------

@router.get("/bank-accounts", response_model=list[BankAccountResponse])
@require_permissions(["backoffice.finance.view"])
def list_bank_accounts(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return db.query(BankAccount).filter(BankAccount.is_active == True).order_by(BankAccount.account_name).all()


@router.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
@require_permissions(["backoffice.finance.view"])
def get_bank_account(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Konto nicht gefunden")
    return account


# ---------------------------
# Bank Transactions
# ---------------------------

@router.get("/bank-transactions", response_model=list[BankTransactionResponse])
@require_permissions(["backoffice.finance.view"])
def list_bank_transactions(
    account_id: Optional[uuid.UUID] = Query(None),
    reconciliation_status: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(BankTransaction)
    if account_id:
        query = query.filter(BankTransaction.account_id == account_id)
    if reconciliation_status:
        query = query.filter(BankTransaction.reconciliation_status == reconciliation_status)
    return query.order_by(BankTransaction.transaction_date.desc()).limit(limit).all()
