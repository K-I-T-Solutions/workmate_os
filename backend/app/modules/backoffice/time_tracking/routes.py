# app/modules/backoffice/time_tracking/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.modules.backoffice.time_tracking import crud, schemas

router = APIRouter(prefix="/backoffice/time-tracking", tags=["Backoffice Time Tracking"])

@router.get("/", response_model=List[schemas.TimeEntryResponse])
def list_entries(db: Session = Depends(get_db)):
    return db.query(crud.models.TimeEntry).all()


@router.get("/{entry_id}", response_model=schemas.TimeEntryResponse)
def get_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = crud.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.post("/", response_model=schemas.TimeEntryResponse)
def create_entry(data: schemas.TimeEntryCreate, db: Session = Depends(get_db)):
    return crud.create_entry(db, data)


@router.put("/{entry_id}", response_model=schemas.TimeEntryResponse)
def update_entry(entry_id: str, data: schemas.TimeEntryUpdate, db: Session = Depends(get_db)):
    entry = crud.update_entry(db, entry_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.delete("/{entry_id}")
def delete_entry(entry_id: str, db: Session = Depends(get_db)):
    ok = crud.delete_entry(db, entry_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}
