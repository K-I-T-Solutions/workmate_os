"""Support Tickets CRUD"""
from datetime import datetime
from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Ticket, TicketComment, TicketEvent, TicketStatus, TicketEventType
from .schemas import TicketCreate, TicketUpdate, TicketCommentCreate


def _next_ticket_number(db: Session) -> str:
    count = db.query(func.count(Ticket.id)).scalar() or 0
    return f"TKT-{count + 1:05d}"


def _log_event(
    db: Session,
    ticket_id: UUID,
    event_type: str,
    actor_id: Optional[str] = None,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    comment: Optional[str] = None,
) -> TicketEvent:
    event = TicketEvent(
        ticket_id=ticket_id,
        event_type=event_type,
        actor_id=actor_id,
        old_value=old_value,
        new_value=new_value,
        comment=comment,
    )
    db.add(event)
    return event


def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    assignee_id: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    search: Optional[str] = None,
    include_deleted: bool = False,
) -> Tuple[List[Ticket], int]:
    query = db.query(Ticket)
    if not include_deleted:
        query = query.filter(Ticket.deleted_at.is_(None))
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if type:
        query = query.filter(Ticket.type == type)
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


def get_ticket(db: Session, ticket_id: UUID, include_deleted: bool = False) -> Optional[Ticket]:
    query = db.query(Ticket).filter(Ticket.id == ticket_id)
    if not include_deleted:
        query = query.filter(Ticket.deleted_at.is_(None))
    return query.first()


def create_ticket(db: Session, data: TicketCreate, reporter_id: Optional[str] = None) -> Ticket:
    ticket = Ticket(
        **data.model_dump(),
        ticket_number=_next_ticket_number(db),
        reporter_id=reporter_id,
    )
    db.add(ticket)
    db.flush()
    _log_event(
        db, ticket.id,
        event_type=TicketEventType.CREATED,
        actor_id=reporter_id,
        new_value={"type": ticket.type, "title": ticket.title, "priority": ticket.priority},
    )
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(
    db: Session, ticket_id: UUID, data: TicketUpdate, actor_id: Optional[str] = None
) -> Optional[Ticket]:
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None

    changes = data.model_dump(exclude_unset=True)
    now = datetime.utcnow()

    # Status-Timestamps
    if changes.get("status") == TicketStatus.RESOLVED and not ticket.resolved_at:
        changes["resolved_at"] = now
    if changes.get("status") == TicketStatus.CLOSED and not ticket.closed_at:
        changes["closed_at"] = now

    # Event Logs pro Änderungstyp
    if "status" in changes and changes["status"] != ticket.status:
        _log_event(db, ticket.id, TicketEventType.STATUS_CHANGE, actor_id=actor_id,
                   old_value={"status": ticket.status}, new_value={"status": changes["status"]})

    if "assignee_id" in changes and changes["assignee_id"] != ticket.assignee_id:
        _log_event(db, ticket.id, TicketEventType.ASSIGNMENT, actor_id=actor_id,
                   old_value={"assignee_id": ticket.assignee_id},
                   new_value={"assignee_id": changes["assignee_id"]})

    for k, v in changes.items():
        setattr(ticket, k, v)

    db.commit()
    db.refresh(ticket)
    return ticket


def soft_delete_ticket(db: Session, ticket_id: UUID, actor_id: Optional[str] = None) -> bool:
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return False
    ticket.deleted_at = datetime.utcnow()
    _log_event(db, ticket.id, TicketEventType.CLOSED, actor_id=actor_id,
               comment="Ticket archiviert (Soft Delete)")
    db.commit()
    return True


def get_events(db: Session, ticket_id: UUID) -> List[TicketEvent]:
    return (
        db.query(TicketEvent)
        .filter(TicketEvent.ticket_id == ticket_id)
        .order_by(TicketEvent.created_at.asc())
        .all()
    )


def get_comment_count(db: Session, ticket_id: UUID) -> int:
    return (
        db.query(func.count(TicketComment.id))
        .filter(TicketComment.ticket_id == ticket_id)
        .scalar() or 0
    )


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
    db.flush()
    _log_event(db, ticket_id, TicketEventType.COMMENT, actor_id=author_id,
               new_value={"is_internal": data.is_internal},
               comment=data.content[:200] if not data.is_internal else "[intern]")
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
