
"""
WorkmateOS - Employee Schemas
Pydantic models for request/response validation
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


# ============================================================================
# DEPARTMENT SCHEMAS
# ============================================================================

class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[UUID] = None


class DepartmentResponse(DepartmentBase):
    id: UUID
    manager_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# ROLE SCHEMAS
# ============================================================================

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions_json: Optional[list[str]] = Field(default_factory=list)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions_json: Optional[list[str]] = None


class RoleResponse(RoleBase):
    id: UUID
    keycloak_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# EMPLOYEE SCHEMAS
# ============================================================================

class EmployeeBase(BaseModel):
    """Base fields for Employee"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None
    
    # Address
    address_street: Optional[str] = None
    address_zip: Optional[str] = None
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    
    # Organization
    department_id: Optional[UUID] = None
    role_id: Optional[UUID] = None
    reports_to: Optional[UUID] = None
    
    # Employment
    employment_type: Optional[str] = Field(default="fulltime")
    hire_date: Optional[date] = None
    status: Optional[str] = Field(default="active")
    
    # Preferences
    timezone: Optional[str] = Field(default="Europe/Berlin")
    language: Optional[str] = Field(default="de")
    theme: Optional[str] = Field(default="catppuccin-frappe")
    notifications_enabled: Optional[bool] = Field(default=True)


class EmployeeCreate(EmployeeBase):
    """Create new employee"""
    employee_code: str = Field(..., description="Unique employee code like KIT-0001")
    email: EmailStr


class EmployeeUpdate(BaseModel):
    """Update existing employee - all fields optional"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    
    # Address
    address_street: Optional[str] = None
    address_zip: Optional[str] = None
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    
    # Organization
    department_id: Optional[UUID] = None
    role_id: Optional[UUID] = None
    reports_to: Optional[UUID] = None
    
    # Employment
    employment_type: Optional[str] = None
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    status: Optional[str] = None
    
    # Preferences
    timezone: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    matrix_username: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Employee response with all fields"""
    id: UUID
    employee_code: str
    uuid_keycloak: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    termination_date: Optional[date] = None
    matrix_username: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    # Nested objects (optional)
    department: Optional[DepartmentResponse] = None
    role: Optional[RoleResponse] = None
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Paginated list of employees"""
    total: int
    page: int
    page_size: int
    employees: list[EmployeeResponse]