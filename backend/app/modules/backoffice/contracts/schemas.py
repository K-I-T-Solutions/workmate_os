# app/modules/backoffice/contracts/schemas.py
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

ContractTypeLiteral = Literal["maintenance", "managed_service", "subscription", "hosting", "license", "other"]
ContractStatusLiteral = Literal["draft", "active", "paused", "cancelled", "expired"]
BillingIntervalLiteral = Literal["monthly", "quarterly", "semiannual", "yearly"]


# ─── Positionen ──────────────────────────────────────────────

class ContractItemBase(BaseModel):
    product_id: Optional[uuid.UUID] = None
    position: int = Field(1, ge=1)
    description: str = Field(..., min_length=1, max_length=1000)
    quantity: Decimal = Field(Decimal("1.00"), gt=0)
    unit: str = Field("Monat", max_length=50)
    unit_price: Decimal = Field(..., ge=0)
    tax_rate: Decimal = Field(Decimal("19.00"), ge=0, le=100)
    discount_percent: Decimal = Field(Decimal("0.00"), ge=0, le=100)


class ContractItemCreate(ContractItemBase):
    pass


class ContractItemResponse(ContractItemBase):
    id: uuid.UUID
    net_amount: Decimal
    model_config = ConfigDict(from_attributes=True)


# ─── Vertrag ─────────────────────────────────────────────────

class ContractBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    contract_type: ContractTypeLiteral = "maintenance"
    customer_id: uuid.UUID
    start_date: date
    end_date: Optional[date] = None
    auto_renew: bool = True
    renewal_months: int = Field(12, ge=1, le=60)
    notice_period_days: int = Field(90, ge=0, le=730)
    billing_interval: BillingIntervalLiteral = "monthly"
    payment_terms_days: int = Field(14, ge=0, le=120)
    included_hours: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _check_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date darf nicht vor start_date liegen")
        return self


class ContractCreate(ContractBase):
    status: ContractStatusLiteral = "draft"
    next_billing_date: Optional[date] = Field(None, description="Leer = start_date")
    items: list[ContractItemCreate] = Field(default_factory=list)


class ContractUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    contract_type: Optional[ContractTypeLiteral] = None
    status: Optional[ContractStatusLiteral] = None
    end_date: Optional[date] = None
    auto_renew: Optional[bool] = None
    renewal_months: Optional[int] = Field(None, ge=1, le=60)
    notice_period_days: Optional[int] = Field(None, ge=0, le=730)
    billing_interval: Optional[BillingIntervalLiteral] = None
    next_billing_date: Optional[date] = None
    payment_terms_days: Optional[int] = Field(None, ge=0, le=120)
    included_hours: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    items: Optional[list[ContractItemCreate]] = Field(None, description="Ersetzt alle Positionen")


class ContractResponse(ContractBase):
    id: uuid.UUID
    contract_number: str
    status: ContractStatusLiteral
    next_billing_date: Optional[date] = None
    last_billed_date: Optional[date] = None
    customer_name: Optional[str] = None
    net_amount_per_period: Decimal
    monthly_recurring_revenue: Decimal
    items: list[ContractItemResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ContractListResponse(BaseModel):
    items: list[ContractResponse]
    total: int
    skip: int
    limit: int


class ContractCancelRequest(BaseModel):
    end_date: date = Field(..., description="Vertragsende (letzter Leistungstag)")
    reason: Optional[str] = None


class ContractStatsResponse(BaseModel):
    active_contracts: int
    monthly_recurring_revenue: Decimal
    annual_recurring_revenue: Decimal
    due_for_billing: int
    notice_deadlines_30d: int


# ─── Abrechnungslauf ─────────────────────────────────────────

class BillingRunRequest(BaseModel):
    run_date: Optional[date] = Field(None, description="Stichtag, Standard: heute")


class BillingRunResponse(BaseModel):
    run_date: date
    invoices_created: list[dict]
    contracts_renewed: list[str]
    contracts_expired: list[str]
    errors: list[dict]
    notice_deadlines: list[dict] = []


class ContractInvoiceBrief(BaseModel):
    id: uuid.UUID
    invoice_number: str
    status: str
    issued_date: Optional[date] = None
    total: Decimal
    model_config = ConfigDict(from_attributes=True)
