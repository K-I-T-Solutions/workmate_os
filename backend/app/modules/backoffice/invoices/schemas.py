# app/modules/backoffice/invoices/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel
import uuid


# === ENUMS (for frontend compatibility) ===
class InvoiceStatus(str):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    SEPA = "sepa"
    OTHER = "other"


# === LINE ITEMS ===
class InvoiceLineItemBase(BaseModel):
    position: int = 1
    description: str
    quantity: Decimal = Decimal("1.00")
    unit: str = "Stück"
    unit_price: Decimal
    tax_rate: Decimal = Decimal("19.00")
    discount_percent: Decimal = Decimal("0.00")


class InvoiceLineItemCreate(InvoiceLineItemBase):
    pass


class InvoiceLineItemResponse(InvoiceLineItemBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


# === PAYMENTS ===
class PaymentBase(BaseModel):
    amount: Decimal
    payment_date: Optional[date] = None
    method: Optional[str] = "bank_transfer"
    reference: Optional[str] = None
    note: Optional[str] = None


class PaymentCreate(PaymentBase):
    invoice_id: uuid.UUID


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === INVOICES ===
class InvoiceBase(BaseModel):
    invoice_number: str
    issued_date: Optional[date] = None
    due_date: Optional[date] = None
    customer_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    status: Optional[str] = InvoiceStatus.DRAFT
    notes: Optional[str] = None
    terms: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    line_items: List[InvoiceLineItemCreate] = []


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    total: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    created_at: datetime
    updated_at: datetime
    line_items: List[InvoiceLineItemResponse] = []
    payments: List[PaymentResponse] = []

    class Config:
        from_attributes = True
