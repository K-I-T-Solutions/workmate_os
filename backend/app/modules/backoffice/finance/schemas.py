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


# ============================================================================
# FINTS/HBCI SCHEMAS
# ============================================================================

class FinTsCredentials(BaseModel):
    """FinTS-Zugangsdaten (NIE in DB speichern!)."""
    blz: str = Field(
        min_length=8,
        max_length=8,
        description="Bankleitzahl (8-stellig)"
    )
    login: str = Field(
        min_length=1,
        max_length=50,
        description="Online-Banking Benutzerkennung"
    )
    pin: str = Field(
        min_length=4,
        max_length=20,
        description="PIN für Online-Banking"
    )
    endpoint: Optional[str] = Field(
        default=None,
        description="Optional: FinTS-Server-URL (automatisch ermittelt wenn leer)"
    )


class FinTsSyncRequest(BaseModel):
    """Request für FinTS Transaction Sync."""
    account_id: uuid.UUID = Field(
        description="Bank Account ID (muss mit IBAN übereinstimmen)"
    )
    credentials: FinTsCredentials
    from_date: Optional[date] = Field(
        default=None,
        description="Startdatum (default: vor 90 Tagen)"
    )
    to_date: Optional[date] = Field(
        default=None,
        description="Enddatum (default: heute)"
    )
    skip_duplicates: bool = Field(
        default=True,
        description="Duplikate überspringen"
    )
    auto_reconcile: bool = Field(
        default=True,
        description="Automatische Reconciliation"
    )


class FinTsSyncResponse(BaseModel):
    """Response nach FinTS Sync."""
    success: bool
    total: int
    imported: int
    skipped: int
    reconciled: int
    errors: list[str]


class FinTsAccountSyncResponse(BaseModel):
    """Response nach FinTS Account Sync."""
    success: bool
    total_accounts: int
    existing: int
    created: int
    errors: list[str]


class FinTsBalanceRequest(BaseModel):
    """Request für FinTS Balance Check."""
    credentials: FinTsCredentials
    iban: str = Field(
        min_length=15,
        max_length=34,
        description="IBAN des Kontos"
    )


class FinTsBalanceResponse(BaseModel):
    """Response mit Kontostand."""
    success: bool
    balance: Optional[Decimal] = None
    iban: str
    error: Optional[str] = None


# ============================================================================
# SEVDESK INTEGRATION SCHEMAS
# ============================================================================

class SevDeskConfigRequest(BaseModel):
    """Request für SevDesk Konfiguration."""
    api_token: str = Field(
        min_length=32,
        max_length=32,
        description="SevDesk API Token (32 Zeichen hexadezimal)"
    )
    auto_sync_enabled: bool = Field(
        default=False,
        description="Automatische tägliche Synchronisation aktivieren"
    )
    sync_invoices: bool = Field(
        default=True,
        description="Rechnungen synchronisieren"
    )
    sync_bank_accounts: bool = Field(
        default=True,
        description="Bankkonten synchronisieren"
    )
    sync_transactions: bool = Field(
        default=True,
        description="Transaktionen synchronisieren"
    )


class SevDeskConfigResponse(BaseModel):
    """Response mit SevDesk Konfigurationsstatus."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    configured: bool
    auto_sync_enabled: bool
    sync_invoices: bool
    sync_bank_accounts: bool
    sync_transactions: bool
    last_sync_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SevDeskSyncInvoiceRequest(BaseModel):
    """Request zum Synchronisieren einer einzelnen Rechnung."""
    invoice_id: uuid.UUID = Field(
        description="WorkmateOS Invoice ID"
    )


class SevDeskSyncInvoiceResponse(BaseModel):
    """Response nach Invoice Sync."""
    success: bool
    invoice_id: uuid.UUID
    sevdesk_invoice_id: Optional[str] = None
    message: str
    synced_at: Optional[datetime] = None


class SevDeskSyncBankAccountRequest(BaseModel):
    """Request zum Synchronisieren eines Bankkontos."""
    bank_account_id: uuid.UUID = Field(
        description="WorkmateOS BankAccount ID"
    )


class SevDeskSyncBankAccountResponse(BaseModel):
    """Response nach BankAccount Sync."""
    success: bool
    bank_account_id: uuid.UUID
    sevdesk_check_account_id: Optional[str] = None
    message: str
    synced_at: Optional[datetime] = None


class SevDeskSyncTransactionsRequest(BaseModel):
    """Request zum Pullen von Transaktionen von SevDesk."""
    check_account_id: Optional[str] = Field(
        default=None,
        description="SevDesk CheckAccount ID (optional, alle wenn nicht angegeben)"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Max. Anzahl zu synchronisierender Transaktionen"
    )


class SevDeskSyncTransactionsResponse(BaseModel):
    """Response nach Transaction Sync."""
    success: bool
    total: int
    imported: int
    skipped: int
    errors: list[str] = []


class SevDeskSyncAllRequest(BaseModel):
    """Request für vollständige bidirektionale Synchronisation."""
    sync_invoices: bool = Field(
        default=True,
        description="Rechnungen synchronisieren"
    )
    sync_bank_accounts: bool = Field(
        default=True,
        description="Bankkonten synchronisieren"
    )
    sync_transactions: bool = Field(
        default=True,
        description="Transaktionen synchronisieren"
    )
    sync_payments: bool = Field(
        default=True,
        description="Zahlungen von SevDesk pullen"
    )


class SevDeskSyncAllResponse(BaseModel):
    """Response nach vollständiger Synchronisation."""
    success: bool
    invoices_synced: int = 0
    bank_accounts_synced: int = 0
    transactions_synced: int = 0
    payments_synced: int = 0
    errors: list[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None


class SevDeskInvoiceMappingRead(BaseModel):
    """Response für Invoice Mapping."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    invoice_id: uuid.UUID
    sevdesk_invoice_id: str
    last_synced_at: Optional[datetime]
    sync_status: str
    sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime


