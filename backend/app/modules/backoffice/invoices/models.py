# app/modules/backoffice/invoices/models.py
"""
Invoices Module Models - WorkmateOS Phase 2.

Verwaltet:
- Invoices (Rechnungen & Angebote)
- InvoiceLineItems (Rechnungspositionen)
- Payments (Zahlungseingänge)
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Date,
    Numeric,
    func,
    Index,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.crm.models import Customer
    from app.modules.backoffice.projects.models import Project
    from app.modules.backoffice.finance.models import Expense


class InvoiceStatus(str, Enum):
    """Status einer Rechnung."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Zahlungsmethoden."""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    SEPA = "sepa"
    OTHER = "other"


class Invoice(Base, UUIDMixin, TimestampMixin):
    """
    Kundenrechnungen und Angebote.
    
    Verwaltet Rechnungen mit automatischer Berechnung von
    Gesamtbeträgen, Zahlungsstatus und Fälligkeiten.
    
    Attributes:
        invoice_number: Eindeutige Rechnungsnummer (z.B. "RE-2025-001")
        total: Gesamtbetrag inkl. MwSt
        status: Aktueller Status der Rechnung
        issued_date: Rechnungsdatum
        due_date: Fälligkeitsdatum
        customer: Zugehöriger Kunde
        project: Optional zugehöriges Projekt
        line_items: Rechnungspositionen
        payments: Zahlungseingänge
    """
    __tablename__ = "invoices"
    __table_args__ = (
        Index("ix_invoices_customer_id", "customer_id"),
        Index("ix_invoices_project_id", "project_id"),
        Index("ix_invoices_status", "status"),
        Index("ix_invoices_issued_date", "issued_date"),
        Index("ix_invoices_invoice_number", "invoice_number"),
        CheckConstraint("total >= 0", name="check_invoice_total_positive"),
    )

    # Business Fields
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="Eindeutige Rechnungsnummer (z.B. RE-2025-001)"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Gesamtbetrag inkl. MwSt"
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Zwischensumme ohne MwSt"
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        server_default="0.00",
        comment="MwSt-Betrag"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=InvoiceStatus.DRAFT.value,
        server_default=InvoiceStatus.DRAFT.value,
        comment="Status: draft, sent, paid, partial, overdue, cancelled"
    )

    # Dates
    issued_date: Mapped[date | None] = mapped_column(
        Date,
        comment="Rechnungsdatum"
    )
    due_date: Mapped[date | None] = mapped_column(
        Date,
        comment="Fälligkeitsdatum"
    )

    # Optional Fields
    pdf_path: Mapped[str | None] = mapped_column(
        Text,
        comment="Pfad zur generierten PDF-Rechnung"
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment="Interne Notizen"
    )
    terms: Mapped[str | None] = mapped_column(
        Text,
        comment="Zahlungsbedingungen und AGB"
    )

    # Foreign Keys
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        comment="Zugehöriger Kunde"
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        comment="Optional zugehöriges Projekt"
    )

    # Relationships
    customer: Mapped[Customer] = relationship(
        "Customer",
        back_populates="invoices"
    )
    project: Mapped[Project | None] = relationship(
        "Project",
        back_populates="invoices"
    )
    line_items: Mapped[list[InvoiceLineItem]] = relationship(
        "InvoiceLineItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceLineItem.position"
    )
    payments: Mapped[list[Payment]] = relationship(
        "Payment",
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="Payment.payment_date.desc()"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )


    @property
    def is_overdue(self) -> bool:
        """
        Prüft ob Rechnung überfällig ist.
        
        Returns:
            True wenn Fälligkeitsdatum überschritten und nicht vollständig bezahlt
        """
        if self.due_date is None or self.status == InvoiceStatus.PAID.value:
            return False
        from datetime import date
        return date.today() > self.due_date

    @property
    def paid_amount(self) -> Decimal:
        """
        Summe aller Zahlungseingänge.
        
        Returns:
            Gesamtbetrag aller Zahlungen
        """
        return sum((p.amount for p in self.payments), Decimal("0.00"))

    @property
    def outstanding_amount(self) -> Decimal:
        """
        Offener Betrag.
        
        Returns:
            Differenz zwischen Rechnungsbetrag und bezahltem Betrag
        """
        return self.total - self.paid_amount

    @property
    def is_paid(self) -> bool:
        """
        Prüft ob Rechnung vollständig bezahlt ist.
        
        Returns:
            True wenn kein offener Betrag mehr vorhanden
        """
        return self.outstanding_amount <= Decimal("0.00")

    def __repr__(self) -> str:
        return (
            f"<Invoice(number='{self.invoice_number}', "
            f"total={self.total}, status='{self.status}')>"
        )


