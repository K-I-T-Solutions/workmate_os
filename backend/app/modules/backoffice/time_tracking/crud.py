# app/modules/backoffice/time_tracking/crud.py
from collections import defaultdict
from datetime import datetime, date, timedelta, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.backoffice.time_tracking import models, schemas


def _calculate_duration(start_time: datetime, end_time: Optional[datetime]) -> Optional[int]:
    if end_time and start_time:
        delta = end_time - start_time
        return max(0, int(delta.total_seconds() / 60))
    return None


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
        query = query.filter(models.TimeEntry.start_time >= datetime.combine(start_date, time.min))
    if end_date:
        query = query.filter(models.TimeEntry.start_time <= datetime.combine(end_date, time.max))
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

    project_map: dict[str, float] = {}
    for e in entries:
        pid = str(e.project_id) if e.project_id else "no_project"
        project_map[pid] = project_map.get(pid, 0) + (e.duration_minutes or 0)
    hours_by_project = [{"project_id": k, "hours": round(v / 60, 2)} for k, v in project_map.items()]

    type_map: dict[str, float] = {}
    for e in entries:
        tt = e.task_type or "unspecified"
        type_map[tt] = type_map.get(tt, 0) + (e.duration_minutes or 0)
    hours_by_task_type = [{"task_type": k, "hours": round(v / 60, 2)} for k, v in type_map.items()]

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


def get_billable_uninvoiced(
    db: Session,
    customer_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    employee_id: Optional[UUID] = None,
) -> schemas.BillableUninvoicedResponse:
    from app.modules.employees.models import Employee
    from app.modules.backoffice.projects.models import Project

    query = (
        db.query(models.TimeEntry)
        .join(Employee, models.TimeEntry.employee_id == Employee.id)
        .outerjoin(Project, models.TimeEntry.project_id == Project.id)
        .filter(
            models.TimeEntry.billable == True,
            models.TimeEntry.is_invoiced == False,
        )
    )

    if customer_id:
        query = query.filter(
            or_(
                Project.customer_id == customer_id,
                models.TimeEntry.customer_id == customer_id,
            )
        )
    if project_id:
        query = query.filter(models.TimeEntry.project_id == project_id)
    if employee_id:
        query = query.filter(models.TimeEntry.employee_id == employee_id)

    entries = query.order_by(models.TimeEntry.start_time.desc()).all()

    billable_entries: list[schemas.BillableEntry] = []
    total_hours = 0.0
    total_amount = Decimal("0.00")

    for entry in entries:
        duration_hours = entry.duration_hours or 0.0
        hourly_rate = entry.hourly_rate
        amount: Optional[Decimal] = None
        if hourly_rate is not None:
            amount = Decimal(str(round(duration_hours, 4))) * hourly_rate
            total_amount += amount

        total_hours += duration_hours

        # customer_id: direkt auf Entry oder über Projekt
        effective_customer_id = entry.customer_id or (
            entry.project.customer_id if entry.project else None
        )
        billable_entries.append(
            schemas.BillableEntry(
                id=entry.id,
                date=entry.start_time.date(),
                employee_name=f"{entry.employee.first_name} {entry.employee.last_name}",
                project_id=entry.project_id,
                project_name=entry.project.title if entry.project else None,
                customer_id=effective_customer_id,
                task_type=entry.task_type,
                note=entry.note,
                duration_hours=round(duration_hours, 2),
                hourly_rate=hourly_rate,
                amount=amount,
            )
        )

    return schemas.BillableUninvoicedResponse(
        entries=billable_entries,
        total_hours=round(total_hours, 2),
        total_amount=total_amount,
    )


def create_invoice_from_entries(
    db: Session,
    data: schemas.CreateInvoiceFromEntries,
):
    from app.modules.backoffice.invoices import crud as invoices_crud
    from app.modules.backoffice.invoices import schemas as invoice_schemas

    # 1. Einträge laden und validieren
    entries = (
        db.query(models.TimeEntry)
        .filter(models.TimeEntry.id.in_(data.time_entry_ids))
        .all()
    )

    found_ids = {e.id for e in entries}
    missing = set(data.time_entry_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Zeiteinträge nicht gefunden: {[str(i) for i in missing]}",
        )

    invalid = [e for e in entries if not e.billable or e.is_invoiced]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Folgende Einträge sind nicht billable oder bereits abgerechnet: "
                f"{[str(e.id) for e in invalid]}"
            ),
        )

    # 2. Line Items erstellen
    if data.group_by_task_type:
        groups: dict[str, list] = defaultdict(list)
        for entry in entries:
            key = entry.task_type or "IT-Dienstleistung"
            groups[key].append(entry)

        line_items = []
        for pos, (task_type, group_entries) in enumerate(groups.items(), start=1):
            total_group_hours = sum(e.duration_hours or 0.0 for e in group_entries)
            line_items.append(
                invoice_schemas.InvoiceLineItemCreate(
                    position=pos,
                    description=task_type,
                    quantity=Decimal(str(round(total_group_hours, 2))),
                    unit="Stunden",
                    unit_price=data.hourly_rate,
                )
            )
    else:
        total_hours = sum(e.duration_hours or 0.0 for e in entries)
        line_items = [
            invoice_schemas.InvoiceLineItemCreate(
                position=1,
                description="Erbrachte Leistungen",
                quantity=Decimal(str(round(total_hours, 2))),
                unit="Stunden",
                unit_price=data.hourly_rate,
            )
        ]

    # 3. Rechnung erstellen (AUTO-Nummernvergabe)
    invoice_create = invoice_schemas.InvoiceCreate(
        invoice_number="AUTO",
        customer_id=data.customer_id,
        project_id=data.project_id,
        issued_date=date.today(),
        notes=data.notes,
        line_items=line_items,
    )
    invoice = invoices_crud.create_invoice(db, invoice_create)

    # 4. Einträge als abgerechnet markieren
    for entry in entries:
        entry.is_invoiced = True
    db.commit()

    return invoice


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
            daily[day_key]["hours"] = round(daily[day_key]["hours"] + (e.duration_minutes or 0) / 60, 2)
            daily[day_key]["entries_count"] += 1

    total = round(sum(d["hours"] for d in daily.values()), 2)
    return {
        "employee_id": employee_id,
        "week": f"{year}-W{week:02d}",
        "total_hours": total,
        "daily_breakdown": list(daily.values()),
    }
