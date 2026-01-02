# app/modules/backoffice/finance/schemas.py
from __future__ import annotations

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import (
    ExpenseCategory,
    AccountType,
    TransactionType,
    ReconciliationStatus
)


class ExpenseBase(BaseModel):
    """Gemeinsame Felder für Expense-Create/Update."""
    title: str = Field(
        description="Bezeichnung der kosten"
    )
    category: ExpenseCategory = Field(
        description="Ausgabenkategorie (travel, material, software, etc.)"
    )
    amount: Decimal = Field(
        gt=0,
        description="Ausgabenbetrag"
    )
    description: str = Field(
        description="Beschreibung der Ausgabe"
    )
    receipt_path: Optional[str] = Field(
        default=None,
        description="Pfad zum Beleg/Quittung (PDF, Bild)"
    )
    note: Optional[str] = Field(
        default=None,
        description="Zusätzliche Notizen"
    )
    is_billable: bool = Field(
        default=True,
        description="Kann an Kunden weiterberechnet werden"
    )
    project_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional zugehöriges Projekt"
    )
    invoice_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional zugehörige Rechnung (wenn bereits abgerechnet)"
    )


class ExpenseCreate(ExpenseBase):
    """Schema zum Anlegen einer neuen Ausgabe."""
    pass


class ExpenseUpdate(BaseModel):
    """Schema für partielle Updates (PATCH). Alle Felder optional."""
    title : Optional[str] = ""
    category: Optional[ExpenseCategory] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    description: Optional[str] = None
    receipt_path: Optional[str] = None
    note: Optional[str] = None
    is_billable: Optional[bool] = None
    project_id: Optional[uuid.UUID] = None
    invoice_id: Optional[uuid.UUID] = None


class ExpenseRead(BaseModel):
    """Ausgabe einer Expense Richtung API-Consumer."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title:str
    category: ExpenseCategory
    amount: Decimal
    description: str
    receipt_path: Optional[str]
    note: Optional[str]
    is_billable: bool

    project_id: Optional[uuid.UUID]
    invoice_id: Optional[uuid.UUID]

    created_at: datetime
    updated_at: datetime

    @property
    def is_invoiced(self) -> bool:
        return self.invoice_id is not None


class ExpenseListResponse(BaseModel):
    """Standard-Liste mit Paging-Option (für später vorbereitet)."""
    items: list[ExpenseRead]
    total: int


class ExpenseKpiRequest(BaseModel):
    """Optional – falls du später einen POST-KPI-Endpoint willst."""
    month: Optional[str] = Field(
        default=None,
        description="Optional: Monat im Format YYYY-MM"
    )
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    project_id: Optional[uuid.UUID] = None
    category: Optional[ExpenseCategory] = None


class ExpenseKpiResponse(BaseModel):
    """KPI Antwort – Summe und Verteilung nach Kategorie."""
    total: Decimal
    by_category: dict[ExpenseCategory, Decimal]


# ============================================================================
# BANKING SCHEMAS
# ============================================================================

class BankAccountBase(BaseModel):
    """Gemeinsame Felder für BankAccount-Create/Update."""
    account_name: str = Field(
        description="Bezeichnung des Kontos (z.B. 'Geschäftskonto N26')"
    )
    account_type: AccountType = Field(
        default=AccountType.CHECKING,
        description="Kontotyp: checking, savings, credit, cash"
    )
    iban: Optional[str] = Field(
        default=None,
        max_length=34,
        description="Internationale Bankkontonummer"
    )
    bic: Optional[str] = Field(
        default=None,
        max_length=11,
        description="Bank Identifier Code (SWIFT)"
    )
    bank_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Name der Bank"
    )
    account_holder: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Kontoinhaber"
    )
    is_active: bool = Field(
        default=True,
        description="Konto ist aktiv?"
    )
    note: Optional[str] = Field(
        default=None,
        description="Notizen zum Konto"
    )


class BankAccountCreate(BankAccountBase):
    """Schema zum Anlegen eines neuen Bankkontos."""
    balance: Decimal = Field(
        default=Decimal("0.00"),
        description="Initialer Kontostand"
    )


class BankAccountUpdate(BaseModel):
    """Schema für partielle Updates (PATCH). Alle Felder optional."""
    account_name: Optional[str] = None
    account_type: Optional[AccountType] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    bank_name: Optional[str] = None
    account_holder: Optional[str] = None
    balance: Optional[Decimal] = None
    is_active: Optional[bool] = None
    note: Optional[str] = None


class BankAccountRead(BaseModel):
    """Ausgabe eines BankAccount Richtung API-Consumer."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_name: str
    account_type: AccountType
    iban: Optional[str]
    bic: Optional[str]
    bank_name: Optional[str]
    account_holder: Optional[str]
    balance: Decimal
    is_active: bool
    note: Optional[str]
    created_at: datetime
    updated_at: datetime


