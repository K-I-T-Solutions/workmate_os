"""Support Ticket Schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TicketCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_internal: bool = False


class TicketCommentResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    author_id: Optional[str] = None
    content: str
    is_internal: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TicketEventResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    event_type: str
    actor_id: Optional[str] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    comment: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    type: str = "support"
    priority: str = "medium"
    category: str = "general"
    channel: str = "manual"
    customer_id: Optional[UUID] = None
    assignee_id: Optional[str] = None
    reporter_email: Optional[str] = None
    sla_deadline: Optional[datetime] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    channel: Optional[str] = None
    customer_id: Optional[UUID] = None
    assignee_id: Optional[str] = None
    reporter_email: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    sla_breached: Optional[bool] = None


class TicketReplyRequest(BaseModel):
    body: str = Field(..., min_length=1)


class TicketResponse(BaseModel):
    id: UUID
    ticket_number: str
    title: str
    description: Optional[str] = None
    type: str
    status: str
    priority: str
    category: str
    channel: str
    customer_id: Optional[UUID] = None
    assignee_id: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_email: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    sla_breached: bool = False
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    comment_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    comments: List[TicketCommentResponse] = []
    events: List[TicketEventResponse] = []


class TicketListResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    skip: int
    limit: int
