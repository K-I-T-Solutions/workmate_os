# app/modules/backoffice/assets/models.py
"""
WorkmateOS - Kunden-Assets (v5.0)

Hardware beim Kunden (Geräte) und Software-Lizenzen inkl. Garantie- und
Ablaufüberwachung. Optional einem Wartungsvertrag zugeordnet.
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
    from app.modules.backoffice.contracts.models import Contract
    from app.modules.backoffice.crm.models import Contact, Customer


class AssetType(str, Enum):
    WORKSTATION = "workstation"
    LAPTOP = "laptop"
    SERVER = "server"
    NETWORK = "network"        # Switch, Router, Firewall, AP
    STORAGE = "storage"        # NAS, SAN
    PRINTER = "printer"
    PHONE = "phone"
    MOBILE = "mobile"
    PERIPHERAL = "peripheral"
    OTHER = "other"


class AssetStatus(str, Enum):
    ACTIVE = "active"
    IN_REPAIR = "in_repair"
    IN_STOCK = "in_stock"
    RETIRED = "retired"


class LicenseType(str, Enum):
    SUBSCRIPTION = "subscription"
    PERPETUAL = "perpetual"
    VOLUME = "volume"
    OEM = "oem"


class CustomerAsset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customer_assets"
    __table_args__ = (
        Index("ix_customer_assets_customer_id", "customer_id"),
        Index("ix_customer_assets_serial_number", "serial_number"),
        Index("ix_customer_assets_warranty_until", "warranty_until"),
    )

    asset_tag: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(30), default=AssetType.WORKSTATION.value, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=AssetStatus.ACTIVE.value, nullable=False)

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"), comment="Nutzer / Ansprechpartner"
    )
    contract_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("contracts.id", ondelete="SET NULL"), comment="Durch Wartungsvertrag abgedeckt"
    )

    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(150))
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Netzwerk / System
    hostname: Mapped[Optional[str]] = mapped_column(String(100))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    mac_address: Mapped[Optional[str]] = mapped_column(String(17))
    operating_system: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(200))

    # Lebenszyklus
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    warranty_until: Mapped[Optional[date]] = mapped_column(Date)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship("Customer")
    contact: Mapped[Optional["Contact"]] = relationship("Contact")
    contract: Mapped[Optional["Contract"]] = relationship("Contract")
    licenses: Mapped[list["SoftwareLicense"]] = relationship("SoftwareLicense", back_populates="asset")

    @property
    def customer_name(self) -> Optional[str]:
        return self.customer.name if self.customer else None

    @property
    def contract_number(self) -> Optional[str]:
        return self.contract.contract_number if self.contract else None


class SoftwareLicense(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "software_licenses"
    __table_args__ = (
        Index("ix_software_licenses_customer_id", "customer_id"),
        Index("ix_software_licenses_valid_until", "valid_until"),
    )

    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    vendor: Mapped[Optional[str]] = mapped_column(String(100))
    license_type: Mapped[str] = mapped_column(String(20), default=LicenseType.SUBSCRIPTION.value, nullable=False)

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("customer_assets.id", ondelete="SET NULL"), comment="Optional an ein Gerät gebunden"
    )
    contract_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("contracts.id", ondelete="SET NULL"), comment="Abrechnung über Vertrag"
    )

    license_key: Mapped[Optional[str]] = mapped_column(Text, comment="Nur intern sichtbar")
    seats: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    seats_used: Mapped[Optional[int]] = mapped_column(Integer)

    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, comment="Leer = unbefristet")
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="Einkauf pro Zeitraum")
    sale_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="Verkauf pro Zeitraum")

    notes: Mapped[Optional[str]] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship("Customer")
    asset: Mapped[Optional[CustomerAsset]] = relationship("CustomerAsset", back_populates="licenses")
    contract: Mapped[Optional["Contract"]] = relationship("Contract")

    @property
    def customer_name(self) -> Optional[str]:
        return self.customer.name if self.customer else None

    @property
    def asset_name(self) -> Optional[str]:
        return self.asset.name if self.asset else None
