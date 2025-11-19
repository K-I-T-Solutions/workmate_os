# app/modules/backoffice/invoices/schemas.py
"""
WorkmateOS - Invoices Schemas (IMPROVED)

CHANGES:
- ✅ Pydantic Validators (date validation, amount validation)
- ✅ Computed Fields (is_overdue, outstanding_amount)
- ✅ Filter Schemas
- ✅ Bulk Operation Schemas
- ✅ Pagination Response
- ✅ Statistics Response
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, computed_field
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class InvoiceStatus:
    """Invoice Status Constants."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod:
    """Payment Method Constants."""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    SEPA = "sepa"
    OTHER = "other"


# ============================================================================
# LINE ITEMS
# ============================================================================

class InvoiceLineItemBase(BaseModel):
    """Base Schema für Invoice Line Items."""
    position: int = Field(1, ge=1, description="Sortierungsreihenfolge")
    description: str = Field(..., min_length=1, max_length=1000, description="Leistungsbeschreibung")
    quantity: Decimal = Field(Decimal("1.00"), gt=0, description="Menge/Anzahl")
    unit: str = Field("Stück", max_length=50, description="Einheit")
    unit_price: Decimal = Field(..., ge=0, description="Einzelpreis netto")
    tax_rate: Decimal = Field(Decimal("19.00"), ge=0, le=100, description="MwSt-Satz in Prozent")
    discount_percent: Decimal = Field(Decimal("0.00"), ge=0, le=100, description="Rabatt in Prozent")

    @field_validator("quantity", "unit_price", "tax_rate", "discount_percent", mode="before")
    @classmethod
    def convert_to_decimal(cls, v):
        """Konvertiert Strings zu Decimal."""
        if isinstance(v, str):
            return Decimal(v)
        return v


class InvoiceLineItemCreate(InvoiceLineItemBase):
    """Schema für Line Item Creation."""
    pass


class InvoiceLineItemResponse(InvoiceLineItemBase):
    """Schema für Line Item Response."""
    id: uuid.UUID

    # Computed fields (from model properties)
    subtotal: Decimal = Field(description="Zwischensumme ohne Rabatt")
    discount_amount: Decimal = Field(description="Rabattbetrag")
    subtotal_after_discount: Decimal = Field(description="Zwischensumme nach Rabatt")
    tax_amount: Decimal = Field(description="MwSt-Betrag")
    total: Decimal = Field(description="Gesamtbetrag inkl. MwSt")

    class Config:
        from_attributes = True


# ============================================================================
# PAYMENTS
# ============================================================================

class PaymentBase(BaseModel):
    """Base Schema für Payments."""
    amount: Decimal = Field(..., gt=0, description="Zahlungsbetrag")
    payment_date: Optional[date] = Field(None, description="Datum des Zahlungseingangs")
    method: Optional[str] = Field("bank_transfer", description="Zahlungsmethode")
    reference: Optional[str] = Field(None, max_length=100, description="Buchungsreferenz")
    note: Optional[str] = Field(None, max_length=1000, description="Interne Notiz")

    @field_validator("amount", mode="before")
    @classmethod
    def convert_amount_to_decimal(cls, v):
        """Konvertiert String zu Decimal."""
        if isinstance(v, str):
            return Decimal(v)
        return v


class PaymentCreate(PaymentBase):
    """Schema für Payment Creation."""
    pass  # invoice_id wird als URL param übergeben


