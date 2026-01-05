"""
Compliance Logic for Invoice Module (GoBD, HGB, AO)

Provides validation functions for:
1. Invoice Immutability (§238 HGB)
2. State Machine for Status Transitions
3. Allowed Field Updates after "sent" status
"""
from typing import Dict, Set, Optional
from fastapi import HTTPException

from app.modules.backoffice.invoices.models import InvoiceStatus


# ============================================================================
# INVOICE IMMUTABILITY (§238 HGB)
# ============================================================================

# Felder die IMMER editiert werden dürfen (auch nach "sent")
ALWAYS_EDITABLE_FIELDS: Set[str] = {
    "notes",  # Interne Notizen
    "terms",  # Zahlungsbedingungen (dürfen nachträglich ergänzt werden)
}

# Felder die NIE editiert werden dürfen nach "sent"
IMMUTABLE_AFTER_SENT: Set[str] = {
    "customer_id",
    "project_id",
    "invoice_number",
    "subtotal",
    "tax_amount",
    "total",
    "issued_date",
    "due_date",
    "document_type",
    "line_items",  # Positionen dürfen nicht mehr geändert werden
}

# Status-Level für Immutability-Checks
STATUS_LEVELS = {
    InvoiceStatus.DRAFT: 0,
    InvoiceStatus.SENT: 1,
    InvoiceStatus.PARTIAL: 2,
    InvoiceStatus.PAID: 3,
    InvoiceStatus.OVERDUE: 2,
    InvoiceStatus.CANCELLED: 4,
}


def is_invoice_locked(status: str) -> bool:
    """
    Prüft ob Invoice gesperrt ist (immutable).

    Returns:
        True wenn Status >= "sent" (also sent, partial, paid, overdue, cancelled)
    """
    return status in [
        InvoiceStatus.SENT.value,
        InvoiceStatus.PARTIAL.value,
        InvoiceStatus.PAID.value,
        InvoiceStatus.OVERDUE.value,
        InvoiceStatus.CANCELLED.value,
    ]


def validate_invoice_editable(invoice, update_fields: Set[str]) -> None:
    """
    Validiert ob die angegebenen Felder editiert werden dürfen.

    Wirft HTTPException wenn Invoice locked ist und unerlaubte Felder
    geändert werden sollen.

    Args:
        invoice: Invoice-Instanz
        update_fields: Set von Feldnamen die geändert werden sollen

    Raises:
        HTTPException 403: Wenn Invoice locked und unerlaubte Felder geändert werden
    """
    if not is_invoice_locked(invoice.status):
        return  # Draft darf alles ändern

    # Filtere erlaubte Felder raus
    forbidden_fields = update_fields - ALWAYS_EDITABLE_FIELDS

    if forbidden_fields:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Invoice {invoice.invoice_number} is locked (status={invoice.status}). "
                f"Cannot modify fields: {', '.join(forbidden_fields)}. "
                f"Only 'notes' and 'terms' can be edited after invoice is sent. "
                f"(§238 HGB: Unveränderbarkeit nach Rechnungsstellung)"
            )
        )


# ============================================================================
# STATE MACHINE FOR STATUS TRANSITIONS
# ============================================================================

# Erlaubte Status-Übergänge
ALLOWED_STATUS_TRANSITIONS: Dict[str, Set[str]] = {
    # Von DRAFT kann man zu sent oder cancelled wechseln
    InvoiceStatus.DRAFT.value: {
        InvoiceStatus.SENT.value,
        InvoiceStatus.CANCELLED.value,
    },

    # Von SENT kann man zu partial, paid, overdue oder cancelled wechseln
    InvoiceStatus.SENT.value: {
        InvoiceStatus.PARTIAL.value,
        InvoiceStatus.PAID.value,
        InvoiceStatus.OVERDUE.value,
        InvoiceStatus.CANCELLED.value,
    },

    # Von PARTIAL kann man zu paid, overdue oder cancelled wechseln
    InvoiceStatus.PARTIAL.value: {
        InvoiceStatus.PAID.value,
        InvoiceStatus.OVERDUE.value,
        InvoiceStatus.CANCELLED.value,
    },

    # Von OVERDUE kann man zu partial, paid oder cancelled wechseln
    InvoiceStatus.OVERDUE.value: {
        InvoiceStatus.PARTIAL.value,
        InvoiceStatus.PAID.value,
        InvoiceStatus.CANCELLED.value,
    },

    # Von PAID kann man NUR zu cancelled wechseln (Storno/Gutschrift)
    InvoiceStatus.PAID.value: {
        InvoiceStatus.CANCELLED.value,
    },

    # Von CANCELLED kann man NIRGENDWO mehr hin
    InvoiceStatus.CANCELLED.value: set(),
}


