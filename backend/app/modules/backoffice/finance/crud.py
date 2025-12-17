# app/modules/backoffice/finance/service.py
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Expense, ExpenseCategory
from .schemas import ExpenseCreate, ExpenseUpdate, ExpenseKpiResponse


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
