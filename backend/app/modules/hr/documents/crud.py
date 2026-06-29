"""
HR Documents CRUD Operations
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from . import models, schemas


def get_employee_documents(
    db: Session,
    employee_id: UUID,
    document_type: Optional[str] = None
) -> list[models.HRDocument]:
    """Holt alle Dokumente eines Mitarbeiters"""
    query = db.query(models.HRDocument).filter(
        models.HRDocument.employee_id == employee_id
    )
    if document_type:
        query = query.filter(models.HRDocument.document_type == document_type)
    return query.order_by(models.HRDocument.created_at.desc()).all()


def create_document(
    db: Session,
    employee_id: UUID,
    data: schemas.HRDocumentCreate,
    uploaded_by_id: Optional[UUID] = None
) -> models.HRDocument:
    """Erstellt ein neues Personaldokument"""
    doc_data = data.model_dump(exclude={"employee_id"})
    doc = models.HRDocument(
        employee_id=employee_id,
        uploaded_by_id=uploaded_by_id,
        **doc_data
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(
    db: Session,
    document_id: UUID
) -> Optional[models.HRDocument]:
    """Holt ein spezifisches Dokument"""
    return db.query(models.HRDocument).filter(
        models.HRDocument.id == document_id
    ).first()


def delete_document(
    db: Session,
    document_id: UUID
) -> bool:
    """Löscht ein Dokument"""
    doc = get_document(db, document_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
