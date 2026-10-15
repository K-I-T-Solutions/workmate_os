# app/modules/portal/service.py
"""
Kundenportal – Magic-Link-Versand, Verifizierung und Ticket-Zugriff.

Alle Ticket-Abfragen sind auf session.customer_id eingeschränkt.
Interne Kommentare und Ticket-Typen ohne Kundenbezug sind nie sichtbar.
"""
from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.settings.config import settings
from app.modules.backoffice.crm.models import Contact
from app.modules.portal import schemas
from app.modules.portal.models import PortalLoginToken
from app.modules.portal.security import (
    PortalSession,
    create_session_token,
    generate_link_token,
    hash_link_token,
)
from app.modules.support import crud as support_crud
from app.modules.support.models import Ticket, TicketChannel, TicketStatus, TicketType
from app.modules.support.schemas import TicketCommentCreate, TicketCreate, TicketUpdate

logger = logging.getLogger(__name__)

# Max. angeforderte Links pro Kontakt im Zeitfenster
LINK_RATE_LIMIT = 3
LINK_RATE_WINDOW = timedelta(minutes=15)

# Ticket-Typen, die Kunden sehen dürfen
CUSTOMER_VISIBLE_TYPES = (
    TicketType.SUPPORT,
    TicketType.INVOICE_REQUEST,
    TicketType.CUSTOMER_ONBOARDING,
)


# ─── Magic Link ──────────────────────────────────────────────

def _portal_contacts_for_email(db: Session, email: str) -> list[Contact]:
    return (
        db.query(Contact)
        .filter(func.lower(Contact.email) == email.strip().lower(), Contact.portal_enabled.is_(True))
        .all()
    )


