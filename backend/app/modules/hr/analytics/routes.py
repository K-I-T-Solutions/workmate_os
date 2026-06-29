"""
HR Analytics Routes
Aggregierte HR-Kennzahlen ohne eigene Tabellen.
"""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions


router = APIRouter(prefix="/analytics", tags=["HR Analytics"])


@router.get("/headcount")
@require_permissions(["hr.view"])
async def headcount(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Headcount-Übersicht: gesamt, aktiv, nach Abteilung und Beschäftigungsart
    (benötigt: hr.view)
    """
    from app.modules.employees.models import Employee, Department

    total = db.query(func.count(Employee.id)).scalar() or 0
    active = db.query(func.count(Employee.id)).filter(Employee.status == "active").scalar() or 0

    # Nach Abteilung
    dept_rows = (
        db.query(Department.name, func.count(Employee.id).label("cnt"))
        .join(Employee, Employee.department_id == Department.id, isouter=True)
        .group_by(Department.name)
        .all()
    )
    by_department = {row.name: row.cnt for row in dept_rows}

    # Nach Beschäftigungsart
    type_rows = (
        db.query(Employee.employment_type, func.count(Employee.id).label("cnt"))
        .filter(Employee.employment_type.isnot(None))
        .group_by(Employee.employment_type)
        .all()
    )
    by_employment_type = {row.employment_type: row.cnt for row in type_rows}

    return {
        "total": total,
        "active": active,
        "by_department": by_department,
        "by_employment_type": by_employment_type,
    }


@router.get("/leave-summary")
@require_permissions(["hr.view"])
async def leave_summary(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Urlaubs-Zusammenfassung: offene Anträge, genehmigt diesen Monat, Tage dieses Jahr
    (benötigt: hr.view)
    """
    from app.modules.hr.leave.models import LeaveRequest

    today = date.today()

    pending = db.query(func.count(LeaveRequest.id)).filter(
        LeaveRequest.status == "pending"
    ).scalar() or 0

    approved_this_month = db.query(func.count(LeaveRequest.id)).filter(
        LeaveRequest.status == "approved",
        extract("year", LeaveRequest.approved_date) == today.year,
        extract("month", LeaveRequest.approved_date) == today.month,
    ).scalar() or 0

    total_days_result = db.query(func.sum(LeaveRequest.total_days)).filter(
        LeaveRequest.status == "approved",
        extract("year", LeaveRequest.start_date) == today.year,
    ).scalar()
    total_days_taken = float(total_days_result) if total_days_result else 0.0

    return {
        "pending_requests": pending,
        "approved_this_month": approved_this_month,
        "total_days_taken_this_year": total_days_taken,
    }


@router.get("/recruiting-funnel")
@require_permissions(["hr.view"])
async def recruiting_funnel(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Recruiting-Funnel: offene Stellen, Bewerbungen gesamt, nach Status
    (benötigt: hr.view)
    """
    from app.modules.hr.recruiting.models import JobPosting, Application

    open_positions = db.query(func.count(JobPosting.id)).filter(
        JobPosting.status == "published"
    ).scalar() or 0

    total_applications = db.query(func.count(Application.id)).scalar() or 0

    status_rows = (
        db.query(Application.status, func.count(Application.id).label("cnt"))
        .group_by(Application.status)
        .all()
    )
    by_status = {row.status: row.cnt for row in status_rows}

    return {
        "open_positions": open_positions,
        "total_applications": total_applications,
        "by_status": by_status,
    }
