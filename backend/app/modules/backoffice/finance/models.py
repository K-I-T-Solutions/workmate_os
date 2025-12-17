# app/modules/backoffice/finance/models.py
"""
Finance Module Models - WorkmateOS Phase 2.

Verwaltet:
- Expenses (Ausgaben/Kosten für Projekte)
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Numeric,
    Index,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.projects.models import Project
    from app.modules.backoffice.invoices.models import Invoice


class ExpenseCategory(str, Enum):
    """Kategorien für Ausgaben."""
    TRAVEL = "travel"
    MATERIAL = "material"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    CONSULTING = "consulting"
    MARKETING = "marketing"
    OFFICE = "office"
    TRAINING = "training"
    OTHER = "other"


class Expense(Base, UUIDMixin, TimestampMixin):
    """
    Ausgaben und Kosten.

    Verwaltet projektbezogene oder allgemeine Ausgaben mit
    Kategorisierung und optionaler Zuordnung zu Rechnungen.

    Attributes:
        category: Ausgabenkategorie (travel, material, software, etc.)
        amount: Ausgabenbetrag
        description: Beschreibung der Ausgabe
        receipt_path: Pfad zum Beleg/Quittung
        project: Optional zugehöriges Projekt
        invoice: Optional zugehörige Rechnung (wenn bereits abgerechnet)
        note: Zusätzliche Notizen
    """
    __tablename__ = "expenses"
    __table_args__ = (
        Index("ix_expenses_project_id", "project_id"),
        Index("ix_expenses_invoice_id", "invoice_id"),
        Index("ix_expenses_category", "category"),
        Index("ix_expenses_created_at", "created_at"),
        CheckConstraint("amount > 0", name="check_expense_amount_positive"),
    )

    # Business Fields
    title : Mapped[str] = mapped_column(
        String(50),
        comment="Bezeichnung der kosten"
    )
    category: Mapped[str] = mapped_column(
        String(50),
        comment="Ausgabenkategorie (travel, material, software, etc.)"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Ausgabenbetrag"
    )
    description: Mapped[str] = mapped_column(
        Text,
        comment="Beschreibung der Ausgabe"
    )
    receipt_path: Mapped[str | None] = mapped_column(
        Text,
        comment="Pfad zum Beleg/Quittung (PDF, Bild)"
    )
    note: Mapped[str | None] = mapped_column(
        Text,
        comment="Zusätzliche Notizen"
    )
    is_billable: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
        comment="Kann an Kunden weiterberechnet werden"
    )

    # Foreign Keys
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        comment="Optional zugehöriges Projekt"
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("invoices.id", ondelete="SET NULL"),
        comment="Optional zugehörige Rechnung (wenn bereits abgerechnet)"
    )

    # Relationships
    project: Mapped[Project | None] = relationship(
        "Project",
        back_populates="expenses"
    )
    invoice: Mapped[Invoice | None] = relationship(
        "Invoice",
        back_populates="expenses"
    )

    @property
    def is_invoiced(self) -> bool:
        """
        Prüft ob Ausgabe bereits abgerechnet wurde.

        Returns:
            True wenn eine Rechnung zugeordnet ist
        """
        return self.invoice_id is not None

    def __repr__(self) -> str:
        return (
            f"<Expense(category='{self.category}', "
            f"amount={self.amount}, "
            f"invoiced={self.is_invoiced})>"
        )
