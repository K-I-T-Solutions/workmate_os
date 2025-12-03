"""
WorkmateOS - Dashboards Schemas
Pydantic models for dashboard, OS preferences, settings, notifications & activity
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


# ============================================================
# DASHBOARD CORE (Widgets, Layout, Theme)
# ============================================================

class DashboardBase(BaseModel):
    widgets_json: Dict[str, Any] = Field(default_factory=dict)
    layout_json: Dict[str, Any] = Field(default_factory=dict)
    theme: str = "catppuccin-frappe"


class DashboardCreate(DashboardBase):
    owner_id: UUID


class DashboardUpdate(BaseModel):
    widgets_json: Optional[Dict[str, Any]] = None
    layout_json: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None


class DashboardResponse(DashboardBase):
    id: UUID
    owner_id: UUID
    last_accessed: Optional[datetime]

    class Config:
        from_attributes = True


class DashboardListResponse(BaseModel):
    total: int
    dashboards: List[DashboardResponse]


# ============================================================
# OS PREFERENCES (Sidebar, Theme Mode, Dock, Apps)
# ============================================================

class OSPreferencesBase(BaseModel):
    sidebar_collapsed: bool = False
    theme_mode: str = "system"       # light | dark | system
    favorite_apps: List[str] = Field(default_factory=list)
    dock_order: List[str] = Field(default_factory=list)
    wallpaper: Optional[str] = None


class OSPreferencesResponse(OSPreferencesBase):
    owner_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# ============================================================
# USER SETTINGS (Profile Settings)
# ============================================================

class UserSettingsBase(BaseModel):
    language: str = "de-DE"
    timezone: str = "Europe/Berlin"
    notifications_enabled: bool = True


class UserSettingsResponse(UserSettingsBase):
    owner_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# ============================================================
# SYSTEM NOTIFICATIONS
# ============================================================

class NotificationBase(BaseModel):
    title: str
    body: Optional[str] = None
    read: bool = False
    type: str = "info"  # info | warning | error | success
    data: Dict[str, Any] = Field(default_factory=dict)


class Notification(NotificationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# ACTIVITY FEED
# ============================================================

class ActivityEntryBase(BaseModel):
    type: str             # project, invoice, customer, reminder, system
    message: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class ActivityEntry(ActivityEntryBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================================
# FULL RESPONSE (Dashboard + OS + Settings + Stats + Activity)
# ============================================================

class DashboardFullResponse(BaseModel):
    dashboard: DashboardResponse
    os_preferences: OSPreferencesResponse
    user_settings: UserSettingsResponse
    stats: Dict[str, int]
    recent_reminders: List[Dict[str, Any]]
    notifications: List[Notification]
    activity_feed: List[ActivityEntry]

    class Config:
        from_attributes = True
