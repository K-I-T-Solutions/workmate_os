# app/modules/backoffice/invoices/models.py
"""
Invoices Module Models - WorkmateOS Phase 2 (IMPROVED)

Verwaltet:
- Invoices (Rechnungen & Angebote)
- InvoiceLineItems (Rechnungspositionen)
- Payments (Zahlungseingänge)

CHANGES:
- ✅ recalculate_totals() method hinzugefügt
- ✅ Bessere CheckConstraints
- ✅ Auto-Status-Update bei Zahlungen
- ✅ Validierung für Dates
- ✅ Zusätzliche Properties
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
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
    CheckConstraint,
    event,
    Integer,
    UniqueConstraint,
    DateTime,
    JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.crm.models import Customer
    from app.modules.backoffice.projects.models import Project
    from app.modules.backoffice.finance.models import Expense


# ============================================================================
# ENUMS
# ============================================================================

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


# ============================================================================
# MODELS
# ============================================================================

class Invoice(Base, UUIDMixin, TimestampMixin):
    """
    Kundenrechnungen und Angebote.

    Verwaltet Rechnungen mit automatischer Berechnung von
    Gesamtbeträgen, Zahlungsstatus und Fälligkeiten.

    Attributes:
        invoice_number: Eindeutige Rechnungsnummer (z.B. "RE-2025-001")
        total: Gesamtbetrag inkl. MwSt
        subtotal: Zwischensumme ohne MwSt
        tax_amount: MwSt-Betrag
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
        Index("ix_invoices_due_date", "due_date"),
        Index("ix_invoices_invoice_number", "invoice_number"),
        CheckConstraint("total >= 0", name="check_invoice_total_positive"),
        CheckConstraint("subtotal >= 0", name="check_invoice_subtotal_positive"),
        CheckConstraint("tax_amount >= 0", name="check_invoice_tax_positive"),
        CheckConstraint(
            "status IN ('draft', 'sent', 'paid', 'partial', 'overdue', 'cancelled')",
            name="check_invoice_status_valid"
        ),
        CheckConstraint(
            "due_date IS NULL OR issued_date IS NULL OR due_date >= issued_date",
            name="check_invoice_due_after_issued"
        ),
    )

    # Business Fields
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Eindeutige Rechnungsnummer (z.B. RE-2025-001)"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        server_default="0.00",
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
    document_type: Mapped[str] = mapped_column(
        String(50),
        default="invoice",
        server_default="invoice",
        nullable=False,
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

    # Soft-Delete (GoBD Compliance)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Zeitpunkt der Soft-Deletion (NULL = nicht gelöscht)"
    )

    # Foreign Keys
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
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
        order_by="InvoiceLineItem.position",
        lazy="selectin"
    )
    payments: Mapped[list[Payment]] = relationship(
        "Payment",
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="Payment.payment_date.desc()",
        lazy="selectin"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )



    # ========================================================================
    # METHODS
    # ========================================================================

    def recalculate_totals(self) -> None:
        """
        Berechnet subtotal, tax_amount und total aus line_items neu.

        WICHTIG: Nach Änderungen an line_items aufrufen!
        """
        self.subtotal = sum(
            item.subtotal_after_discount for item in self.line_items
        )
        self.tax_amount = sum(
            item.tax_amount for item in self.line_items
        )
        self.total = self.subtotal + self.tax_amount

    def update_status_from_payments(self) -> None:
        """
        DEPRECATED: Use invoices_crud.update_invoice_status_from_payments() instead.

        Diese Methode wird nicht mehr verwendet. Status-Updates erfolgen jetzt
        über die zentrale CRUD-Funktion für konsistentes Audit Logging und
        State Machine Handling.

        Old logic (for reference):
        - outstanding = 0 → PAID
        - 0 < outstanding < total → PARTIAL
        - outstanding = total → SENT (falls bereits gesendet)
        - overdue falls due_date überschritten
        """
        import warnings
        warnings.warn(
            "update_status_from_payments() is deprecated. "
            "Use invoices_crud.update_invoice_status_from_payments() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Legacy implementation (minimal, for backward compatibility)
        if self.status == InvoiceStatus.CANCELLED.value:
            return

        outstanding = self.outstanding_amount

        if outstanding <= Decimal("0.00"):
            self.status = InvoiceStatus.PAID.value
        elif outstanding < self.total:
            self.status = InvoiceStatus.PARTIAL.value
        elif self.is_overdue:
            self.status = InvoiceStatus.OVERDUE.value

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def is_overdue(self) -> bool:
        """
        Prüft ob Rechnung überfällig ist.

        Returns:
            True wenn Fälligkeitsdatum überschritten und nicht vollständig bezahlt
        """
        if self.due_date is None or self.status == InvoiceStatus.PAID.value:
            return False
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

    @property
    def days_until_due(self) -> int | None:
        """
        Tage bis zur Fälligkeit (negativ = überfällig).

        Returns:
            Anzahl Tage oder None wenn kein due_date
        """
        if self.due_date is None:
            return None
        delta = self.due_date - date.today()
        return delta.days

    @property
    def payment_rate(self) -> float:
        """
        Zahlungsquote in Prozent.

        Returns:
            0.0 bis 100.0
        """
        if self.total <= Decimal("0.00"):
            return 0.0
        return float((self.paid_amount / self.total) * Decimal("100"))

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
        CheckConstraint("tax_rate >= 0 AND tax_rate <= 100", name="check_tax_rate_valid"),
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
        nullable=False,
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
        nullable=False,
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

    # Soft-Delete (GoBD Compliance)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Zeitpunkt der Soft-Deletion (NULL = nicht gelöscht)"
    )

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        comment="Zugehörige Rechnung"
    )

    # Relationships
    invoice: Mapped[Invoice] = relationship(
        "Invoice",
        back_populates="line_items"
    )

    # ========================================================================
    # PROPERTIES
    # ========================================================================

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
        desc = self.description[:30] + "..." if len(self.description) > 30 else self.description
        return (
            f"<InvoiceLineItem(description='{desc}', "
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
        CheckConstraint(
            "method IN ('cash', 'bank_transfer', 'credit_card', 'debit_card', 'paypal', 'sepa', 'other')",
            name="check_payment_method_valid"
        ),
    )

    # Business Fields
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Zahlungsbetrag"
    )
    payment_date: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
        comment="Datum des Zahlungseingangs"
    )
    method: Mapped[str | None] = mapped_column(
        String(50),
        default=PaymentMethod.BANK_TRANSFER.value,
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

    # Soft-Delete (GoBD Compliance)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Zeitpunkt der Soft-Deletion (NULL = nicht gelöscht)"
    )

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
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


