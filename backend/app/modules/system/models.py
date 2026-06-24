"""
WorkmateOS - System Module Models
Infrastructure services and system management
"""
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base, generate_uuid


class InfraService(Base):
    """Technical integrations managed by admins (DB, Keycloak, Matrix, etc.)"""
    __tablename__ = "infra_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    type = Column(
        String,
        comment="database, auth, mail, chat, storage, external_api"
    )
    connection_url = Column(String)
    status = Column(String, default="active")
    last_sync = Column(TIMESTAMP)
    managed_by = Column(UUID(as_uuid=True), ForeignKey("employees.id"))

    # Relationships
    manager = relationship("Employee", back_populates="managed_services")