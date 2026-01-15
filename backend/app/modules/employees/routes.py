"""
WorkmateOS - Employee API Routes
REST endpoints for Employee, Department, Role management
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.core.email.service import send_password_reset_notification
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
@require_permissions(["admin.employees.view", "admin.*"])
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    department_id: Optional[UUID] = Query(None),
    role_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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


@employee_router.get("/statistics", response_model=schemas.EmployeeStatistics)
@require_permissions(["admin.employees.view", "admin.*"])
def get_employee_statistics(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Get employee statistics for dashboard

    Returns counts by department, employment type, and active/total employees
    """
    from sqlalchemy import func
    from app.modules.employees.models import Employee, Department

    # Total and active employees
    total = db.query(func.count(Employee.id)).scalar() or 0
    active = db.query(func.count(Employee.id)).filter(
        Employee.status == "active"
    ).scalar() or 0

    # By department
    dept_name_col = func.coalesce(Department.name, "Keine Abteilung")
    dept_stats = db.query(
        dept_name_col.label("dept_name"),
        func.count(Employee.id).label("count")
    ).outerjoin(Department, Employee.department_id == Department.id)\
     .group_by(dept_name_col)\
     .all()

    by_department = {dept: count for dept, count in dept_stats}

    # By employment type
    emp_type_col = func.coalesce(Employee.employment_type, "fulltime")
    type_stats = db.query(
        emp_type_col.label("emp_type"),
        func.count(Employee.id).label("count")
    ).group_by(emp_type_col).all()

    by_employment_type = {emp_type: count for emp_type, count in type_stats}

    return schemas.EmployeeStatistics(
        total_employees=total,
        active_employees=active,
        by_department=by_department,
        by_employment_type=by_employment_type
    )


@employee_router.get("/{employee_id}", response_model=schemas.EmployeeResponse)
@require_permissions(["admin.employees.view", "admin.*"])
def get_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get employee by ID"""
    employee = crud.get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@employee_router.get("/code/{employee_code}", response_model=schemas.EmployeeResponse)
@require_permissions(["admin.employees.view", "admin.*"])
def get_employee_by_code(
    employee_code: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get employee by employee code (e.g. KIT-0001)"""
    employee = crud.get_employee_by_code(db, employee_code)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@employee_router.post("", response_model=schemas.EmployeeResponse, status_code=201)
@require_permissions(["admin.employees.write", "admin.*"])
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
@require_permissions(["admin.employees.write", "admin.*"])
def update_employee(
    employee_id: UUID,
    employee_update: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
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
@require_permissions(["admin.employees.delete", "admin.*"])
def delete_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Soft delete employee (sets status to 'inactive')
    """
    success = crud.delete_employee(db, employee_id)
    if not success:  # bool ist ok
        raise HTTPException(status_code=404, detail="Employee not found")
    return None


# ============================================================================
# ADMIN / USER MANAGEMENT ENDPOINTS
# ============================================================================

@employee_router.post("/{employee_id}/reset-password", status_code=200)
@require_permissions(["admin.employees.write", "admin.*"])
async def reset_employee_password(
    employee_id: UUID,
    password_reset: schemas.PasswordResetRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Reset employee password (Admin only)

    Requires permission: admin.employees.write or admin.*

    Args:
        employee_id: UUID of employee
        password_reset: Password reset data (new password, send notification flag)
        db: Database session
        user: Current authenticated user

    Returns:
        Success message
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Hash new password
    hashed_password = pwd_context.hash(password_reset.new_password)
    employee.password_hash = hashed_password
    db.commit()

    # Send email notification if requested
    if password_reset.send_notification:
        try:
            # Get admin name
            admin_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get('email', 'Administrator')

            # Get employee name
            employee_name = f"{employee.first_name or ''} {employee.last_name or ''}".strip() or employee.email

            # Format reset date
            reset_date = datetime.now().strftime("%d.%m.%Y %H:%M")

            # Send email
            await send_password_reset_notification(
                db=db,
                employee_name=employee_name,
                employee_email=employee.email,
                admin_name=admin_name,
                reset_date=reset_date
            )
        except Exception as e:
            # Log error but don't fail the password reset
            print(f"[PasswordReset] Failed to send email notification: {str(e)}")

    return {"success": True, "message": "Password reset successfully"}


@employee_router.patch("/{employee_id}/status", response_model=schemas.EmployeeResponse)
@require_permissions(["admin.employees.write", "admin.*"])
def update_employee_status(
    employee_id: UUID,
    status_update: schemas.EmployeeStatusUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Update employee status (active, inactive, on_leave)

    Requires permission: admin.employees.write or admin.*

    Args:
        employee_id: UUID of employee
        status_update: Status update data (status, optional reason)
        db: Database session
        user: Current authenticated user

    Returns:
        Updated employee
    """
    # Prevent self-deactivation
    user_id = user.get('id') if isinstance(user, dict) else getattr(user, 'id', None)

    if str(employee_id) == str(user_id) and status_update.status == 'inactive':
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )

    employee = crud.update_status(db, employee_id, status_update.status)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


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
