# app/modules/backoffice/assets/schemas.py
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

AssetTypeLiteral = Literal[
    "workstation", "laptop", "server", "network", "storage",
    "printer", "phone", "mobile", "peripheral", "other",
]
AssetStatusLiteral = Literal["active", "in_repair", "in_stock", "retired"]
LicenseTypeLiteral = Literal["subscription", "perpetual", "volume", "oem"]


# ─── Geräte ──────────────────────────────────────────────────

class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    asset_type: AssetTypeLiteral = "workstation"
    status: AssetStatusLiteral = "active"
    customer_id: uuid.UUID
    contact_id: Optional[uuid.UUID] = None
    contract_id: Optional[uuid.UUID] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=150)
    serial_number: Optional[str] = Field(None, max_length=100)
    hostname: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)
    mac_address: Optional[str] = Field(None, max_length=17)
    operating_system: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    warranty_until: Optional[date] = None
    notes: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    asset_type: Optional[AssetTypeLiteral] = None
    status: Optional[AssetStatusLiteral] = None
    contact_id: Optional[uuid.UUID] = None
    contract_id: Optional[uuid.UUID] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=150)
    serial_number: Optional[str] = Field(None, max_length=100)
    hostname: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)
    mac_address: Optional[str] = Field(None, max_length=17)
    operating_system: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    warranty_until: Optional[date] = None
    notes: Optional[str] = None


class AssetResponse(AssetBase):
    id: uuid.UUID
    asset_tag: str
    customer_name: Optional[str] = None
    contract_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    skip: int
    limit: int


# ─── Lizenzen ────────────────────────────────────────────────

class LicenseBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200)
    vendor: Optional[str] = Field(None, max_length=100)
    license_type: LicenseTypeLiteral = "subscription"
    customer_id: uuid.UUID
    asset_id: Optional[uuid.UUID] = None
    contract_id: Optional[uuid.UUID] = None
    license_key: Optional[str] = None
    seats: int = Field(1, ge=1)
    seats_used: Optional[int] = Field(None, ge=0)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    auto_renew: bool = False
    cost_price: Optional[Decimal] = Field(None, ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=200)
    vendor: Optional[str] = Field(None, max_length=100)
    license_type: Optional[LicenseTypeLiteral] = None
    asset_id: Optional[uuid.UUID] = None
    contract_id: Optional[uuid.UUID] = None
    license_key: Optional[str] = None
    seats: Optional[int] = Field(None, ge=1)
    seats_used: Optional[int] = Field(None, ge=0)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    auto_renew: Optional[bool] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class LicenseResponse(LicenseBase):
    id: uuid.UUID
    customer_name: Optional[str] = None
    asset_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LicenseListResponse(BaseModel):
    items: list[LicenseResponse]
    total: int
    skip: int
    limit: int


# ─── Ablaufüberwachung ───────────────────────────────────────

class ExpiringItem(BaseModel):
    kind: Literal["warranty", "license"]
    id: uuid.UUID
    name: str
    customer_id: uuid.UUID
    customer_name: Optional[str] = None
    expires_on: date
    days_left: int
    auto_renew: bool = False


class ExpiringResponse(BaseModel):
    within_days: int
    items: list[ExpiringItem]
