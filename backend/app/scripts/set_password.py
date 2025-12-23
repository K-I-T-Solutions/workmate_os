#!/usr/bin/env python3
"""
Script to set password for a user
Usage: python set_password.py <email> <password>
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.settings.database import SessionLocal
from app.core.auth.service import AuthService
from app.modules.employees.models import Employee
from sqlalchemy import select


def set_user_password(email: str, password: str):
    """Set password for a user by email"""
    db = SessionLocal()

    try:
        # Find user
        employee = db.scalar(select(Employee).where(Employee.email == email))

        if not employee:
            print(f"❌ User with email '{email}' not found")
            return False

        # Set password
        success = AuthService.set_user_password(db, str(employee.id), password)

        if success:
            print(f"✅ Password set successfully for user: {employee.first_name} {employee.last_name} ({email})")
            print(f"   Employee Code: {employee.employee_code}")
            return True
        else:
            print(f"❌ Failed to set password")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_password.py <email> <password>")
        print("\nExample:")
        print("  python set_password.py joshua@kit-it-koblenz.de MySecurePassword123")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    print(f"\n🔐 Setting password for user: {email}")
    print(f"   Password length: {len(password)} characters\n")

    success = set_user_password(email, password)

    sys.exit(0 if success else 1)
