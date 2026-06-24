# app/modules/backoffice/projects/crud.py
from sqlalchemy.orm import Session
from app.modules.backoffice.projects import models, schemas


def get_projects(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Project).offset(skip).limit(limit).all()


def get_project(db: Session, project_id: str):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def create_project(db: Session, data: schemas.ProjectCreate):
    project = models.Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: str, data: schemas.ProjectUpdate):
    project = get_project(db, project_id)
    if not project:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: str):
    project = get_project(db, project_id)
    if project:
        db.delete(project)
        db.commit()
        return True
    return False
