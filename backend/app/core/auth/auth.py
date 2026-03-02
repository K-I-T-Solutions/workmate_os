# app/core/auth.py
from __future__ import annotations
import json
import logging
import requests
import jwt as pyjwt
from jwt import ExpiredSignatureError, InvalidTokenError
from jwt.algorithms import RSAAlgorithm
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.settings.database import get_db
from app.core.errors import ErrorCode, get_error_detail

logger = logging.getLogger(__name__)


# ============================================================
# ⚙️ Keycloak / OpenID Konfiguration
# ============================================================
from app.core.settings.config import settings

OIDC_ISSUER = settings.KEYCLOAK_ISSUER
CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
JWKS_URI = settings.KEYCLOAK_JWKS_URI

auth_scheme = HTTPBearer(auto_error=False)
_JWKS_CACHE = None


# ============================================================
# 🔑 JWKS Key Retrieval (cached)
# ============================================================
def get_jwks(force_refresh=False):
    """Lädt und cached die öffentlichen JWKS-Schlüssel vom Keycloak-Server."""
    global _JWKS_CACHE
    if _JWKS_CACHE and not force_refresh:
        return _JWKS_CACHE
    try:
        res = requests.get(JWKS_URI, timeout=5)
        res.raise_for_status()
        jwks = res.json()
        _JWKS_CACHE = {key["kid"]: key for key in jwks["keys"]}
        return _JWKS_CACHE
    except Exception as e:
        logger.error("Fehler beim Laden der JWKS: %s", e)
        raise HTTPException(
            status_code=500,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR)
        )


