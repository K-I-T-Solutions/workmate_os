# app/modules/backoffice/time_tracking/crud.py
from sqlalchemy.orm import Session
from app.modules.backoffice.time_tracking import models, schemas


def get_entries(db: Session, project_id: str):
    return db.query(models.TimeEntry).filter(models.TimeEntry.project_id == project_id).all()


def get_entry(db: Session, entry_id: str):
    return db.query(models.TimeEntry).filter(models.TimeEntry.id == entry_id).first()


def create_entry(db: Session, data: schemas.TimeEntryCreate):
    entry = models.TimeEntry(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, entry_id: str, data: schemas.TimeEntryUpdate):
    entry = get_entry(db, entry_id)
    if not entry:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(db: Session, entry_id: str):
    entry = get_entry(db, entry_id)
    if entry:
        db.delete(entry)
        db.commit()
        return True
    return False
