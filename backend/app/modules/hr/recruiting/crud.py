"""Recruiting CRUD"""
from datetime import datetime
from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from .models import JobPosting, Application
from .schemas import JobPostingCreate, JobPostingUpdate, ApplicationCreate, ApplicationUpdate


# ── Job Postings ──

def get_job_postings(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    department_id: Optional[UUID] = None,
) -> Tuple[List[JobPosting], int]:
    query = db.query(JobPosting)
    if status:
        query = query.filter(JobPosting.status == status)
    if department_id:
        query = query.filter(JobPosting.department_id == department_id)
    total = query.count()
    items = query.order_by(JobPosting.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_job_posting(db: Session, job_id: UUID) -> Optional[JobPosting]:
    return db.query(JobPosting).filter(JobPosting.id == job_id).first()


def create_job_posting(db: Session, data: JobPostingCreate) -> JobPosting:
    obj = JobPosting(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_job_posting(db: Session, job_id: UUID, data: JobPostingUpdate) -> Optional[JobPosting]:
    obj = get_job_posting(db, job_id)
    if not obj:
        return None
    changes = data.model_dump(exclude_unset=True)
    if changes.get("status") == "published" and not obj.published_at:
        changes["published_at"] = datetime.utcnow()
    for k, v in changes.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_job_posting(db: Session, job_id: UUID) -> bool:
    obj = get_job_posting(db, job_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def get_application_count(db: Session, job_id: UUID) -> int:
    return db.query(func.count(Application.id)).filter(Application.job_posting_id == job_id).scalar() or 0


# ── Applications ──

def get_applications(
    db: Session,
    job_posting_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[Application], int]:
    query = db.query(Application)
    if job_posting_id:
        query = query.filter(Application.job_posting_id == job_posting_id)
    if status:
        query = query.filter(Application.status == status)
    total = query.count()
    items = query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_application(db: Session, app_id: UUID) -> Optional[Application]:
    return db.query(Application).filter(Application.id == app_id).first()


def create_application(db: Session, data: ApplicationCreate) -> Application:
    obj = Application(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_application(db: Session, app_id: UUID, data: ApplicationUpdate) -> Optional[Application]:
    obj = get_application(db, app_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_application(db: Session, app_id: UUID) -> bool:
    obj = get_application(db, app_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
