# app/modules/backoffice/finance/service.py
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import (
    Expense,
    ExpenseCategory,
    BankAccount,
    BankTransaction,
    AccountType,
    TransactionType,
    ReconciliationStatus
)
from .schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseKpiResponse,
    BankAccountCreate,
    BankAccountUpdate,
    BankTransactionCreate,
    BankTransactionUpdate
)


def create_expense(db: Session, data: ExpenseCreate) -> Expense:
    expense = Expense(
        title = data.title,
        category=data.category.value if isinstance(data.category, ExpenseCategory) else data.category,
        amount=data.amount,
        description=data.description,
        receipt_path=data.receipt_path,
        note=data.note,
        is_billable=data.is_billable,
        project_id=data.project_id,
        invoice_id=data.invoice_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expense(db: Session, expense_id: uuid.UUID) -> Optional[Expense]:
    stmt = select(Expense).where(Expense.id == expense_id)
    return db.scalar(stmt)


def list_expenses(
    db: Session,
    *,
    title : Optional[str]= None,
    category: Optional[ExpenseCategory] = None,
    project_id: Optional[uuid.UUID] = None,
    invoice_id: Optional[uuid.UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[Expense], int]:
    """Liste von Ausgaben mit einfachen Filtern + total count."""
    stmt = select(Expense)
    count_stmt = select(func.count(Expense.id))
    if title is not None:
        stmt = stmt.where(Expense.title == title)
        count_stmt=count_stmt.where(Expense.title == title)
    if category is not None:
        stmt = stmt.where(Expense.category == category.value)
        count_stmt = count_stmt.where(Expense.category == category.value)

    if project_id is not None:
        stmt = stmt.where(Expense.project_id == project_id)
        count_stmt = count_stmt.where(Expense.project_id == project_id)

    if invoice_id is not None:
        stmt = stmt.where(Expense.invoice_id == invoice_id)
        count_stmt = count_stmt.where(Expense.invoice_id == invoice_id)

    if from_date is not None:
        from_dt = datetime.combine(from_date, datetime.min.time())
        stmt = stmt.where(Expense.created_at >= from_dt)
        count_stmt = count_stmt.where(Expense.created_at >= from_dt)

    if to_date is not None:
        to_dt = datetime.combine(to_date, datetime.max.time())
        stmt = stmt.where(Expense.created_at <= to_dt)
        count_stmt = count_stmt.where(Expense.created_at <= to_dt)

    stmt = stmt.order_by(Expense.created_at.desc()).limit(limit).offset(offset)

    items = list(db.scalars(stmt).all())
    total = db.scalar(count_stmt) or 0

    return items, total


def update_expense(
    db: Session,
    expense: Expense,
    data: ExpenseUpdate,
) -> Expense:
    payload = data.model_dump(exclude_unset=True)

    if "category" in payload and isinstance(payload["category"], ExpenseCategory):
        payload["category"] = payload["category"].value

    for field, value in payload.items():
        setattr(expense, field, value)

    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense: Expense) -> None:
    """Hard Delete (v0.1)."""
    db.delete(expense)
    db.commit()


def get_expense_kpis(
    db: Session,
    *,
    title: Optional[str]=None,
    category: Optional[ExpenseCategory] = None,
    project_id: Optional[uuid.UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> ExpenseKpiResponse:
    """Einfache KPI-Berechnung: Gesamtsumme + Summe pro Kategorie."""
    stmt = select(
        func.coalesce(func.sum(Expense.amount), 0)
    )
    cat_stmt = select(
        Expense.category,
        func.coalesce(func.sum(Expense.amount), 0)
    ).group_by(Expense.category)
    if title is not None:
        stmt = stmt.where(Expense.title == title)
        cat_stmt=cat_stmt.where(Expense.title == title)
    if category is not None:
        stmt = stmt.where(Expense.category == category.value)
        cat_stmt = cat_stmt.where(Expense.category == category.value)

    if project_id is not None:
        stmt = stmt.where(Expense.project_id == project_id)
        cat_stmt = cat_stmt.where(Expense.project_id == project_id)

    if from_date is not None:
        from_dt = datetime.combine(from_date, datetime.min.time())
        stmt = stmt.where(Expense.created_at >= from_dt)
        cat_stmt = cat_stmt.where(Expense.created_at >= from_dt)

    if to_date is not None:
        to_dt = datetime.combine(to_date, datetime.max.time())
        stmt = stmt.where(Expense.created_at <= to_dt)
        cat_stmt = cat_stmt.where(Expense.created_at <= to_dt)

    total: Decimal = db.scalar(stmt) or Decimal("0.00")

    rows = db.execute(cat_stmt).all()
    by_category: dict[ExpenseCategory, Decimal] = {}
    for cat_value, amount in rows:
        by_category[ExpenseCategory(cat_value)] = amount

    return ExpenseKpiResponse(total=total, by_category=by_category)


# ============================================================================
# BANKING CRUD
# ============================================================================

def create_bank_account(db: Session, data: BankAccountCreate) -> BankAccount:
    """Erstellt ein neues Bankkonto."""
    account = BankAccount(
        account_name=data.account_name,
        account_type=data.account_type.value if isinstance(data.account_type, AccountType) else data.account_type,
        iban=data.iban,
        bic=data.bic,
        bank_name=data.bank_name,
        account_holder=data.account_holder,
        balance=data.balance,
        is_active=data.is_active,
        note=data.note,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_bank_account(db: Session, account_id: uuid.UUID) -> Optional[BankAccount]:
    """Holt ein einzelnes Bankkonto."""
    stmt = select(BankAccount).where(BankAccount.id == account_id)
    return db.scalar(stmt)


def list_bank_accounts(
    db: Session,
    *,
    is_active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[BankAccount], int]:
    """Liste aller Bankkonten mit Filtern."""
    stmt = select(BankAccount)
    count_stmt = select(func.count(BankAccount.id))

    if is_active is not None:
        stmt = stmt.where(BankAccount.is_active == is_active)
        count_stmt = count_stmt.where(BankAccount.is_active == is_active)

    stmt = stmt.order_by(BankAccount.account_name).limit(limit).offset(offset)

    items = list(db.scalars(stmt).all())
    total = db.scalar(count_stmt) or 0

    return items, total


def update_bank_account(
    db: Session,
    account: BankAccount,
    data: BankAccountUpdate,
) -> BankAccount:
    """Aktualisiert ein Bankkonto."""
    payload = data.model_dump(exclude_unset=True)

    if "account_type" in payload and isinstance(payload["account_type"], AccountType):
        payload["account_type"] = payload["account_type"].value

    for field, value in payload.items():
        setattr(account, field, value)

    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def delete_bank_account(db: Session, account: BankAccount) -> None:
    """Löscht ein Bankkonto (CASCADE löscht auch alle Transaktionen)."""
    db.delete(account)
    db.commit()


def create_bank_transaction(db: Session, data: BankTransactionCreate) -> BankTransaction:
    """Erstellt eine neue Banktransaktion."""
    transaction = BankTransaction(
        account_id=data.account_id,
        transaction_date=data.transaction_date,
        value_date=data.value_date,
        amount=data.amount,
        transaction_type=data.transaction_type.value if isinstance(data.transaction_type, TransactionType) else data.transaction_type,
        counterparty_name=data.counterparty_name,
        counterparty_iban=data.counterparty_iban,
        purpose=data.purpose,
        reference=data.reference,
    )
    db.add(transaction)

    # Update account balance
    account = get_bank_account(db, data.account_id)
    if account:
        account.balance += data.amount
        db.add(account)

    db.commit()
    db.refresh(transaction)
    return transaction


def get_bank_transaction(db: Session, transaction_id: uuid.UUID) -> Optional[BankTransaction]:
    """Holt eine einzelne Transaktion."""
    stmt = select(BankTransaction).where(BankTransaction.id == transaction_id)
    return db.scalar(stmt)


def list_bank_transactions(
    db: Session,
    *,
    account_id: Optional[uuid.UUID] = None,
    reconciliation_status: Optional[ReconciliationStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[BankTransaction], int]:
    """Liste aller Transaktionen mit Filtern."""
    stmt = select(BankTransaction)
    count_stmt = select(func.count(BankTransaction.id))

    if account_id is not None:
        stmt = stmt.where(BankTransaction.account_id == account_id)
        count_stmt = count_stmt.where(BankTransaction.account_id == account_id)

    if reconciliation_status is not None:
        status_value = reconciliation_status.value if isinstance(reconciliation_status, ReconciliationStatus) else reconciliation_status
        stmt = stmt.where(BankTransaction.reconciliation_status == status_value)
        count_stmt = count_stmt.where(BankTransaction.reconciliation_status == status_value)

    if from_date is not None:
        stmt = stmt.where(BankTransaction.transaction_date >= from_date)
        count_stmt = count_stmt.where(BankTransaction.transaction_date >= from_date)

    if to_date is not None:
        stmt = stmt.where(BankTransaction.transaction_date <= to_date)
        count_stmt = count_stmt.where(BankTransaction.transaction_date <= to_date)

    stmt = stmt.order_by(BankTransaction.transaction_date.desc()).limit(limit).offset(offset)

    items = list(db.scalars(stmt).all())
    total = db.scalar(count_stmt) or 0

    return items, total


def update_bank_transaction(
    db: Session,
    transaction: BankTransaction,
    data: BankTransactionUpdate,
) -> BankTransaction:
    """Aktualisiert eine Transaktion."""
    payload = data.model_dump(exclude_unset=True)

    if "transaction_type" in payload and isinstance(payload["transaction_type"], TransactionType):
        payload["transaction_type"] = payload["transaction_type"].value

    if "reconciliation_status" in payload and isinstance(payload["reconciliation_status"], ReconciliationStatus):
        payload["reconciliation_status"] = payload["reconciliation_status"].value

    for field, value in payload.items():
        setattr(transaction, field, value)

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_bank_transaction(db: Session, transaction: BankTransaction) -> None:
    """Löscht eine Transaktion (und korrigiert den Kontostand)."""
    # Update account balance (revert the transaction)
    account = get_bank_account(db, transaction.account_id)
    if account:
        account.balance -= transaction.amount
        db.add(account)

    db.delete(transaction)
    db.commit()


def reconcile_transaction(
    db: Session,
    transaction: BankTransaction,
    payment_id: Optional[uuid.UUID] = None,
    expense_id: Optional[uuid.UUID] = None,
    reconciliation_note: Optional[str] = None,
    user_id: Optional[str] = None,
) -> BankTransaction:
    """
    Gleicht eine Transaktion manuell mit einer Zahlung oder Ausgabe ab.

    Args:
        transaction: Die abzugleichende Transaktion
        payment_id: Optional Payment ID
        expense_id: Optional Expense ID
        reconciliation_note: Notiz zum Abgleich
        user_id: Benutzer der den Abgleich durchführt
    """
    transaction.matched_payment_id = payment_id
    transaction.matched_expense_id = expense_id
    transaction.reconciliation_status = ReconciliationStatus.CONFIRMED.value
    transaction.reconciliation_note = reconciliation_note
    transaction.reconciled_at = datetime.utcnow()
    transaction.reconciled_by = user_id

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def unreconcile_transaction(
    db: Session,
    transaction: BankTransaction,
) -> BankTransaction:
    """
    Entfernt den Abgleich einer Transaktion.
    """
    transaction.matched_payment_id = None
    transaction.matched_expense_id = None
    transaction.reconciliation_status = ReconciliationStatus.UNMATCHED.value
    transaction.reconciliation_note = None
    transaction.reconciled_at = None
    transaction.reconciled_by = None

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
