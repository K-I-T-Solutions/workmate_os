"""
WorkmateOS - Dashboards CRUD Operations (SQLAlchemy 2.x Compatible)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.modules.dashboards.models import (
    Dashboard,
    OSPreferences,
    UserSettings,
    Notification,
    ActivityEntry,
)
from app.modules.dashboards.schemas import DashboardCreate, DashboardUpdate


# ================================================================
# BASIC DASHBOARD CRUD
# ================================================================

def get_dashboard(db: Session, dashboard_id: UUID) -> Optional[Dashboard]:
    return db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()


def get_dashboard_by_owner(db: Session, owner_id: UUID) -> Optional[Dashboard]:
    return db.query(Dashboard).filter(Dashboard.owner_id == owner_id).first()


def get_dashboards(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[Dashboard], int]:
    query = db.query(Dashboard)
    total = query.count()
    dashboards = query.offset(skip).limit(limit).all()
    return dashboards, total


def create_dashboard(db: Session, dashboard: DashboardCreate) -> Dashboard:
    db_dashboard = Dashboard(**dashboard.model_dump())
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


def update_dashboard(
    db: Session,
    dashboard_id: UUID,
    dashboard_update: DashboardUpdate,
) -> Optional[Dashboard]:
    db_dashboard = get_dashboard(db, dashboard_id)
    if not db_dashboard:
        return None

    for field, value in dashboard_update.model_dump(exclude_unset=True).items():
        setattr(db_dashboard, field, value)

    db_dashboard.last_accessed = datetime.utcnow()
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


def delete_dashboard(db: Session, dashboard_id: UUID) -> bool:
    db_dashboard = get_dashboard(db, dashboard_id)
    if not db_dashboard:
        return False
    db.delete(db_dashboard)
    db.commit()
    return True


def touch_dashboard(db: Session, dashboard_id: UUID) -> Optional[Dashboard]:
    db_dashboard = get_dashboard(db, dashboard_id)
    if not db_dashboard:
        return None
    db_dashboard.last_accessed = datetime.utcnow()
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


def get_or_create_dashboard_for_owner(
    db: Session,
    owner_id: UUID,
) -> Dashboard:
    dashboard = get_dashboard_by_owner(db, owner_id)
    if dashboard:
        touch_dashboard(db, dashboard.id)
        return dashboard

    # Default-Layout & Widgets für neue User
    dashboard_create = DashboardCreate(
        owner_id=owner_id,
        widgets_json={
            "stats": {"enabled": True, "type": "stats"},
            "recentReminders": {"enabled": True, "type": "reminders"},
            "shortcuts": {"enabled": True, "type": "actions"},
        },
        layout_json={
            "stats": {"x": 0, "y": 0, "w": 3, "h": 2},
            "recentReminders": {"x": 3, "y": 0, "w": 3, "h": 2},
            "shortcuts": {"x": 0, "y": 2, "w": 6, "h": 1},
        },
    )
    return create_dashboard(db, dashboard_create)


# ================================================================
# OS PREFERENCES & USER SETTINGS
# ================================================================

def get_or_create_os_preferences(db: Session, owner_id: UUID) -> OSPreferences:
    prefs = db.query(OSPreferences).filter(OSPreferences.owner_id == owner_id).first()
    if prefs:
        return prefs

    prefs = OSPreferences(
        owner_id=owner_id,
        sidebar_collapsed=False,
        theme_mode="system",
        favorite_apps=[],
        dock_order=["crm", "projects", "time_tracking", "invoices", "finance"],
        wallpaper=None,
    )
    db.add(prefs)
    db.commit()
    db.refresh(prefs)
    return prefs


def get_or_create_user_settings(db: Session, owner_id: UUID) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.owner_id == owner_id).first()
    if settings:
        return settings

    settings = UserSettings(
        owner_id=owner_id,
        language="de-DE",
        timezone="Europe/Berlin",
        notifications_enabled=True,
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


# ================================================================
# LIVE DASHBOARD DATA
# ================================================================

def get_dashboard_stats(db: Session, owner_id: UUID) -> Dict[str, int]:
    # Active Projects
    projects = db.execute(
        text("SELECT COUNT(*) FROM projects WHERE status='active'")
    ).scalar() or 0

    # Pending Invoices
    invoices = db.execute(
        text("SELECT COUNT(*) FROM invoices WHERE status='sent'")
    ).scalar() or 0

    # Registered Customers
    customers = db.execute(
        text("SELECT COUNT(*) FROM customers WHERE status='active'")
    ).scalar() or 0

    # Open Reminders
    reminders = db.execute(
        text("""
            SELECT COUNT(*)
            FROM reminders
            WHERE owner_id = :oid
              AND status = 'open'
        """),
        {"oid": str(owner_id)},
    ).scalar() or 0

    return {
        "activeProjects": projects,
        "pendingInvoices": invoices,
        "registeredCustomers": customers,
        "openReminders": reminders,
    }


def get_recent_reminders(db: Session, owner_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT id, title, priority, due_date
            FROM reminders
            WHERE owner_id = :oid
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        {"oid": str(owner_id), "limit": limit},
    )
    return list(result.mappings().all())


def get_notifications_for_owner(
    db: Session,
    owner_id: UUID,
    limit: int = 10,
) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.owner_id == owner_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def get_activity_for_owner(
    db: Session,
    owner_id: UUID,
    limit: int = 20,
) -> List[ActivityEntry]:
    return (
        db.query(ActivityEntry)
        .filter(ActivityEntry.owner_id == owner_id)
        .order_by(ActivityEntry.timestamp.desc())
        .limit(limit)
        .all()
    )


# ================================================================
# FULL DASHBOARD VIEW (für /dashboards/my-dashboard)
# ================================================================

def get_full_dashboard(
    db: Session,
    owner_id: UUID,
) -> Dict[str, Any]:
    """
    Aggregiert:
    - Dashboard (layout, widgets, theme)
    - OS Preferences
    - User Settings
    - Stats
    - Recent Reminders
    - Notifications
    - Activity Feed
    """
    dashboard = get_or_create_dashboard_for_owner(db, owner_id)
    os_prefs = get_or_create_os_preferences(db, owner_id)
    user_settings = get_or_create_user_settings(db, owner_id)
    stats = get_dashboard_stats(db, owner_id)
    recent_reminders = get_recent_reminders(db, owner_id, limit=5)
    notifications = get_notifications_for_owner(db, owner_id, limit=10)
    activity = get_activity_for_owner(db, owner_id, limit=20)

    return {
        "dashboard": dashboard,
        "os_preferences": os_prefs,
        "user_settings": user_settings,
        "stats": stats,
        "recent_reminders": recent_reminders,
        "notifications": notifications,
        "activity_feed": activity,
    }
