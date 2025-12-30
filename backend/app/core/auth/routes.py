"""
WorkmateOS - Authentication Routes
Endpoints for login, logout, and session management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.settings.database import get_db
from app.core.auth.service import AuthService
from app.core.auth.zitadel import ZitadelAuth
from app.modules.employees.models import Employee
from sqlalchemy import select

# Router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security
security = HTTPBearer(auto_error=False)


# ============================================================================
# SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class OIDCLoginRequest(BaseModel):
    """OIDC/SSO login request schema"""
    id_token: str
    access_token: str | None = None  # Optional: used to fetch user info


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    """Current user response schema"""
    id: str
    employee_code: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    gender: Optional[str]
    birth_date: Optional[str]
    nationality: Optional[str]
    bio: Optional[str]
    address_street: Optional[str]
    address_zip: Optional[str]
    address_city: Optional[str]
    address_country: Optional[str]
    role: Optional[dict]
    department: Optional[dict]
    employment_type: Optional[str]
    hire_date: Optional[str]
    status: Optional[str]
    timezone: Optional[str]
    language: Optional[str]
    theme: Optional[str]
    permissions: list[str]
    photo_url: Optional[str]


class SetPasswordRequest(BaseModel):
    """Set password request schema"""
    employee_id: str
    password: str


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str
    new_password: str


# ============================================================================
# DEPENDENCY: Get Current User from Token
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Employee:
    """
    Dependency to get current authenticated user from JWT token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = AuthService.decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Get user from database
    employee = db.scalar(select(Employee).where(Employee.id == user_id))

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if employee.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active",
        )

    return employee


# ============================================================================
# ROUTES
# ============================================================================

@auth_router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password
    Returns JWT access token
    """
    # Authenticate user
    employee = AuthService.authenticate_user(db, request.email, request.password)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token
    token_data = AuthService.create_token_for_user(db, employee)

    # Prepare user data
    user_data = {
        "id": str(employee.id),
        "employee_code": employee.employee_code,
        "email": employee.email,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "role": {
            "id": str(employee.role.id),
            "name": employee.role.name,
        } if employee.role else None,
        "department": {
            "id": str(employee.department.id),
            "name": employee.department.name,
            "code": employee.department.code,
        } if employee.department else None,
        "permissions": AuthService.get_user_permissions(db, employee),
        "theme": employee.theme or "kit-standard",
    }

    return {
        **token_data,
        "user": user_data,
    }


@auth_router.post("/oidc/login", response_model=LoginResponse)
async def oidc_login(
    request: OIDCLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Zitadel OIDC token (SSO)
    Returns JWT access token compatible with existing frontend
    """
    # Verify Zitadel token
    zitadel_payload = await ZitadelAuth.verify_token(request.id_token)

    if not zitadel_payload:
        print("[DEBUG OIDC] Token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OIDC token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"[DEBUG OIDC] Token verified, payload: {zitadel_payload}")

    # Fetch user info from UserInfo endpoint if access_token provided
    user_info = None
    if request.access_token:
        user_info = await ZitadelAuth.get_user_info(request.access_token)
        print(f"[DEBUG OIDC] UserInfo fetched: {user_info}")

    # Merge user_info into payload (userinfo takes priority)
    combined_payload = {**zitadel_payload}
    if user_info:
        combined_payload.update(user_info)

    print(f"[DEBUG OIDC] Combined payload: {combined_payload}")

    # Get or create user from Zitadel data
    employee = ZitadelAuth.get_or_create_user(db, combined_payload)

    print(f"[DEBUG OIDC] Employee result: {employee}")

    if not employee:
        print("[DEBUG OIDC] Failed to get/create employee")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate user via OIDC",
        )

    # Create local JWT token (same as password login)
    token_data = AuthService.create_token_for_user(db, employee)

    # Prepare user data
    user_data = {
        "id": str(employee.id),
        "employee_code": employee.employee_code,
        "email": employee.email,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "role": {
            "id": str(employee.role.id),
            "name": employee.role.name,
        } if employee.role else None,
        "department": {
            "id": str(employee.department.id),
            "name": employee.department.name,
            "code": employee.department.code,
        } if employee.department else None,
        "permissions": AuthService.get_user_permissions(db, employee),
        "theme": employee.theme or "kit-standard",
    }

    return {
        **token_data,
        "user": user_data,
    }


@auth_router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    """
    permissions = AuthService.get_user_permissions(db, current_user)

    return {
        "id": str(current_user.id),
        "employee_code": current_user.employee_code,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "gender": current_user.gender,
        "birth_date": current_user.birth_date.isoformat() if current_user.birth_date else None,
        "nationality": current_user.nationality,
        "bio": current_user.bio,
        "address_street": current_user.address_street,
        "address_zip": current_user.address_zip,
        "address_city": current_user.address_city,
        "address_country": current_user.address_country,
        "role": {
            "id": str(current_user.role.id),
            "name": current_user.role.name,
            "description": current_user.role.description,
        } if current_user.role else None,
        "department": {
            "id": str(current_user.department.id),
            "name": current_user.department.name,
            "code": current_user.department.code,
        } if current_user.department else None,
        "employment_type": current_user.employment_type,
        "hire_date": current_user.hire_date.isoformat() if current_user.hire_date else None,
        "status": current_user.status,
        "timezone": current_user.timezone,
        "language": current_user.language,
        "theme": current_user.theme,
        "permissions": permissions,
        "photo_url": current_user.photo_url,
    }


@auth_router.post("/logout")
async def logout(
    current_user: Employee = Depends(get_current_user)
):
    """
    Logout current user
    Note: With JWT, logout is handled client-side by removing the token
    This endpoint is kept for consistency and future session management
    """
    return {
        "message": "Successfully logged out",
        "user_id": str(current_user.id),
    }


@auth_router.post("/set-password")
async def set_password(
    request: SetPasswordRequest,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set or update password for a user
    Note: In production, this should have proper authorization checks
    """
    success = AuthService.set_user_password(db, request.employee_id, request.password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to set password"
        )

    return {
        "message": "Password set successfully",
        "employee_id": request.employee_id,
    }


@auth_router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for the currently authenticated user
    """
    # Verify current password
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No password set for this account"
        )

    if not AuthService.verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )

    # Set new password
    success = AuthService.set_user_password(db, str(current_user.id), request.new_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )

    return {
        "message": "Password changed successfully",
    }


@auth_router.get("/check")
async def check_auth(
    current_user: Employee = Depends(get_current_user)
):
    """
    Quick check if token is valid
    """
    return {
        "authenticated": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
    }
