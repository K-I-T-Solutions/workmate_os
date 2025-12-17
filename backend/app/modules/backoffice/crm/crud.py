# app/modules/backoffice/crm/crud.py
"""
CRUD Operations für CRM Module.

Datenbank-Operationen für Customer und Contact Models.
"""
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from . import models, schemas


# === Customer CRUD ===

def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> list[models.Customer]:
    """
    Hole alle Kunden mit optionalen Filtern.

    Args:
        db: Database Session
        skip: Anzahl zu überspringende Einträge
        limit: Maximum Anzahl Einträge
        status: Optional Status Filter
        search: Optional Suchbegriff (Name, Email)

    Returns:
        Liste von Customer Models
    """
    query = db.query(models.Customer)

    if status:
        query = query.filter(models.Customer.status == status)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Customer.name.ilike(search_filter)) |
            (models.Customer.email.ilike(search_filter))
        )

    return query.offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: UUID) -> Optional[models.Customer]:
    """
    Hole einen einzelnen Kunden.

    Args:
        db: Database Session
        customer_id: Customer UUID

    Returns:
        Customer Model oder None
    """
    return db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()


def create_customer(db: Session, data: schemas.CustomerCreate) -> models.Customer:
    """
    Erstelle einen neuen Kunden.

    Args:
        db: Database Session
        data: Customer Creation Schema

    Returns:
        Erstellter Customer
    """
    new_customer = models.Customer(**data.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def update_customer(
    db: Session,
    customer_id: UUID,
    data: schemas.CustomerUpdate
) -> Optional[models.Customer]:
    """
    Aktualisiere einen Kunden.

    Args:
        db: Database Session
        customer_id: Customer UUID
        data: Customer Update Schema

    Returns:
        Aktualisierter Customer oder None
    """
    customer = get_customer(db, customer_id)
    if customer is None:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_id: UUID) -> bool:
    """
    Lösche einen Kunden.

    Args:
        db: Database Session
        customer_id: Customer UUID

    Returns:
        True wenn erfolgreich, False wenn nicht gefunden
    """
    customer = get_customer(db, customer_id)
    if customer is None:
        return False

    db.delete(customer)
    db.commit()
    return True


# === Contact CRUD ===

def get_contacts(
    db: Session,
    customer_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> list[models.Contact]:
    """
    Hole alle Kontakte mit optionalem Customer Filter.

    Args:
        db: Database Session
        customer_id: Optional Customer UUID Filter
        skip: Anzahl zu überspringende Einträge
        limit: Maximum Anzahl Einträge

    Returns:
        Liste von Contact Models
    """
    query = db.query(models.Contact)

    if customer_id:
        query = query.filter(models.Contact.customer_id == customer_id)

    return query.offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: UUID) -> Optional[models.Contact]:
    """
    Hole einen einzelnen Kontakt.

    Args:
        db: Database Session
        contact_id: Contact UUID

    Returns:
        Contact Model oder None
    """
    return db.query(models.Contact).filter(
        models.Contact.id == contact_id
    ).first()


def create_contact(db: Session, data: schemas.ContactCreate) -> models.Contact:
    """
    Erstelle einen neuen Kontakt.

    Args:
        db: Database Session
        data: Contact Creation Schema

    Returns:
        Erstellter Contact
    """
    # Prüfe ob Customer existiert
    customer = get_customer(db, data.customer_id)
    if customer is None:
        raise ValueError(f"Customer with id {data.customer_id} not found")

    new_contact = models.Contact(**data.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def update_contact(
    db: Session,
    contact_id: UUID,
    data: schemas.ContactUpdate
) -> Optional[models.Contact]:
    """
    Aktualisiere einen Kontakt.

    Args:
        db: Database Session
        contact_id: Contact UUID
        data: Contact Update Schema

    Returns:
        Aktualisierter Contact oder None
    """
    contact = get_contact(db, contact_id)
    if contact is None:
        return None

    # Wenn customer_id geändert wird, prüfe ob neuer Customer existiert
    if data.customer_id and data.customer_id != contact.customer_id:
        customer = get_customer(db, data.customer_id)
        if customer is None:
            raise ValueError(f"Customer with id {data.customer_id} not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: UUID) -> bool:
    """
    Lösche einen Kontakt.

    Args:
        db: Database Session
        contact_id: Contact UUID

    Returns:
        True wenn erfolgreich, False wenn nicht gefunden
    """
    contact = get_contact(db, contact_id)
    if contact is None:
        return False

    db.delete(contact)
    db.commit()
    return True


def get_primary_contact(db: Session, customer_id: UUID) -> Optional[models.Contact]:
    """
    Hole den primären Kontakt eines Kunden.

    Args:
        db: Database Session
        customer_id: Customer UUID

    Returns:
        Primary Contact oder None
    """
    return (
    db.query(models.Contact)
    .filter(
        models.Contact.customer_id == customer_id,
        models.Contact.is_primary.is_(True)
    )
    .first()
)


def set_primary_contact(
    db: Session,
    contact_id: UUID,
    customer_id: UUID
) -> Optional[models.Contact]:
    """
    Setze einen Kontakt als primär und entferne Flag von anderen.

    Args:
        db: Database Session
        contact_id: Contact UUID der primär werden soll
        customer_id: Customer UUID

    Returns:
        Updated Contact oder None
    """
    contact = get_contact(db, contact_id)
    if contact is None or contact.customer_id != customer_id:
        return None

    # Entferne is_primary Flag von allen anderen Kontakten
    db.query(models.Contact).filter(
        models.Contact.customer_id == customer_id,
        models.Contact.id != contact_id
    ).update({"is_primary": False})

    # Setze neuen primären Kontakt
    contact.is_primary = True
    db.commit()
    db.refresh(contact)
    return contact

def create_activity(db: Session, data: schemas.ActivityCreate) -> models.Activity:
    obj = models.Activity(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def latest_activities(db: Session, limit: int = 5):
    return (
        db.query(models.Activity)
        .order_by(models.Activity.occurred_at.desc())
        .limit(limit)
        .all()
    )

def activities_by_customer(
    db: Session,
    customer_id: UUID,
    contact_id: Optional[UUID] = None,
    limit: Optional[int] = None,
):
    query = (
        db.query(models.Activity)
        .filter(models.Activity.customer_id == customer_id)
        .order_by(models.Activity.occurred_at.desc())
    )

    if contact_id is not None:
        query = query.filter(models.Activity.contact_id == contact_id)

    if limit is not None:
        query = query.limit(limit)

    return query.all()

def get_stats(db: Session):
    customers = db.query(models.Customer).all()

    return {
        "total_customers": len(customers),
        "active_customers": sum(1 for c in customers if c.status == models.CustomerStatus.ACTIVE.value),
        "leads": sum(1 for c in customers if c.status == models.CustomerStatus.LEAD.value),
        "blocked_customers": sum(1 for c in customers if c.status == models.CustomerStatus.BLOCKED.value),
        "total_revenue": sum(c.total_revenue for c in customers),
        "outstanding_revenue": sum(c.outstanding_amount for c in customers),
        "active_projects": sum(c.active_projects_count for c in customers),
    }
