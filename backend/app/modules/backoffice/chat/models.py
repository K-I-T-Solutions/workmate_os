# app/modules/backoffice/chat/models.py
"""
Chat Module Models - WorkmateOS Phase 2.

Verwaltet:
- ChatMessages (Projekt-bezogene Kommunikation)
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.backoffice.projects.models import Project
    from app.modules.employees.models import Employee


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    """
    Chat-Nachrichten für Projekte.

    Ermöglicht projektbezogene Kommunikation zwischen
    Teammitgliedern mit vollständiger Historie.

    Attributes:
        message: Nachrichteninhalt
        author: Verfasser der Nachricht
        project: Zugehöriges Projekt
        is_system_message: Markiert System-Nachrichten (z.B. "Status geändert")
        reply_to_id: Optional Referenz zu einer anderen Nachricht (für Threads)
    """
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_project_id", "project_id"),
        Index("ix_chat_messages_author_id", "author_id"),
        Index("ix_chat_messages_created_at", "created_at"),
        Index("ix_chat_messages_reply_to_id", "reply_to_id"),
    )

    # Business Fields
    message: Mapped[str] = mapped_column(
        Text,
        comment="Nachrichteninhalt"
    )
    is_system_message: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        comment="System-Nachricht (z.B. 'Status geändert zu Active')"
    )
    message_type: Mapped[str] = mapped_column(
        String(50),
        default="text",
        server_default="text",
        comment="Nachrichtentyp (text, file, system)"
    )
    attachment_path: Mapped[str | None] = mapped_column(
        Text,
        comment="Pfad zu angehängter Datei"
    )

    # Foreign Keys
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        comment="Zugehöriges Projekt"
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        comment="Verfasser der Nachricht"
    )
    reply_to_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="SET NULL"),
        comment="Referenz zu einer anderen Nachricht (für Threads)"
    )

    # Relationships
    project: Mapped[Project] = relationship(
        "Project",
        back_populates="chat_messages"
    )
    author: Mapped[Employee] = relationship(
        "Employee",
        back_populates="chat_messages",
        foreign_keys=[author_id]
    )
    reply_to: Mapped[ChatMessage | None] = relationship(
        "ChatMessage",
        remote_side="ChatMessage.id",
        back_populates="replies"
    )
    replies: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage",
        back_populates="reply_to",
        cascade="all, delete-orphan"
    )

    @property
    def is_reply(self) -> bool:
        """
        Prüft ob Nachricht eine Antwort ist.

        Returns:
            True wenn reply_to_id gesetzt ist
        """
        return self.reply_to_id is not None

    def __repr__(self) -> str:
        message_preview = (
            self.message[:50] + "..."
            if len(self.message) > 50
            else self.message
        )
        return (
            f"<ChatMessage(author='{self.author.firstname if self.author else 'Unknown'}', "
            f"message='{message_preview}')>"
        )
