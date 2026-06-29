"""
Training & Certifications Schemas
Pydantic Schemas für Request/Response Validierung.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================================
# TRAINING COURSE SCHEMAS
# ============================================================================

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    provider: Optional[str] = None
    course_type: str = "internal"
    duration_hours: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    is_active: bool = True


class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    provider: Optional[str] = None
    course_type: str
    duration_hours: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    is_active: bool
    participant_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# TRAINING PARTICIPANT SCHEMAS
# ============================================================================

class ParticipantCreate(BaseModel):
    employee_id: UUID
    enrolled_at: Optional[date] = None
    notes: Optional[str] = None


class ParticipantStatusUpdate(BaseModel):
    status: str
    completed_at: Optional[date] = None
    score: Optional[float] = None


class ParticipantResponse(BaseModel):
    id: UUID
    course_id: UUID
    employee_id: UUID
    status: str
    enrolled_at: date
    completed_at: Optional[date] = None
    score: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# CERTIFICATION SCHEMAS
# ============================================================================

class CertificationCreate(BaseModel):
    employee_id: UUID
    name: str
    issuer: Optional[str] = None
    issued_date: date
    expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None
    skill_level: Optional[str] = None


class CertificationResponse(BaseModel):
    id: UUID
    employee_id: UUID
    name: str
    issuer: Optional[str] = None
    issued_date: date
    expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None
    skill_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
