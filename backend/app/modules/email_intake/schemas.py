"""
Pydantic Schemas für das Email Intake Modul
--------------------------------------------
EmailIngestRequest   – Body für POST /api/v1/email/ingest
EmailIngestResponse  – Antwort nach erfolgreichem Ingest
EmailContactResponse – Kontakt-Darstellung
EmailTicketResponse  – Ticket-Darstellung (mit optionalem Kontakt)
EmailTicketListResponse – Paginierte Ticket-Liste
ApiKeyCreateResponse – Einmalige Rückgabe des Klartext-Keys
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ---------------------------------------------------------------------------
# Validierungs-Konstanten
# ---------------------------------------------------------------------------

VALID_MAILBOXES = {"support", "kontakt", "info"}
VALID_STATUSES = {"open", "in_progress", "closed"}


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

class EmailIngestRequest(BaseModel):
    subject: str
    body: str
    from_email: EmailStr
    from_name: Optional[str] = None
    mailbox: str  # support | kontakt | info
    received_at: Optional[datetime] = None

    @field_validator("mailbox")
    @classmethod
    def validate_mailbox(cls, v: str) -> str:
        if v not in VALID_MAILBOXES:
            raise ValueError(f"mailbox muss einer von {VALID_MAILBOXES} sein")
        return v


class EmailIngestResponse(BaseModel):
    ticket_id: int
    contact_id: uuid.UUID
    contact_created: bool
    ticket_type: str
    status: str


# ---------------------------------------------------------------------------
# Kontakt
# ---------------------------------------------------------------------------

class EmailContactResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Ticket
# ---------------------------------------------------------------------------

class EmailTicketResponse(BaseModel):
    id: int
    subject: str
    body: Optional[str] = None
    from_email: str
    from_name: Optional[str] = None
    source: str
    mailbox: str
    ticket_type: str
    status: str
    contact_id: Optional[uuid.UUID] = None
    received_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    contact: Optional[EmailContactResponse] = None

    model_config = {"from_attributes": True}


class EmailTicketListResponse(BaseModel):
    items: list[EmailTicketResponse]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# API-Key Management
# ---------------------------------------------------------------------------

class ApiKeyCreateResponse(BaseModel):
    id: uuid.UUID
    name: str
    key: str          # Klartext – nur einmalig sichtbar!
    scopes: list[str]
    active: bool
    created_at: datetime
    warning: str = "Diesen Key sicher speichern – er wird nicht erneut angezeigt!"
