"""Recruiting Schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class JobPostingBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    remote: bool = False
    employment_type: Optional[str] = None
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    department_id: Optional[UUID] = None
    deadline: Optional[date] = None


class JobPostingCreate(JobPostingBase):
    status: str = "draft"


class JobPostingUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    employment_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    department_id: Optional[UUID] = None
    status: Optional[str] = None
    deadline: Optional[date] = None


class JobPostingResponse(JobPostingBase):
    id: UUID
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    application_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class JobPostingListResponse(BaseModel):
    items: List[JobPostingResponse]
    total: int
    skip: int
    limit: int


# ── Applications ──

class ApplicationBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    cover_letter: Optional[str] = None
    cv_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    job_posting_id: UUID


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    phone: Optional[str] = None
    cv_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: UUID
    job_posting_id: UUID
    status: str
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    rating: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    items: List[ApplicationResponse]
    total: int
    skip: int
    limit: int
