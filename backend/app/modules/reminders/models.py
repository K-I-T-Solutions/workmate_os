"""
WorkmateOS - Reminders Module Models
Universal reminder and notification system
"""
from sqlalchemy import Column, String, Text, Date, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.settings.database import Base, generate_uuid


class Reminder(Base):
    """Universal reminder and notification system"""
    __tablename__ = "reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    title = Column(String)
    description = Column(Text)
    due_date = Column(Date)
    priority = Column(String, comment="low, medium, high, critical")

    # Polymorphic entity linking
    linked_entity_type = Column(String, comment="Target type, e.g. Document, Ticket")
    linked_entity_id = Column(UUID(as_uuid=True))

    owner_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    status = Column(String, default="open", comment="open, done, overdue")
    created_at = Column(TIMESTAMP, server_default=func.now())
    notified = Column(Boolean, default=False)

    # Relationships
    owner = relationship("Employee", back_populates="reminders")
