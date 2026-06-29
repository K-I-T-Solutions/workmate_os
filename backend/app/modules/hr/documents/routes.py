"""
HR Documents Routes
REST API Endpoints für Personaldokumente.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions

from . import crud, schemas


router = APIRouter(prefix="/documents", tags=["HR Documents"])


@router.get("/employees/{employee_id}/documents", response_model=list[schemas.HRDocumentResponse])
@require_permissions(["hr.view"])
async def list_employee_documents(
    employee_id: UUID,
    document_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Liste der Personaldokumente eines Mitarbeiters (benötigt: hr.view)"""
    return crud.get_employee_documents(db, employee_id, document_type)


@router.post("/employees/{employee_id}/documents", response_model=schemas.HRDocumentResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["hr.manage"])
async def create_document(
    employee_id: UUID,
    data: schemas.HRDocumentCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Personaldokument anlegen (benötigt: hr.manage)"""
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = getattr(user, "id", None)
    return crud.create_document(db, employee_id, data, user_id)


@router.get("/documents/{document_id}", response_model=schemas.HRDocumentResponse)
@require_permissions(["hr.view"])
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Holt ein Personaldokument (benötigt: hr.view)"""
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dokument nicht gefunden")
    return doc


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["hr.manage"])
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Löscht ein Personaldokument (benötigt: hr.manage)"""
    success = crud.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dokument nicht gefunden")
