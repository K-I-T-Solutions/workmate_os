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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.settings.config import settings
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
# Ausgehende E-Mails
# ---------------------------------------------------------------------------

def send_confirmation_email(
    to_email: str,
    to_name: str,
    ticket_number: str,
    subject: str,
) -> None:
    """Sendet eine Bestätigungsmail an den Kunden nach Ticket-Erstellung."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Ihre Anfrage wurde erhalten – {ticket_number}"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        msg["To"] = to_email
        msg["References"] = f"<{ticket_number}@kit-it-koblenz.de>"

        text_body = f"""Hallo {to_name},

vielen Dank fuer Ihre Nachricht. Wir haben Ihre Anfrage erhalten und bearbeiten sie so schnell wie moeglich.

Ihre Ticketnummer: {ticket_number}
Betreff: {subject}

Bitte verwenden Sie bei weiteren Rueckfragen Ihre Ticketnummer als Referenz.

Mit freundlichen Gruessen
K.I.T. Solutions Support-Team
support@kit-it-koblenz.de
"""

        html_body = f"""<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; background: #0a0f1e; font-family: 'Segoe UI', Arial, sans-serif;">
  <div style="max-width: 600px; margin: 0 auto; padding: 24px 16px;">
    <!-- Gradient top bar -->
    <div style="height: 4px; background: linear-gradient(90deg, #FF6B35 0%, #3B82F6 50%, #06B6D4 100%); border-radius: 4px 4px 0 0;"></div>
    <!-- Header -->
    <div style="background: #0F1629; padding: 28px 32px 24px; border-left: 1px solid #1E2D4A; border-right: 1px solid #1E2D4A;">
      <table cellpadding="0" cellspacing="0" style="width: 100%;">
        <tr>
          <td>
            <span style="font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">K.I.T.</span>
            <span style="font-size: 22px; font-weight: 300; color: #FF6B35;"> Solutions</span>
            <p style="margin: 4px 0 0; color: #64748b; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase;">Support-Team</p>
          </td>
          <td style="text-align: right;">
            <div style="width: 3px; height: 40px; background: linear-gradient(180deg, #FF6B35, #3B82F6); display: inline-block; border-radius: 2px;"></div>
          </td>
        </tr>
      </table>
    </div>
    <!-- Content -->
    <div style="background: #1E2D4A; padding: 32px; border-left: 1px solid #263a5a; border-right: 1px solid #263a5a;">
      <p style="color: #e2e8f0; font-size: 16px; margin: 0 0 12px;">Hallo {to_name},</p>
      <p style="color: #94a3b8; font-size: 15px; line-height: 1.6; margin: 0 0 24px;">vielen Dank fuer Ihre Nachricht. Wir haben Ihre Anfrage erhalten und bearbeiten sie so schnell wie moeglich.</p>

      <!-- Ticket card -->
      <div style="background: #0F1629; border: 1px solid #263a5a; border-left: 4px solid #FF6B35; border-radius: 8px; padding: 20px 24px; margin: 0 0 24px;">
        <p style="margin: 0 0 6px; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em;">Ihre Ticketnummer</p>
        <p style="margin: 0 0 8px; font-size: 26px; font-weight: 700; color: #FF6B35; letter-spacing: 0.08em; font-family: 'Courier New', monospace;">{ticket_number}</p>
        <p style="margin: 0; color: #94a3b8; font-size: 14px; border-top: 1px solid #1E2D4A; padding-top: 10px;">{subject}</p>
      </div>

      <p style="color: #94a3b8; font-size: 14px; line-height: 1.6; margin: 0;">Bitte verwenden Sie bei weiteren Rueckfragen Ihre Ticketnummer als Referenz.</p>
    </div>
    <!-- Footer -->
    <div style="background: #0F1629; padding: 20px 32px; border: 1px solid #1E2D4A; border-top: none; border-radius: 0 0 4px 4px;">
      <p style="margin: 0; color: #475569; font-size: 12px; line-height: 1.6;">
        <span style="color: #FF6B35; font-weight: 600;">K.I.T. Solutions</span> &bull;
        <a href="mailto:support@kit-it-koblenz.de" style="color: #3B82F6; text-decoration: none;">support@kit-it-koblenz.de</a>
      </p>
    </div>
    <!-- Bottom gradient line -->
    <div style="height: 2px; background: linear-gradient(90deg, #06B6D4 0%, #3B82F6 50%, #FF6B35 100%); border-radius: 0 0 4px 4px;"></div>
  </div>
