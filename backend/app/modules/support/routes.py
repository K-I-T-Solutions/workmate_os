"""Support Tickets API Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.settings.database import get_db
from app.core.auth.roles import require_permissions, get_current_user
from app.core.email.service import send_ticket_reply
from . import crud, schemas

router = APIRouter(prefix="/api/support", tags=["Support"])


@router.get("/tickets", response_model=schemas.TicketListResponse)
@require_permissions(["support.view", "support.*", "*"])
def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items, total = crud.get_tickets(
        db, skip=skip, limit=limit, status=status, priority=priority,
        category=category, assignee_id=assignee_id, customer_id=customer_id, search=search,
    )
    result = []
    for t in items:
        data = schemas.TicketResponse.model_validate(t)
        data.comment_count = crud.get_comment_count(db, t.id)
        result.append(data)
    return {"items": result, "total": total, "skip": skip, "limit": limit}


@router.get("/tickets/{ticket_id}", response_model=schemas.TicketDetailResponse)
@require_permissions(["support.view", "support.*", "*"])
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    data = schemas.TicketDetailResponse.model_validate(ticket)
    data.comment_count = len(ticket.comments)
    return data


@router.post("/tickets", response_model=schemas.TicketResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["support.create", "support.*", "*"])
def create_ticket(
    data: schemas.TicketCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ticket = crud.create_ticket(db, data, reporter_id=user.get("id"))
    result = schemas.TicketResponse.model_validate(ticket)
    result.comment_count = 0
    return result


@router.put("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
@require_permissions(["support.update", "support.*", "*"])
def update_ticket(
    ticket_id: UUID,
    data: schemas.TicketUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ticket = crud.update_ticket(db, ticket_id, data)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    result = schemas.TicketResponse.model_validate(ticket)
    result.comment_count = crud.get_comment_count(db, ticket.id)
    return result


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["support.delete", "support.*", "*"])
def delete_ticket(ticket_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.delete_ticket(db, ticket_id):
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")


@router.post("/tickets/{ticket_id}/comments", response_model=schemas.TicketCommentResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["support.view", "support.*", "*"])
def add_comment(
    ticket_id: UUID,
    data: schemas.TicketCommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not crud.get_ticket(db, ticket_id):
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    return crud.add_comment(db, ticket_id, data, author_id=user.get("id"))


@router.post("/tickets/{ticket_id}/reply")
@require_permissions(["support.update", "support.*", "*"])
async def reply_to_ticket(
    ticket_id: UUID,
    data: schemas.TicketReplyRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Sendet eine E-Mail-Antwort an den Ticket-Ersteller und
    speichert die Antwort als öffentlichen Kommentar.
    """
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")

    if not ticket.reporter_email:
        raise HTTPException(
            status_code=400,
            detail="Keine Empfänger-E-Mail für dieses Ticket gespeichert."
        )

    sent = await send_ticket_reply(
        db=db,
        to_email=ticket.reporter_email,
        ticket_number=ticket.ticket_number,
        ticket_title=ticket.title,
        reply_body=data.body,
    )

    if not sent:
        raise HTTPException(
            status_code=502,
            detail="E-Mail konnte nicht gesendet werden. SMTP-Konfiguration prüfen."
        )

    # Antwort als Kommentar speichern
    comment_data = schemas.TicketCommentCreate(
        content=f"📧 Per E-Mail gesendet an {ticket.reporter_email}:\n\n{data.body}",
        is_internal=False,
    )
    crud.add_comment(db, ticket_id, comment_data, author_id=user.get("id"))

    return {"sent": True, "to": ticket.reporter_email}


@router.delete("/tickets/{ticket_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["support.delete", "support.*", "*"])
def delete_comment(
    ticket_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not crud.delete_comment(db, comment_id):
        raise HTTPException(status_code=404, detail="Kommentar nicht gefunden")
