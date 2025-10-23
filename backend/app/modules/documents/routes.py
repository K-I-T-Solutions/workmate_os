"""
WorkmateOS - Documents API Routes
REST endpoints for document management (Upload, Download, List, Delete)
"""
import hashlib
import os
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.modules.documents import crud, schemas

router = APIRouter(prefix="/documents", tags=["Documents"])

# Upload directory
UPLOAD_DIR = Path(settings.UPLOAD_DIR or "/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def calculate_checksum(file_content: bytes) -> str:
    """Calculate SHA256 checksum of file"""
    return hashlib.sha256(file_content).hexdigest()


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@router.get("", response_model=schemas.DocumentListResponse)
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    linked_module: Optional[str] = Query(None),
    owner_id: Optional[UUID] = Query(None),
    is_confidential: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get list of documents with filtering and pagination
    
    - **skip**: Number of records to skip
    - **limit**: Max number of records to return
    - **search**: Search in title and filename
    - **category**: Filter by category (Contract, Invoice, etc.)
    - **linked_module**: Filter by module (HR, Finance, etc.)
    - **owner_id**: Filter by owner
    - **is_confidential**: Filter confidential documents
    """
    documents, total = crud.get_documents(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        linked_module=linked_module,
        owner_id=owner_id,
        is_confidential=is_confidential
    )
    
    # Add download URLs
    for doc in documents:
        doc.download_url = f"/api/documents/{doc.id}/download"  # type: ignore[attr-defined]
    
    page = (skip // limit) + 1
    
    return {
        "total": total,
        "page": page,
        "page_size": limit,
        "documents": documents
    }


@router.get("/{document_id}", response_model=schemas.DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Get document metadata by ID"""
    document = crud.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Add download URL
    document.download_url = f"/api/documents/{document.id}/download"  # type: ignore[attr-defined]
    
    return document


@router.post("", response_model=schemas.DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    linked_module: Optional[str] = Form(None),
    is_confidential: bool = Form(False),
    owner_id: UUID = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new document
    
    **Form Data:**
    - **file**: The file to upload (required)
    - **owner_id**: UUID of the document owner (required)
    - **title**: Document title (optional, uses filename if not provided)
    - **category**: Document category (Contract, Invoice, etc.)
    - **linked_module**: Origin module (HR, Finance, etc.)
    - **is_confidential**: Mark as confidential (default: false)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Read file content
    content = await file.read()
    
    # Calculate checksum
    checksum = calculate_checksum(content)
    
    # Generate unique filename
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Detect file type from extension
    file_type = file_extension.lstrip(".")
    
    # Use filename as title if not provided
    doc_title = title or file.filename
    
    # Create document record
    document_data = schemas.DocumentUpload(
        title=doc_title,
        type=file_type,
        category=category,
        linked_module=linked_module,
        is_confidential=is_confidential
    )
    
    document = crud.create_document(
        db,
        file_path=str(file_path),
        checksum=checksum,
        owner_id=owner_id,
        document_data=document_data
    )
    
    # Add download URL
    document.download_url = f"/api/documents/{document.id}/download"  # type: ignore[attr-defined]
    document.file_size = len(content)  # type: ignore[attr-defined]
    
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download document file
    
    Returns the actual file for download
    """
    document = crud.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = Path(str(document.file_path))  # type: ignore[arg-type]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Get original filename from title or use document ID
    filename: str = str(document.title) if document.title is not None else f"document_{document_id}{file_path.suffix}"
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@router.put("/{document_id}", response_model=schemas.DocumentResponse)
def update_document(
    document_id: UUID,
    document_update: schemas.DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update document metadata (not the file itself)"""
    document = crud.update_document(db, document_id, document_update)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.download_url = f"/api/documents/{document.id}/download"  # type: ignore[attr-defined]
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete document (both database record and file)
    """
    document = crud.delete_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete physical file
    file_path = Path(str(document.file_path))  # type: ignore[arg-type]
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Could not delete file {file_path}: {e}")
    
    return None