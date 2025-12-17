"""
WorkmateOS - Employee Module Models
Departments, Roles & Employees (Core Entities)
"""
from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from app.core.settings.database import Base, generate_uuid
from app.modules.backoffice.chat.models import ChatMessage
from app.modules.dashboards.models import Dashboard, OSPreferences, UserSettings, Notification, ActivityEntry


# ============================================================================
# DEPARTMENTS
# ============================================================================

class Department(Base):
    """Organizational unit such as IT, HR, Finance"""
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True, comment="Short code, e.g. HR, FIN, IT")
    description = Column(Text)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    manager = relationship("Employee", foreign_keys=[manager_id], post_update=True)


# ============================================================================
# ROLES
# ============================================================================

class Role(Base):
    """System roles and access levels"""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    keycloak_id = Column(String, comment="Linked Keycloak role ID")
    permissions_json = Column(
        JSONB,
        default=list,
        comment="List of permissions, e.g. ['hr.view', 'finance.edit']"
    )

    # Relationships
    employees = relationship("Employee", back_populates="role")


# ============================================================================
# EMPLOYEE (Core Entity)
# ============================================================================

class Employee(Base):
    """Core employee entity with organizational & personal info"""
    __tablename__ = "employees"

    # Primary Info
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    employee_code = Column(String, nullable=False, unique=True, comment="KIT-0001 etc.")
    uuid_keycloak = Column(String, comment="Linked Keycloak user ID")

    # Personal Info
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(String, comment="male, female, diverse, other")
    birth_date = Column(Date)
    nationality = Column(String)
    photo_url = Column(String, comment="/uploads/avatars/...")
    bio = Column(Text)

    # Contact Info
    email = Column(String, nullable=False, unique=True)
    phone = Column(String)

    # Address
    address_street = Column(String)
    address_zip = Column(String)
    address_city = Column(String)
    address_country = Column(String)

    # Organization
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    reports_to = Column(UUID(as_uuid=True), ForeignKey("employees.id"), comment="Supervisor")

    # Employment
    employment_type = Column(
        String,
        default="fulltime",
        comment="fulltime, parttime, intern, external"
    )
    hire_date = Column(Date)
    termination_date = Column(Date)
    status = Column(
        String,
        default="active",
        comment="active, inactive, on_leave"
    )

    # Preferences
    timezone = Column(String, default="Europe/Berlin")
    language = Column(String, default="de")
    theme = Column(String, default="catppuccin-frappe")
    notifications_enabled = Column(Boolean, default=True)

    # External Services
    matrix_username = Column(String, comment="@user:intern.phudevelopement.xyz")

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP)

    # Relationships
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    role = relationship("Role", back_populates="employees")
    supervisor = relationship("Employee", remote_side=[id], foreign_keys=[reports_to])
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
    "ChatMessage",
    back_populates="author",
    cascade="all, delete-orphan"
)

    # Reverse relationships (defined in other modules)
    documents = relationship("Document", back_populates="owner")
    reminders = relationship("Reminder", back_populates="owner")
    dashboards = relationship("Dashboard", back_populates="owner", cascade="all, delete-orphan")
    managed_services = relationship("InfraService", back_populates="manager")

    os_preferences: Mapped["OSPreferences"] = relationship(
        "OSPreferences",
        back_populates="owner",
        uselist=False,
        cascade="all, delete-orphan"
    )
    user_settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="owner",
        uselist=False,
        cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    activity_entries: Mapped[list["ActivityEntry"]] = relationship(
        "ActivityEntry",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
