"""
Compensation CRUD Operations
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from . import models, schemas


def get_salary_history(
    db: Session,
    employee_id: UUID
) -> list[models.SalaryRecord]:
    """Holt Gehaltshistorie eines Mitarbeiters"""
    return db.query(models.SalaryRecord).filter(
        models.SalaryRecord.employee_id == employee_id
    ).order_by(models.SalaryRecord.effective_date.desc()).all()


def create_salary_record(
    db: Session,
    employee_id: UUID,
    data: schemas.SalaryRecordCreate,
    created_by_id: Optional[UUID] = None
) -> models.SalaryRecord:
    """Erstellt einen neuen Gehaltseintrag"""
    record = models.SalaryRecord(
        employee_id=employee_id,
        created_by_id=created_by_id,
        **data.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_current_salary(
    db: Session,
    employee_id: UUID
) -> Optional[models.SalaryRecord]:
    """Holt aktuellen Gehaltseintrag (neuester nach effective_date)"""
    return db.query(models.SalaryRecord).filter(
        models.SalaryRecord.employee_id == employee_id
    ).order_by(models.SalaryRecord.effective_date.desc()).first()


def get_bonuses(
    db: Session,
    employee_id: UUID
) -> list[models.Bonus]:
    """Holt alle Boni eines Mitarbeiters"""
    return db.query(models.Bonus).filter(
        models.Bonus.employee_id == employee_id
    ).order_by(models.Bonus.payment_date.desc()).all()


def create_bonus(
    db: Session,
    employee_id: UUID,
    data: schemas.BonusCreate,
    created_by_id: Optional[UUID] = None
) -> models.Bonus:
    """Erstellt einen neuen Bonus"""
    bonus = models.Bonus(
        employee_id=employee_id,
        created_by_id=created_by_id,
        **data.model_dump()
    )
    db.add(bonus)
    db.commit()
    db.refresh(bonus)
    return bonus


def get_benefits(
    db: Session,
    employee_id: UUID,
    is_active: Optional[bool] = None
) -> list[models.Benefit]:
    """Holt Benefits eines Mitarbeiters"""
    query = db.query(models.Benefit).filter(
        models.Benefit.employee_id == employee_id
    )
    if is_active is not None:
        query = query.filter(models.Benefit.is_active == is_active)
    return query.order_by(models.Benefit.start_date.desc()).all()


def create_benefit(
    db: Session,
    employee_id: UUID,
    data: schemas.BenefitCreate
) -> models.Benefit:
    """Erstellt einen neuen Benefit"""
    benefit = models.Benefit(
        employee_id=employee_id,
        **data.model_dump()
    )
    db.add(benefit)
    db.commit()
    db.refresh(benefit)
    return benefit


def deactivate_benefit(
    db: Session,
    benefit_id: UUID
) -> Optional[models.Benefit]:
    """Deaktiviert einen Benefit"""
    benefit = db.query(models.Benefit).filter(
        models.Benefit.id == benefit_id
    ).first()
    if not benefit:
        return None
    benefit.is_active = False
    db.commit()
    db.refresh(benefit)
    return benefit
