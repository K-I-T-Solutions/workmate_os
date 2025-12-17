# app/modules/backoffice/crm/routes.py
"""
FastAPI Routes für CRM Module.

REST API Endpoints für Customer und Contact Management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.settings.database import get_db
from . import  schemas, crud


router = APIRouter(
    prefix="/backoffice/crm",
    tags=["Backoffice CRM"]
)


# === Customer Endpoints ===

@router.get("/customers", response_model=list[schemas.CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0, description="Anzahl zu überspringende Einträge"),
    limit: int = Query(50, ge=1, le=100, description="Maximum Anzahl Einträge"),
    status: Optional[str] = Query(None, description="Filter nach Status"),
    search: Optional[str] = Query(None, description="Suche in Name und Email"),
    db: Session = Depends(get_db)
):
    """
    Liste alle Kunden.

    Optional mit Filtern:
    - status: active, inactive, lead, blocked
    - search: Suche in Name und Email
    """
    return crud.get_customers(
        db,
        skip=skip,
        limit=limit,
        status=status,
        search=search
    )


@router.get("/customers/{customer_id}", response_model=schemas.CustomerResponseWithContacts)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Hole einen einzelnen Kunden mit allen Kontakten.
    """
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    return db_customer


@router.post("/customers", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Erstelle einen neuen Kunden.
    """
    return crud.create_customer(db, data)


@router.put("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
    customer_id: UUID,
    data: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Aktualisiere Kundendetails.
    """
    updated = crud.update_customer(db, customer_id, data)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    return updated


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Lösche einen Kunden.

    ACHTUNG: Löscht auch alle zugehörigen Kontakte, Projekte und Rechnungen!
    """
    success = crud.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    return None


# === Contact Endpoints ===

@router.get("/contacts", response_model=list[schemas.ContactResponse])
def list_contacts(
    customer_id: Optional[UUID] = Query(None, description="Filter nach Customer ID"),
    skip: int = Query(0, ge=0, description="Anzahl zu überspringende Einträge"),
    limit: int = Query(100, ge=1, le=200, description="Maximum Anzahl Einträge"),
    db: Session = Depends(get_db)
):
    """
    Liste alle Kontakte.

    Optional gefiltert nach customer_id.
    """
    return crud.get_contacts(
        db,
        customer_id=customer_id,
        skip=skip,
        limit=limit
    )


@router.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Hole einen einzelnen Kontakt.
    """
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found"
        )
    return db_contact


@router.post("/contacts", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    data: schemas.ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Erstelle einen neuen Kontakt.
    """
    try:
        return crud.create_contact(db, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(
    contact_id: UUID,
    data: schemas.ContactUpdate,
    db: Session = Depends(get_db)
):
    """
    Aktualisiere Kontaktdetails.
    """
    try:
        updated = crud.update_contact(db, contact_id, data)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact with id {contact_id} not found"
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Lösche einen Kontakt.
    """
    success = crud.delete_contact(db, contact_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found"
        )
    return None


# === Special Contact Endpoints ===

@router.get("/customers/{customer_id}/contacts/primary", response_model=schemas.ContactResponse)
def get_primary_contact(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Hole den primären Kontakt eines Kunden.
    """
    # Prüfe ob Customer existiert
    customer = crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )

    contact = crud.get_primary_contact(db, customer_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No primary contact found for customer {customer_id}"
        )
    return contact


@router.put("/customers/{customer_id}/contacts/{contact_id}/set-primary", response_model=schemas.ContactResponse)
def set_primary_contact(
    customer_id: UUID,
    contact_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Setze einen Kontakt als primären Ansprechpartner.

    Entfernt automatisch das Primary-Flag von allen anderen Kontakten des Kunden.
    """
    contact = crud.set_primary_contact(db, contact_id, customer_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found or does not belong to customer {customer_id}"
        )
    return contact
