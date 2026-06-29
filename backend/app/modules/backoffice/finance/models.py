# app/modules/backoffice/finance/models.py
"""
Finance Module Models - WorkmateOS Phase 2.

Verwaltet:
- Expenses (Ausgaben/Kosten für Projekte)
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Index,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.projects.models import Project
    from app.modules.backoffice.invoices.models import Invoice


class ExpenseCategory(str, Enum):
    """Kategorien für Ausgaben."""
    TRAVEL = "travel"
    MATERIAL = "material"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    CONSULTING = "consulting"
    MARKETING = "marketing"
    OFFICE = "office"
    TRAINING = "training"
    OTHER = "other"


class Expense(Base, UUIDMixin, TimestampMixin):
    """
    Ausgaben und Kosten.
    
    Verwaltet projektbezogene oder allgemeine Ausgaben mit
    Kategorisierung und optionaler Zuordnung zu Rechnungen.
    
    Attributes:
        category: Ausgabenkategorie (travel, material, software, etc.)
        amount: Ausgabenbetrag
        description: Beschreibung der Ausgabe
        receipt_path: Pfad zum Beleg/Quittung
        project: Optional zugehöriges Projekt
        invoice: Optional zugehörige Rechnung (wenn bereits abgerechnet)
        note: Zusätzliche Notizen
    """
    __tablename__ = "expenses"
    __table_args__ = (
        Index("ix_expenses_project_id", "project_id"),
        Index("ix_expenses_invoice_id", "invoice_id"),
        Index("ix_expenses_category", "category"),
        Index("ix_expenses_created_at", "created_at"),
        CheckConstraint("amount > 0", name="check_expense_amount_positive"),
    )

    # Business Fields
    category: Mapped[str] = mapped_column(
        String(50),
        comment="Ausgabenkategorie (travel, material, software, etc.)"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Ausgabenbetrag"
    )
    description: Mapped[str] = mapped_column(
        Text,
        comment="Beschreibung der Ausgabe"
    )
    receipt_path: Mapped[str | None] = mapped_column(
        Text,
        comment="Pfad zum Beleg/Quittung (PDF, Bild)"
    )
    note: Mapped[str | None] = mapped_column(
        Text,
        comment="Zusätzliche Notizen"
    )
    is_billable: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
        comment="Kann an Kunden weiterberechnet werden"
    )

    # Foreign Keys
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        comment="Optional zugehöriges Projekt"
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("invoices.id", ondelete="SET NULL"),
        comment="Optional zugehörige Rechnung (wenn bereits abgerechnet)"
    )

    # Relationships
    project: Mapped[Project | None] = relationship(
        "Project",
        back_populates="expenses"
    )
    invoice: Mapped[Invoice | None] = relationship(
        "Invoice",
        back_populates="expenses"
    )

    @property
    def is_invoiced(self) -> bool:
        """
        Prüft ob Ausgabe bereits abgerechnet wurde.
        
        Returns:
            True wenn eine Rechnung zugeordnet ist
        """
        return self.invoice_id is not None

    def __repr__(self) -> str:
        return (
            f"<Expense(category='{self.category}', "
            f"amount={self.amount}, "
            f"invoiced={self.is_invoiced})>"
        )


class BankAccount(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bank_accounts"
    __table_args__ = (
        Index("ix_bank_accounts_is_active", "is_active"),
    )

    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), default="checking")
    iban: Mapped[str | None] = mapped_column(String(34), unique=True)
    bic: Mapped[str | None] = mapped_column(String(11))
    bank_name: Mapped[str | None] = mapped_column(String(100))
    account_holder: Mapped[str | None] = mapped_column(String(100))
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    note: Mapped[str | None] = mapped_column(Text)

    transactions: Mapped[list["BankTransaction"]] = relationship(
        "BankTransaction", back_populates="account", cascade="all, delete-orphan"
    )


class BankTransaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bank_transactions"
    __table_args__ = (
        Index("ix_bank_transactions_account_id", "account_id"),
        Index("ix_bank_transactions_transaction_date", "transaction_date"),
        Index("ix_bank_transactions_reconciliation_status", "reconciliation_status"),
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False
    )
    matched_payment_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL")
    )
    matched_expense_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("expenses.id", ondelete="SET NULL")
    )

    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    value_date: Mapped[Optional[date]] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    counterparty_name: Mapped[Optional[str]] = mapped_column(String(255))
    counterparty_iban: Mapped[Optional[str]] = mapped_column(String(34))
    purpose: Mapped[Optional[str]] = mapped_column(Text)
    reference: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    reconciliation_status: Mapped[str] = mapped_column(String(50), default="unmatched")
    reconciliation_note: Mapped[Optional[str]] = mapped_column(Text)
    reconciled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    reconciled_by: Mapped[Optional[str]] = mapped_column(String(100))

    account: Mapped["BankAccount"] = relationship("BankAccount", back_populates="transactions")


class StripeConfig(Base, UUIDMixin, TimestampMixin):
    """Stripe-Zahlungsintegration Konfiguration"""
    __tablename__ = "stripe_config"

    publishable_key: Mapped[str] = mapped_column(String(255), nullable=False)
    secret_key: Mapped[str] = mapped_column(String(255), nullable=False)
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(255))
    test_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)