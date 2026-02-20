# app/modules/backoffice/projects/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.modules.backoffice.projects import crud, schemas

router = APIRouter(prefix="/backoffice/projects", tags=["Backoffice Projects"])

@router.get("/", response_model=List[schemas.ProjectResponse])
@require_permissions(["backoffice.projects.view", "backoffice.*"])
def list_projects(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return crud.get_projects(db, customer_id=customer_id)


@router.get("/{project_id}", response_model=schemas.ProjectResponse)
@require_permissions(["backoffice.projects.view", "backoffice.*"])
def get_project(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=schemas.ProjectResponse)
@require_permissions(["backoffice.projects.write", "backoffice.*"])
def create_project(data: schemas.ProjectCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.create_project(db, data)


@router.put("/{project_id}", response_model=schemas.ProjectResponse)
@require_permissions(["backoffice.projects.write", "backoffice.*"])
def update_project(project_id: str, data: schemas.ProjectUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = crud.update_project(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
@require_permissions(["backoffice.projects.delete", "backoffice.*"])
def delete_project(project_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    ok = crud.delete_project(db, project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted"}
