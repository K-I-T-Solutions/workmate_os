"""Support Tickets CRUD"""
from datetime import datetime
from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from .models import Ticket, TicketComment
from .schemas import TicketCreate, TicketUpdate, TicketCommentCreate


def _next_ticket_number(db: Session) -> str:
    count = db.query(func.count(Ticket.id)).scalar() or 0
    return f"TKT-{count + 1:05d}"


def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assignee_id: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    search: Optional[str] = None,
) -> Tuple[List[Ticket], int]:
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if assignee_id:
        query = query.filter(Ticket.assignee_id == assignee_id)
    if customer_id:
        query = query.filter(Ticket.customer_id == customer_id)
    if search:
        query = query.filter(
            Ticket.title.ilike(f"%{search}%") | Ticket.description.ilike(f"%{search}%")
        )
    total = query.count()
    items = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_ticket(db: Session, ticket_id: UUID) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_ticket_by_number(db: Session, number: str) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.ticket_number == number).first()


def create_ticket(db: Session, data: TicketCreate, reporter_id: Optional[str] = None) -> Ticket:
    ticket = Ticket(
        **data.model_dump(),
        ticket_number=_next_ticket_number(db),
        reporter_id=reporter_id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(db: Session, ticket_id: UUID, data: TicketUpdate) -> Optional[Ticket]:
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None
    changes = data.model_dump(exclude_unset=True)
    now = datetime.utcnow()
    if changes.get("status") == "resolved" and not ticket.resolved_at:
        changes["resolved_at"] = now
    if changes.get("status") == "closed" and not ticket.closed_at:
        changes["closed_at"] = now
    for k, v in changes.items():
        setattr(ticket, k, v)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: UUID) -> bool:
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return False
    db.delete(ticket)
    db.commit()
    return True


def get_comment_count(db: Session, ticket_id: UUID) -> int:
    return db.query(func.count(TicketComment.id)).filter(TicketComment.ticket_id == ticket_id).scalar() or 0


def add_comment(
    db: Session, ticket_id: UUID, data: TicketCommentCreate, author_id: Optional[str] = None
) -> TicketComment:
    comment = TicketComment(
        ticket_id=ticket_id,
        content=data.content,
        is_internal=data.is_internal,
        author_id=author_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: UUID) -> bool:
    comment = db.query(TicketComment).filter(TicketComment.id == comment_id).first()
    if not comment:
        return False
    db.delete(comment)
    db.commit()
    return True