def is_status_transition_allowed(old_status: str, new_status: str) -> bool:
    """
    Prüft ob ein Status-Übergang erlaubt ist.

    Args:
        old_status: Aktueller Status
        new_status: Gewünschter neuer Status

    Returns:
        True wenn Übergang erlaubt, False sonst
    """
    # Gleicher Status ist immer erlaubt (no-op)
    if old_status == new_status:
        return True

    allowed_targets = ALLOWED_STATUS_TRANSITIONS.get(old_status, set())
    return new_status in allowed_targets


def validate_status_transition(old_status: str, new_status: str, invoice_number: str) -> None:
    """
    Validiert einen Status-Übergang und wirft Exception bei ungültigem Übergang.

    Args:
        old_status: Aktueller Status
        new_status: Gewünschter neuer Status
        invoice_number: Rechnungsnummer für Error-Message

    Raises:
        HTTPException 400: Wenn Übergang nicht erlaubt
    """
    if not is_status_transition_allowed(old_status, new_status):
        allowed = ALLOWED_STATUS_TRANSITIONS.get(old_status, set())
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition for invoice {invoice_number}: "
                f"'{old_status}' → '{new_status}' is not allowed. "
                f"Allowed transitions from '{old_status}': {', '.join(allowed) if allowed else 'none'}"
            )
        )


# ============================================================================
# SOFT-DELETE VALIDATION
# ============================================================================

def validate_invoice_not_paid_for_deletion(invoice) -> None:
    """
    Validiert dass Invoice gelöscht werden darf.

    Paid Invoices sollten nicht gelöscht werden, sondern storniert (cancelled).

    Args:
        invoice: Invoice-Instanz

    Raises:
        HTTPException 403: Wenn Invoice bereits bezahlt ist
    """
    if invoice.status == InvoiceStatus.PAID.value:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Cannot delete paid invoice {invoice.invoice_number}. "
                f"Use status 'cancelled' for stornierung/cancellation instead. "
                f"(GoBD: Bezahlte Rechnungen dürfen nicht gelöscht werden)"
            )
        )


def validate_invoice_not_deleted(invoice) -> None:
    """
    Prüft ob Invoice bereits soft-deleted ist.

    Args:
        invoice: Invoice-Instanz

    Raises:
        HTTPException 404: Wenn Invoice gelöscht ist
    """
    if invoice.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice.invoice_number} has been deleted"
        )


# ============================================================================
# COMBINED VALIDATION FOR CRUD OPERATIONS
# ============================================================================

def validate_invoice_update(invoice, update_fields: Set[str]) -> None:
    """
    Kombinierte Validierung für Invoice-Updates.

    Args:
        invoice: Invoice-Instanz
        update_fields: Set von Feldnamen die geändert werden sollen

    Raises:
        HTTPException: Bei Validierungsfehlern
    """
    # Prüfe ob gelöscht
    validate_invoice_not_deleted(invoice)

    # Prüfe Immutability
    validate_invoice_editable(invoice, update_fields)


def validate_invoice_deletion(invoice) -> None:
    """
    Kombinierte Validierung für Invoice-Löschung.

    Args:
        invoice: Invoice-Instanz

    Raises:
        HTTPException: Bei Validierungsfehlern
    """
    # Prüfe ob bereits gelöscht
    validate_invoice_not_deleted(invoice)

    # Prüfe ob paid (darf nicht gelöscht werden)
    validate_invoice_not_paid_for_deletion(invoice)


def validate_invoice_status_change(invoice, new_status: str) -> None:
    """
    Kombinierte Validierung für Status-Änderungen.

    Args:
        invoice: Invoice-Instanz
        new_status: Gewünschter neuer Status

    Raises:
        HTTPException: Bei Validierungsfehlern
    """
    # Prüfe ob gelöscht
    validate_invoice_not_deleted(invoice)

    # Prüfe State Machine
    validate_status_transition(invoice.status, new_status, invoice.invoice_number)
