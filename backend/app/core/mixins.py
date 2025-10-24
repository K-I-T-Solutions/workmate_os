# app/core/mixins.py
"""
Zentrale SQLAlchemy Mixins für WorkmateOS.

Diese Mixins werden von allen Models verwendet um konsistente
ID- und Timestamp-Felder zu gewährleisten.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """
    Mixin für UUID Primary Key.
    
    Verwendet UUID v4 für alle Entities.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )


class TimestampMixin:
    """
    Mixin für automatische Zeitstempel.
    
    Verwendet PostgreSQL server_default für konsistente
    Timestamps unabhängig von der Anwendungslogik.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )