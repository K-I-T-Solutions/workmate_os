# app/modules/backoffice/projects/crud.py
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import time

from app.modules.backoffice.projects import models, schemas
from app.modules.backoffice.invoices.models import NumberSequence


def get_projects(db: Session, skip: int = 0, limit: int = 50, customer_id: str = None):
    query = db.query(models.Project)
    if customer_id:
        query = query.filter(models.Project.customer_id == customer_id)
    return query.offset(skip).limit(limit).all()


def get_project(db: Session, project_id: str):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def _generate_next_number(db: Session, doc_type: str, year: int) -> int:
    """
    Holt die nächste laufende Nummer aus number_sequences.

    - Legt bei Bedarf einen neuen Eintrag an (startet bei 1)
    - Verwendet SELECT ... FOR UPDATE für concurrency safety
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            seq_row = (
                db.query(NumberSequence)
                .filter(
                    NumberSequence.doc_type == doc_type,
                    NumberSequence.year == year,
                )
                .with_for_update(nowait=False)
                .first()
            )

            if not seq_row:
                # Neue Sequence anlegen
                seq_row = NumberSequence(
                    doc_type=doc_type,
                    year=year,
                    current_number=1,
                )
                db.add(seq_row)
                db.flush()
                return 1
            else:
                # Incrementieren
                seq_row.current_number += 1
                db.flush()
                return seq_row.current_number

        except IntegrityError:
            db.rollback()
            if attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise

    raise RuntimeError("Failed to generate project number after retries")


def _generate_project_number(db: Session, start_date: Optional[date] = None) -> str:
    """
    Generiert eine neue Projektnummer nach Schema: PRJ-YYYY-NNNN

    Beispiele:
      PRJ-2026-0001
      PRJ-2026-0002

    Reset pro Jahr.
    """
    year = (start_date or date.today()).year
    prefix = "PRJ"
    doc_type = "project"

    # Laufende Nummer (atomic)
    next_num = _generate_next_number(db, doc_type=doc_type, year=year)

    # 4-stellige laufende Nummer
    seq_str = f"{next_num:04d}"
    return f"{prefix}-{year}-{seq_str}"


def create_project(db: Session, data: schemas.ProjectCreate):
    # Generate project number if not provided
    project_data = data.model_dump()
    if not project_data.get("project_number"):
        project_data["project_number"] = _generate_project_number(
            db=db,
            start_date=project_data.get("start_date")
        )

    project = models.Project(**project_data)
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
