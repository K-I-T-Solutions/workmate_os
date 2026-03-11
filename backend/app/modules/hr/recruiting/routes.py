"""Recruiting API Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.settings.database import get_db
from app.core.auth.roles import require_permissions, get_current_user
from . import crud, schemas

router = APIRouter(prefix="/recruiting", tags=["HR Recruiting"])


# ── Job Postings ──

@router.get("/jobs", response_model=schemas.JobPostingListResponse)
@require_permissions(["hr.view", "hr.*"])
def list_job_postings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    department_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items, total = crud.get_job_postings(db, skip=skip, limit=limit, status=status, department_id=department_id)
    result = []
    for item in items:
        data = schemas.JobPostingResponse.model_validate(item)
        data.application_count = crud.get_application_count(db, item.id)
        result.append(data)
    return {"items": result, "total": total, "skip": skip, "limit": limit}


@router.get("/jobs/{job_id}", response_model=schemas.JobPostingResponse)
@require_permissions(["hr.view", "hr.*"])
def get_job_posting(job_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get_job_posting(db, job_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Stellenausschreibung nicht gefunden")
    data = schemas.JobPostingResponse.model_validate(obj)
    data.application_count = crud.get_application_count(db, obj.id)
    return data


@router.post("/jobs", response_model=schemas.JobPostingResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage_policies", "hr.*"])
def create_job_posting(
    data: schemas.JobPostingCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return crud.create_job_posting(db, data)


@router.put("/jobs/{job_id}", response_model=schemas.JobPostingResponse)
@require_permissions(["hr.manage_policies", "hr.*"])
def update_job_posting(
    job_id: UUID,
    data: schemas.JobPostingUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.update_job_posting(db, job_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Stellenausschreibung nicht gefunden")
    result = schemas.JobPostingResponse.model_validate(obj)
    result.application_count = crud.get_application_count(db, obj.id)
    return result


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["hr.delete", "hr.*"])
def delete_job_posting(job_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.delete_job_posting(db, job_id):
        raise HTTPException(status_code=404, detail="Stellenausschreibung nicht gefunden")


# ── Applications ──

@router.get("/applications", response_model=schemas.ApplicationListResponse)
@require_permissions(["hr.view", "hr.*"])
def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    job_posting_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items, total = crud.get_applications(db, job_posting_id=job_posting_id, status=status, skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/applications/{app_id}", response_model=schemas.ApplicationResponse)
@require_permissions(["hr.view", "hr.*"])
def get_application(app_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get_application(db, app_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    return obj


@router.post("/applications", response_model=schemas.ApplicationResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.view", "hr.*"])
def create_application(
    data: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not crud.get_job_posting(db, data.job_posting_id):
        raise HTTPException(status_code=404, detail="Stellenausschreibung nicht gefunden")
    return crud.create_application(db, data)


@router.put("/applications/{app_id}", response_model=schemas.ApplicationResponse)
@require_permissions(["hr.approve", "hr.*"])
def update_application(
    app_id: UUID,
    data: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.update_application(db, app_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    return obj


@router.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["hr.delete", "hr.*"])
def delete_application(app_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.delete_application(db, app_id):
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
