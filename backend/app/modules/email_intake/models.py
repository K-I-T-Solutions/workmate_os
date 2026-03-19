"""
Email Intake Models
-------------------
EmailContact  – Absender aus dem E-Mail-Eingang (eindeutig per E-Mail)
EmailTicket   – Ticket, das aus einer eingehenden E-Mail erzeugt wird
ApiKey        – Service-API-Keys für externe Dienste (z. B. n8n)
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.settings.database import Base, generate_uuid


class EmailContact(Base):
    """
    Vereinfachter Kontakt für den E-Mail-Eingang.

    Wird beim ersten Auftauchen einer Absender-Adresse automatisch angelegt
    und bei wiederholten Mails gematcht (nicht doppelt erstellt).
    """

    __tablename__ = "email_contacts"
    __table_args__ = (
        Index("ix_email_contacts_email", "email", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    company: Mapped[Optional[str]] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    tickets: Mapped[list[EmailTicket]] = relationship(
        "EmailTicket",
        back_populates="contact",
        cascade="all, delete-orphan",
        order_by="EmailTicket.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<EmailContact(id={self.id}, email='{self.email}')>"


class EmailTicket(Base):
    """
    Ticket aus dem E-Mail-Eingang (via n8n / IMAP-Polling).

    Felder:
        source     – Eingangskanal: "email" | "web" | "manual"
        mailbox    – Quell-Postfach: "support" | "kontakt" | "info"
        ticket_type – Typ des Tickets: "support" | "anfrage" | "info"
        status     – Bearbeitungsstatus: "open" | "in_progress" | "closed"
    """

    __tablename__ = "email_tickets"
    __table_args__ = (
        Index("ix_email_tickets_mailbox", "mailbox"),
        Index("ix_email_tickets_status", "status"),
        Index("ix_email_tickets_ticket_type", "ticket_type"),
        Index("ix_email_tickets_contact_id", "contact_id"),
        Index("ix_email_tickets_from_email", "from_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_name: Mapped[Optional[str]] = mapped_column(String(255))

    # Eingangskanal
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, default="email", server_default="email"
    )
    # Quell-Postfach: support | kontakt | info
    mailbox: Mapped[str] = mapped_column(String(20), nullable=False)
    # Ticket-Typ: support | anfrage | info
    ticket_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Status: open | in_progress | closed
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="open", server_default="open"
    )

    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("email_contacts.id", ondelete="SET NULL"), nullable=True
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    contact: Mapped[Optional[EmailContact]] = relationship(
        "EmailContact", back_populates="tickets"
    )

    def __repr__(self) -> str:
        return (
            f"<EmailTicket(id={self.id}, mailbox='{self.mailbox}', "
            f"type='{self.ticket_type}', status='{self.status}')>"
        )


class ApiKey(Base):
    """
    Service-API-Key für externe Integrationen (z. B. n8n).

    Der Klartext-Key wird nur einmalig beim Erstellen zurückgegeben.
    In der Datenbank wird ausschließlich der bcrypt-Hash gespeichert.

    scopes – JSON-Liste von erlaubten Scopes, z. B. ["email:ingest"]
    """

    __tablename__ = "api_keys"
    __table_args__ = (Index("ix_api_keys_name", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    scopes: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name='{self.name}', active={self.active})>"
