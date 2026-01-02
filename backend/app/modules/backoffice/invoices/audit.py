"""
Audit Trail Helper Functions for GoBD Compliance

Provides utilities to log all changes to financial entities (Invoice, Payment, Expense)
for compliance with German accounting standards (HGB, AO, GoBD).

Usage:
    from app.modules.backoffice.invoices.audit import log_audit

    # Log invoice creation
    log_audit(db, "Invoice", invoice.id, "create", new_values=invoice_dict)

    # Log invoice update
    log_audit(db, "Invoice", invoice.id, "update", old_values=old_dict, new_values=new_dict)

    # Log status change
    log_audit(db, "Invoice", invoice.id, "status_change",
              old_values={"status": "draft"}, new_values={"status": "sent"})

    # Log deletion
    log_audit(db, "Payment", payment.id, "delete", old_values=payment_dict)
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.backoffice.invoices.models import AuditLog


def log_audit(
    db: Session,
    entity_type: str,
    entity_id: UUID,
    action: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Erstellt einen Audit-Log-Eintrag für eine Entitätsänderung.

    Args:
        db: Database Session
        entity_type: Typ der Entität ("Invoice", "Payment", "Expense", "InvoiceLineItem")
        entity_id: UUID der geänderten Entität
        action: Art der Änderung ("create", "update", "delete", "status_change")
        old_values: Alte Werte als Dictionary (bei update/delete)
        new_values: Neue Werte als Dictionary (bei create/update)
        user_id: Optionale User-ID (für zukünftige Auth-Integration)
        ip_address: Optionale IP-Adresse

    Returns:
        AuditLog: Der erstellte Audit-Log-Eintrag

    Raises:
        ValueError: Wenn action ungültig ist
    """
    valid_actions = {"create", "update", "delete", "status_change"}
    if action not in valid_actions:
        raise ValueError(f"Invalid action '{action}'. Must be one of: {valid_actions}")

    audit_entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_values=old_values,
        new_values=new_values,
        user_id=user_id,
        ip_address=ip_address,
        timestamp=datetime.utcnow()
    )

    db.add(audit_entry)
    db.flush()

    return audit_entry


def serialize_for_audit(obj: Any, exclude_fields: Optional[set] = None) -> Dict[str, Any]:
    """
    Serialisiert ein SQLAlchemy-Objekt für Audit-Logging.

    Konvertiert ein Modell-Objekt in ein Dictionary mit JSON-serialisierbaren Werten.
    Filtert technische Felder wie relationships und timestamps heraus.

    Args:
        obj: SQLAlchemy Model-Instanz
        exclude_fields: Set von Feldnamen die ausgeschlossen werden sollen

    Returns:
        Dict mit serialisierten Werten

    Example:
        invoice_dict = serialize_for_audit(invoice, exclude_fields={"customer", "line_items"})
    """
    if exclude_fields is None:
        # Standard-Ausschlüsse: Relationships und Metadaten
        exclude_fields = {
            "customer", "project", "line_items", "payments", "expenses",
            "invoice", "created_at", "updated_at"
        }

    result = {}

    # Hole alle Spalten des Models
    for column in obj.__table__.columns:
        field_name = column.name
        if field_name in exclude_fields:
            continue

        value = getattr(obj, field_name, None)

        # Konvertiere nicht-JSON-serialisierbare Typen
        if value is not None:
            if hasattr(value, 'isoformat'):  # datetime, date
                value = value.isoformat()
            elif isinstance(value, UUID):
                value = str(value)
            elif hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool)):
                # Decimal, Enum, etc.
                value = str(value)

        result[field_name] = value

    return result


def get_changed_fields(old_values: Dict[str, Any], new_values: Dict[str, Any]) -> Dict[str, tuple]:
    """
    Ermittelt die geänderten Felder zwischen zwei Dictionaries.

    Args:
        old_values: Alte Werte
        new_values: Neue Werte

    Returns:
        Dict mit Feldnamen als Keys und (old_value, new_value) Tuples als Values

    Example:
        changes = get_changed_fields(
            {"status": "draft", "total": 100.0},
            {"status": "sent", "total": 100.0}
        )
        # Returns: {"status": ("draft", "sent")}
    """
    changes = {}

    all_keys = set(old_values.keys()) | set(new_values.keys())

    for key in all_keys:
        old_val = old_values.get(key)
        new_val = new_values.get(key)

        if old_val != new_val:
            changes[key] = (old_val, new_val)

    return changes


