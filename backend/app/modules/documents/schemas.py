"""
WorkmateOS - Documents Schemas
Pydantic models for document management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class DocumentBase(BaseModel):
    """Base document fields"""
    title: Optional[str] = None
    type: Optional[str] = Field(None, description="pdf, image, doc, xlsx, etc.")
    category: Optional[str] = Field(None, description="Contract, Invoice, Certificate, etc.")
    linked_module: Optional[str] = Field(None, description="HR, Finance, Backoffice")
    is_confidential: bool = Field(default=False)


class DocumentUpload(DocumentBase):
    """Document upload metadata"""
    pass


class DocumentUpdate(BaseModel):
    """Update document metadata"""
    title: Optional[str] = None
    category: Optional[str] = None
    linked_module: Optional[str] = None
    is_confidential: Optional[bool] = None


class DocumentResponse(DocumentBase):
    """Document response with all fields"""
    id: UUID
    file_path: str
    owner_id: Optional[UUID] = None
    uploaded_at: Optional[datetime] = None
    checksum: Optional[str] = None
    
    # File info
    file_size: Optional[int] = Field(None, description="File size in bytes")
    download_url: Optional[str] = Field(None, description="Download URL")
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Paginated list of documents"""
    total: int
    page: int
    page_size: int
    documents: list[DocumentResponse]