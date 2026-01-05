# app/modules/backoffice/finance/models.py
"""
Finance Module Models - WorkmateOS Phase 3.

Verwaltet:
- Expenses (Ausgaben/Kosten für Projekte)
- BankAccounts (Bankkonten)
- BankTransactions (Banktransaktionen)
- Payment Reconciliation (Zahlungsabgleich)
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Numeric,
    Index,
    CheckConstraint,
    Date,
    DateTime,
    Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.projects.models import Project
    from app.modules.backoffice.invoices.models import Invoice, Payment


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
    title : Mapped[str] = mapped_column(
        String(50),
        comment="Bezeichnung der kosten"
    )
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


# ============================================================================
# BANKING
# ============================================================================

class AccountType(str, Enum):
    """Kontotypen."""
    CHECKING = "checking"  # Girokonto
    SAVINGS = "savings"    # Sparkonto
    CREDIT = "credit"      # Kreditkarte
    CASH = "cash"          # Bargeld


class TransactionType(str, Enum):
    """Transaktionstypen."""
    INCOME = "income"        # Eingang (z.B. Zahlung von Kunde)
    EXPENSE = "expense"      # Ausgang (z.B. Lieferantenrechnung)
    TRANSFER = "transfer"    # Umbuchung zwischen eigenen Konten
    FEE = "fee"             # Bankgebühren
    INTEREST = "interest"    # Zinsen


class ReconciliationStatus(str, Enum):
    """Status des Zahlungsabgleichs."""
    UNMATCHED = "unmatched"      # Noch nicht zugeordnet
    MATCHED = "matched"          # Automatisch zugeordnet
    CONFIRMED = "confirmed"      # Manuell bestätigt
    IGNORED = "ignored"          # Bewusst ignoriert


class BankAccount(Base, UUIDMixin, TimestampMixin):
    """
    Bankkonten.

    Verwaltet Unternehmens-Bankkonten mit IBAN, BIC und aktuellem Saldo.

    Attributes:
        account_name: Bezeichnung des Kontos (z.B. "Geschäftskonto")
        account_type: Kontotyp (checking, savings, credit, cash)
        iban: Internationale Bankkontonummer
        bic: Bank Identifier Code
        bank_name: Name der Bank
        account_holder: Kontoinhaber
        balance: Aktueller Kontostand
        is_active: Konto aktiv?
        transactions: Alle Transaktionen auf diesem Konto
    """
    __tablename__ = "bank_accounts"
    __table_args__ = (
        Index("ix_bank_accounts_iban", "iban"),
        Index("ix_bank_accounts_is_active", "is_active"),
        CheckConstraint("account_type IN ('checking', 'savings', 'credit', 'cash')", name="check_account_type_valid"),
    )

    # Business Fields
    account_name: Mapped[str] = mapped_column(
        String(100),
        comment="Bezeichnung des Kontos (z.B. 'Geschäftskonto')"
    )
    account_type: Mapped[str] = mapped_column(
        String(50),
        default=AccountType.CHECKING.value,
        server_default=AccountType.CHECKING.value,
        comment="Kontotyp: checking, savings, credit, cash"
    )
    iban: Mapped[str | None] = mapped_column(
        String(34),
        unique=True,
        comment="Internationale Bankkontonummer"
    )
    bic: Mapped[str | None] = mapped_column(
        String(11),
        comment="Bank Identifier Code (SWIFT)"
    )
    bank_name: Mapped[str | None] = mapped_column(
        String(100),
        comment="Name der Bank"
    )
    account_holder: Mapped[str | None] = mapped_column(
        String(100),
        comment="Kontoinhaber"
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Aktueller Kontostand"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        comment="Konto ist aktiv?"
    )
    note: Mapped[str | None] = mapped_column(
        Text,
        comment="Notizen zum Konto"
    )

    # Relationships
    transactions: Mapped[list["BankTransaction"]] = relationship(
        "BankTransaction",
        back_populates="account",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<BankAccount(name='{self.account_name}', "
            f"iban='{self.iban}', "
            f"balance={self.balance})>"
        )


class BankTransaction(Base, UUIDMixin, TimestampMixin):
    """
    Banktransaktionen.

    Verwaltet alle Ein- und Ausgänge auf Bankkonten mit automatischem
    Zahlungsabgleich zu Rechnungen.

    Attributes:
        account: Zugehöriges Bankkonto
        transaction_date: Buchungsdatum
        value_date: Wertstellungsdatum
        amount: Betrag (positiv=Eingang, negativ=Ausgang)
        transaction_type: Typ (income, expense, transfer, fee, interest)
        counterparty_name: Name Zahlungspartner
        counterparty_iban: IBAN Zahlungspartner
        purpose: Verwendungszweck
        reference: Referenz/Transaktions-ID der Bank
        reconciliation_status: Status des Zahlungsabgleichs
        matched_payment: Zugeordnete Zahlung (Payment)
        matched_expense: Zugeordnete Ausgabe (Expense)
    """
    __tablename__ = "bank_transactions"
    __table_args__ = (
        Index("ix_bank_transactions_account_id", "account_id"),
        Index("ix_bank_transactions_transaction_date", "transaction_date"),
        Index("ix_bank_transactions_reconciliation_status", "reconciliation_status"),
        Index("ix_bank_transactions_reference", "reference"),
        CheckConstraint(
            "transaction_type IN ('income', 'expense', 'transfer', 'fee', 'interest')",
            name="check_transaction_type_valid"
        ),
        CheckConstraint(
            "reconciliation_status IN ('unmatched', 'matched', 'confirmed', 'ignored')",
            name="check_reconciliation_status_valid"
        ),
    )

    # Foreign Keys
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="CASCADE"),
        nullable=False,
        comment="Zugehöriges Bankkonto"
    )
    matched_payment_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL"),
        comment="Zugeordnete Zahlung (Payment aus Invoices)"
    )
    matched_expense_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("expenses.id", ondelete="SET NULL"),
        comment="Zugeordnete Ausgabe"
    )

    # Business Fields
    transaction_date: Mapped[Date] = mapped_column(
        Date,
        comment="Buchungsdatum"
    )
    value_date: Mapped[Date | None] = mapped_column(
        Date,
        comment="Wertstellungsdatum"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="Betrag (positiv=Eingang, negativ=Ausgang)"
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        comment="Typ: income, expense, transfer, fee, interest"
    )
    counterparty_name: Mapped[str | None] = mapped_column(
        String(255),
        comment="Name des Zahlungspartners"
    )
    counterparty_iban: Mapped[str | None] = mapped_column(
        String(34),
        comment="IBAN des Zahlungspartners"
    )
    purpose: Mapped[str | None] = mapped_column(
        Text,
        comment="Verwendungszweck"
    )
    reference: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        comment="Eindeutige Transaktions-ID der Bank"
    )
    reconciliation_status: Mapped[str] = mapped_column(
        String(50),
        default=ReconciliationStatus.UNMATCHED.value,
        server_default=ReconciliationStatus.UNMATCHED.value,
        comment="Status des Zahlungsabgleichs"
    )
    reconciliation_note: Mapped[str | None] = mapped_column(
        Text,
        comment="Notizen zum Abgleich"
    )
    reconciled_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        comment="Zeitpunkt des Abgleichs"
    )
    reconciled_by: Mapped[str | None] = mapped_column(
        String(100),
        comment="Benutzer der den Abgleich durchgeführt hat"
    )

    # Relationships
    account: Mapped["BankAccount"] = relationship(
        "BankAccount",
        back_populates="transactions"
    )
    matched_payment: Mapped["Payment | None"] = relationship(
        "Payment",
        foreign_keys=[matched_payment_id]
    )
    matched_expense: Mapped["Expense | None"] = relationship(
        "Expense",
        foreign_keys=[matched_expense_id]
    )

    @property
    def is_reconciled(self) -> bool:
        """
        Prüft ob Transaktion abgeglichen wurde.

        Returns:
            True wenn Status matched oder confirmed
        """
        return self.reconciliation_status in [
            ReconciliationStatus.MATCHED.value,
            ReconciliationStatus.CONFIRMED.value
        ]

    def __repr__(self) -> str:
        return (
            f"<BankTransaction(date={self.transaction_date}, "
            f"amount={self.amount}, "
            f"counterparty='{self.counterparty_name}', "
            f"reconciled={self.is_reconciled})>"
        )


# ============================================================================
# SEVDESK INTEGRATION
# ============================================================================

class SevDeskSyncStatus(str, Enum):
    """Status der SevDesk Synchronisation."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class SevDeskConfig(Base, UUIDMixin, TimestampMixin):
    """
    SevDesk Konfiguration.

    Speichert API-Token und Sync-Einstellungen für die
    bidirektionale Synchronisation mit SevDesk.

    Attributes:
        api_token: SevDesk API Token (verschlüsselt)
        auto_sync_enabled: Automatische Synchronisation aktiviert?
        sync_invoices: Rechnungen synchronisieren?
        sync_bank_accounts: Bankkonten synchronisieren?
        sync_transactions: Transaktionen synchronisieren?
        last_sync_at: Zeitpunkt der letzten Synchronisation
        is_active: Konfiguration aktiv?
    """
    __tablename__ = "sevdesk_config"
    __table_args__ = (
        Index("ix_sevdesk_config_is_active", "is_active"),
    )

    # Configuration Fields
    api_token: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="SevDesk API Token (verschlüsselt mit Fernet)"
    )
    auto_sync_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        comment="Automatische tägliche Synchronisation aktiviert?"
    )
    sync_invoices: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        comment="Rechnungen synchronisieren?"
    )
    sync_bank_accounts: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        comment="Bankkonten synchronisieren?"
    )
    sync_transactions: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        comment="Transaktionen synchronisieren?"
    )
    last_sync_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        comment="Zeitpunkt der letzten erfolgreichen Synchronisation"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        comment="Konfiguration ist aktiv?"
    )

    def __repr__(self) -> str:
        return (
            f"<SevDeskConfig(auto_sync={self.auto_sync_enabled}, "
            f"last_sync={self.last_sync_at})>"
        )


