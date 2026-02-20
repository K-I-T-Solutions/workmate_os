"""
Workmate OS - Keycloak OIDC Integration
Handles SSO authentication via Keycloak
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
from app.core.auth.role_mapping import extract_roles_from_token, map_keycloak_roles
import re

logger = logging.getLogger(__name__)


class KeycloakAuth:
    """Keycloak OIDC authentication handler"""

    @staticmethod
    async def get_user_info(access_token: str) -> Optional[Dict]:
        """
        Fetch user information from Keycloak UserInfo endpoint
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    settings.KEYCLOAK_USERINFO_URI,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.debug(f"Failed to fetch user info: {e}")
            return None

    @staticmethod
    async def get_jwks() -> dict:
        """
        Fetch JWKS (JSON Web Key Set) from Keycloak
        Used to verify JWT token signatures
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.KEYCLOAK_JWKS_URI, timeout=10.0)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def decode_access_token(token: str) -> Optional[Dict]:
        """
        Decode Keycloak access token to extract realm_access.roles.
        Access tokens contain role claims that ID tokens don't have.
        """
        try:
            jwks = await KeycloakAuth.get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            rsa_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = key
                    break

            if not rsa_key:
                return None

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                options={
                    "verify_aud": False,
                    "verify_at_hash": False,
                }
            )
            return payload

        except JWTError as e:
            logger.warning(f"Failed to decode access token: {e}")
            return None
        except Exception as e:
            logger.warning(f"Exception decoding access token: {e}")
            return None

    @staticmethod
    async def verify_token(token: str) -> Optional[Dict]:
        """
        Verify Keycloak JWT token
        Returns decoded payload if valid, None otherwise
        """
        try:
            # Get JWKS
            jwks = await KeycloakAuth.get_jwks()

            # Decode token header to get kid (key ID)
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            logger.debug(f"Token kid: {kid}")
            logger.debug(f"Available kids: {[k.get('kid') for k in jwks.get('keys', [])]}")

            # Find matching key in JWKS
            rsa_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = key
                    break

            if not rsa_key:
                logger.debug(f"RSA key not found for kid: {kid}")
                return None

            # Verify and decode token
            # Accept tokens issued for the frontend (workmate-ui) or backend client,
            # and also "account" which Keycloak sets by default
            issuer = settings.KEYCLOAK_ISSUER
            logger.info(f"Verifying token with issuer: {issuer}")
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                issuer=issuer,
                options={
                    "verify_at_hash": False,
                    "verify_aud": False,
                }
            )

            logger.info(f"Token verified successfully! Sub: {payload.get('sub')}")
            return payload

        except JWTError as e:
            logger.warning(f"JWTError: {e}")
            return None
        except Exception as e:
            logger.debug(f"Exception: {e}")
            return None

    @staticmethod
    def get_next_employee_code(db: Session, prefix: str = "KIT") -> str:
        """
        Generate next sequential employee code (e.g., KIT-0001, KIT-0002, ...)
        """
        pattern = f"{prefix}-%"
        employees = db.execute(
            select(Employee.employee_code).where(
                Employee.employee_code.like(pattern)
            )
        ).scalars().all()

        max_number = 0
        code_pattern = re.compile(rf"{prefix}-(\d+)")

        for code in employees:
            match = code_pattern.match(code)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

        next_number = max_number + 1
        return f"{prefix}-{next_number:04d}"

    @staticmethod
    def get_or_create_user(db: Session, keycloak_payload: Dict) -> Optional[Employee]:
        """
        Get existing user by Keycloak ID or create new one

        Args:
            db: Database session
            keycloak_payload: Decoded JWT payload from Keycloak

        Returns:
            Employee object or None
        """
        keycloak_user_id = keycloak_payload.get("sub")
        email = keycloak_payload.get("email")
        given_name = keycloak_payload.get("given_name", "")
        family_name = keycloak_payload.get("family_name", "")

        logger.debug(f"[get_or_create_user] keycloak_user_id: {keycloak_user_id}")
        logger.debug(f"[get_or_create_user] email: {email}")

        if not keycloak_user_id or not email:
            logger.debug(f"[get_or_create_user] Missing required fields! user_id={keycloak_user_id}, email={email}")
            return None

        # Extract and map roles from Keycloak token
        keycloak_roles = extract_roles_from_token(keycloak_payload)
        mapped_role_name, keycloak_role_id = map_keycloak_roles(keycloak_roles)

        logger.debug(f"[get_or_create_user] Extracted roles: {keycloak_roles}")
        logger.debug(f"[get_or_create_user] Mapped to Workmate role: {mapped_role_name}")

        # Find the role in the database
        role = None
        if mapped_role_name:
            role = db.scalar(
                select(Role).where(Role.name == mapped_role_name)
            )
            if role:
                logger.debug(f"[get_or_create_user] Found role in DB: {role.name} (ID: {role.id})")

                if keycloak_role_id and role.keycloak_id != keycloak_role_id:
                    role.keycloak_id = keycloak_role_id
                    db.commit()

        # Try to find existing user by Keycloak ID
        employee = db.scalar(
            select(Employee).where(Employee.uuid_keycloak == keycloak_user_id)
        )

        if employee:
            # Update user info if changed
            if employee.email != email:
                employee.email = email
            if employee.first_name != given_name:
                employee.first_name = given_name
            if employee.last_name != family_name:
                employee.last_name = family_name
            if role and employee.role_id != role.id:
                logger.debug(f"[get_or_create_user] Updating role to '{role.name}'")
                employee.role_id = role.id
            db.commit()
            return employee

        # Try to find by email (user might exist from password auth)
        employee = db.scalar(
            select(Employee).where(Employee.email == email)
        )

        if employee:
            employee.uuid_keycloak = keycloak_user_id
            if role and employee.role_id != role.id:
                employee.role_id = role.id
            db.commit()
            return employee

        # Create new user (AUTO-PROVISIONING)
        from uuid import uuid4

        employee_code = KeycloakAuth.get_next_employee_code(db, prefix="KIT")
        logger.debug(f"[get_or_create_user] Creating new user with code: {employee_code}")

        new_employee = Employee(
            id=str(uuid4()),
            employee_code=employee_code,
            email=email,
            first_name=given_name,
            last_name=family_name,
            uuid_keycloak=keycloak_user_id,
            role_id=role.id if role else None,
            status="active",
        )

        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

        return new_employee
