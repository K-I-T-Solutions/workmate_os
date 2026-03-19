"""
Email Intake Service
---------------------
Business-Logik für den E-Mail-Eingang:
- Kontakt matchen oder neu anlegen
- Ticket erstellen und mit Kontakt verknüpfen
- API-Key generieren und verifizieren
- HTML-Body in Plaintext konvertieren (optional)
"""
from __future__ import annotations

import logging
import re
import secrets
import uuid
from datetime import datetime
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.modules.email_intake.models import ApiKey, EmailContact, EmailTicket
from app.modules.email_intake.schemas import EmailIngestRequest, EmailIngestResponse
from app.modules.support.crud import create_ticket as create_support_ticket
from app.modules.support.schemas import TicketCreate

logger = logging.getLogger(__name__)

# Bcrypt-Kontext für API-Key-Hashing
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mapping Postfach → Ticket-Typ
MAILBOX_TO_TYPE: dict[str, str] = {
    "support": "support",
    "kontakt": "anfrage",
    "info": "info",
}


# ---------------------------------------------------------------------------
# HTML → Plaintext
# ---------------------------------------------------------------------------

def _html_to_text(html: str) -> str:
    """
    Einfache HTML-zu-Plaintext-Konvertierung.
    Entfernt Tags und normalisiert Whitespace.
    Wird genutzt wenn kein Plaintext-Part vorhanden ist.
    """
    try:
        import html2text as _h2t
        converter = _h2t.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0  # kein Zeilenumbruch
        return converter.handle(html).strip()
    except ImportError:
        # Fallback: naive Tag-Entfernung
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


def _prepare_body(body: str) -> str:
    """Prüft ob body HTML enthält und konvertiert ggf. zu Plaintext."""
    if body and re.search(r"<[a-z][\s\S]*>", body, re.IGNORECASE):
        return _html_to_text(body)
    return body


# ---------------------------------------------------------------------------
# Kontakt
# ---------------------------------------------------------------------------

def get_or_create_contact(
    db: Session,
    email: str,
    name: Optional[str] = None,
) -> tuple[EmailContact, bool]:
    """
    Sucht einen EmailContact per E-Mail-Adresse.
    Legt ihn an, falls er nicht existiert.

    Returns:
        (contact, created) – created=True wenn neu angelegt
    """
    email_lower = email.strip().lower()

    contact = db.query(EmailContact).filter(
        EmailContact.email == email_lower
    ).first()

    if contact:
        logger.debug("EmailContact gefunden: %s (id=%s)", email_lower, contact.id)
        return contact, False

    contact = EmailContact(
        id=uuid.uuid4(),
        email=email_lower,
        name=name,
    )
    db.add(contact)
    db.flush()  # ID bereits verfügbar, noch kein Commit
    logger.info("Neuer EmailContact angelegt: %s (id=%s)", email_lower, contact.id)
    return contact, True


# ---------------------------------------------------------------------------
# Ticket
# ---------------------------------------------------------------------------

def create_email_ticket(
    db: Session,
    payload: EmailIngestRequest,
    contact: EmailContact,
) -> EmailTicket:
    """Erstellt ein neues EmailTicket und verknüpft es mit dem Kontakt."""
    ticket_type = MAILBOX_TO_TYPE.get(payload.mailbox, payload.mailbox)
    clean_body = _prepare_body(payload.body) if payload.body else None

    ticket = EmailTicket(
        subject=payload.subject,
        body=clean_body,
        from_email=payload.from_email.strip().lower(),
        from_name=payload.from_name,
        source="email",
        mailbox=payload.mailbox,
        ticket_type=ticket_type,
        status="open",
        contact_id=contact.id,
        received_at=payload.received_at,
    )
    db.add(ticket)
    db.flush()
    logger.info(
        "EmailTicket erstellt: id=%s, mailbox=%s, type=%s, contact=%s",
        ticket.id, ticket.mailbox, ticket.ticket_type, contact.email,
    )
    return ticket


# ---------------------------------------------------------------------------
# Ingest-Orchestrierung
# ---------------------------------------------------------------------------

