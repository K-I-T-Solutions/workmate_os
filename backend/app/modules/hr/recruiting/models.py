"""
Recruiting Module Models
JobPosting + Application
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.settings.database import Base, generate_uuid
from app.modules.hr.enums import JobPostingStatus, ApplicationStatus


class JobPosting(Base):
    __tablename__ = "hr_job_postings"
    __table_args__ = (
        Index("ix_job_postings_status", "status"),
        Index("ix_job_postings_department_id", "department_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    remote: Mapped[bool] = mapped_column(Boolean, default=False)
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    salary_min: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    salary_max: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    department_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(50), default=JobPostingStatus.DRAFT.value)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deadline: Mapped[Optional[date]] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    applications: Mapped[list["Application"]] = relationship("Application", back_populates="job_posting", cascade="all, delete-orphan")
    department: Mapped[Optional[object]] = relationship("Department", foreign_keys=[department_id])


class Application(Base):
    __tablename__ = "hr_applications"
    __table_args__ = (
        Index("ix_applications_job_posting_id", "job_posting_id"),
        Index("ix_applications_status", "status"),
        Index("ix_applications_email", "email"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)

    job_posting_id: Mapped[UUID] = mapped_column(ForeignKey("hr_job_postings.id", ondelete="CASCADE"), nullable=False)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    cv_url: Mapped[Optional[str]] = mapped_column(String(500))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default=ApplicationStatus.RECEIVED.value)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    job_posting: Mapped["JobPosting"] = relationship("JobPosting", back_populates="applications")
