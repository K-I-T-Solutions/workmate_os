"""
Workmate OS - Zitadel OIDC Integration
Handles SSO authentication via Zitadel
"""
import logging
import httpx
from jose import jwt, JWTError
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.settings.config import settings
from app.modules.employees.models import Employee, Role
from app.core.auth.role_mapping import extract_roles_from_token, map_zitadel_roles
import re

logger = logging.getLogger(__name__)


class ZitadelAuth:
    """Zitadel OIDC authentication handler"""

    @staticmethod
    async def get_user_info(access_token: str) -> Optional[Dict]:
        """
        Fetch user information from Zitadel UserInfo endpoint
        """
        try:
            userinfo_uri = f"{settings.ZITADEL_ISSUER}/oidc/v1/userinfo"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    userinfo_uri,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.debug(" Failed to fetch user info: {e}")
            return None

    @staticmethod
    async def get_jwks() -> dict:
        """
        Fetch JWKS (JSON Web Key Set) from Zitadel
        Used to verify JWT token signatures
        """
        jwks_uri = f"{settings.ZITADEL_ISSUER}/oauth/v2/keys"

        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_uri, timeout=10.0)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def verify_token(token: str) -> Optional[Dict]:
        """
        Verify Zitadel JWT token
        Returns decoded payload if valid, None otherwise
        """
        try:
            # Get JWKS
            jwks = await ZitadelAuth.get_jwks()

            # Decode token header to get kid (key ID)
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            logger.debug(" Token kid: {kid}")
            logger.debug(" Available kids: {[k.get('kid') for k in jwks.get('keys', [])]}")

            # Find matching key in JWKS
            rsa_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = key
                    break

            if not rsa_key:
                logger.debug(" RSA key not found for kid: {kid}")
                return None

            # Verify and decode token
            logger.debug(" Verifying token with issuer: {settings.ZITADEL_ISSUER}, audience: {settings.ZITADEL_CLIENT_ID}")
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.ZITADEL_CLIENT_ID,
                issuer=settings.ZITADEL_ISSUER,
                options={
                    "verify_at_hash": False  # Disable at_hash validation (we only have ID token)
                }
            )

            logger.debug(" Token verified successfully! Sub: {payload.get('sub')}")
            return payload

        except JWTError as e:
            logger.debug(" JWTError: {e}")
            return None
        except Exception as e:
            logger.debug(" Exception: {e}")
            return None

    @staticmethod
    def get_next_employee_code(db: Session, prefix: str = "KIT") -> str:
        """
        Generate next sequential employee code (e.g., KIT-0001, KIT-0002, ...)

        Args:
            db: Database session
            prefix: Code prefix (default: "KIT")

        Returns:
            Next sequential employee code
        """
        # Query all employee codes with this prefix
        pattern = f"{prefix}-%"
        employees = db.execute(
            select(Employee.employee_code).where(
                Employee.employee_code.like(pattern)
            )
        ).scalars().all()

        # Extract numeric parts and find highest number
        max_number = 0
        code_pattern = re.compile(rf"{prefix}-(\d+)")

        for code in employees:
            match = code_pattern.match(code)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

        # Generate next code
        next_number = max_number + 1
        return f"{prefix}-{next_number:04d}"

    @staticmethod
    def get_or_create_user(db: Session, zitadel_payload: Dict) -> Optional[Employee]:
        """
        Get existing user by Zitadel ID or create new one

        Args:
            db: Database session
            zitadel_payload: Decoded JWT payload from Zitadel

        Returns:
            Employee object or None
        """
        # Extract user info from Zitadel token
        zitadel_user_id = zitadel_payload.get("sub")
        email = zitadel_payload.get("email")
        given_name = zitadel_payload.get("given_name", "")
        family_name = zitadel_payload.get("family_name", "")

        logger.debug("[DEBUG get_or_create_user] zitadel_user_id: {zitadel_user_id}")
        logger.debug("[DEBUG get_or_create_user] email: {email}")
        logger.debug("[DEBUG get_or_create_user] given_name: {given_name}")
        logger.debug("[DEBUG get_or_create_user] family_name: {family_name}")
        logger.debug("[DEBUG get_or_create_user] Full payload keys: {list(zitadel_payload.keys())}")

        if not zitadel_user_id or not email:
            logger.debug("[DEBUG get_or_create_user] Missing required fields! user_id={zitadel_user_id}, email={email}")
            return None

        # Extract and map roles from Zitadel token
        zitadel_roles = extract_roles_from_token(zitadel_payload)
        mapped_role_name, zitadel_role_id = map_zitadel_roles(zitadel_roles)

        logger.debug("[DEBUG get_or_create_user] Zitadel roles: {zitadel_roles}")
        logger.debug("[DEBUG get_or_create_user] Mapped to Workmate role: {mapped_role_name}")
        logger.debug("[DEBUG get_or_create_user] Zitadel Role ID: {zitadel_role_id}")

        # Find the role in the database (by name or by keycloak_id)
        role = None
        if mapped_role_name:
            # First try to find by name
            role = db.scalar(
                select(Role).where(Role.name == mapped_role_name)
            )
            if role:
                logger.debug("[DEBUG get_or_create_user] Found role in DB: {role.name} (ID: {role.id})")

                # Update keycloak_id if we have a Zitadel role ID and it's not set
                if zitadel_role_id and role.keycloak_id != zitadel_role_id:
                    logger.debug("[DEBUG get_or_create_user] Updating role.keycloak_id from '{role.keycloak_id}' to '{zitadel_role_id}'")
                    role.keycloak_id = zitadel_role_id
                    db.commit()
            else:
                logger.debug("[DEBUG get_or_create_user] Role '{mapped_role_name}' not found in DB!")

        # Try to find existing user by Zitadel ID
        employee = db.scalar(
            select(Employee).where(Employee.uuid_keycloak == zitadel_user_id)
        )

        if employee:
            # Update user info if changed
            if employee.email != email:
                employee.email = email
            if employee.first_name != given_name:
                employee.first_name = given_name
            if employee.last_name != family_name:
                employee.last_name = family_name
            # Update role from Zitadel
            if role and employee.role_id != role.id:
                logger.debug("[DEBUG get_or_create_user] Updating role from '{employee.role.name if employee.role else None}' to '{role.name}'")
                employee.role_id = role.id
            db.commit()
            return employee

        # Try to find by email (user might exist from password auth)
        employee = db.scalar(
            select(Employee).where(Employee.email == email)
        )

        if employee:
            # Link existing user to Zitadel
            employee.uuid_keycloak = zitadel_user_id
            # Update role from Zitadel
            if role and employee.role_id != role.id:
                logger.debug("[DEBUG get_or_create_user] Linking user and setting role to '{role.name}'")
                employee.role_id = role.id
            db.commit()
            return employee

        # Create new user (AUTO-PROVISIONING)
        # NOTE: Adjust this based on your user creation requirements
        from uuid import uuid4

        logger.debug("[DEBUG get_or_create_user] Creating new user with role: {mapped_role_name}")

        # Generate next sequential employee code
        employee_code = ZitadelAuth.get_next_employee_code(db, prefix="KIT")
        logger.debug("[DEBUG get_or_create_user] Generated employee code: {employee_code}")

        new_employee = Employee(
            id=str(uuid4()),
            employee_code=employee_code,
            email=email,
            first_name=given_name,
            last_name=family_name,
            uuid_keycloak=zitadel_user_id,
            role_id=role.id if role else None,  # Assign role from Zitadel
            status="active",
            # password_hash will be None (SSO users don't need password)
        )

        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

        logger.debug("[DEBUG get_or_create_user] Created new user: {new_employee.email} with role: {new_employee.role.name if new_employee.role else 'None'}")

        return new_employee