class InvoiceLineItem(Base, UUIDMixin):
    """
    Rechnungspositionen.
    
    Einzelne Positionen einer Rechnung mit automatischer
    Berechnung von Zwischensummen, MwSt und Gesamtbeträgen.
    
    Attributes:
        position: Sortierungsreihenfolge in der Rechnung
        description: Leistungsbeschreibung
        quantity: Menge/Anzahl
        unit: Einheit (z.B. Stunden, Stück)
        unit_price: Einzelpreis netto
        tax_rate: MwSt-Satz in Prozent
        discount_percent: Rabatt in Prozent
    """
    __tablename__ = "invoice_line_items"
    __table_args__ = (
        Index("ix_invoice_line_items_invoice_id", "invoice_id"),
        Index("ix_invoice_line_items_position", "invoice_id", "position"),
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="check_unit_price_positive"),
        CheckConstraint("tax_rate >= 0", name="check_tax_rate_positive"),
        CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="check_discount_valid"
        ),
    )

    # Business Fields
    position: Mapped[int] = mapped_column(
        default=1,
        comment="Sortierungsreihenfolge"
    )
    description: Mapped[str] = mapped_column(
        Text,
        comment="Leistungsbeschreibung"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("1.00"),
        comment="Menge/Anzahl"
    )
    unit: Mapped[str] = mapped_column(
        String(50),
        default="Stück",
        server_default="Stück",
        comment="Einheit (z.B. Stunden, Stück, m²)"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Einzelpreis netto"
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("19.00"),
        server_default="19.00",
        comment="MwSt-Satz in Prozent"
    )
    discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Rabatt in Prozent"
    )

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        comment="Zugehörige Rechnung"
    )

    # Relationships
    invoice: Mapped[Invoice] = relationship(
        "Invoice",
        back_populates="line_items"
    )

    @property
    def subtotal(self) -> Decimal:
        """
        Zwischensumme ohne MwSt und ohne Rabatt.
        
        Returns:
            quantity * unit_price
        """
        return self.quantity * self.unit_price

    @property
    def discount_amount(self) -> Decimal:
        """
        Rabattbetrag.
        
        Returns:
            Rabatt berechnet auf Zwischensumme
        """
        return self.subtotal * (self.discount_percent / Decimal("100"))

    @property
    def subtotal_after_discount(self) -> Decimal:
        """
        Zwischensumme nach Rabatt, ohne MwSt.
        
        Returns:
            Zwischensumme minus Rabatt
        """
        return self.subtotal - self.discount_amount

    @property
    def tax_amount(self) -> Decimal:
        """
        MwSt-Betrag.
        
        Returns:
            MwSt berechnet auf Zwischensumme nach Rabatt
        """
        return self.subtotal_after_discount * (self.tax_rate / Decimal("100"))

    @property
    def total(self) -> Decimal:
        """
        Gesamtbetrag inkl. MwSt.
        
        Returns:
            Zwischensumme nach Rabatt plus MwSt
        """
        return self.subtotal_after_discount + self.tax_amount

    def __repr__(self) -> str:
        return (
            f"<InvoiceLineItem(description='{self.description[:30]}...', "
            f"quantity={self.quantity}, total={self.total})>"
        )


class Payment(Base, UUIDMixin, TimestampMixin):
    """
    Zahlungseingänge für Rechnungen.
    
    Erfasst alle Zahlungen mit Datum, Betrag, Methode und
    optionaler Referenz (z.B. Überweisungsreferenz).
    
    Attributes:
        amount: Zahlungsbetrag
        payment_date: Datum des Zahlungseingangs
        method: Zahlungsmethode
        reference: Buchungsreferenz (z.B. Transaktions-ID)
        note: Optionale Notiz
    """
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_invoice_id", "invoice_id"),
        Index("ix_payments_payment_date", "payment_date"),
        Index("ix_payments_method", "method"),
        CheckConstraint("amount > 0", name="check_payment_amount_positive"),
    )

    # Business Fields
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Zahlungsbetrag"
    )
    payment_date: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
        comment="Datum des Zahlungseingangs"
    )
    method: Mapped[str | None] = mapped_column(
        String(50),
        comment="Zahlungsmethode (cash, bank_transfer, etc.)"
    )
    reference: Mapped[str | None] = mapped_column(
        String(100),
        comment="Buchungsreferenz (z.B. Transaktions-ID, Verwendungszweck)"
    )
    note: Mapped[str | None] = mapped_column(
        Text,
        comment="Interne Notiz zum Zahlungseingang"
    )

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        comment="Zugehörige Rechnung"
    )

    # Relationships
    invoice: Mapped[Invoice] = relationship(
        "Invoice",
        back_populates="payments"
    )

    def __repr__(self) -> str:
        invoice_number = (
            self.invoice.invoice_number
            if self.invoice else "N/A"
        )
        return (
            f"<Payment(invoice='{invoice_number}', "
            f"amount={self.amount}, date={self.payment_date})>"
        )