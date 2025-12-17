# app/modules/backoffice/crm/schemas.py
"""
Pydantic Schemas für CRM Module.

Validierung und Serialisierung für Customer und Contact Models.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# === Customer Schemas ===

class CustomerBase(BaseModel):
    """Base schema für Customer."""
    name: str = Field(..., min_length=1, max_length=255, description="Kundenname")
    type: Optional[str] = Field(None, max_length=50, description="Kundentyp (business, individual, government)")
    email: Optional[EmailStr] = Field(None, description="E-Mail Adresse")
    phone: Optional[str] = Field(None, max_length=50, description="Telefonnummer")
    tax_id: Optional[str] = Field(None, max_length=100, description="Steuernummer/USt-IdNr")
    website: Optional[str] = Field(None, max_length=255, description="Webseite")
    notes: Optional[str] = Field(None, description="Interne Notizen")
    status: str = Field(default="active", description="Status (active, inactive, lead, blocked)")

    # Address Fields
    street: Optional[str] = Field(None, max_length=255, description="Straße und Hausnummer")
    zip_code: Optional[str] = Field(None, max_length=20, description="Postleitzahl")
    city: Optional[str] = Field(None, max_length=100, description="Stadt")
    country: Optional[str] = Field(None, max_length=100, description="Land")


class CustomerCreate(CustomerBase):
    """Schema für Customer Creation."""
    pass


class CustomerUpdate(BaseModel):
    """Schema für Customer Update (alle Felder optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    status: Optional[str] = None
    street: Optional[str] = Field(None, max_length=255)
    zip_code: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class CustomerResponse(CustomerBase):
    """Schema für Customer Response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# === Contact Schemas ===

class ContactBase(BaseModel):
    """Base schema für Contact."""
    customer_id: UUID = Field(..., description="Zugehöriger Kunde")
    firstname: str = Field(..., min_length=1, max_length=100, description="Vorname")
    lastname: str = Field(..., min_length=1, max_length=100, description="Nachname")
    email: Optional[EmailStr] = Field(None, description="E-Mail Adresse")
    phone: Optional[str] = Field(None, max_length=50, description="Telefonnummer")
    mobile: Optional[str] = Field(None, max_length=50, description="Mobilnummer")
    position: Optional[str] = Field(None, max_length=100, description="Position im Unternehmen")
    department: Optional[str] = Field(None, max_length=100, description="Abteilung")
    is_primary: bool = Field(default=False, description="Ist Hauptansprechpartner")
    notes: Optional[str] = Field(None, description="Notizen zum Kontakt")


class ContactCreate(ContactBase):
    """Schema für Contact Creation."""
    pass


class ContactUpdate(BaseModel):
    """Schema für Contact Update (alle Felder optional)."""
    customer_id: Optional[UUID] = None
    firstname: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = None
    notes: Optional[str] = None


class ContactResponse(ContactBase):
    """Schema für Contact Response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# === Extended Response Schemas (mit Relationships) ===

class ContactResponseSimple(BaseModel):
    """Vereinfachte Contact Response ohne Customer (verhindert circular imports)."""
    id: UUID
    firstname: str
    lastname: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    position: Optional[str] = None
    is_primary: bool

    model_config = ConfigDict(from_attributes=True)


class CustomerResponseWithContacts(CustomerResponse):
    """Customer Response mit allen Contacts."""
    contacts: list[ContactResponseSimple] = []

# === Activity Schemas ===

ALLOWED_TYPES = {"call", "email", "onsite", "remote", "note"}

class ActivityCreate(BaseModel):
    customer_id: UUID
    contact_id: UUID | None = None
    type: str = Field(..., description="call, email, onsite, remote, note")
    description: str = Field(..., min_length=1)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def validate_type(cls, v: str):
        if v not in ALLOWED_TYPES:
            raise ValueError(f"type must be one of {ALLOWED_TYPES}")
        return v

class ActivityResponse(BaseModel):
    id: UUID
    customer_id: UUID
    contact_id: UUID | None
    type: str
    description: str
    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# === CRM Stats ===
class CrmStatsResponse(BaseModel):
    total_customers: int
    active_customers: int
    leads: int
    blocked_customers: int

    total_revenue: float
    outstanding_revenue: float

    active_projects: int
