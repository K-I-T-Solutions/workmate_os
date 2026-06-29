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
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.storage.factory import get_storage
from app.modules.documents import crud, schemas

router = APIRouter(prefix="/documents", tags=["Documents"])


def calculate_checksum(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def _resolve_download(file_path_str: str) -> bytes:
    """
    Datei über Storage-Backend laden.
    Fallback auf lokales Dateisystem für Legacy-Records mit absolutem Pfad.
    """
    storage = get_storage()
    path = Path(file_path_str)

    # Legacy: absoluter Pfad → direkt von Disk lesen
    if path.is_absolute():
        if not path.exists():
            raise FileNotFoundError(f"File not found on disk: {file_path_str}")
        return path.read_bytes()

    # Neu: relativer Pfad → über Storage-Backend
    return storage.download(file_path_str)


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
    for doc in documents:
        doc.download_url = f"/api/documents/{doc.id}/download"  # type: ignore[attr-defined]

    return {
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "documents": documents
    }


@router.get("/{document_id}", response_model=schemas.DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    document = crud.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
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
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    checksum = calculate_checksum(content)

    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid4()}{file_extension}"

    # Storage-Backend verwenden (local / nextcloud / s3)
    storage = get_storage()
    try:
        storage.upload(unique_filename, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload fehlgeschlagen: {e}")

    file_type = file_extension.lstrip(".")
    doc_title = title or file.filename

    document_data = schemas.DocumentUpload(
        title=doc_title,
        type=file_type,
        category=category,
        linked_module=linked_module,
        is_confidential=is_confidential
    )

    document = crud.create_document(
        db,
        file_path=unique_filename,   # relativer Pfad, nicht absolut
        checksum=checksum,
        owner_id=owner_id,
        document_data=document_data
    )

    document.download_url = f"/api/documents/{document.id}/download"  # type: ignore[attr-defined]
    document.file_size = len(content)  # type: ignore[attr-defined]
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    document = crud.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path_str = str(document.file_path)
    suffix = Path(file_path_str).suffix
    filename = str(document.title) if document.title else f"document_{document_id}{suffix}"

    try:
        content = _resolve_download(file_path_str)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden (Storage)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage-Fehler: {e}")

    # MIME-Typ aus Extension ableiten
    ext = suffix.lstrip(".").lower()
    mime_map = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png", "gif": "image/gif",
        "webp": "image/webp", "svg": "image/svg+xml",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
        "txt": "text/plain",
        "zip": "application/zip",
    }
    media_type = mime_map.get(ext, "application/octet-stream")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.put("/{document_id}", response_model=schemas.DocumentResponse)
def update_document(
    document_id: UUID,
    document_update: schemas.DocumentUpdate,
    db: Session = Depends(get_db)
):
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
    document = crud.delete_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path_str = str(document.file_path)
    storage = get_storage()
    try:
        path = Path(file_path_str)
        if path.is_absolute():
            if path.exists():
                os.remove(path)
        else:
            storage.delete(file_path_str)
    except Exception:
        pass  # Datei schon weg oder Storage-Fehler → DB-Eintrag trotzdem gelöscht

    return None