class SevDeskInvoiceMapping(Base, UUIDMixin, TimestampMixin):
    """
    Mapping zwischen WorkmateOS Invoice und SevDesk Invoice.

    Speichert die Zuordnung von lokalen Rechnungen zu SevDesk-Rechnungen
    für bidirektionale Synchronisation.

    Attributes:
        invoice_id: WorkmateOS Invoice UUID
        sevdesk_invoice_id: SevDesk Invoice ID (Integer)
        last_synced_at: Zeitpunkt der letzten Synchronisation
        sync_status: Status der letzten Synchronisation
    """
    __tablename__ = "sevdesk_invoice_mappings"
    __table_args__ = (
        Index("ix_sevdesk_invoice_mappings_invoice_id", "invoice_id"),
        Index("ix_sevdesk_invoice_mappings_sevdesk_id", "sevdesk_invoice_id"),
    )

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="WorkmateOS Invoice ID"
    )

    # Mapping Fields
    sevdesk_invoice_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="SevDesk Invoice ID"
    )
    last_synced_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        comment="Zeitpunkt der letzten Synchronisation"
    )
    sync_status: Mapped[str] = mapped_column(
        String(50),
        default=SevDeskSyncStatus.SUCCESS.value,
        comment="Status der letzten Synchronisation"
    )
    sync_error: Mapped[str | None] = mapped_column(
        Text,
        comment="Fehlermeldung bei fehlgeschlagener Synchronisation"
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(
        "Invoice",
        foreign_keys=[invoice_id]
    )

    def __repr__(self) -> str:
        return (
            f"<SevDeskInvoiceMapping(invoice_id={self.invoice_id}, "
            f"sevdesk_id={self.sevdesk_invoice_id})>"
        )


class SevDeskBankAccountMapping(Base, UUIDMixin, TimestampMixin):
    """
    Mapping zwischen WorkmateOS BankAccount und SevDesk CheckAccount.

    Speichert die Zuordnung von lokalen Bankkonten zu SevDesk-CheckAccounts
    für bidirektionale Synchronisation.

    Attributes:
        bank_account_id: WorkmateOS BankAccount UUID
        sevdesk_check_account_id: SevDesk CheckAccount ID (Integer)
        last_synced_at: Zeitpunkt der letzten Synchronisation
        sync_status: Status der letzten Synchronisation
    """
    __tablename__ = "sevdesk_bank_account_mappings"
    __table_args__ = (
        Index("ix_sevdesk_bank_account_mappings_bank_account_id", "bank_account_id"),
        Index("ix_sevdesk_bank_account_mappings_sevdesk_id", "sevdesk_check_account_id"),
    )

    # Foreign Keys
    bank_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="WorkmateOS BankAccount ID"
    )

    # Mapping Fields
    sevdesk_check_account_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="SevDesk CheckAccount ID"
    )
    last_synced_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        comment="Zeitpunkt der letzten Synchronisation"
    )
    sync_status: Mapped[str] = mapped_column(
        String(50),
        default=SevDeskSyncStatus.SUCCESS.value,
        comment="Status der letzten Synchronisation"
    )
    sync_error: Mapped[str | None] = mapped_column(
        Text,
        comment="Fehlermeldung bei fehlgeschlagener Synchronisation"
    )

    # Relationships
    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount",
        foreign_keys=[bank_account_id]
    )

    def __repr__(self) -> str:
        return (
            f"<SevDeskBankAccountMapping(bank_account_id={self.bank_account_id}, "
            f"sevdesk_id={self.sevdesk_check_account_id})>"
        )


