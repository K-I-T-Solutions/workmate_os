# app/modules/backoffice/chat/schemas.py
from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    is_system_message: bool = False
    message_type: str = "text"  # v0.1: nur "text"
    attachment_path: str | None = None


class ChatMessageCreate(ChatMessageBase):
    """
    Payload zum Erstellen einer Chat-Nachricht.
    author_id kommt aus dem aktuellen User (Employee),
    project_id aus der URL.
    """
    pass


class ChatMessageRead(ChatMessageBase):
    id: uuid.UUID
    project_id: uuid.UUID
    author_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True  # für SQLAlchemy-Objekte