class PaymentUpdate(BaseModel):
    """Schema für Payment Update."""
    amount: Optional[Decimal] = None
    payment_date: Optional[date] = None
    method: Optional[str] = None
    reference: Optional[str] = None
    note: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Schema für Payment Response."""
    id: uuid.UUID
    invoice_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CUSTOMER (Nested Response)
# ============================================================================

class CustomerBriefResponse(BaseModel):
    """Kurze Customer-Info für Invoice Response."""
    id: uuid.UUID
    name: str
    email: Optional[str] = None
    city: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# INVOICES
# ============================================================================

class InvoiceBase(BaseModel):
    """Base Schema für Invoices."""
    invoice_number: str = Field(..., min_length=1, max_length=50, description="Rechnungsnummer")
    issued_date: Optional[date] = Field(None, description="Rechnungsdatum")
    due_date: Optional[date] = Field(None, description="Fälligkeitsdatum")
    customer_id: uuid.UUID = Field(..., description="Zugehöriger Kunde")
    project_id: Optional[uuid.UUID] = Field(None, description="Optional zugehöriges Projekt")
    status: Optional[str] = Field(InvoiceStatus.DRAFT, description="Status")
    notes: Optional[str] = Field(None, max_length=5000, description="Interne Notizen")
    terms: Optional[str] = Field(None, max_length=5000, description="Zahlungsbedingungen")

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v, info):
        """Fälligkeitsdatum muss nach Rechnungsdatum liegen."""
        if v and info.data.get("issued_date") and v < info.data["issued_date"]:
            raise ValueError("due_date must be after or equal to issued_date")
        return v


class InvoiceCreate(InvoiceBase):
    """Schema für Invoice Creation."""
    line_items: List[InvoiceLineItemCreate] = Field(
        default_factory=list,
        min_length=1,
        description="Mindestens 1 Line Item erforderlich"
    )


class InvoiceUpdate(BaseModel):
    """Schema für Invoice Update (Partial)."""
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=5000)
    terms: Optional[str] = Field(None, max_length=5000)


class InvoiceStatusUpdate(BaseModel):
    """Schema für Status-Update."""
    status: str = Field(..., description="Neuer Status")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Status muss gültig sein."""
        valid_statuses = [
            InvoiceStatus.DRAFT,
            InvoiceStatus.SENT,
            InvoiceStatus.PAID,
            InvoiceStatus.PARTIAL,
            InvoiceStatus.OVERDUE,
            InvoiceStatus.CANCELLED
        ]
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v


class InvoiceResponse(InvoiceBase):
    """Schema für Invoice Response."""
    id: uuid.UUID
    total: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    created_at: datetime
    updated_at: datetime
    pdf_path: Optional[str] = None

    # Relations
    customer: CustomerBriefResponse
    line_items: List[InvoiceLineItemResponse] = []
    payments: List[PaymentResponse] = []

    # Computed fields (from model properties)
    paid_amount: Decimal = Field(description="Summe aller Zahlungen")
    outstanding_amount: Decimal = Field(description="Offener Betrag")
    is_paid: bool = Field(description="Vollständig bezahlt?")
    is_overdue: bool = Field(description="Überfällig?")

    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION & LISTS
# ============================================================================

class InvoiceListResponse(BaseModel):
    """Response für Invoice-Liste mit Pagination."""
    items: List[InvoiceResponse]
    total: int = Field(description="Gesamtanzahl (ohne Pagination)")
    skip: int = Field(description="Offset")
    limit: int = Field(description="Max Anzahl pro Seite")

    @computed_field
    @property
    def page(self) -> int:
        """Aktuelle Seite (1-basiert)."""
        return (self.skip // self.limit) + 1 if self.limit > 0 else 1

    @computed_field
    @property
    def pages(self) -> int:
        """Gesamtanzahl Seiten."""
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 1


# ============================================================================
# STATISTICS
# ============================================================================

class InvoiceStatisticsResponse(BaseModel):
    """Statistiken über Invoices."""
    total_count: int = Field(description="Gesamtanzahl Invoices")
    total_revenue: Decimal = Field(description="Gesamtumsatz (paid)")
    outstanding_amount: Decimal = Field(description="Offene Forderungen")
    overdue_count: int = Field(description="Anzahl überfällige Rechnungen")
    draft_count: int = Field(description="Anzahl Entwürfe")
    sent_count: int = Field(description="Anzahl versendete")
    paid_count: int = Field(description="Anzahl bezahlte")
    cancelled_count: int = Field(description="Anzahl stornierte")


# ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkStatusUpdate(BaseModel):
    """Schema für Bulk Status Update."""
    invoice_ids: List[uuid.UUID] = Field(..., min_length=1, description="Liste von Invoice IDs")
    new_status: str = Field(..., description="Neuer Status")

    @field_validator("new_status")
    @classmethod
    def validate_status(cls, v):
        """Status muss gültig sein."""
        valid_statuses = [
            InvoiceStatus.DRAFT,
            InvoiceStatus.SENT,
            InvoiceStatus.PAID,
            InvoiceStatus.PARTIAL,
            InvoiceStatus.OVERDUE,
            InvoiceStatus.CANCELLED
        ]
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v


class BulkUpdateResponse(BaseModel):
    """Response für Bulk Operations."""
    success_count: int = Field(description="Anzahl erfolgreich aktualisiert")
    failed_count: int = Field(description="Anzahl fehlgeschlagen")
    failed_ids: List[str] = Field(default_factory=list, description="IDs fehlgeschlagener Updates")


# ============================================================================
# FILTERS
# ============================================================================

class InvoiceFilterParams(BaseModel):
    """Query Parameters für Invoice Filtering."""
    status: Optional[str] = None
    customer_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)
