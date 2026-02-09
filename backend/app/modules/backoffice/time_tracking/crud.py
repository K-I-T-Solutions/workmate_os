# app/modules/backoffice/time_tracking/crud.py
from datetime import datetime, date, timedelta, time
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.backoffice.time_tracking import models, schemas


# ─── Helpers ─────────────────────────────────────────────────

def _calculate_duration(start_time: datetime, end_time: Optional[datetime]) -> Optional[int]:
    """Berechnet duration_minutes aus start_time und end_time."""
    if end_time and start_time:
        delta = end_time - start_time
        return max(0, int(delta.total_seconds() / 60))
    return None


# ─── Read ────────────────────────────────────────────────────

def get_entries(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    employee_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    task_type: Optional[str] = None,
    billable: Optional[bool] = None,
    is_approved: Optional[bool] = None,
    is_invoiced: Optional[bool] = None,
    search: Optional[str] = None,
):
    query = db.query(models.TimeEntry)

    if employee_id:
        query = query.filter(models.TimeEntry.employee_id == employee_id)
    if project_id:
        query = query.filter(models.TimeEntry.project_id == project_id)
    if start_date:
        query = query.filter(
            models.TimeEntry.start_time >= datetime.combine(start_date, time.min)
        )
    if end_date:
        query = query.filter(
            models.TimeEntry.start_time <= datetime.combine(end_date, time.max)
        )
    if task_type:
        query = query.filter(models.TimeEntry.task_type == task_type)
    if billable is not None:
        query = query.filter(models.TimeEntry.billable == billable)
    if is_approved is not None:
        query = query.filter(models.TimeEntry.is_approved == is_approved)
    if is_invoiced is not None:
        query = query.filter(models.TimeEntry.is_invoiced == is_invoiced)
    if search:
        query = query.filter(models.TimeEntry.note.ilike(f"%{search}%"))

    return query.order_by(models.TimeEntry.start_time.desc()).offset(skip).limit(limit).all()


def get_entry(db: Session, entry_id) -> Optional[models.TimeEntry]:
    return db.query(models.TimeEntry).filter(models.TimeEntry.id == entry_id).first()


# ─── Create / Update / Delete ────────────────────────────────

def create_entry(db: Session, data: schemas.TimeEntryCreate) -> models.TimeEntry:
    entry_data = data.model_dump()
    entry_data["duration_minutes"] = _calculate_duration(
        entry_data["start_time"], entry_data.get("end_time")
    )
    entry = models.TimeEntry(**entry_data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, entry_id, data: schemas.TimeEntryUpdate) -> Optional[models.TimeEntry]:
    entry = get_entry(db, entry_id)
    if not entry:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    # Duration neu berechnen
    entry.duration_minutes = _calculate_duration(entry.start_time, entry.end_time)
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(db: Session, entry_id) -> bool:
    entry = get_entry(db, entry_id)
    if entry:
        db.delete(entry)
        db.commit()
        return True
    return False


# ─── Approval ────────────────────────────────────────────────

def approve_entry(db: Session, entry_id) -> Optional[models.TimeEntry]:
    entry = get_entry(db, entry_id)
    if not entry:
        return None
    entry.is_approved = True
    db.commit()
    db.refresh(entry)
    return entry


def reject_entry(db: Session, entry_id) -> Optional[models.TimeEntry]:
    entry = get_entry(db, entry_id)
    if not entry:
        return None
    entry.is_approved = False
    db.commit()
    db.refresh(entry)
    return entry


# ─── Statistics ──────────────────────────────────────────────

def get_stats(db: Session, employee_id: Optional[UUID] = None) -> dict:
    query = db.query(models.TimeEntry)
    if employee_id:
        query = query.filter(models.TimeEntry.employee_id == employee_id)

    entries = query.all()

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    def _sum_hours(items):
        return round(sum((e.duration_minutes or 0) for e in items) / 60, 2)

    today_entries = [e for e in entries if e.start_time >= today_start]
    week_entries = [e for e in entries if e.start_time >= week_start]
    month_entries = [e for e in entries if e.start_time >= month_start]

    # Stunden nach Projekt
    project_map: dict[str, float] = {}
    for e in entries:
        pid = str(e.project_id) if e.project_id else "no_project"
        project_map[pid] = project_map.get(pid, 0) + (e.duration_minutes or 0)
    hours_by_project = [
        {"project_id": k, "hours": round(v / 60, 2)}
        for k, v in project_map.items()
    ]

    # Stunden nach Task-Type
    type_map: dict[str, float] = {}
    for e in entries:
        tt = e.task_type or "unspecified"
        type_map[tt] = type_map.get(tt, 0) + (e.duration_minutes or 0)
    hours_by_task_type = [
        {"task_type": k, "hours": round(v / 60, 2)}
        for k, v in type_map.items()
    ]

    return {
        "total_hours_today": _sum_hours(today_entries),
        "total_hours_week": _sum_hours(week_entries),
        "total_hours_month": _sum_hours(month_entries),
        "total_entries": len(entries),
        "billable_hours": _sum_hours([e for e in entries if e.billable]),
        "non_billable_hours": _sum_hours([e for e in entries if not e.billable]),
        "hours_by_project": hours_by_project,
        "hours_by_task_type": hours_by_task_type,
    }


# ─── Weekly Summary ──────────────────────────────────────────

def get_weekly_summary(db: Session, employee_id: UUID, year: int, week: int) -> dict:
    monday = date.fromisocalendar(year, week, 1)
    sunday = monday + timedelta(days=6)

    entries = (
        db.query(models.TimeEntry)
        .filter(
            models.TimeEntry.employee_id == employee_id,
            models.TimeEntry.start_time >= datetime.combine(monday, time.min),
            models.TimeEntry.start_time <= datetime.combine(sunday, time.max),
        )
        .all()
    )

    daily: dict[str, dict] = {}
    for i in range(7):
        day = monday + timedelta(days=i)
        daily[day.isoformat()] = {"date": day.isoformat(), "hours": 0.0, "entries_count": 0}

    for e in entries:
        day_key = e.start_time.date().isoformat()
        if day_key in daily:
            daily[day_key]["hours"] = round(
                daily[day_key]["hours"] + (e.duration_minutes or 0) / 60, 2
            )
            daily[day_key]["entries_count"] += 1

    total = round(sum(d["hours"] for d in daily.values()), 2)

    return {
        "employee_id": employee_id,
        "week": f"{year}-W{week:02d}",
        "total_hours": total,
        "daily_breakdown": list(daily.values()),
    }
