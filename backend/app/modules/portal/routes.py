# app/modules/portal/routes.py
"""
Kundenportal (v5.0)

Öffentlich:   POST /api/portal/auth/request-link, POST /api/portal/auth/verify
Kunde:        /api/portal/me, /api/portal/tickets…   (Portal-Session-Token)
Intern:       POST /api/portal/admin/contacts/{id}/invite (backoffice.crm.write)
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.core.settings.database import get_db
from app.modules.backoffice.crm.models import Contact
from app.modules.portal import schemas, service
from app.modules.portal.security import PortalSession, get_portal_session

router = APIRouter(prefix="/api/portal", tags=["Kundenportal"])


# ─── Login ───────────────────────────────────────────────────

@router.post("/auth/request-link", response_model=schemas.LinkRequestResponse, status_code=status.HTTP_202_ACCEPTED)
def request_link(
    data: schemas.LinkRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Antwortet immer gleich – verrät nicht, ob die Adresse einen Zugang hat."""
    ip = request.client.host if request.client else None
    mails = service.request_links(db, data.email, requested_ip=ip)
    if mails:
        background_tasks.add_task(service.send_link_mails, mails)
    return schemas.LinkRequestResponse()


@router.post("/auth/verify", response_model=schemas.VerifyResponse)
def verify(data: schemas.VerifyRequest, db: Session = Depends(get_db)):
    return service.verify_link(db, data.token)


# ─── Kundensicht ─────────────────────────────────────────────

@router.get("/me", response_model=schemas.PortalMe)
def me(session: PortalSession = Depends(get_portal_session)):
    return service.build_me(session.contact)


@router.get("/tickets", response_model=schemas.PortalTicketList)
def list_tickets(
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(open|closed)$"),
    db: Session = Depends(get_db),
    session: PortalSession = Depends(get_portal_session),
):
    return service.list_tickets(db, session, status=status_filter)


@router.post("/tickets", response_model=schemas.PortalTicketDetail, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: schemas.PortalTicketCreate,
    db: Session = Depends(get_db),
    session: PortalSession = Depends(get_portal_session),
):
    ticket = service.create_ticket(db, session, data)
    return service.ticket_detail(ticket)


@router.get("/tickets/{ticket_id}", response_model=schemas.PortalTicketDetail)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    session: PortalSession = Depends(get_portal_session),
):
    return service.ticket_detail(service.get_ticket(db, session, ticket_id))


@router.post("/tickets/{ticket_id}/comments", response_model=schemas.PortalTicketDetail, status_code=status.HTTP_201_CREATED)
def add_comment(
    ticket_id: UUID,
    data: schemas.PortalCommentCreate,
    db: Session = Depends(get_db),
    session: PortalSession = Depends(get_portal_session),
):
    ticket = service.get_ticket(db, session, ticket_id)
    service.add_comment(db, session, ticket, data)
    db.refresh(ticket)
    return service.ticket_detail(ticket)


# ─── Intern: Kontakt einladen ────────────────────────────────

@router.post("/admin/contacts/{contact_id}/invite", response_model=schemas.PortalInviteResponse)
@require_permissions(["backoffice.crm.write", "backoffice.crm.*", "backoffice.*"])
def invite_contact(
    contact_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Portal-Zugang aktivieren und sofort einen Anmeldelink senden."""
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nicht gefunden")
    if not contact.email:
        raise HTTPException(status_code=422, detail="Kontakt hat keine E-Mail-Adresse")

    contact.portal_enabled = True
    db.commit()

    issued = service.issue_link(db, contact, requested_ip=request.client.host if request.client else None)
    if not issued:
        raise HTTPException(status_code=429, detail="Zu viele Anmeldelinks – bitte in 15 Minuten erneut versuchen")
    to, link = issued
    sent = service.send_link_mail(to, contact.firstname, contact.customer.name, link)
    return schemas.PortalInviteResponse(contact_id=contact.id, email=to, sent=sent)
