# app/modules/backoffice/contracts/models.py
"""
WorkmateOS - Verträge & Abos (v5.0)

Wartungsverträge, Managed Services und Abos mit wiederkehrender Abrechnung.
Fällige Verträge erzeugen Rechnungs-ENTWÜRFE (siehe billing.py), die
manuell geprüft und versendet werden.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampMixin, UUIDMixin
from app.core.settings.database import Base

if TYPE_CHECKING:
    from app.modules.backoffice.crm.models import Customer


class ContractType(str, Enum):
    MAINTENANCE = "maintenance"          # Wartungsvertrag
    MANAGED_SERVICE = "managed_service"  # Managed Service
    SUBSCRIPTION = "subscription"        # Abo (z.B. Software, Backup)
    HOSTING = "hosting"
    LICENSE = "license"                  # Lizenz-Weiterverkauf
    OTHER = "other"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"   # gekündigt – läuft bis end_date
    EXPIRED = "expired"


class BillingInterval(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    YEARLY = "yearly"


# Monate pro Abrechnungsintervall
INTERVAL_MONTHS: dict[str, int] = {
    BillingInterval.MONTHLY.value: 1,
    BillingInterval.QUARTERLY.value: 3,
    BillingInterval.SEMIANNUAL.value: 6,
    BillingInterval.YEARLY.value: 12,
}


class Contract(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contracts"
    __table_args__ = (
        Index("ix_contracts_customer_id", "customer_id"),
        Index("ix_contracts_status", "status"),
        Index("ix_contracts_next_billing_date", "next_billing_date"),
    )

    contract_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    contract_type: Mapped[str] = mapped_column(String(30), default=ContractType.MAINTENANCE.value, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=ContractStatus.DRAFT.value, nullable=False)

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False
    )

    # Laufzeit
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, comment="Leer = unbefristet")
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    renewal_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False, comment="Verlängerung bei auto_renew")
    notice_period_days: Mapped[int] = mapped_column(Integer, default=90, nullable=False, comment="Kündigungsfrist in Tagen")

    # Abrechnung (Vorauszahlung: Rechnung zu Beginn des Zeitraums)
    billing_interval: Mapped[str] = mapped_column(String(20), default=BillingInterval.MONTHLY.value, nullable=False)
    next_billing_date: Mapped[Optional[date]] = mapped_column(Date, comment="Beginn des nächsten abzurechnenden Zeitraums")
    last_billed_date: Mapped[Optional[date]] = mapped_column(Date)
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=14, nullable=False)

    # Stundenkontingent (z.B. Wartungsvertrag mit 5 Std./Monat inklusive)
    included_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), comment="Inklusiv-Stunden pro Abrechnungszeitraum")

    notes: Mapped[Optional[str]] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship("Customer")
    items: Mapped[list["ContractItem"]] = relationship(
        "ContractItem", back_populates="contract", cascade="all, delete-orphan",
        order_by="ContractItem.position",
    )

    @property
    def customer_name(self) -> Optional[str]:
        return self.customer.name if self.customer else None

    @property
    def net_amount_per_period(self) -> Decimal:
        return sum((i.net_amount for i in self.items), Decimal("0.00"))

    @property
    def monthly_recurring_revenue(self) -> Decimal:
        months = INTERVAL_MONTHS.get(self.billing_interval, 1)
        return (self.net_amount_per_period / months).quantize(Decimal("0.01"))

    def __repr__(self) -> str:
        return f"<Contract({self.contract_number}, status={self.status})>"


class ContractItem(Base, UUIDMixin):
    """Position eines Vertrags – wird pro Zeitraum als Rechnungsposition übernommen."""
    __tablename__ = "contract_items"
    __table_args__ = (Index("ix_contract_items_contract_id", "contract_id"),)

    contract_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    position: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="Monat", nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("19.00"), nullable=False)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)

    contract: Mapped[Contract] = relationship("Contract", back_populates="items")

    @property
    def net_amount(self) -> Decimal:
        gross = Decimal(self.quantity) * Decimal(self.unit_price)
        discount = gross * Decimal(self.discount_percent or 0) / Decimal("100")
        return (gross - discount).quantize(Decimal("0.01"))
