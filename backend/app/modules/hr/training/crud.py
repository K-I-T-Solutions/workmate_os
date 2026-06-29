"""
Training & Certifications CRUD Operations
"""
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


def get_courses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> tuple[list[models.TrainingCourse], int]:
    """Holt alle Kurse mit optionalem Filter"""
    query = db.query(models.TrainingCourse)
    if is_active is not None:
        query = query.filter(models.TrainingCourse.is_active == is_active)
    total = query.count()
    courses = query.order_by(models.TrainingCourse.title).offset(skip).limit(limit).all()
    return courses, total


def create_course(db: Session, data: schemas.CourseCreate) -> models.TrainingCourse:
    """Erstellt einen neuen Kurs"""
    course = models.TrainingCourse(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_course(db: Session, course_id: UUID) -> Optional[models.TrainingCourse]:
    """Holt einen spezifischen Kurs"""
    return db.query(models.TrainingCourse).filter(
        models.TrainingCourse.id == course_id
    ).first()


def enroll_participant(
    db: Session,
    course_id: UUID,
    employee_id: UUID
) -> models.TrainingParticipant:
    """Schreibt Mitarbeiter in Kurs ein"""
    participant = models.TrainingParticipant(
        course_id=course_id,
        employee_id=employee_id,
        enrolled_at=date.today(),
        status="planned"
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def update_participant_status(
    db: Session,
    participant_id: UUID,
    status: str,
    completed_at: Optional[date] = None,
    score: Optional[float] = None
) -> Optional[models.TrainingParticipant]:
    """Aktualisiert Status einer Teilnahme"""
    participant = db.query(models.TrainingParticipant).filter(
        models.TrainingParticipant.id == participant_id
    ).first()
    if not participant:
        return None
    participant.status = status
    if completed_at is not None:
        participant.completed_at = completed_at
    if score is not None:
        participant.score = score
    db.commit()
    db.refresh(participant)
    return participant


def get_employee_trainings(
    db: Session,
    employee_id: UUID
) -> list[models.TrainingParticipant]:
    """Holt alle Schulungen eines Mitarbeiters"""
    return db.query(models.TrainingParticipant).filter(
        models.TrainingParticipant.employee_id == employee_id
    ).order_by(models.TrainingParticipant.enrolled_at.desc()).all()


def get_certifications(
    db: Session,
    employee_id: Optional[UUID] = None
) -> list[models.HRCertification]:
    """Holt Zertifikate, optional gefiltert nach Mitarbeiter"""
    query = db.query(models.HRCertification)
    if employee_id:
        query = query.filter(models.HRCertification.employee_id == employee_id)
    return query.order_by(models.HRCertification.issued_date.desc()).all()


def create_certification(
    db: Session,
    employee_id: UUID,
    data: schemas.CertificationCreate
) -> models.HRCertification:
    """Erstellt ein neues Zertifikat"""
    cert_data = data.model_dump(exclude={"employee_id"})
    cert = models.HRCertification(employee_id=employee_id, **cert_data)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def get_course_participant_count(db: Session, course_id: UUID) -> int:
    """Zählt Teilnehmer eines Kurses"""
    return db.query(func.count(models.TrainingParticipant.id)).filter(
        models.TrainingParticipant.course_id == course_id
    ).scalar() or 0
