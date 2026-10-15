# app/modules/portal/models.py
"""
Kundenportal (v5.0) – Magic-Link-Tokens.

Im Klartext existiert der Token nur in der versendeten E-Mail;
gespeichert wird ausschließlich der SHA-256-Hash. Einmalig verwendbar.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.settings.database import Base, generate_uuid


class PortalLoginToken(Base):
    __tablename__ = "portal_login_tokens"
    __table_args__ = (
        Index("ix_portal_login_tokens_contact_id", "contact_id"),
        Index("ix_portal_login_tokens_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    contact_id: Mapped[UUID] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    requested_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    contact = relationship("Contact")
