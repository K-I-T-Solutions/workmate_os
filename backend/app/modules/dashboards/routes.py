"""
WorkmateOS - Dashboards API Routes
REST endpoints for user dashboard configuration
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.modules.dashboards import crud, schemas

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get("", response_model=schemas.DashboardListResponse)
def list_dashboards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    dashboards, total = crud.get_dashboards(db, skip=skip, limit=limit)
    return {
        "total": total,
        "dashboards": dashboards,
    }


@router.get("/my-dashboard", response_model=schemas.DashboardFullResponse)
def get_my_dashboard(
    owner_id: UUID = Query(..., description="Current user's UUID"),
    db: Session = Depends(get_db),
):
    """
    Vollständiges WorkmateOS-Dashboard für den aktuellen User:
    - Dashboard (widgets + layout + theme)
    - OS Preferences
    - User Settings
    - Stats
    - Recent Reminders
    - Notifications
    - Activity Feed
    """
    full = crud.get_full_dashboard(db, owner_id)
    return full


@router.get("/{dashboard_id}", response_model=schemas.DashboardResponse)
def get_dashboard(
    dashboard_id: UUID,
    db: Session = Depends(get_db),
):
    dashboard = crud.get_dashboard(db, dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    crud.touch_dashboard(db, dashboard_id)
    return dashboard


@router.post("", response_model=schemas.DashboardResponse, status_code=201)
def create_dashboard(
    dashboard: schemas.DashboardCreate,
    db: Session = Depends(get_db),
):
    existing = crud.get_dashboard_by_owner(db, dashboard.owner_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already has a dashboard. Use PUT to update.",
        )
    return crud.create_dashboard(db, dashboard)


@router.put("/{dashboard_id}", response_model=schemas.DashboardResponse)
def update_dashboard(
    dashboard_id: UUID,
    dashboard_update: schemas.DashboardUpdate,
    db: Session = Depends(get_db),
):
    dashboard = crud.update_dashboard(db, dashboard_id, dashboard_update)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.delete("/{dashboard_id}", status_code=204)
def delete_dashboard(
    dashboard_id: UUID,
    db: Session = Depends(get_db),
):
    success = crud.delete_dashboard(db, dashboard_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return None
