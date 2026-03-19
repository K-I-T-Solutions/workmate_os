"""
Email Intake API Routes
------------------------
POST /api/v1/email/ingest            – E-Mail entgegennehmen (n8n)
GET  /api/v1/email/tickets           – Tickets auflisten
GET  /api/v1/email/tickets/{id}      – Einzelticket
GET  /api/v1/email/contacts          – Kontakt per E-Mail suchen
POST /api/v1/email/admin/keys        – API-Key anlegen (nur Admin)
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth.roles import get_current_user, require_permissions
from app.core.settings.database import get_db
from app.modules.email_intake import schemas, service
from app.modules.email_intake.auth import require_api_key
from app.modules.email_intake.models import EmailContact, EmailTicket

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/email", tags=["Email Intake"])


# ---------------------------------------------------------------------------
# POST /ingest
# ---------------------------------------------------------------------------

@router.post(
    "/ingest",
    response_model=schemas.EmailIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="E-Mail entgegennehmen und Ticket erstellen",
)
def ingest_email(
    payload: schemas.EmailIngestRequest,
    db: Session = Depends(get_db),
    _api_key=Depends(require_api_key),
):
    """
    Nimmt eine eingehende E-Mail entgegen (via n8n IMAP-Trigger):
    - Matched oder erstellt einen EmailContact anhand der from_email
    - Erstellt ein EmailTicket mit korrektem ticket_type (mailbox-abhängig)
    - Verknüpft Ticket mit Kontakt
    - Gibt ticket_id, contact_id und Metadaten zurück
    """
    try:
        result = service.ingest_email(db, payload)
        logger.info(
            "Ingest abgeschlossen: ticket_id=%s, contact_id=%s, mailbox=%s",
            result.ticket_id, result.contact_id, payload.mailbox,
        )
        return result
    except Exception as exc:
        logger.error("Ingest-Fehler: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Verarbeiten der E-Mail",
        ) from exc


# ---------------------------------------------------------------------------
# GET /tickets
# ---------------------------------------------------------------------------

@router.get(
    "/tickets",
    response_model=schemas.EmailTicketListResponse,
    summary="Alle Email-Tickets auflisten",
)
@require_permissions(["support.view", "support.*", "*"])
def list_tickets(
    mailbox: str | None = Query(None, description="support | kontakt | info"),
    status_filter: str | None = Query(None, alias="status", description="open | in_progress | closed"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Listet EmailTickets mit optionaler Filterung nach mailbox und status."""
    query = db.query(EmailTicket)

    if mailbox:
        query = query.filter(EmailTicket.mailbox == mailbox)
    if status_filter:
        query = query.filter(EmailTicket.status == status_filter)

    total = query.count()
    items = (
        query.order_by(EmailTicket.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return schemas.EmailTicketListResponse(
        items=[schemas.EmailTicketResponse.model_validate(t) for t in items],
        total=total,
        skip=offset,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# GET /tickets/{ticket_id}
# ---------------------------------------------------------------------------

@router.get(
    "/tickets/{ticket_id}",
    response_model=schemas.EmailTicketResponse,
    summary="Einzelnes Ticket abrufen",
)
@require_permissions(["support.view", "support.*", "*"])
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Gibt ein einzelnes EmailTicket inkl. zugehörigem Kontakt zurück."""
    ticket = db.query(EmailTicket).filter(EmailTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    return schemas.EmailTicketResponse.model_validate(ticket)


# ---------------------------------------------------------------------------
# GET /contacts
# ---------------------------------------------------------------------------

@router.get(
    "/contacts",
    response_model=schemas.EmailContactResponse,
    summary="Kontakt per E-Mail suchen",
)
@require_permissions(["support.view", "support.*", "*"])
def get_contact_by_email(
    email: str = Query(..., description="E-Mail-Adresse des Kontakts"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Sucht einen EmailContact anhand der E-Mail-Adresse."""
    contact = (
        db.query(EmailContact)
        .filter(EmailContact.email == email.strip().lower())
        .first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nicht gefunden")
    return schemas.EmailContactResponse.model_validate(contact)


# ---------------------------------------------------------------------------
# POST /admin/keys – API-Key anlegen (nur für Admins mit JWT-Auth)
# ---------------------------------------------------------------------------

@router.post(
    "/admin/keys",
    response_model=schemas.ApiKeyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Neuen Service-API-Key erstellen (einmalig)",
)
@require_permissions(["admin.*", "*"])
def create_api_key(
    name: str = Query(..., description="Bezeichnung des Keys (z. B. 'n8n-email-intake')"),
    scopes: str = Query("email:ingest", description="Kommagetrennte Scopes"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Erstellt einen neuen API-Key für externe Service-Accounts.

    Der Klartext-Key wird **nur einmalig** in der Antwort zurückgegeben
    und anschließend **nicht mehr** abfragbar (nur Hash gespeichert).

    Scope-Format: 'email:ingest' (kommagetrennt für mehrere Scopes)
    """
    scope_list = [s.strip() for s in scopes.split(",") if s.strip()]
    api_key_obj, plain_key = service.create_api_key(db, name=name, scopes=scope_list)
    logger.info(
        "API-Key '%s' von User %s erstellt", name, user.get("email", "unknown")
    )
    return schemas.ApiKeyCreateResponse(
        id=api_key_obj.id,
        name=api_key_obj.name,
        key=plain_key,
        scopes=api_key_obj.scopes or [],
        active=api_key_obj.active,
        created_at=api_key_obj.created_at,
    )
