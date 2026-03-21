"""Support Ticket Models"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.settings.database import Base, generate_uuid


class Ticket(Base):
    __tablename__ = "support_tickets"
    __table_args__ = (
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_priority", "priority"),
        Index("ix_tickets_assignee_id", "assignee_id"),
        Index("ix_tickets_customer_id", "customer_id"),
        Index("ix_tickets_number", "ticket_number"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(50), default="open")
    priority: Mapped[str] = mapped_column(String(50), default="medium")
    category: Mapped[str] = mapped_column(String(50), default="general")

    # Relations (optional)
    customer_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    assignee_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reporter_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reporter_email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="E-Mail des Erstellers für Antwort"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment", back_populates="ticket", cascade="all, delete-orphan",
        order_by="TicketComment.created_at"
    )
    customer: Mapped[Optional[object]] = relationship("Customer", foreign_keys=[customer_id])


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