def ingest_email(
    db: Session,
    payload: EmailIngestRequest,
) -> EmailIngestResponse:
    """
    Haupt-Einstiegspunkt für den E-Mail-Ingest:
    1. Kontakt matchen / anlegen
    2. Ticket erstellen
    3. Commit
    4. Antwort aufbauen
    """
    contact, created = get_or_create_contact(
        db,
        email=str(payload.from_email),
        name=payload.from_name,
    )
    ticket = create_email_ticket(db, payload, contact)
    db.commit()
    db.refresh(ticket)

    # Zusätzlich im sichtbaren Support-Ticketsystem anlegen
    name = payload.from_name or "Unbekannt"
    email = str(payload.from_email)
    body_clean = _prepare_body(payload.body) if payload.body else ""

    reply_subject = (payload.subject or '').replace('"', '&quot;')
    description = (
        f"📧 E-Mail-Eingang via {payload.mailbox}@kit-it-koblenz.de\n"
        f"{'─' * 40}\n\n"
        f"👤 Kontakt\n"
        f"  Name:    {name}\n"
        f'  E-Mail:  <a href="mailto:{email}?subject=Re: {reply_subject}">{email}</a>\n\n'
        f"{'─' * 40}\n\n"
        f"💬 Nachricht\n\n"
        f"{body_clean}"
    )
    create_support_ticket(
        db,
        TicketCreate(
            title=payload.subject or "(kein Betreff)",
            description=description,
            category=MAILBOX_TO_TYPE.get(payload.mailbox, payload.mailbox),
            priority="medium",
        ),
        reporter_id=f"email:{payload.from_email}",
    )

    return EmailIngestResponse(
        ticket_id=ticket.id,
        contact_id=contact.id,
        contact_created=created,
        ticket_type=ticket.ticket_type,
        status=ticket.status,
    )


# ---------------------------------------------------------------------------
# API-Key Management
# ---------------------------------------------------------------------------

def generate_api_key() -> str:
    """Generiert einen sicheren, zufälligen API-Key (Präfix wm_)."""
    return "wm_" + secrets.token_urlsafe(32)


def hash_api_key(key: str) -> str:
    """Hashed einen API-Key mit bcrypt."""
    return _pwd_ctx.hash(key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verifiziert einen API-Key gegen seinen Hash."""
    return _pwd_ctx.verify(plain_key, hashed_key)


def create_api_key(
    db: Session,
    name: str,
    scopes: list[str],
) -> tuple[ApiKey, str]:
    """
    Legt einen neuen API-Key an.

    Returns:
        (ApiKey-Objekt, plaintext_key) – plaintext_key wird NICHT gespeichert
    """
    plain_key = generate_api_key()
    key_hash = hash_api_key(plain_key)

    api_key = ApiKey(
        id=uuid.uuid4(),
        name=name,
        key_hash=key_hash,
        scopes=scopes,
        active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    logger.info("API-Key erstellt: name='%s', scopes=%s", name, scopes)
    return api_key, plain_key


def authenticate_api_key(
    db: Session,
    plain_key: str,
    required_scope: Optional[str] = None,
) -> Optional[ApiKey]:
    """
    Prüft einen API-Key gegen die Datenbank.

    Args:
        plain_key:      Klartext-Key aus dem Authorization-Header
        required_scope: Wenn angegeben, muss dieser Scope im Key enthalten sein

    Returns:
        ApiKey wenn gültig, None sonst
    """
    # Alle aktiven Keys laden und hashen vergleichen
    # Hinweis: Bei vielen Keys (>100) sollte ein Key-Präfix als DB-Filter genutzt werden.
    active_keys = db.query(ApiKey).filter(ApiKey.active.is_(True)).all()
    for key_obj in active_keys:
        if verify_api_key(plain_key, key_obj.key_hash):
            if required_scope and required_scope not in (key_obj.scopes or []):
                logger.warning(
                    "API-Key '%s' hat nicht den Scope '%s'", key_obj.name, required_scope
                )
                return None
            return key_obj
    return None
