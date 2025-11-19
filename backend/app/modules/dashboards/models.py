"""
WorkmateOS - Dashboards Module Models
User-specific workspace layout and preferences
"""
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base, generate_uuid


class Dashboard(Base):
    """User-specific workspace layout and preferences"""
    __tablename__ = "dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    widgets_json = Column(JSONB)
    layout_json = Column(JSONB)
    theme = Column(String, default="catppuccin-frappe")
    last_accessed = Column(TIMESTAMP)

    # Relationships
    owner = relationship("Employee", back_populates="dashboards")