class SevDeskSyncHistory(Base, UUIDMixin, TimestampMixin):
    """
    Synchronisations-Historie für SevDesk.

    Protokolliert alle Synchronisations-Vorgänge für Audit-Trail
    und Fehleranalyse.

    Attributes:
        sync_type: Typ der Synchronisation (invoice, bank_account, transaction)
        direction: Richtung (push_to_sevdesk, pull_from_sevdesk)
        status: Status (success, failed, partial)
        records_processed: Anzahl verarbeiteter Datensätze
        records_success: Anzahl erfolgreich synchronisierter Datensätze
        records_failed: Anzahl fehlgeschlagener Datensätze
        error_message: Fehlermeldung bei fehlgeschlagener Synchronisation
        started_at: Startzeitpunkt
        completed_at: Endzeitpunkt
    """
    __tablename__ = "sevdesk_sync_history"
    __table_args__ = (
        Index("ix_sevdesk_sync_history_sync_type", "sync_type"),
        Index("ix_sevdesk_sync_history_status", "status"),
        Index("ix_sevdesk_sync_history_started_at", "started_at"),
    )

    # Sync Fields
    sync_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Typ: invoice, bank_account, transaction, payment"
    )
    direction: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Richtung: push_to_sevdesk, pull_from_sevdesk"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Status: success, failed, partial"
    )
    records_processed: Mapped[int] = mapped_column(
        default=0,
        comment="Anzahl verarbeiteter Datensätze"
    )
    records_success: Mapped[int] = mapped_column(
        default=0,
        comment="Anzahl erfolgreich synchronisierter Datensätze"
    )
    records_failed: Mapped[int] = mapped_column(
        default=0,
        comment="Anzahl fehlgeschlagener Datensätze"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        comment="Fehlermeldung"
    )
    started_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Startzeitpunkt"
    )
    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        comment="Endzeitpunkt"
    )

    def __repr__(self) -> str:
        return (
            f"<SevDeskSyncHistory(type={self.sync_type}, "
            f"direction={self.direction}, "
            f"status={self.status}, "
            f"success={self.records_success}/{self.records_processed})>"
        )


# ============================================================================
# Stripe Payment Integration
# ============================================================================


class StripeConfig(UUIDMixin, TimestampMixin, Base):
    """
    Stripe API Configuration
    Stores API keys for Stripe payment processing
    """
    __tablename__ = "stripe_config"

    publishable_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Stripe Publishable Key (pk_test_... or pk_live_...)"
    )
    secret_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Stripe Secret Key (ENCRYPTED: sk_test_... or sk_live_...)"
    )
    webhook_secret: Mapped[str | None] = mapped_column(
        String(255),
        comment="Webhook Signing Secret (whsec_...)"
    )
    test_mode: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Test Mode (true) or Live Mode (false)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Config aktiv/inaktiv"
    )

    def __repr__(self) -> str:
        mode = "TEST" if self.test_mode else "LIVE"
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"<StripeConfig(mode={mode}, status={status})>"
