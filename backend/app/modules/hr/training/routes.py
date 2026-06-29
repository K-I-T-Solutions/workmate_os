"""
Training & Certifications Routes
REST API Endpoints für Schulungen und Zertifizierungen.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions

from . import crud, schemas


router = APIRouter(prefix="/training", tags=["Training & Certifications"])


# ============================================================================
# COURSES
# ============================================================================

@router.get("/courses", response_model=schemas.CourseListResponse)
@require_permissions(["hr.view"])
async def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste aller Schulungskurse (benötigt: hr.view)"""
    courses, total = crud.get_courses(db, skip, limit, is_active)
    items = []
    for course in courses:
        count = crud.get_course_participant_count(db, course.id)
        item = schemas.CourseResponse.model_validate(course)
        item.participant_count = count
        items.append(item)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/courses", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def create_course(
    data: schemas.CourseCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Erstellt einen neuen Schulungskurs (benötigt: hr.manage)"""
    return crud.create_course(db, data)


@router.get("/courses/{course_id}", response_model=schemas.CourseResponse)
@require_permissions(["hr.view"])
async def get_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt einen Kurs (benötigt: hr.view)"""
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kurs nicht gefunden")
    count = crud.get_course_participant_count(db, course.id)
    item = schemas.CourseResponse.model_validate(course)
    item.participant_count = count
    return item


@router.post("/courses/{course_id}/enroll", response_model=schemas.ParticipantResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def enroll_in_course(
    course_id: UUID,
    body: schemas.ParticipantCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Schreibt Mitarbeiter in Kurs ein (benötigt: hr.manage)"""
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kurs nicht gefunden")
    return crud.enroll_participant(db, course_id, body.employee_id)


# ============================================================================
# PARTICIPANTS
# ============================================================================

@router.patch("/participants/{participant_id}/status", response_model=schemas.ParticipantResponse)
@require_permissions(["hr.manage"])
async def update_participant_status(
    participant_id: UUID,
    body: schemas.ParticipantStatusUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Aktualisiert Teilnahmestatus (benötigt: hr.manage)"""
    participant = crud.update_participant_status(
        db, participant_id, body.status, body.completed_at, body.score
    )
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teilnahme nicht gefunden")
    return participant


# ============================================================================
# SELF-SERVICE
# ============================================================================

@router.get("/my-trainings", response_model=list[schemas.ParticipantResponse])
async def my_trainings(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Eigene Schulungen (Self-Service)"""
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Benutzer nicht identifizierbar")
    return crud.get_employee_trainings(db, user_id)


# ============================================================================
# CERTIFICATIONS
# ============================================================================

@router.get("/certifications", response_model=list[schemas.CertificationResponse])
@require_permissions(["hr.view"])
async def list_certifications(
    employee_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste aller Zertifikate, optional gefiltert nach Mitarbeiter (benötigt: hr.view)"""
    return crud.get_certifications(db, employee_id)


@router.post("/certifications", response_model=schemas.CertificationResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def create_certification(
    data: schemas.CertificationCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Erstellt ein Zertifikat (benötigt: hr.manage)"""
    return crud.create_certification(db, data.employee_id, data)
