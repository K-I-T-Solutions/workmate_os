# app/modules/backoffice/crm/models.py
"""
WorkmateOS - Backoffice CRM Models
Customer Relationship Management entities
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.projects.models import Project
    from app.modules.backoffice.invoices.models import Invoice


class Customer(Base, UUIDMixin, TimestampMixin):
    """
    Represents a client or organization.
    
    A customer can have multiple contacts, projects, and invoices.
    """
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_name", "name"),
        Index("ix_customers_email", "email"),
        Index("ix_customers_tax_id", "tax_id"),
        Index("ix_customers_status", "status"),
    )

    # Basic Info
    name: Mapped[str] = mapped_column(
        String(255),
        comment="Kundenname / Firmenname"
    )
    type: Mapped[str | None] = mapped_column(
        String(50),
        comment="Kundentyp: business, individual, government"
    )
    
    # Contact Info
    email: Mapped[str | None] = mapped_column(
        String(255),
        comment="Haupt-E-Mail Adresse"
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        comment="Telefonnummer"
    )
    website: Mapped[str | None] = mapped_column(
        String(255),
        comment="Webseite"
    )
    
    # Business Info
    tax_id: Mapped[str | None] = mapped_column(
        String(100),
        comment="Steuernummer / USt-IdNr"
    )
    
    # Address
    street: Mapped[str | None] = mapped_column(
        String(255),
        comment="Straße und Hausnummer"
    )
    zip_code: Mapped[str | None] = mapped_column(
        String(20),
        comment="Postleitzahl"
    )
    city: Mapped[str | None] = mapped_column(
        String(100),
        comment="Stadt"
    )
    country: Mapped[str | None] = mapped_column(
        String(100),
        comment="Land"
    )
    
    # Additional
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment="Interne Notizen"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        server_default="active",
        comment="Status: active, inactive, lead, blocked"
    )

    # Relationships
    contacts: Mapped[list[Contact]] = relationship(
        "Contact",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    projects: Mapped[list[Project]] = relationship(
        "Project",
        back_populates="customer",
        cascade="all, delete-orphan"
    )
    invoices: Mapped[list[Invoice]] = relationship(
        "Invoice",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    @property
    def full_address(self) -> str | None:
        """
        Gibt vollständige Adresse als String zurück.
        
        Returns:
            Formatierte Adresse oder None
        """
        parts = [
            self.street,
            f"{self.zip_code} {self.city}" if self.zip_code and self.city else self.city,
            self.country
        ]
        address_parts = [p for p in parts if p]
        return ", ".join(address_parts) if address_parts else None

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name='{self.name}')>"


class Contact(Base, UUIDMixin, TimestampMixin):
    """
    Represents a contact person associated with a customer.
    
    Each contact belongs to exactly one customer.
    """
    __tablename__ = "contacts"
    __table_args__ = (
        Index("ix_contacts_customer_id", "customer_id"),
        Index("ix_contacts_email", "email"),
        Index("ix_contacts_is_primary", "customer_id", "is_primary"),
    )

    # Foreign Key
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        comment="Zugehöriger Kunde"
    )
    
    # Personal Info
    firstname: Mapped[str] = mapped_column(
        String(100),
        comment="Vorname"
    )
    lastname: Mapped[str] = mapped_column(
        String(100),
        comment="Nachname"
    )
    
    # Contact Info
    email: Mapped[str | None] = mapped_column(
        String(255),
        comment="E-Mail Adresse"
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        comment="Telefonnummer"
    )
    mobile: Mapped[str | None] = mapped_column(
        String(50),
        comment="Mobilnummer"
    )
    
    # Position
    position: Mapped[str | None] = mapped_column(
        String(100),
        comment="Position im Unternehmen"
    )
    department: Mapped[str | None] = mapped_column(
        String(100),
        comment="Abteilung"
    )
    
    # Additional
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment="Notizen zum Kontakt"
    )
    is_primary: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        comment="Hauptansprechpartner für diesen Kunden"
    )

    # Relationship
    customer: Mapped[Customer] = relationship(
        "Customer",
        back_populates="contacts"
    )

    @property
    def full_name(self) -> str:
        """
        Gibt vollständigen Namen zurück.
        
        Returns:
            Vorname + Nachname
        """
        return f"{self.firstname} {self.lastname}"

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.full_name}')>"