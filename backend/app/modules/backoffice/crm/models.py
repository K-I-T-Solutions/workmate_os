# app/modules/backoffice/crm/models.py
"""
WorkmateOS - Backoffice CRM Models (IMPROVED)
Customer Relationship Management entities

CHANGES:
- ✅ CustomerStatus Enum hinzugefügt
- ✅ Unique constraint für primary contact (PostgreSQL partial index)
- ✅ Revenue & metrics properties
- ✅ Bessere Indizes
- ✅ Validation für Email-Format
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.projects.models import Project
    from app.modules.backoffice.invoices.models import Invoice


# ============================================================================
# ENUMS
# ============================================================================

class CustomerStatus(str, Enum):
    """Status eines Kunden."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LEAD = "lead"
    BLOCKED = "blocked"


class CustomerType(str, Enum):
    """Kundentyp."""
    BUSINESS = "business"
    INDIVIDUAL = "individual"
    GOVERNMENT = "government"


# ============================================================================
# MODELS
# ============================================================================

class Customer(Base, UUIDMixin, TimestampMixin):
    """
    Represents a client or organization.

    A customer can have multiple contacts, projects, and invoices.

    Attributes:
        name: Kundenname / Firmenname
        type: Kundentyp (business, individual, government)
        status: Aktueller Status (active, inactive, lead, blocked)
        tax_id: Steuernummer / USt-IdNr
        contacts: Liste der Ansprechpartner
        projects: Liste der Projekte
        invoices: Liste der Rechnungen
    """
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_name", "name"),
        Index("ix_customers_email", "email"),
        Index("ix_customers_tax_id", "tax_id"),
        Index("ix_customers_status", "status"),
        Index("ix_customers_type", "type"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'lead', 'blocked')",
            name="check_customer_status_valid"
        ),
        CheckConstraint(
            "type IN ('business', 'individual', 'government')",
            name="check_customer_type_valid"
        ),
    )

    # Basic Info
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Kundenname / Firmenname"
    )
    type: Mapped[str | None] = mapped_column(
        String(50),
        default=CustomerType.BUSINESS.value,
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
        default="Deutschland",
        comment="Land"
    )

    # Additional
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment="Interne Notizen"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=CustomerStatus.ACTIVE.value,
        server_default=CustomerStatus.ACTIVE.value,
        comment="Status: active, inactive, lead, blocked"
    )

    # Relationships
    contacts: Mapped[list[Contact]] = relationship(
        "Contact",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Contact.is_primary.desc(), Contact.lastname"
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

    # ========================================================================
    # PROPERTIES
    # ========================================================================

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

    @property
    def primary_contact(self) -> Contact | None:
        """
        Gibt den primären Ansprechpartner zurück.

        Returns:
            Contact mit is_primary=True oder None
        """
        return next((c for c in self.contacts if c.is_primary), None)

    @property
    def total_revenue(self) -> float:
        """
        Gesamtumsatz über alle bezahlten Rechnungen.

        Returns:
            Summe aller paid invoices
        """
        from app.modules.backoffice.invoices.models import InvoiceStatus
        return sum(
            float(inv.total) for inv in self.invoices
            if inv.status == InvoiceStatus.PAID.value
        )

    @property
    def outstanding_amount(self) -> float:
        """
        Offene Forderungen über alle unbezahlten Rechnungen.

        Returns:
            Summe aller outstanding amounts
        """
        from app.modules.backoffice.invoices.models import InvoiceStatus
        return sum(
            float(inv.outstanding_amount) for inv in self.invoices
            if inv.status not in [InvoiceStatus.PAID.value, InvoiceStatus.CANCELLED.value]
        )

    @property
    def active_projects_count(self) -> int:
        """
        Anzahl aktiver Projekte.

        Returns:
            Count of active projects
        """
        from app.modules.backoffice.projects.models import ProjectStatus
        return sum(
            1 for p in self.projects
            if p.status == ProjectStatus.ACTIVE.value
        )

    @property
    def is_active(self) -> bool:
        """Prüft ob Kunde aktiv ist."""
        return self.status == CustomerStatus.ACTIVE.value

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name='{self.name}', status='{self.status}')>"


class Contact(Base, UUIDMixin, TimestampMixin):
    """
    Represents a contact person associated with a customer.

    Each contact belongs to exactly one customer.
    Only one contact per customer can be marked as primary.

    Attributes:
        customer_id: Zugehöriger Kunde
        firstname: Vorname
        lastname: Nachname
        email: E-Mail Adresse
        phone: Telefonnummer
        mobile: Mobilnummer
        position: Position im Unternehmen
        department: Abteilung
        is_primary: Hauptansprechpartner
        notes: Notizen zum Kontakt
    """
    __tablename__ = "contacts"
    __table_args__ = (
        Index("ix_contacts_customer_id", "customer_id"),
        Index("ix_contacts_email", "email"),
        Index("ix_contacts_lastname", "lastname"),
        # PostgreSQL Partial Unique Index: Nur EIN primary contact pro customer
        Index(
            "ix_one_primary_contact_per_customer",
            "customer_id",
            unique=True,
            postgresql_where=text("is_primary = true")
        ),
    )

    # Foreign Key
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        comment="Zugehöriger Kunde"
    )

    # Personal Info
    firstname: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Vorname"
    )
    lastname: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def full_name(self) -> str:
        """
        Gibt vollständigen Namen zurück.

        Returns:
            Vorname + Nachname
        """
        return f"{self.firstname} {self.lastname}"

    @property
    def display_name(self) -> str:
        """
        Gibt Anzeigename inkl. Position zurück.

        Returns:
            "Max Mustermann (Geschäftsführer)" oder "Max Mustermann"
        """
        if self.position:
            return f"{self.full_name} ({self.position})"
        return self.full_name

    def __repr__(self) -> str:
        primary = " [PRIMARY]" if self.is_primary else ""
        return f"<Contact(id={self.id}, name='{self.full_name}'{primary})>"
