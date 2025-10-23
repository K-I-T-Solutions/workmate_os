"""
WorkmateOS - Dashboards CRUD Operations
Database operations for user dashboards
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.modules.dashboards.models import Dashboard
from app.modules.dashboards.schemas import DashboardCreate, DashboardUpdate


def get_dashboard(db: Session, dashboard_id: UUID) -> Optional[Dashboard]:
    """Get dashboard by ID"""
    return db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()


def get_dashboard_by_owner(db: Session, owner_id: UUID) -> Optional[Dashboard]:
    """Get dashboard by owner (user typically has one dashboard)"""
    return db.query(Dashboard).filter(Dashboard.owner_id == owner_id).first()


def get_dashboards(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> tuple[list[Dashboard], int]:
    """
    Get all dashboards with pagination
    Returns: (dashboards list, total count)
    """
    query = db.query(Dashboard)
    
    total = query.count()
    dashboards = query.offset(skip).limit(limit).all()
    
    return dashboards, total


def create_dashboard(db: Session, dashboard: DashboardCreate) -> Dashboard:
    """Create new dashboard"""
    db_dashboard = Dashboard(**dashboard.model_dump())
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


def update_dashboard(
    db: Session,
    dashboard_id: UUID,
    dashboard_update: DashboardUpdate
) -> Optional[Dashboard]:
    """Update dashboard"""
    db_dashboard = get_dashboard(db, dashboard_id)
    if db_dashboard is None:
        return None
    
    update_data = dashboard_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dashboard, field, value)
    
    # Update last_accessed
    db_dashboard.last_accessed = datetime.utcnow()  # type: ignore[assignment]
    
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


def delete_dashboard(db: Session, dashboard_id: UUID) -> bool:
    """Delete dashboard"""
    db_dashboard = get_dashboard(db, dashboard_id)
    if db_dashboard is None:
        return False
    
    db.delete(db_dashboard)
    db.commit()
    return True


def touch_dashboard(db: Session, dashboard_id: UUID) -> Optional[Dashboard]:
    """Update last_accessed timestamp"""
    db_dashboard = get_dashboard(db, dashboard_id)
    if db_dashboard is None:
        return None
    
    db_dashboard.last_accessed = datetime.utcnow()  # type: ignore[assignment]
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard