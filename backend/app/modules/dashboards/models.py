"""
WorkmateOS - Dashboards Module Models
User-specific workspace layout, OS preferences, and activity
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import String, ForeignKey, TIMESTAMP, Boolean

from app.core.settings.database import Base, generate_uuid

if TYPE_CHECKING:
    # Nur für Typing – vermeidet Zirkularimporte
    from app.modules.employees.models import Employee


class Dashboard(Base):
    __tablename__ = "dashboards"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    widgets_json: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    layout_json: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    theme: Mapped[str] = mapped_column(
        String,
        default="catppuccin-frappe",
        nullable=False,
    )

    last_accessed: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=False),
        default=None,
        nullable=True,
    )

    owner: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="dashboards",
    )


class OSPreferences(Base):
    """
    OS-bezogene Einstellungen pro User (WorkmateOS-Shell)
    """
    __tablename__ = "os_preferences"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False,
        unique=True,  # 1:1 zu Employee
    )

    sidebar_collapsed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    theme_mode: Mapped[str] = mapped_column(
        String,
        default="system",  # "light" | "dark" | "system"
        nullable=False,
    )

    favorite_apps: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    dock_order: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    wallpaper: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    owner: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="os_preferences",
    )


class UserSettings(Base):
    """
    Generelle User-Einstellungen (Sprache, Zeitzone, Notifications etc.)
    """
    __tablename__ = "user_settings"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False,
        unique=True,
    )

    language: Mapped[str] = mapped_column(
        String,
        default="de-DE",
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String,
        default="Europe/Berlin",
        nullable=False,
    )

    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    owner: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="user_settings",
    )


class Notification(Base):
    """
    Systemweite Notifications für den User (WorkmateOS Notification Center)
    """
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    type: Mapped[str] = mapped_column(
        String,
        default="info",   # info | warning | error | success
        nullable=False,
    )

    data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )

    read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    owner: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="notifications",
    )


class ActivityEntry(Base):
    """
    Activity Feed Einträge für WorkmateOS (was ist zuletzt passiert?)
    """
    __tablename__ = "activity_entries"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )  # z.B. "project", "invoice", "customer", "reminder", "system"

    message: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    owner: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="activity_entries",
    )
