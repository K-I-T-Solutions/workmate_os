# app/modules/backoffice/chat/crud.py
from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ChatMessage
from .schemas import ChatMessageCreate


def get_project_messages(
    db: Session,
    project_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[ChatMessage]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.project_id == project_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()


def create_message(
    db: Session,
    *,
    project_id: uuid.UUID,
    author_id: uuid.UUID,
    data: ChatMessageCreate,
    reply_to_id: uuid.UUID | None = None,
) -> ChatMessage:
    obj = ChatMessage(
        message=data.message,
        is_system_message=data.is_system_message,
        message_type=data.message_type,
        attachment_path=data.attachment_path,
        project_id=project_id,
        author_id=author_id,
        reply_to_id=reply_to_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