def log_invoice_creation(db: Session, invoice, user_id: Optional[str] = None, ip_address: Optional[str] = None):
    """
    Convenience-Funktion für Invoice-Erstellung.

    Args:
        db: Database Session
        invoice: Invoice-Instanz
        user_id: Optionale User-ID
        ip_address: Optionale IP-Adresse
    """
    invoice_data = serialize_for_audit(invoice)
    return log_audit(
        db=db,
        entity_type="Invoice",
        entity_id=invoice.id,
        action="create",
        new_values=invoice_data,
        user_id=user_id,
        ip_address=ip_address
    )


def log_invoice_update(
    db: Session,
    invoice,
    old_invoice_data: Dict[str, Any],
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """
    Convenience-Funktion für Invoice-Updates.

    Args:
        db: Database Session
        invoice: Aktuelle Invoice-Instanz
        old_invoice_data: Alte Werte als Dictionary
        user_id: Optionale User-ID
        ip_address: Optionale IP-Adresse
    """
    new_invoice_data = serialize_for_audit(invoice)
    changes = get_changed_fields(old_invoice_data, new_invoice_data)

    if not changes:
        return None  # Keine Änderungen

    return log_audit(
        db=db,
        entity_type="Invoice",
        entity_id=invoice.id,
        action="update",
        old_values=old_invoice_data,
        new_values=new_invoice_data,
        user_id=user_id,
        ip_address=ip_address
    )


def log_invoice_status_change(
    db: Session,
    invoice,
    old_status: str,
    new_status: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """
    Spezialisierte Funktion für Status-Änderungen (wichtig für GoBD).

    Args:
        db: Database Session
        invoice: Invoice-Instanz
        old_status: Alter Status
        new_status: Neuer Status
        user_id: Optionale User-ID
        ip_address: Optionale IP-Adresse
    """
    return log_audit(
        db=db,
        entity_type="Invoice",
        entity_id=invoice.id,
        action="status_change",
        old_values={"status": old_status},
        new_values={"status": new_status},
        user_id=user_id,
        ip_address=ip_address
    )


def log_invoice_deletion(
    db: Session,
    invoice,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """
    Convenience-Funktion für Invoice-Soft-Deletion.

    Args:
        db: Database Session
        invoice: Invoice-Instanz
        user_id: Optionale User-ID
        ip_address: Optionale IP-Adresse
    """
    invoice_data = serialize_for_audit(invoice)
    return log_audit(
        db=db,
        entity_type="Invoice",
        entity_id=invoice.id,
        action="delete",
        old_values=invoice_data,
        user_id=user_id,
        ip_address=ip_address
    )


def log_payment_creation(db: Session, payment, user_id: Optional[str] = None, ip_address: Optional[str] = None):
    """Convenience-Funktion für Payment-Erstellung."""
    payment_data = serialize_for_audit(payment)
    return log_audit(
        db=db,
        entity_type="Payment",
        entity_id=payment.id,
        action="create",
        new_values=payment_data,
        user_id=user_id,
        ip_address=ip_address
    )


def log_payment_update(
    db: Session,
    payment,
    old_payment_data: Dict[str, Any],
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """Convenience-Funktion für Payment-Updates."""
    new_payment_data = serialize_for_audit(payment)
    changes = get_changed_fields(old_payment_data, new_payment_data)

    if not changes:
        return None

    return log_audit(
        db=db,
        entity_type="Payment",
        entity_id=payment.id,
        action="update",
        old_values=old_payment_data,
        new_values=new_payment_data,
        user_id=user_id,
        ip_address=ip_address
    )


def log_payment_deletion(
    db: Session,
    payment,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """Convenience-Funktion für Payment-Soft-Deletion."""
    payment_data = serialize_for_audit(payment)
    return log_audit(
        db=db,
        entity_type="Payment",
        entity_id=payment.id,
        action="delete",
        old_values=payment_data,
        user_id=user_id,
        ip_address=ip_address
    )