class BankAccountListResponse(BaseModel):
    """Liste von Bankkonten mit Pagination."""
    items: list[BankAccountRead]
    total: int


# ============================================================================
# BANK TRANSACTION SCHEMAS
# ============================================================================

class BankTransactionBase(BaseModel):
    """Gemeinsame Felder für BankTransaction-Create/Update."""
    transaction_date: date = Field(
        description="Buchungsdatum"
    )
    value_date: Optional[date] = Field(
        default=None,
        description="Wertstellungsdatum"
    )
    amount: Decimal = Field(
        description="Betrag (positiv=Eingang, negativ=Ausgang)"
    )
    transaction_type: TransactionType = Field(
        description="Typ: income, expense, transfer, fee, interest"
    )
    counterparty_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Name des Zahlungspartners"
    )
    counterparty_iban: Optional[str] = Field(
        default=None,
        max_length=34,
        description="IBAN des Zahlungspartners"
    )
    purpose: Optional[str] = Field(
        default=None,
        description="Verwendungszweck"
    )
    reference: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Eindeutige Transaktions-ID der Bank"
    )


class BankTransactionCreate(BankTransactionBase):
    """Schema zum Anlegen einer neuen Transaktion."""
    account_id: uuid.UUID = Field(
        description="Zugehöriges Bankkonto"
    )


class BankTransactionUpdate(BaseModel):
    """Schema für partielle Updates (PATCH). Alle Felder optional."""
    transaction_date: Optional[date] = None
    value_date: Optional[date] = None
    amount: Optional[Decimal] = None
    transaction_type: Optional[TransactionType] = None
    counterparty_name: Optional[str] = None
    counterparty_iban: Optional[str] = None
    purpose: Optional[str] = None
    reference: Optional[str] = None
    reconciliation_status: Optional[ReconciliationStatus] = None
    reconciliation_note: Optional[str] = None


class BankTransactionRead(BaseModel):
    """Ausgabe einer BankTransaction Richtung API-Consumer."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    transaction_date: date
    value_date: Optional[date]
    amount: Decimal
    transaction_type: TransactionType
    counterparty_name: Optional[str]
    counterparty_iban: Optional[str]
    purpose: Optional[str]
    reference: Optional[str]
    reconciliation_status: ReconciliationStatus
    reconciliation_note: Optional[str]
    reconciled_at: Optional[datetime]
    reconciled_by: Optional[str]
    matched_payment_id: Optional[uuid.UUID]
    matched_expense_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    @property
    def is_reconciled(self) -> bool:
        return self.reconciliation_status in [
            ReconciliationStatus.MATCHED,
            ReconciliationStatus.CONFIRMED
        ]


class BankTransactionListResponse(BaseModel):
    """Liste von Transaktionen mit Pagination."""
    items: list[BankTransactionRead]
    total: int


class ReconcileRequest(BaseModel):
    """Request zum manuellen Abgleich einer Transaktion."""
    payment_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Invoice Payment ID zum Abgleich"
    )
    expense_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Expense ID zum Abgleich"
    )
    reconciliation_note: Optional[str] = Field(
        default=None,
        description="Notizen zum Abgleich"
    )


# ============================================================================
# CSV IMPORT SCHEMAS
# ============================================================================

class CsvImportRequest(BaseModel):
    """Request für CSV-Import."""
    account_id: uuid.UUID = Field(
        description="Ziel-Bankkonto für Import"
    )
    delimiter: str = Field(
        default=",",
        max_length=1,
        description="CSV-Trennzeichen (default: ,)"
    )
    skip_duplicates: bool = Field(
        default=True,
        description="Duplikate überspringen (basierend auf reference)"
    )
    auto_reconcile: bool = Field(
        default=True,
        description="Automatische Reconciliation nach Import"
    )


class CsvImportResponse(BaseModel):
    """Response nach CSV-Import."""
    success: bool
    bank_format: Optional[str] = None
    total: int
    imported: int
    skipped: int
    reconciled: int
    errors: list[str]
