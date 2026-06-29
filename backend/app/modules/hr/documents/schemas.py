"""
HR Documents Schemas
Pydantic Schemas für Personaldokumente.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HRDocumentCreate(BaseModel):
    employee_id: UUID
    document_type: str
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_confidential: bool = True


class HRDocumentResponse(BaseModel):
    id: UUID
    employee_id: UUID
    document_type: str
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_confidential: bool
    uploaded_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
