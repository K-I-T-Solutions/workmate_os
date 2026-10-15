# app/modules/portal/schemas.py
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LinkRequest(BaseModel):
    email: EmailStr


class LinkRequestResponse(BaseModel):
    message: str = "Falls ein Portal-Zugang für diese Adresse besteht, wurde ein Anmeldelink versendet."


class VerifyRequest(BaseModel):
    token: str = Field(..., min_length=20, max_length=200)


class PortalMe(BaseModel):
    contact_id: UUID
    firstname: str
    lastname: str
    email: Optional[str] = None
    customer_id: UUID
    customer_name: str


class VerifyResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    me: PortalMe


# ─── Tickets (Kundensicht – ohne interne Felder) ─────────────

class PortalTicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    description: str = Field(..., min_length=1, max_length=20000)
    priority: Literal["low", "medium", "high"] = "medium"


class PortalCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=20000)


class PortalComment(BaseModel):
    id: UUID
    content: str
    from_customer: bool
    created_at: datetime


class PortalTicket(BaseModel):
    id: UUID
    ticket_number: str
    title: str
    status: str
    priority: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class PortalTicketDetail(PortalTicket):
    description: Optional[str] = None
    comments: list[PortalComment] = []


class PortalTicketList(BaseModel):
    items: list[PortalTicket]
    total: int


class PortalInviteResponse(BaseModel):
    contact_id: UUID
    email: str
    sent: bool