def send_link_mail(to_email: str, firstname: str, customer_name: str, link: str) -> bool:
    msg = MIMEMultipart()
    msg["From"] = f"{settings.NOREPLY_SMTP_FROM_NAME} <{settings.NOREPLY_SMTP_FROM}>"
    msg["To"] = to_email
    msg["Subject"] = "Ihr Anmeldelink zum Kundenportal"
    body = (
        f"Hallo {firstname},\n\n"
        f"mit folgendem Link melden Sie sich im Kundenportal für {customer_name} an:\n\n"
        f"{link}\n\n"
        f"Der Link ist {settings.PORTAL_LINK_TTL_MINUTES} Minuten gültig und kann nur einmal verwendet werden.\n"
        f"Falls Sie keinen Link angefordert haben, können Sie diese E-Mail ignorieren.\n\n"
        f"Mit freundlichen Grüßen\n{settings.NOREPLY_SMTP_FROM_NAME}"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(settings.NOREPLY_SMTP_USER, settings.NOREPLY_SMTP_PASSWORD)
            smtp.sendmail(settings.NOREPLY_SMTP_FROM, [to_email], msg.as_string())
        return True
    except Exception:  # noqa: BLE001
        logger.exception("Portal-Link an %s konnte nicht gesendet werden", to_email)
        return False


def issue_link(db: Session, contact: Contact, requested_ip: Optional[str] = None) -> Optional[tuple[str, str]]:
    """
    Legt einen Login-Token an. Returns (Empfänger, Link) oder None bei Rate-Limit.
    Der Versand erfolgt separat (Background-Task), damit die Antwortzeit nichts verrät.
    """
    now = datetime.utcnow()
    recent = (
        db.query(func.count(PortalLoginToken.id))
        .filter(
            PortalLoginToken.contact_id == contact.id,
            PortalLoginToken.created_at >= now - LINK_RATE_WINDOW,
        )
        .scalar()
        or 0
    )
    if recent >= LINK_RATE_LIMIT:
        logger.warning("Portal-Link Rate-Limit für Kontakt %s erreicht", contact.id)
        return None

    token = generate_link_token()
    db.add(PortalLoginToken(
        contact_id=contact.id,
        token_hash=hash_link_token(token),
        expires_at=now + timedelta(minutes=settings.PORTAL_LINK_TTL_MINUTES),
        requested_ip=requested_ip,
        created_at=now,
    ))
    db.commit()
    link = f"{settings.PORTAL_BASE_URL.rstrip('/')}/portal/verify#token={token}"
    return contact.email, link


def request_links(db: Session, email: str, requested_ip: Optional[str] = None) -> list[tuple[str, str, str, str]]:
    """Returns Liste (email, firstname, customer_name, link) – Versand durch Aufrufer."""
    mails = []
    for contact in _portal_contacts_for_email(db, email):
        issued = issue_link(db, contact, requested_ip)
        if issued:
            to, link = issued
            mails.append((to, contact.firstname, contact.customer.name, link))
    return mails


def send_link_mails(mails: list[tuple[str, str, str, str]]) -> None:
    for to, firstname, customer_name, link in mails:
        send_link_mail(to, firstname, customer_name, link)


def verify_link(db: Session, token: str) -> schemas.VerifyResponse:
    invalid = HTTPException(status_code=401, detail="Anmeldelink ungültig oder abgelaufen")
    now = datetime.utcnow()

    # Atomar als benutzt markieren (verhindert doppelte Einlösung bei parallelen Requests)
    row = (
        db.query(PortalLoginToken)
        .filter(PortalLoginToken.token_hash == hash_link_token(token))
        .with_for_update()
        .first()
    )
    if not row or row.used_at is not None or row.expires_at < now:
        db.rollback()
        raise invalid

    contact = db.get(Contact, row.contact_id)
    if not contact or not contact.portal_enabled:
        db.rollback()
        raise invalid

    row.used_at = now
    contact.portal_last_login_at = now
    db.commit()

    access_token, expires = create_session_token(contact)
    return schemas.VerifyResponse(access_token=access_token, expires_at=expires, me=build_me(contact))


def build_me(contact: Contact) -> schemas.PortalMe:
    return schemas.PortalMe(
        contact_id=contact.id,
        firstname=contact.firstname,
        lastname=contact.lastname,
        email=contact.email,
        customer_id=contact.customer_id,
        customer_name=contact.customer.name,
    )


# ─── Tickets ─────────────────────────────────────────────────

def _customer_tickets(db: Session, session: PortalSession):
    return db.query(Ticket).filter(
        Ticket.customer_id == session.customer_id,
        Ticket.deleted_at.is_(None),
        Ticket.type.in_(CUSTOMER_VISIBLE_TYPES),
    )


def list_tickets(db: Session, session: PortalSession, status: Optional[str] = None) -> schemas.PortalTicketList:
    query = _customer_tickets(db, session)
    if status == "open":
        query = query.filter(Ticket.status.notin_([TicketStatus.RESOLVED, TicketStatus.CLOSED]))
    elif status == "closed":
        query = query.filter(Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED]))
    items = query.order_by(Ticket.created_at.desc()).limit(200).all()
    return schemas.PortalTicketList(
        items=[schemas.PortalTicket.model_validate(t) for t in items],
        total=len(items),
    )


def get_ticket(db: Session, session: PortalSession, ticket_id: UUID) -> Ticket:
    ticket = _customer_tickets(db, session).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    return ticket


def ticket_detail(ticket: Ticket) -> schemas.PortalTicketDetail:
    comments = [
        schemas.PortalComment(
            id=c.id,
            content=c.content,
            from_customer=(c.author_id or "").startswith("portal:"),
            created_at=c.created_at,
        )
        for c in ticket.comments
        if not c.is_internal
    ]
    base = schemas.PortalTicket.model_validate(ticket).model_dump()
    return schemas.PortalTicketDetail(**base, description=ticket.description, comments=comments)


def create_ticket(db: Session, session: PortalSession, data: schemas.PortalTicketCreate) -> Ticket:
    return support_crud.create_ticket(
        db,
        TicketCreate(
            title=data.title,
            description=data.description,
            type=TicketType.SUPPORT,
            priority=data.priority,
            channel=TicketChannel.PORTAL,
            customer_id=session.customer_id,
            reporter_email=session.contact.email,
        ),
        reporter_id=session.actor_id,
    )


def add_comment(db: Session, session: PortalSession, ticket: Ticket, data: schemas.PortalCommentCreate):
    comment = support_crud.add_comment(
        db, ticket.id,
        TicketCommentCreate(content=data.content, is_internal=False),
        author_id=session.actor_id,
    )
    # Kundenantwort auf erledigtes Ticket → wieder öffnen
    if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
        support_crud.update_ticket(db, ticket.id, TicketUpdate(status=TicketStatus.OPEN), actor_id=session.actor_id)
    return comment
