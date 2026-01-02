# app/modules/backoffice/products/schemas.py
"""
Products & Services Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid


# ============================================================================
# ENUMS (matching models)
# ============================================================================

from app.modules.backoffice.products.models import PriceType, ProductCategory


# ============================================================================
# PRODUCTS
# ============================================================================

class ProductBase(BaseModel):
    """Base Schema für Products."""
    name: str = Field(..., min_length=1, max_length=200, description="Produktname")
    description: Optional[str] = Field(None, description="Ausführliche Beschreibung")
    short_description: Optional[str] = Field(None, max_length=500, description="Kurzbeschreibung")
    sku: Optional[str] = Field(None, max_length=50, description="SKU/Artikelnummer")
    category: ProductCategory = Field(ProductCategory.OTHER, description="Kategorie")
    is_active: bool = Field(True, description="Aktiv?")
    is_service: bool = Field(True, description="Ist eine Dienstleistung?")
    price_type: PriceType = Field(PriceType.FIXED, description="Preistyp")
    unit_price: Decimal = Field(..., ge=0, description="Preis pro Einheit (€)")
    unit: str = Field("Stück", max_length=50, description="Einheit")
    default_tax_rate: Decimal = Field(Decimal("19.00"), ge=0, le=100, description="Standard-MwSt. (%)")
    min_quantity: Optional[Decimal] = Field(None, ge=0, description="Mindestmenge")
    max_quantity: Optional[Decimal] = Field(None, ge=0, description="Maximalmenge")
    internal_notes: Optional[str] = Field(None, description="Interne Notizen")


class ProductCreate(ProductBase):
    """Schema für Product Creation."""
    pass


class ProductUpdate(BaseModel):
    """Schema für Product Update (Partial)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, max_length=50)
    category: Optional[ProductCategory] = None
    is_active: Optional[bool] = None
    is_service: Optional[bool] = None
    price_type: Optional[PriceType] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    default_tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    min_quantity: Optional[Decimal] = Field(None, ge=0)
    max_quantity: Optional[Decimal] = Field(None, ge=0)
    internal_notes: Optional[str] = None


class ProductResponse(ProductBase):
    """Schema für Product Response."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema für Product List Response mit Pagination."""
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int