class SevDeskBankAccountMappingRead(BaseModel):
    """Response für BankAccount Mapping."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bank_account_id: uuid.UUID
    sevdesk_check_account_id: str
    last_synced_at: Optional[datetime]
    sync_status: str
    sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime


class SevDeskSyncHistoryRead(BaseModel):
    """Response für Sync History."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sync_type: str
    direction: str
    status: str
    records_processed: int
    records_success: int
    records_failed: int
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class SevDeskSyncHistoryListResponse(BaseModel):
    """Liste von Sync History Einträgen."""
    items: list[SevDeskSyncHistoryRead]
    total: int


# ============================================================================
# PAYMENT SYNC SCHEMAS
# ============================================================================

class SevDeskSyncPaymentsRequest(BaseModel):
    """Request für Payment-Synchronisation von SevDesk."""
    invoice_id: Optional[uuid.UUID] = Field(
        None,
        description="Optionale Invoice ID - nur für diese Rechnung synchronisieren"
    )
    sync_all: bool = Field(
        default=True,
        description="Alle gemappten Invoices synchronisieren"
    )


class SevDeskPaymentDetail(BaseModel):
    """Details einer synchronisierten Zahlung."""
    invoice_id: uuid.UUID
    invoice_number: str
    sevdesk_invoice_id: str
    sevdesk_paid_amount: float
    workmate_paid_amount: float
    payment_created: bool
    payment_id: Optional[uuid.UUID]
    payment_amount: Optional[float]
    new_invoice_status: Optional[str]


class SevDeskSyncPaymentsResponse(BaseModel):
    """Response für Payment-Synchronisation."""
    success: bool
    total_invoices_checked: int
    payments_created: int
    payments_updated: int
    invoices_status_updated: int
    details: list[SevDeskPaymentDetail]
    errors: list[str] = Field(default_factory=list)


# ============================================================================
# STRIPE PAYMENT INTEGRATION SCHEMAS
# ============================================================================

class StripeConfigRequest(BaseModel):
    """Request für Stripe Konfiguration."""
    publishable_key: str = Field(
        min_length=10,
        description="Stripe Publishable Key (pk_test_... oder pk_live_...)"
    )
    secret_key: str = Field(
        min_length=10,
        description="Stripe Secret Key (sk_test_... oder sk_live_...)"
    )
    webhook_secret: Optional[str] = Field(
        default=None,
        description="Stripe Webhook Signing Secret (whsec_...)"
    )
    test_mode: bool = Field(
        default=True,
        description="Test Mode (true) oder Live Mode (false)"
    )


class StripeConfigResponse(BaseModel):
    """Response mit Stripe Konfigurationsstatus."""
    id: str
    configured: bool
    test_mode: bool
    is_active: bool
    created_at: str
    updated_at: str


class StripePaymentIntentRequest(BaseModel):
    """Request für Payment Intent Erstellung."""
    invoice_id: uuid.UUID = Field(
        description="Invoice ID für die Zahlung"
    )


class StripePaymentIntentResponse(BaseModel):
    """Response nach Payment Intent Erstellung."""
    success: bool
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str
    invoice_id: str
    invoice_number: str


class StripePaymentLinkRequest(BaseModel):
    """Request für Payment Link Erstellung."""
    invoice_id: uuid.UUID = Field(
        description="Invoice ID für die Zahlung"
    )


class StripePaymentLinkResponse(BaseModel):
    """Response nach Payment Link Erstellung."""
    success: bool
    payment_link_id: str
    payment_url: str
    amount: float
    currency: str
    invoice_id: str
    invoice_number: str