# ============================================================================
# EVENTS (Auto-Updates)
# ============================================================================

# DEPRECATED: Event-Handler deaktiviert
# Status-Updates werden jetzt explizit in payments_crud.py durchgeführt
# über invoices_crud.update_invoice_status_from_payments()
#
# @event.listens_for(Payment, "after_insert")
# @event.listens_for(Payment, "after_update")
# @event.listens_for(Payment, "after_delete")
# def update_invoice_status_after_payment(mapper, connection, target):
#     """
#     DEPRECATED: Aktualisiert Invoice-Status automatisch nach Payment-Änderungen.
#     Status-Updates erfolgen jetzt über zentrale CRUD-Funktion.
#     """
#     if target.invoice:
#         target.invoice.update_status_from_payments()

# =====================================================================
# Audit Trail
# =====================================================================

class AuditLog(Base, UUIDMixin):
    """
    Audit Trail für Compliance (GoBD, HGB, AO).

    Protokolliert alle Änderungen an Invoices, Payments und Expenses
    für lückenlose Nachvollziehbarkeit und gesetzliche Anforderungen.

    Attributes:
        entity_type: Typ der geänderten Entität (Invoice, Payment, Expense)
        entity_id: UUID der geänderten Entität
        action: Art der Änderung (create, update, delete, status_change)
        old_values: Alte Werte als JSON (bei update/delete)
        new_values: Neue Werte als JSON (bei create/update)
        user_id: Optionale User-ID (für zukünftige Auth-Integration)
        timestamp: Zeitstempel der Änderung
        ip_address: Optionale IP-Adresse für zusätzliche Sicherheit
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_user_id", "user_id"),
        CheckConstraint(
            "action IN ('create', 'update', 'delete', 'status_change')",
            name="check_audit_action_valid"
        ),
    )

    # Business Fields
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Typ der Entität (Invoice, Payment, Expense)"
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
        comment="UUID der geänderten Entität"
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Art der Änderung (create, update, delete, status_change)"
    )
    old_values: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Alte Werte als JSON (bei update/delete)"
    )
    new_values: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Neue Werte als JSON (bei create/update)"
    )
    user_id: Mapped[str | None] = mapped_column(
        String(100),
        comment="User-ID des Benutzers (für zukünftige Integration)"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Zeitstempel der Änderung"
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        comment="IP-Adresse (IPv4/IPv6) für zusätzliche Sicherheit"
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(entity='{self.entity_type}:{self.entity_id}', "
            f"action='{self.action}', timestamp={self.timestamp})>"
        )


# =====================================================================
# Number Generator
# =====================================================================

class NumberSequence(Base, UUIDMixin, TimestampMixin):
    """
    Verwaltet laufende Nummernkreise pro Dokumenttyp & Jahr.

    Beispiel:
      doc_type = "invoice", year = 2025, current_number = 12
      -> nächste Rechnungsnummer: RE-2025-0013
    """
    __tablename__ = "number_sequences"
    __table_args__ = (
        UniqueConstraint("doc_type", "year", name="uq_number_sequence_type_year"),
    )

    doc_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Dokumenttyp: invoice, quote, credit_note, cancellation, etc."
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Jahreszahl für den Nummernkreis"
    )
    current_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Letzte vergebene laufende Nummer"
    )

    def __repr__(self) -> str:
        return f"<NumberSequence(type='{self.doc_type}', year={self.year}, current={self.current_number})>"
