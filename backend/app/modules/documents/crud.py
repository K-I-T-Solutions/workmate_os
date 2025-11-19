"""
WorkmateOS - Documents CRUD Operations
Database operations for document management
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentUpload, DocumentUpdate


def get_document(db: Session, document_id: UUID) -> Optional[Document]:
    """Get document by ID"""
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    linked_module: Optional[str] = None,
    owner_id: Optional[UUID] = None,
    is_confidential: Optional[bool] = None
) -> tuple[list[Document], int]:
    """
    Get documents with filtering and pagination
    Returns: (documents list, total count)
    """
    query = db.query(Document)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Document.title.ilike(search_filter),
                Document.file_path.ilike(search_filter)
            )
        )
    
    if category:
        query = query.filter(Document.category == category)
    
    if linked_module:
        query = query.filter(Document.linked_module == linked_module)
    
    if owner_id:
        query = query.filter(Document.owner_id == owner_id)
    
    if is_confidential is not None:
        query = query.filter(Document.is_confidential == is_confidential)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order
    documents = query.order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    return documents, total


def create_document(
    db: Session,
    file_path: str,
    checksum: str,
    owner_id: UUID,
    document_data: DocumentUpload
) -> Document:
    """Create new document record"""
    db_document = Document(
        file_path=file_path,
        checksum=checksum,
        owner_id=owner_id,
        **document_data.model_dump()
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def update_document(
    db: Session,
    document_id: UUID,
    document_update: DocumentUpdate
) -> Optional[Document]:
    """Update document metadata"""
    db_document = get_document(db, document_id)
    if db_document is None:
        return None
    
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: UUID) -> Optional[Document]:
    """Delete document record (file must be deleted separately)"""
    db_document = get_document(db, document_id)
    if db_document is None:
        return None
    
    db.delete(db_document)
    db.commit()
    return db_document