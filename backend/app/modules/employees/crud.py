"""
WorkmateOS - Employee CRUD Operations
Database operations for Employee, Department, Role
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.modules.employees.models import Employee, Department, Role
from app.modules.employees.schemas import (
    EmployeeCreate, EmployeeUpdate,
    DepartmentCreate, DepartmentUpdate,
    RoleCreate, RoleUpdate
)


# ============================================================================
# EMPLOYEE CRUD
# ============================================================================

def get_employee(db: Session, employee_id: UUID) -> Optional[Employee]:
    """Get employee by ID with relations"""
    return db.query(Employee)\
        .options(joinedload(Employee.department))\
        .options(joinedload(Employee.role))\
        .filter(Employee.id == employee_id)\
        .first()


def get_employee_by_code(db: Session, employee_code: str) -> Optional[Employee]:
    """Get employee by employee code"""
    return db.query(Employee)\
        .filter(Employee.employee_code == employee_code)\
        .first()


def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    """Get employee by email"""
    return db.query(Employee)\
        .filter(Employee.email == email)\
        .first()


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    department_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    status: Optional[str] = None
) -> tuple[list[Employee], int]:
    """
    Get employees with filtering and pagination
    Returns: (employees list, total count)
    """
    query = db.query(Employee)\
        .options(joinedload(Employee.department))\
        .options(joinedload(Employee.role))
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(search_filter),
                Employee.last_name.ilike(search_filter),
                Employee.email.ilike(search_filter),
                Employee.employee_code.ilike(search_filter)
            )
        )
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    if role_id:
        query = query.filter(Employee.role_id == role_id)
    
    if status:
        query = query.filter(Employee.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    employees = query.offset(skip).limit(limit).all()
    
    return employees, total


def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    """Create new employee"""
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(
    db: Session,
    employee_id: UUID,
    employee_update: EmployeeUpdate
) -> Optional[Employee]:
    """Update employee"""
    db_employee = get_employee(db, employee_id)
    if db_employee is None:
        return None
    
    # Update only provided fields
    update_data = employee_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: UUID) -> bool:
    """Delete employee (soft delete by setting status)"""
    db_employee = get_employee(db, employee_id)
    if db_employee is None:
        return False
    
    # Soft delete - type: ignore für SQLAlchemy Column assignment
    db_employee.status = "inactive"  # type: ignore[assignment]
    db.commit()
    return True


# ============================================================================
# DEPARTMENT CRUD
# ============================================================================

def get_department(db: Session, department_id: UUID) -> Optional[Department]:
    """Get department by ID"""
    return db.query(Department).filter(Department.id == department_id).first()


def get_departments(db: Session, skip: int = 0, limit: int = 100) -> list[Department]:
    """Get all departments"""
    return db.query(Department).offset(skip).limit(limit).all()


def create_department(db: Session, department: DepartmentCreate) -> Department:
    """Create new department"""
    db_dept = Department(**department.model_dump())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept


def update_department(
    db: Session,
    department_id: UUID,
    department_update: DepartmentUpdate
) -> Optional[Department]:
    """Update department"""
    db_dept = get_department(db, department_id)
    if db_dept is None:
        return None
    
    update_data = department_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dept, field, value)
    
    db.commit()
    db.refresh(db_dept)
    return db_dept


# ============================================================================
# ROLE CRUD
# ============================================================================

def get_role(db: Session, role_id: UUID) -> Optional[Role]:
    """Get role by ID"""
    return db.query(Role).filter(Role.id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> list[Role]:
    """Get all roles"""
    return db.query(Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: RoleCreate) -> Role:
    """Create new role"""
    db_role = Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(
    db: Session,
    role_id: UUID,
    role_update: RoleUpdate
) -> Optional[Role]:
    """Update role"""
    db_role = get_role(db, role_id)
    if db_role is None:
        return None
    
    update_data = role_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role