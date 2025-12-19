"""
WorkmateOS - Documents API Routes
Central document handling using Nextcloud as storage backend
"""

import hashlib
import os
from tempfile import NamedTemporaryFile
from typing import Optional
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Query,
    Form,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.modules.documents import crud, schemas
from app.modules.documents.storage import NextcloudStorage

# ---------------------------------------------------------------------------

router = APIRouter(prefix="/documents", tags=["Documents"])
storage = NextcloudStorage()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def calculate_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


# ---------------------------------------------------------------------------
# List / Get
# ---------------------------------------------------------------------------

@router.get("", response_model=schemas.DocumentListResponse)
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    linked_module: Optional[str] = Query(None),
    owner_id: Optional[UUID] = Query(None),
    is_confidential: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    documents, total = crud.get_documents(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        linked_module=linked_module,
        owner_id=owner_id,
        is_confidential=is_confidential,
    )

    for doc in documents:
        doc.download_url = f"/api/documents/{doc.id}/download"  # type: ignore

    return {
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "documents": documents,
    }


@router.get("/{document_id}", response_model=schemas.DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.download_url = f"/api/documents/{document.id}/download"  # type: ignore
    return document


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

@router.post("", response_model=schemas.DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    owner_id: UUID = Form(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    linked_module: Optional[str] = Form(None),
    is_confidential: bool = Form(False),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    checksum = calculate_checksum(content)

    extension = get_file_extension(file.filename)
    file_type = extension.lstrip(".")

    remote_path = "/".join([
    "workmate",
    linked_module or "general",
    str(owner_id),
    f"{uuid4()}{extension}",
    ])


    # Upload to Nextcloud
    storage.upload(remote_path, content)

    document_data = schemas.DocumentUpload(
        title=title or file.filename,
        type=file_type,
        category=category,
        linked_module=linked_module,
        is_confidential=is_confidential,
    )

    document = crud.create_document(
        db=db,
        file_path=remote_path,
        checksum=checksum,
        owner_id=owner_id,
        document_data=document_data,
    )

    document.download_url = f"/api/documents/{document.id}/download"  # type: ignore
    document.file_size = len(content)  # type: ignore

    return document


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

@router.get("/{document_id}/download")
def download_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    tmp = NamedTemporaryFile(delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        storage.client.download(
            remote_path=document.file_path,
            local_path=tmp_path,
        )

        filename = document.title or f"document_{document_id}"

        def iterator():
            with open(tmp_path, "rb") as f:
                yield from f

        return StreamingResponse(
            iterator(),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@router.put("/{document_id}", response_model=schemas.DocumentResponse)
def update_document(
    document_id: UUID,
    document_update: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
):
    document = crud.update_document(db, document_id, document_update)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.download_url = f"/api/documents/{document.id}/download"  # type: ignore
    return document


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    storage.delete(str(document.file_path))
    crud.delete_document(db, document_id)

    return None
