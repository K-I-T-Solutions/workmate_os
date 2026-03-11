# app/modules/backoffice/crm/routes.py
"""
FastAPI Routes für CRM Module.

REST API Endpoints für Customer und Contact Management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.modules.backoffice.invoices.models import AuditLog
from . import schemas, crud


router = APIRouter(
    prefix="/backoffice/crm",
    tags=["Backoffice CRM"]
)


# === Customer Endpoints ===

@router.get("/customers", response_model=list[schemas.CustomerResponse])
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def list_customers(
    skip: int = Query(0, ge=0, description="Anzahl zu überspringende Einträge"),
    limit: int = Query(50, ge=1, le=100, description="Maximum Anzahl Einträge"),
    status: Optional[str] = Query(None, description="Filter nach Status"),
    search: Optional[str] = Query(None, description="Suche in Name und Email"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.crm.write", "backoffice.*"])
def create_customer(
    request: Request,
    data: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return crud.create_customer(db, data, user_id=user.get("id"), ip_address=request.client.host if request.client else None)


@router.put("/customers/{customer_id}", response_model=schemas.CustomerResponse)
@require_permissions(["backoffice.crm.write", "backoffice.*"])
def update_customer(
    request: Request,
    customer_id: UUID,
    data: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    updated = crud.update_customer(db, customer_id, data, user_id=user.get("id"), ip_address=request.client.host if request.client else None)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with id {customer_id} not found")
    return updated


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["backoffice.crm.delete", "backoffice.*"])
def delete_customer(
    request: Request,
    customer_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    success = crud.delete_customer(db, customer_id, user_id=user.get("id"), ip_address=request.client.host if request.client else None)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with id {customer_id} not found")
    return None


# === Contact Endpoints ===

@router.get("/contacts", response_model=list[schemas.ContactResponse])
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def list_contacts(
    customer_id: Optional[UUID] = Query(None, description="Filter nach Customer ID"),
    skip: int = Query(0, ge=0, description="Anzahl zu überspringende Einträge"),
    limit: int = Query(100, ge=1, le=200, description="Maximum Anzahl Einträge"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.crm.write", "backoffice.*"])
def create_contact(
    request: Request,
    data: schemas.ContactCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
        return crud.create_contact(db, data, user_id=user.get("id"), ip_address=request.client.host if request.client else None)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
@require_permissions(["backoffice.crm.write", "backoffice.*"])
def update_contact(
    request: Request,
    contact_id: UUID,
    data: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
        updated = crud.update_contact(db, contact_id, data, user_id=user.get("id"), ip_address=request.client.host if request.client else None)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with id {contact_id} not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["backoffice.crm.delete", "backoffice.*"])
def delete_contact(
    request: Request,
    contact_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    success = crud.delete_contact(db, contact_id, user_id=user.get("id"), ip_address=request.client.host if request.client else None)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with id {contact_id} not found")
    return None


# === Special Contact Endpoints ===

@router.get("/customers/{customer_id}/contacts/primary", response_model=schemas.ContactResponse)
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def get_primary_contact(
    customer_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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
@require_permissions(["backoffice.crm.write", "backoffice.*"])
def set_primary_contact(
    customer_id: UUID,
    contact_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
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


@router.post("/activities", response_model=schemas.ActivityResponse)
@require_permissions(["backoffice.crm.write", "backoffice.*"])
def create_activity(data: schemas.ActivityCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.create_activity(db, data)

@router.get("/activities/latest")
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def latest(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # Manuelle Activities
    manual = crud.latest_activities(db, limit)
    result = [
        {
            "id": str(a.id),
            "customer_id": str(a.customer_id),
            "contact_id": str(a.contact_id) if a.contact_id else None,
            "type": a.type,
            "description": a.description,
            "occurred_at": a.occurred_at.isoformat(),
            "created_at": a.created_at.isoformat(),
        }
        for a in manual
    ]

    # Neueste CRM Audit-Logs (Customer + Contact)
    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type.in_(["Customer", "Contact"]))
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    from app.modules.admin.service import _build_user_cache
    user_ids = list({str(log.user_id) for log in audit_logs if log.user_id})
    user_cache = _build_user_cache(db, user_ids)

    for log in audit_logs:
        result.append({
            "id": str(log.id),
            "customer_id": str(log.entity_id),
            "contact_id": None,
            "type": "system",
            "description": _timeline_description(log, user_cache),
            "occurred_at": log.timestamp.isoformat(),
            "created_at": log.timestamp.isoformat(),
        })

    result.sort(key=lambda x: x["occurred_at"], reverse=True)
    return result[:limit]

@router.get("/customers/{customer_id}/activities")
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def by_customer(
    customer_id: UUID,
    contact_id: Optional[UUID] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=200),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    effective_limit = limit or 50

    # Manuelle Activities
    manual = crud.activities_by_customer(db, customer_id=customer_id, contact_id=contact_id, limit=effective_limit)
    result = [
        {
            "id": str(a.id),
            "customer_id": str(a.customer_id),
            "contact_id": str(a.contact_id) if a.contact_id else None,
            "type": a.type,
            "description": a.description,
            "occurred_at": a.occurred_at.isoformat(),
            "created_at": a.created_at.isoformat(),
        }
        for a in manual
    ]

    # Audit-Logs als System-Activities (nur wenn kein contact_id Filter)
    if not contact_id:
        contact_ids = [str(c.id) for c in crud.get_contacts(db, customer_id=customer_id)]
        from sqlalchemy import or_
        audit_filter = [and_(AuditLog.entity_type == "Customer", AuditLog.entity_id == customer_id)]
        if contact_ids:
            audit_filter.append(and_(AuditLog.entity_type == "Contact", AuditLog.entity_id.in_(contact_ids)))

        audit_logs = (
            db.query(AuditLog)
            .filter(or_(*audit_filter))
            .order_by(AuditLog.timestamp.desc())
            .limit(effective_limit)
            .all()
        )

        from app.modules.admin.service import _build_user_cache
        user_ids = list({str(log.user_id) for log in audit_logs if log.user_id})
        user_cache = _build_user_cache(db, user_ids)

        for log in audit_logs:
            result.append({
                "id": str(log.id),
                "customer_id": str(customer_id),
                "contact_id": None,
                "type": "system",
                "description": _timeline_description(log, user_cache),
                "occurred_at": log.timestamp.isoformat(),
                "created_at": log.timestamp.isoformat(),
            })

    # Chronologisch sortiert, neueste zuerst
    result.sort(key=lambda x: x["occurred_at"], reverse=True)
    return result[:effective_limit]

@router.get("/stats", response_model=schemas.CrmStatsResponse)
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def stats(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.get_stats(db)


@router.get("/customers/{customer_id}/timeline")
@require_permissions(["backoffice.crm.view", "backoffice.*"])
def customer_timeline(
    customer_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Vollständige Timeline eines Kunden:
    - Automatische Audit-Events (angelegt, bearbeitet, gelöscht)
    - Manuelle Activities (Anruf, E-Mail, Notiz, etc.)
    - Chronologisch sortiert (neueste zuerst)
    """
    # Manuelle Activities
    activities = crud.activities_by_customer(db, customer_id=customer_id, limit=limit)
    activity_items = [
        {
            "id": str(a.id),
            "source": "activity",
            "type": a.type,
            "description": a.description,
            "timestamp": a.occurred_at.isoformat(),
            "user_id": None,
            "user_name": None,
        }
        for a in activities
    ]

    # Audit-Logs für Customer + alle zugehörigen Contacts
    contact_ids = [str(c.id) for c in crud.get_contacts(db, customer_id=customer_id)]
    audit_filter = [
        and_(AuditLog.entity_type == "Customer", AuditLog.entity_id == customer_id),
    ]
    if contact_ids:
        from sqlalchemy import or_
        audit_filter.append(
            and_(AuditLog.entity_type == "Contact", AuditLog.entity_id.in_(contact_ids))
        )

    from sqlalchemy import or_
    audit_logs = (
        db.query(AuditLog)
        .filter(or_(*audit_filter))
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    # User-Namen nachladen
    from app.modules.admin.service import _build_user_cache, _enrich_log
    user_ids = list({str(log.user_id) for log in audit_logs if log.user_id})
    user_cache = _build_user_cache(db, user_ids)

    audit_items = [
        {
            "id": str(log.id),
            "source": "audit",
            "type": log.action,
            "description": _timeline_description(log, user_cache),
            "timestamp": log.timestamp.isoformat(),
            "user_id": str(log.user_id) if log.user_id else None,
            "user_name": user_cache.get(str(log.user_id), {}).get("name") if log.user_id else None,
            "entity_type": log.entity_type,
            "old_values": log.old_values,
            "new_values": log.new_values,
        }
        for log in audit_logs
    ]

    # Zusammenführen und sortieren
    timeline = sorted(
        activity_items + audit_items,
        key=lambda x: x["timestamp"],
        reverse=True
    )[:limit]

    return {"customer_id": str(customer_id), "total": len(timeline), "items": timeline}


def _timeline_description(log, user_cache: dict) -> str:
    """Generiert einen lesbaren Text für einen Audit-Log-Eintrag."""
    user_name = user_cache.get(str(log.user_id), {}).get("name", "Unbekannt") if log.user_id else "System"
    entity = log.entity_type

    labels = {
        "create": f"{entity} angelegt von {user_name}",
        "update": f"{entity} bearbeitet von {user_name}",
        "delete": f"{entity} gelöscht von {user_name}",
        "status_change": f"{entity} Status geändert von {user_name}",
        "call": f"Anruf von {user_name}",
        "email": f"E-Mail von {user_name}",
        "message": f"Nachricht von {user_name}",
        "note": f"Notiz von {user_name}",
        "ticket_created": f"Ticket erstellt von {user_name}",
        "ticket_updated": f"Ticket aktualisiert von {user_name}",
        "ticket_closed": f"Ticket geschlossen von {user_name}",
        "upload": f"Dokument hochgeladen von {user_name}",
    }
    return labels.get(log.action, f"{log.action} von {user_name}")
