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


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    priority: str = "medium"
    category: str = "general"
    customer_id: Optional[UUID] = None
    assignee_id: Optional[str] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    customer_id: Optional[UUID] = None
    assignee_id: Optional[str] = None


class TicketResponse(BaseModel):
    id: UUID
    ticket_number: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    category: str
    customer_id: Optional[UUID] = None
    assignee_id: Optional[str] = None
    reporter_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    comment_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    comments: List[TicketCommentResponse] = []


class TicketListResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    skip: int
    limit: int
