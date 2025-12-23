"""
WorkmateOS - Authentication Service
Handles password-based authentication, JWT tokens, and sessions
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.modules.employees.models import Employee, Role
from app.core.settings.database import get_db

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[Employee]:
        """
        Authenticate a user with email and password
        Returns the Employee if authentication is successful, None otherwise
        """
        # Find user by email
        employee = db.scalar(select(Employee).where(Employee.email == email))

        if not employee:
            return None

        if not employee.password_hash:
            return None

        # Verify password
        if not AuthService.verify_password(password, employee.password_hash):
            return None

        # Check if user is active
        if employee.status != "active":
            return None

        return employee

    @staticmethod
    def get_user_permissions(db: Session, employee: Employee) -> list[str]:
        """
        Get all permissions for a user based on their role
        Returns list of permission strings like ['hr.view', 'hr.edit', ...]
        """
        if not employee.role_id:
            return []

        role = db.scalar(select(Role).where(Role.id == employee.role_id))

        if not role or not role.permissions_json:
            return []

        return role.permissions_json if isinstance(role.permissions_json, list) else []

    @staticmethod
    def create_token_for_user(db: Session, employee: Employee) -> dict:
        """
        Create a JWT token with user information and permissions
        Returns dict with access_token and token_type
        """
        # Get permissions
        permissions = AuthService.get_user_permissions(db, employee)

        # Create token payload
        token_data = {
            "sub": str(employee.id),
            "email": employee.email,
            "employee_code": employee.employee_code,
            "role_id": str(employee.role_id) if employee.role_id else None,
            "role_name": employee.role.name if employee.role else None,
            "department_id": str(employee.department_id) if employee.department_id else None,
            "permissions": permissions,
        }

        access_token = AuthService.create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        }

    @staticmethod
    def set_user_password(db: Session, employee_id: str, password: str) -> bool:
        """
        Set or update password for a user
        Returns True if successful, False otherwise
        """
        try:
            employee = db.scalar(select(Employee).where(Employee.id == employee_id))

            if not employee:
                return False

            employee.password_hash = AuthService.hash_password(password)
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            print(f"Error setting password: {e}")
            return False