</body>
</html>"""

        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())

        logger.info("Bestätigungsmail gesendet an %s (Ticket: %s)", to_email, ticket_number)
    except Exception as exc:
        logger.error("Bestätigungsmail fehlgeschlagen: %s", exc)


def send_reply_email(
    to_email: str,
    to_name: str,
    subject: str,
    body: str,
    agent_name: str = "Support",
) -> None:
    """Sendet eine Antwort-Mail an den Kunden."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        msg["To"] = to_email

        html_body = f"""<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; background: #0a0f1e; font-family: 'Segoe UI', Arial, sans-serif;">
  <div style="max-width: 600px; margin: 0 auto; padding: 24px 16px;">
    <!-- Gradient top bar -->
    <div style="height: 4px; background: linear-gradient(90deg, #FF6B35 0%, #3B82F6 50%, #06B6D4 100%); border-radius: 4px 4px 0 0;"></div>
    <!-- Header -->
    <div style="background: #0F1629; padding: 28px 32px 24px; border-left: 1px solid #1E2D4A; border-right: 1px solid #1E2D4A;">
      <table cellpadding="0" cellspacing="0" style="width: 100%;">
        <tr>
          <td>
            <span style="font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">K.I.T.</span>
            <span style="font-size: 22px; font-weight: 300; color: #FF6B35;"> Solutions</span>
            <p style="margin: 4px 0 0; color: #64748b; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase;">Support-Team</p>
          </td>
          <td style="text-align: right;">
            <div style="width: 3px; height: 40px; background: linear-gradient(180deg, #FF6B35, #3B82F6); display: inline-block; border-radius: 2px;"></div>
          </td>
        </tr>
      </table>
    </div>
    <!-- Content -->
    <div style="background: #1E2D4A; padding: 32px; border-left: 1px solid #263a5a; border-right: 1px solid #263a5a;">
      <p style="color: #e2e8f0; font-size: 16px; margin: 0 0 20px;">Hallo {to_name or ""},</p>
      <div style="color: #cbd5e1; font-size: 15px; line-height: 1.8; white-space: pre-wrap; background: #0F1629; border: 1px solid #263a5a; border-left: 4px solid #3B82F6; border-radius: 8px; padding: 20px 24px; margin: 0 0 24px;">{body}</div>
    </div>
    <!-- Agent footer -->
    <div style="background: #0F1629; padding: 20px 32px; border: 1px solid #1E2D4A; border-top: none; border-radius: 0 0 4px 4px;">
      <p style="margin: 0; color: #475569; font-size: 12px; line-height: 1.8;">
        <span style="color: #e2e8f0; font-weight: 600;">{agent_name}</span><br>
        <span style="color: #FF6B35; font-weight: 600;">K.I.T. Solutions</span> Support &bull;
        <a href="mailto:support@kit-it-koblenz.de" style="color: #3B82F6; text-decoration: none;">support@kit-it-koblenz.de</a>
      </p>
    </div>
    <!-- Bottom gradient line -->
    <div style="height: 2px; background: linear-gradient(90deg, #06B6D4 0%, #3B82F6 50%, #FF6B35 100%); border-radius: 0 0 4px 4px;"></div>
  </div>
</body>
</html>"""

        msg.attach(MIMEText(body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())

        logger.info("Antwort-Mail gesendet an %s", to_email)
    except Exception as exc:
        logger.error("Antwort-Mail fehlgeschlagen: %s", exc)
        raise


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
    support_ticket = create_support_ticket(
        db,
        TicketCreate(
            title=payload.subject or "(kein Betreff)",
            description=description,
            category=MAILBOX_TO_TYPE.get(payload.mailbox, payload.mailbox),
            priority="medium",
            reporter_email=str(payload.from_email).strip().lower(),
        ),
        reporter_id=f"email:{payload.from_email}",
    )

    # Ticketnummer in Beschreibung nachträglich ergänzen
    support_ticket.description = (
        f"🎫 Ticket: {support_ticket.ticket_number}\n"
        + support_ticket.description
    )
    db.commit()

    # Bestätigungsmail an Kunden
    if support_ticket:
        send_confirmation_email(
            to_email=email,
            to_name=name,
            ticket_number=support_ticket.ticket_number,
            subject=payload.subject or "(kein Betreff)",
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
