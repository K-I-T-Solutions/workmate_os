# app/modules/backoffice/products/models.py
"""
Products & Services Models

Stammdatenverwaltung für wiederkehrende Produkte und Dienstleistungen.
"""
from sqlalchemy import String, Numeric, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin
from decimal import Decimal
import enum


class PriceType(str, enum.Enum):
    """Preistyp für Produkte/Dienstleistungen."""
    HOURLY = "hourly"           # Stundensatz (€/Std.)
    FIXED = "fixed"             # Pauschalpreis (€)
    MONTHLY = "monthly"         # Monatlicher Preis (€/Monat)
    PROJECT = "project"         # Projektbasis (ab €)
    PER_UNIT = "per_unit"       # Pro Einheit (z.B. pro System)


class ProductCategory(str, enum.Enum):
    """Kategorien für Produkte/Dienstleistungen."""
    PRIVATE_CUSTOMER = "private_customer"      # Privatkunden
    SMALL_BUSINESS = "small_business"          # Kleine Unternehmen
    ENTERPRISE = "enterprise"                  # Großkunden
    HARDWARE = "hardware"                      # Hardware-Produkte
    SOFTWARE = "software"                      # Software-Lizenzen
    CONSULTING = "consulting"                  # Beratungsleistungen
    SUPPORT = "support"                        # Support & Wartung
    DEVELOPMENT = "development"                # Entwicklungsleistungen
    OTHER = "other"                            # Sonstiges


class Product(Base, UUIDMixin, TimestampMixin):
    """
    Produkt/Dienstleistung Stammdaten.

    Verwendung:
    - Als Vorlage für Invoice Line Items
    - Preispflege an zentraler Stelle
    - Kategorisierung und Filterung
    """
    __tablename__ = "products"

    # Basis-Informationen
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Produktname/Dienstleistung"
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Ausführliche Beschreibung"
    )

    short_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Kurzbeschreibung für Rechnungen"
    )

    # SKU / Artikelnummer (optional)
    sku: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        comment="SKU / Artikelnummer"
    )

    # Kategorie & Status
    category: Mapped[ProductCategory] = mapped_column(
        SQLEnum(ProductCategory, native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProductCategory.OTHER,
        index=True,
        comment="Produktkategorie"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Aktiv/Inaktiv"
    )

    is_service: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Ist eine Dienstleistung (vs. Produkt)"
    )

    # Preis-Informationen
    price_type: Mapped[PriceType] = mapped_column(
        SQLEnum(PriceType, native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PriceType.FIXED,
        comment="Preistyp (Stundensatz, Pauschal, etc.)"
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Preis pro Einheit (€)"
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Stück",
        comment="Einheit (Stunde, Stück, Projekt, Monat, etc.)"
    )

    # Standard-MwSt.-Satz
    default_tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("19.00"),
        comment="Standard-Steuersatz (%)"
    )

    # Optionale Min/Max-Werte
    min_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Mindestmenge"
    )

    max_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Maximalmenge"
    )

    # Notizen (intern)
    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Interne Notizen (nicht auf Rechnung)"
    )

    def __repr__(self):
        return f"<Product {self.name} ({self.sku or self.id})>"
