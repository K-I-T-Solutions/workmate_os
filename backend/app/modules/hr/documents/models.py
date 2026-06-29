"""
HR Documents Models
Personaldokumente für Mitarbeiter.
"""
from __future__ import annotations
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, ForeignKey, Date, Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.employees.models import Employee


class HRDocument(Base, UUIDMixin, TimestampMixin):
    """Personaldokument eines Mitarbeiters"""
    __tablename__ = "hr_employee_documents"
    __table_args__ = (
        Index("ix_hr_employee_documents_employee_id", "employee_id"),
        Index("ix_hr_employee_documents_document_type", "document_type"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Datei-Metadaten (Nextcloud / Storage)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Gültigkeit
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_until: Mapped[Optional[date]] = mapped_column(Date)

    # Vertraulichkeit
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=True)

    # Hochgeladen von
    uploaded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    uploaded_by: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[uploaded_by_id])
