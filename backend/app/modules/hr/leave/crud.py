"""
Leave Management CRUD Operations
Business-Logik für Urlaubsverwaltung.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, extract, func
from datetime import date, timedelta
from decimal import Decimal

from . import models, schemas
from app.modules.hr.enums import LeaveStatus, LeaveType
from app.modules.hr.utils import get_date_ranges_between


# ============================================================================
# LEAVE POLICY CRUD
# ============================================================================

def get_leave_policies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> tuple[list[models.LeavePolicy], int]:
    """Holt alle Leave Policies mit Filterung"""
    query = db.query(models.LeavePolicy)

    if is_active is not None:
        query = query.filter(models.LeavePolicy.is_active == is_active)

    total = query.count()
    policies = query.order_by(models.LeavePolicy.name).offset(skip).limit(limit).all()

    return policies, total


def get_leave_policy(db: Session, policy_id: UUID) -> Optional[models.LeavePolicy]:
    """Holt eine spezifische Policy"""
    return db.query(models.LeavePolicy).filter(models.LeavePolicy.id == policy_id).first()


def create_leave_policy(
    db: Session,
    policy_data: schemas.LeavePolicyCreate
) -> models.LeavePolicy:
    """Erstellt eine neue Leave Policy"""
    policy = models.LeavePolicy(**policy_data.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def update_leave_policy(
    db: Session,
    policy_id: UUID,
    policy_data: schemas.LeavePolicyUpdate
) -> Optional[models.LeavePolicy]:
    """Aktualisiert eine Leave Policy"""
    policy = get_leave_policy(db, policy_id)
    if not policy:
        return None

    update_data = policy_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)

    db.commit()
    db.refresh(policy)
    return policy


def delete_leave_policy(db: Session, policy_id: UUID) -> bool:
    """Löscht eine Leave Policy"""
    policy = get_leave_policy(db, policy_id)
    if not policy:
        return False

    db.delete(policy)
    db.commit()
    return True


# ============================================================================
# LEAVE BALANCE CRUD
# ============================================================================

def get_leave_balances(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[UUID] = None,
    year: Optional[int] = None
) -> tuple[list[models.LeaveBalance], int]:
    """Holt alle Leave Balances mit Filterung"""
    query = db.query(models.LeaveBalance).options(
        joinedload(models.LeaveBalance.employee),
        joinedload(models.LeaveBalance.policy)
    )

    if employee_id:
        query = query.filter(models.LeaveBalance.employee_id == employee_id)
    if year:
        query = query.filter(models.LeaveBalance.year == year)

    total = query.count()
    balances = query.order_by(models.LeaveBalance.year.desc()).offset(skip).limit(limit).all()

    return balances, total


def get_leave_balance(db: Session, balance_id: UUID) -> Optional[models.LeaveBalance]:
    """Holt einen spezifischen Balance"""
    return db.query(models.LeaveBalance).filter(models.LeaveBalance.id == balance_id).first()


def get_employee_balance(
    db: Session,
    employee_id: UUID,
    year: int
) -> Optional[models.LeaveBalance]:
    """Holt Balance für Mitarbeiter und Jahr"""
    return db.query(models.LeaveBalance).filter(
        and_(
            models.LeaveBalance.employee_id == employee_id,
            models.LeaveBalance.year == year
        )
    ).first()


def create_leave_balance(
    db: Session,
    balance_data: schemas.LeaveBalanceCreate
) -> models.LeaveBalance:
    """Erstellt einen neuen Leave Balance"""
    # Berechne verbleibende Tage
    vacation_remaining = balance_data.vacation_total - Decimal("0.00")

    balance = models.LeaveBalance(
        **balance_data.model_dump(),
        vacation_remaining=vacation_remaining
    )
    db.add(balance)
    db.commit()
    db.refresh(balance)
    return balance


def update_leave_balance(
    db: Session,
    balance_id: UUID,
    balance_data: schemas.LeaveBalanceUpdate
) -> Optional[models.LeaveBalance]:
    """Aktualisiert einen Leave Balance"""
    balance = get_leave_balance(db, balance_id)
    if not balance:
        return None

    update_data = balance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(balance, field, value)

    # Neuberechnung verbleibender Tage
    balance.vacation_remaining = balance.vacation_total - balance.vacation_used

    db.commit()
    db.refresh(balance)
    return balance


def initialize_employee_balance(
    db: Session,
    employee_id: UUID,
    year: int,
    policy_id: Optional[UUID] = None
) -> models.LeaveBalance:
    """Initialisiert Balance für neuen Mitarbeiter/Jahr"""
    # Prüfe ob bereits vorhanden
    existing = get_employee_balance(db, employee_id, year)
    if existing:
        return existing

    # Hole Policy für Standardwerte
    vacation_days = Decimal("20.00")
    sick_days = Decimal("10.00")

    if policy_id:
        policy = get_leave_policy(db, policy_id)
        if policy:
            vacation_days = Decimal(str(policy.vacation_days))
            sick_days = Decimal(str(policy.sick_days))

    balance_data = schemas.LeaveBalanceCreate(
        employee_id=employee_id,
        year=year,
        policy_id=policy_id,
        vacation_total=vacation_days,
        sick_total=sick_days
    )

    return create_leave_balance(db, balance_data)


# ============================================================================
# LEAVE REQUEST CRUD
# ============================================================================

def get_leave_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[UUID] = None,
    status: Optional[str] = None,
    leave_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> tuple[list[models.LeaveRequest], int]:
    """Holt alle Leave Requests mit Filterung"""
    query = db.query(models.LeaveRequest).options(
        joinedload(models.LeaveRequest.employee),
        joinedload(models.LeaveRequest.approved_by)
    )

    # Filter
    if employee_id:
        query = query.filter(models.LeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(models.LeaveRequest.status == status)
    if leave_type:
        query = query.filter(models.LeaveRequest.leave_type == leave_type)
    if date_from:
        query = query.filter(models.LeaveRequest.start_date >= date_from)
    if date_to:
        query = query.filter(models.LeaveRequest.end_date <= date_to)

    total = query.count()
    requests = query.order_by(models.LeaveRequest.start_date.desc()).offset(skip).limit(limit).all()

    return requests, total


def get_leave_request(db: Session, request_id: UUID) -> Optional[models.LeaveRequest]:
    """Holt einen spezifischen Leave Request"""
    return db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()


def create_leave_request(
    db: Session,
    request_data: schemas.LeaveRequestCreate,
    employee_id: UUID
) -> models.LeaveRequest:
    """Erstellt einen neuen Leave Request"""
    leave_request = models.LeaveRequest(
        employee_id=employee_id,
        **request_data.model_dump(exclude={"employee_id"})
    )
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)

    return leave_request


def update_leave_request(
    db: Session,
    request_id: UUID,
    request_data: schemas.LeaveRequestUpdate
) -> Optional[models.LeaveRequest]:
    """Aktualisiert einen Leave Request"""
    leave_request = get_leave_request(db, request_id)
    if not leave_request:
        return None

    # Nur pending requests können aktualisiert werden
    if leave_request.status != LeaveStatus.PENDING.value:
        return None

    update_data = request_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(leave_request, field, value)

    db.commit()
    db.refresh(leave_request)
    return leave_request


def approve_leave_request(
    db: Session,
    request_id: UUID,
    approved_by_id: UUID
) -> Optional[models.LeaveRequest]:
    """Genehmigt einen Leave Request"""
    leave_request = get_leave_request(db, request_id)

    if not leave_request:
        return None

    if leave_request.status != LeaveStatus.PENDING.value:
        return None

    # Status update
    leave_request.status = LeaveStatus.APPROVED.value
    leave_request.approved_by_id = approved_by_id
    leave_request.approved_date = date.today()

    db.commit()
    db.refresh(leave_request)

    # Aktualisiere Balance
    update_balance_after_approval(db, leave_request)

    # Erstelle Absence Calendar Einträge
    create_absence_calendar_entries(db, leave_request)

    return leave_request


def reject_leave_request(
    db: Session,
    request_id: UUID,
    approved_by_id: UUID,
    rejection_reason: str
) -> Optional[models.LeaveRequest]:
    """Lehnt einen Leave Request ab"""
    leave_request = get_leave_request(db, request_id)

    if not leave_request:
        return None

    if leave_request.status != LeaveStatus.PENDING.value:
        return None

    leave_request.status = LeaveStatus.REJECTED.value
    leave_request.approved_by_id = approved_by_id
    leave_request.approved_date = date.today()
    leave_request.rejection_reason = rejection_reason

    db.commit()
    db.refresh(leave_request)
    return leave_request


def cancel_leave_request(
    db: Session,
    request_id: UUID
) -> Optional[models.LeaveRequest]:
    """Storniert einen Leave Request"""
    leave_request = get_leave_request(db, request_id)

    if not leave_request:
        return None

    # Nur pending oder approved requests können storniert werden
    if leave_request.status not in [LeaveStatus.PENDING.value, LeaveStatus.APPROVED.value]:
        return None

    was_approved = leave_request.status == LeaveStatus.APPROVED.value

    leave_request.status = LeaveStatus.CANCELLED.value

    db.commit()
    db.refresh(leave_request)

    # Wenn bereits genehmigt, Balance zurücksetzen
    if was_approved:
        revert_balance_after_cancellation(db, leave_request)
        delete_absence_calendar_entries(db, leave_request.id)

    return leave_request


def delete_leave_request(db: Session, request_id: UUID) -> bool:
    """Löscht einen Leave Request (nur pending)"""
    leave_request = get_leave_request(db, request_id)
    if not leave_request:
        return False

    # Nur pending requests können gelöscht werden
    if leave_request.status != LeaveStatus.PENDING.value:
        return False

    db.delete(leave_request)
    db.commit()
    return True


# ============================================================================
# BALANCE UPDATE LOGIC
# ============================================================================

def update_balance_after_approval(
    db: Session,
    leave_request: models.LeaveRequest
):
    """Aktualisiert Balance nach Genehmigung"""
    year = leave_request.start_date.year
    balance = get_employee_balance(db, leave_request.employee_id, year)

    if not balance:
        # Initialisiere Balance wenn nicht vorhanden
        balance = initialize_employee_balance(db, leave_request.employee_id, year)

    # Aktualisiere basierend auf Leave Type
    if leave_request.leave_type == LeaveType.VACATION.value:
        balance.vacation_used += leave_request.total_days
        balance.vacation_remaining = balance.vacation_total - balance.vacation_used
    elif leave_request.leave_type == LeaveType.SICK.value:
        balance.sick_used += leave_request.total_days
    else:
        balance.other_used += leave_request.total_days

    db.commit()


def revert_balance_after_cancellation(
    db: Session,
    leave_request: models.LeaveRequest
):
    """Setzt Balance zurück nach Stornierung"""
    year = leave_request.start_date.year
    balance = get_employee_balance(db, leave_request.employee_id, year)

    if not balance:
        return

    # Zurücksetzen basierend auf Leave Type
    if leave_request.leave_type == LeaveType.VACATION.value:
        balance.vacation_used = max(Decimal("0.00"), balance.vacation_used - leave_request.total_days)
        balance.vacation_remaining = balance.vacation_total - balance.vacation_used
    elif leave_request.leave_type == LeaveType.SICK.value:
        balance.sick_used = max(Decimal("0.00"), balance.sick_used - leave_request.total_days)
    else:
        balance.other_used = max(Decimal("0.00"), balance.other_used - leave_request.total_days)

    db.commit()


# ============================================================================
# ABSENCE CALENDAR CRUD
# ============================================================================

def create_absence_calendar_entries(
    db: Session,
    leave_request: models.LeaveRequest
):
    """Erstellt Absence Calendar Einträge für genehmigten Urlaub"""
    dates = get_date_ranges_between(leave_request.start_date, leave_request.end_date)

    for current_date in dates:
        # Prüfe ob bereits existiert
        existing = db.query(models.AbsenceCalendar).filter(
            and_(
                models.AbsenceCalendar.employee_id == leave_request.employee_id,
                models.AbsenceCalendar.absence_date == current_date
            )
        ).first()

        if existing:
            continue

        # Bestimme ob ganzer Tag oder halber
        is_full_day = True
        if current_date == leave_request.start_date and leave_request.half_day_start:
            is_full_day = False
        if current_date == leave_request.end_date and leave_request.half_day_end:
            is_full_day = False

        calendar_entry = models.AbsenceCalendar(
            employee_id=leave_request.employee_id,
            leave_request_id=leave_request.id,
            absence_date=current_date,
            is_full_day=is_full_day,
            leave_type=leave_request.leave_type
        )
        db.add(calendar_entry)

    db.commit()


def delete_absence_calendar_entries(db: Session, leave_request_id: UUID):
    """Löscht Absence Calendar Einträge"""
    db.query(models.AbsenceCalendar).filter(
        models.AbsenceCalendar.leave_request_id == leave_request_id
    ).delete()
    db.commit()


def get_absence_calendar(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    employee_id: Optional[UUID] = None
) -> tuple[list[models.AbsenceCalendar], int]:
    """Holt Absence Calendar Einträge mit Filterung"""
    query = db.query(models.AbsenceCalendar).options(
        joinedload(models.AbsenceCalendar.employee),
        joinedload(models.AbsenceCalendar.leave_request)
    )

    if date_from:
        query = query.filter(models.AbsenceCalendar.absence_date >= date_from)
    if date_to:
        query = query.filter(models.AbsenceCalendar.absence_date <= date_to)
    if employee_id:
        query = query.filter(models.AbsenceCalendar.employee_id == employee_id)

    total = query.count()
    entries = query.order_by(models.AbsenceCalendar.absence_date.desc()).offset(skip).limit(limit).all()

    return entries, total


def get_team_absences_for_date(db: Session, target_date: date) -> list[models.AbsenceCalendar]:
    """Holt alle Abwesenheiten für ein bestimmtes Datum"""
    return db.query(models.AbsenceCalendar).options(
        joinedload(models.AbsenceCalendar.employee)
    ).filter(
        models.AbsenceCalendar.absence_date == target_date
    ).all()
