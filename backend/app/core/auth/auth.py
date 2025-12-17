# app/core/auth.py
from __future__ import annotations
import json
import requests
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from jwt.algorithms import RSAAlgorithm
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.settings.database import get_db
from app.modules import  Employee


# ============================================================
# ⚙️ Keycloak / OpenID Konfiguration
# ============================================================
KEYCLOAK_INTERNAL = "http://keycloak:8080"
OIDC_ISSUER = "https://login.workmate.test/realms/kit"
CLIENT_ID = "workmate-ui"
JWKS_URI = f"{KEYCLOAK_INTERNAL}/realms/kit/protocol/openid-connect/certs"

auth_scheme = HTTPBearer(auto_error=False)
_JWKS_CACHE = None


# ============================================================
# 🔑 JWKS Key Retrieval (cached)
# ============================================================
def get_jwks():
    """Lädt und cached die öffentlichen JWKS-Schlüssel vom Keycloak-Server."""
    global _JWKS_CACHE
    if _JWKS_CACHE:
        return _JWKS_CACHE
    try:
        res = requests.get(JWKS_URI, timeout=5)
        res.raise_for_status()
        jwks = res.json()
        _JWKS_CACHE = {key["kid"]: key for key in jwks["keys"]}
        return _JWKS_CACHE
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der JWKS: {e}")


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
        print("🧪 TestAuth aktiv:", request.state.test_user)
        return request.state.test_user

    # 🧪 Alternativ: Direkter Header (z. B. für pytest)
    test_user_header = request.headers.get("X-Test-User")
    if test_user_header:
        try:
            test_user = json.loads(test_user_header)
            print("🧪 TestAuth (Header):", test_user)
            return test_user
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Ungültiges X-Test-User Format")

    # 🧱 Kein Token vorhanden → nicht authentifiziert
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing credentials")

    token = creds.credentials
    try:
        header = jwt.get_unverified_header(token)
        keys = get_jwks()
        key_data = keys.get(header.get("kid"))
        if not key_data:
            raise HTTPException(status_code=401, detail="Unknown key ID in token header")

        public_key = RSAAlgorithm.from_jwk(key_data)
        decoded = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=OIDC_ISSUER,
        )

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")

    # ============================================================
    # 🧭 Benutzer in DB finden
    # ============================================================
    email = decoded.get("email")
    username = decoded.get("preferred_username")
    user = None

    if email:
        user = db.scalar(select(Employee.Employee).where(Employee.Employee.email == email))
    if not user and username:
        user = db.scalar(
            select(Employee.Employee).where(
                (Employee.Employee.name.ilike(username))
                | (Employee.Employee.employee_id.ilike(f"%{username}%"))
            )
        )

    if not user:
        raise HTTPException(status_code=404, detail="Kein Employee für aktuellen Benutzer gefunden")

    # ============================================================
    # 🧩 Rolle ableiten
    # ============================================================
    dept = (user.department or "").lower()
    if dept in ("backoffice", "hr"):
        role = "hr"
    elif dept == "management":
        role = "management"
    elif dept == "support":
        role = "support"
    elif dept in ("facility", "security"):
        role = "admin"
    else:
        role = "employee"

    result = {
        "preferred_username": user.name,
        "email": user.email,
        "employee_id": user.employee_id,
        "department": dept,
        "role": role,
    }

    print("✅ Authenticated as:", result)
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
