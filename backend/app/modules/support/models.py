"""Support Ticket Models"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.settings.database import Base, generate_uuid


class TicketType:
    SUPPORT = "support"
    VACATION_REQUEST = "vacation_request"
    INVOICE_REQUEST = "invoice_request"
    CUSTOMER_ONBOARDING = "customer_onboarding"
    EMPLOYEE_ONBOARDING = "employee_onboarding"
    EMPLOYEE_OFFBOARDING = "employee_offboarding"
    INTERNAL_TASK = "internal_task"
    STRATEGIC_DECISION = "strategic_decision"


class TicketStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketChannel:
    MAIL = "mail"
    PHONE = "phone"
    SYSTEM = "system"
    MANUAL = "manual"
    LINKEDIN = "linkedin"


class TicketEventType:
    CREATED = "created"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    COMMENT = "comment"
    ESCALATION = "escalation"
    APPROVAL = "approval"
    ATTACHMENT = "attachment"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "support_tickets"
    __table_args__ = (
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_priority", "priority"),
        Index("ix_tickets_type", "type"),
        Index("ix_tickets_assignee_id", "assignee_id"),
        Index("ix_tickets_customer_id", "customer_id"),
        Index("ix_tickets_number", "ticket_number"),
        Index("ix_tickets_deleted_at", "deleted_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    type: Mapped[str] = mapped_column(String(50), default=TicketType.SUPPORT, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=TicketStatus.OPEN, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general")
    channel: Mapped[str] = mapped_column(String(50), default=TicketChannel.MANUAL, nullable=False)

    # Relations
    customer_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    assignee_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reporter_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reporter_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # SLA
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment", back_populates="ticket", cascade="all, delete-orphan",
        order_by="TicketComment.created_at"
    )
    events: Mapped[list["TicketEvent"]] = relationship(
        "TicketEvent", back_populates="ticket",
        order_by="TicketEvent.created_at"
    )
    customer: Mapped[Optional[object]] = relationship("Customer", foreign_keys=[customer_id])


class TicketEvent(Base):
    """Append-only audit log — kein UPDATE, kein DELETE"""
    __tablename__ = "ticket_events"
    __table_args__ = (
        Index("ix_ticket_events_ticket_id", "ticket_id"),
        Index("ix_ticket_events_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    ticket_id: Mapped[UUID] = mapped_column(
        ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="events")


class TicketComment(Base):
    __tablename__ = "support_ticket_comments"
    __table_args__ = (
        Index("ix_ticket_comments_ticket_id", "ticket_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    ticket_id: Mapped[UUID] = mapped_column(
        ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[Optional[str]] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="comments")