# ============================================================
# 👤 Benutzer-Authentifizierung (Keycloak + Testmodus)
# ============================================================
async def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
):
    """
    Liefert den aktuellen Benutzer basierend auf:
    - JWT (Keycloak) im Produktivmodus
    - X-Test-User Header im Testmodus
    """

    # 🧪 Testmodus: Wenn Middleware einen Test-User gesetzt hat
    if hasattr(request.state, "test_user") and request.state.test_user:
        logger.debug("🧪 TestAuth aktiv: %s", request.state.test_user)
        return request.state.test_user

    # 🧪 Alternativ: Direkter Header (z. B. für pytest)
    test_user_header = request.headers.get("X-Test-User")
    if test_user_header:
        try:
            test_user = json.loads(test_user_header)
            logger.debug("🧪 TestAuth (Header): %s", test_user)
            return test_user
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail=get_error_detail(ErrorCode.SYSTEM_ERROR)
            )

    # 🧱 Kein Token vorhanden → nicht authentifiziert
    if creds is None:
        raise HTTPException(
            status_code=401,
            detail=get_error_detail(ErrorCode.AUTH_NOT_AUTHENTICATED)
        )

    token = creds.credentials
    decoded = None

    # Try to determine token type by header
    try:
        header = pyjwt.get_unverified_header(token)
        alg = header.get("alg")
        kid = header.get("kid")

        logger.debug("🔍 [Auth] Token algorithm: %s, Key ID: %s", alg, kid)

        # ============================================================
        # Option 1: HS256 Token (Local Auth Service)
        # ============================================================
        if alg == "HS256":
            logger.debug("🔑 [Auth] Validating HS256 token (Local Auth)")
            from app.core.auth.service import SECRET_KEY, ALGORITHM

            try:
                decoded = pyjwt.decode(
                    token,
                    key=SECRET_KEY,
                    algorithms=[ALGORITHM],
                    options={"verify_aud": False},
                )
                logger.debug("✅ [Auth] HS256 token validated successfully")
            except ExpiredSignatureError:
                raise HTTPException(
                    status_code=401,
                    detail=get_error_detail(ErrorCode.AUTH_EXPIRED_TOKEN)
                )
            except InvalidTokenError as e:
                logger.debug("Invalid HS256 token: %s", e)
                raise HTTPException(
                    status_code=401,
                    detail=get_error_detail(ErrorCode.AUTH_INVALID_TOKEN)
                )

        # ============================================================
        # Option 2: RS256 Token (Keycloak)
        # ============================================================
        elif alg == "RS256":
            logger.debug("🔑 [Auth] Validating RS256 token (Keycloak)")

            # Try to get key from cache
            keys = get_jwks()
            key_data = keys.get(kid)

            # If key not found, refresh JWKS cache and try again
            if not key_data:
                logger.warning("⚠️ Key ID %s not found in cache, refreshing JWKS...", kid)
                keys = get_jwks(force_refresh=True)
                key_data = keys.get(kid)

                # If still not found after refresh, fail
                if not key_data:
                    logger.error("Unknown key ID in token header: %s", kid)
                    raise HTTPException(
                        status_code=401,
                        detail=get_error_detail(ErrorCode.AUTH_INVALID_TOKEN)
                    )

            public_key = RSAAlgorithm.from_jwk(key_data)
            decoded = pyjwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                options={"verify_aud": False},
                issuer=OIDC_ISSUER,
            )
            logger.debug("✅ [Auth] RS256 token validated successfully")

        else:
            logger.error("Unsupported token algorithm: %s", alg)
            raise HTTPException(
                status_code=401,
                detail=get_error_detail(ErrorCode.AUTH_INVALID_TOKEN)
            )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail=get_error_detail(ErrorCode.AUTH_EXPIRED_TOKEN)
        )
    except InvalidTokenError as e:
        logger.debug("Invalid token: %s", e)
        raise HTTPException(
            status_code=401,
            detail=get_error_detail(ErrorCode.AUTH_INVALID_TOKEN)
        )
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        logger.error("Token verification failed: %s", e)
        raise HTTPException(
            status_code=401,
            detail=get_error_detail(ErrorCode.AUTH_INVALID_TOKEN)
        )

    if not decoded:
        raise HTTPException(
            status_code=401,
            detail=get_error_detail(ErrorCode.AUTH_INVALID_TOKEN)
        )

    # ============================================================
    # 🧭 Benutzer in DB finden (mit eager loading der Rolle)
    # ============================================================
    from sqlalchemy.orm import joinedload
    from app.modules.employees.models import Employee

    email = decoded.get("email")
    username = decoded.get("preferred_username")
    user = None

    if email:
        user = db.scalar(
            select(Employee)
            .options(joinedload(Employee.role), joinedload(Employee.department))
            .where(Employee.email == email)
        )
    if not user and username:
        user = db.scalar(
            select(Employee)
            .options(joinedload(Employee.role), joinedload(Employee.department))
            .where(
                (Employee.first_name.ilike(username))
                | (Employee.last_name.ilike(username))
                | (Employee.employee_code.ilike(f"%{username}%"))
            )
        )

    if not user:
        raise HTTPException(
            status_code=404,
            detail=get_error_detail(ErrorCode.EMPLOYEE_NOT_FOUND)
        )

    # ============================================================
    # 🧩 Rolle und Permissions aus Datenbank laden
    # ============================================================
    # Primär: Verwende die Rolle aus der Datenbank
    if user.role and hasattr(user.role, 'name'):
        db_role_name = user.role.name
        permissions = user.role.permissions_json if hasattr(user.role, 'permissions_json') else []
    else:
        # Fallback: Keine Rolle in DB → Employee mit Basis-Permissions
        db_role_name = "Employee"
        permissions = ["hr.view_own", "hr.request", "documents.view_own"]

    # Department name für Anzeige
    dept_name = ""
    if user.department:
        if hasattr(user.department, 'name'):
            dept_name = user.department.name or ""
        elif hasattr(user.department, 'code'):
            dept_name = user.department.code or ""
        elif isinstance(user.department, str):
            dept_name = user.department

    # Build full name
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not full_name:
        full_name = user.employee_code

    result = {
        "id": str(user.id),           # Employee UUID für approve/reject operations
        "preferred_username": full_name,
        "email": user.email,
        "employee_code": user.employee_code,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "department": dept_name,
        "role": db_role_name,         # Rollenname aus DB (z.B. "Manager", "Admin")
        "permissions": permissions,   # Permissions-Liste aus DB (z.B. ["hr.view", "hr.approve"])
    }

    logger.debug("✅ Authenticated as: %s (id: %s, role: %s, permissions: %s)",
                 result["email"], user.id, db_role_name, permissions)
    return result


# ============================================================
# 🧱 Rollen-Schutz für Endpoints
# ============================================================
def require_roles(allowed_roles: list[str]):
    """
    Decorator, der prüft, ob der aktuelle Benutzer zu den erlaubten Rollen gehört.
    Beispiel:
    @require_roles(["management", "hr"])
    """
    async def wrapper(user=Depends(get_current_user)):
        role = user.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Required roles {allowed_roles}, got '{role}'",
            )
        return user

    return wrapper
