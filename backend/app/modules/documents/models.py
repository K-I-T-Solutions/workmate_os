"""
WorkmateOS - Documents Module Models
Central file storage and reference system
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base, generate_uuid


class Document(Base):
    """Central file storage and reference system"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    title = Column(String)
    file_path = Column(String, nullable=False)
    type = Column(String, comment="pdf, image, doc, etc.")
    category = Column(String, comment="e.g. Krankmeldung, Vertrag, Rechnung")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    linked_module = Column(String, nullable= True,comment="Origin module e.g. HR, Finance")
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
    checksum = Column(String)
    is_confidential = Column(Boolean, default=False)

    # Relationships
    owner = relationship("Employee", back_populates="documents")