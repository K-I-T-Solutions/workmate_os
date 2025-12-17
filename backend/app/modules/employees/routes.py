"""
WorkmateOS - Employee API Routes
REST endpoints for Employee, Department, Role management
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.modules.employees import crud, schemas

# Create routers
router = APIRouter()
employee_router = APIRouter(prefix="/employees", tags=["Employees"])
department_router = APIRouter(prefix="/departments", tags=["Departments"])
role_router = APIRouter(prefix="/roles", tags=["Roles"])


# ============================================================================
# EMPLOYEE ENDPOINTS
# ============================================================================

@employee_router.get("", response_model=schemas.EmployeeListResponse)
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    department_id: Optional[UUID] = Query(None),
    role_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get list of employees with filtering and pagination

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Max number of records to return
    - **search**: Search in name, email, employee_code
    - **department_id**: Filter by department
    - **role_id**: Filter by role
    - **status**: Filter by status (active, inactive, on_leave)
    """
    employees, total = crud.get_employees(
        db,
        skip=skip,
        limit=limit,
        search=search,
        department_id=department_id,
        role_id=role_id,
        status=status
    )

    page = (skip // limit) + 1

    return {
        "total": total,
        "page": page,
        "page_size": limit,
        "employees": employees
    }


@employee_router.get("/{employee_id}", response_model=schemas.EmployeeResponse)
def get_employee(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """Get employee by ID"""
    employee = crud.get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@employee_router.get("/code/{employee_code}", response_model=schemas.EmployeeResponse)
def get_employee_by_code(
    employee_code: str,
    db: Session = Depends(get_db)
):
    """Get employee by employee code (e.g. KIT-0001)"""
    employee = crud.get_employee_by_code(db, employee_code)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@employee_router.post("", response_model=schemas.EmployeeResponse, status_code=201)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    """
    Create new employee

    **Required fields:**
    - employee_code: Unique code (e.g. KIT-0001)
    - email: Valid email address
    """
    # Check if employee_code already exists
    existing = crud.get_employee_by_code(db, employee.employee_code)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Employee code '{employee.employee_code}' already exists"
        )

    # Check if email already exists
    existing_email = crud.get_employee_by_email(db, employee.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail=f"Email '{employee.email}' already exists"
        )

    return crud.create_employee(db, employee)


@employee_router.put("/{employee_id}", response_model=schemas.EmployeeResponse)
def update_employee(
    employee_id: UUID,
    employee_update: schemas.EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """Update employee by ID"""
    # Check if email is being changed and already exists
    if employee_update.email is not None:
        existing_email = crud.get_employee_by_email(db, employee_update.email)
        # Type-safe comparison
        if existing_email is not None:
            existing_id: UUID = existing_email.id  # type: ignore[assignment]
            if existing_id != employee_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Email '{employee_update.email}' already exists"
                )

    employee = crud.update_employee(db, employee_id, employee_update)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@employee_router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Soft delete employee (sets status to 'inactive')
    """
    success = crud.delete_employee(db, employee_id)
    if not success:  # bool ist ok
        raise HTTPException(status_code=404, detail="Employee not found")
    return None


# ============================================================================
# DEPARTMENT ENDPOINTS
# ============================================================================

@department_router.get("", response_model=list[schemas.DepartmentResponse])
def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get list of all departments"""
    return crud.get_departments(db, skip=skip, limit=limit)


@department_router.get("/{department_id}", response_model=schemas.DepartmentResponse)
def get_department(
    department_id: UUID,
    db: Session = Depends(get_db)
):
    """Get department by ID"""
    department = crud.get_department(db, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@department_router.post("", response_model=schemas.DepartmentResponse, status_code=201)
def create_department(
    department: schemas.DepartmentCreate,
    db: Session = Depends(get_db)
):
    """Create new department"""
    return crud.create_department(db, department)


@department_router.put("/{department_id}", response_model=schemas.DepartmentResponse)
def update_department(
    department_id: UUID,
    department_update: schemas.DepartmentUpdate,
    db: Session = Depends(get_db)
):
    """Update department by ID"""
    department = crud.update_department(db, department_id, department_update)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


# ============================================================================
# ROLE ENDPOINTS
# ============================================================================

@role_router.get("", response_model=list[schemas.RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get list of all roles"""
    return crud.get_roles(db, skip=skip, limit=limit)


@role_router.get("/{role_id}", response_model=schemas.RoleResponse)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Get role by ID"""
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@role_router.post("", response_model=schemas.RoleResponse, status_code=201)
def create_role(
    role: schemas.RoleCreate,
    db: Session = Depends(get_db)
):
    """Create new role"""
    return crud.create_role(db, role)


@role_router.put("/{role_id}", response_model=schemas.RoleResponse)
def update_role(
    role_id: UUID,
    role_update: schemas.RoleUpdate,
    db: Session = Depends(get_db)
):
    """Update role by ID"""
    role = crud.update_role(db, role_id, role_update)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


# ============================================================================
# Include all routers
# ============================================================================

router.include_router(employee_router)
router.include_router(department_router)
router.include_router(role_router)
