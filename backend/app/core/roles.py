# app/core/roles.py
from typing import Union, List, Callable
from fastapi import Depends, HTTPException, status, Request
from functools import wraps
import inspect, uuid
from datetime import datetime

from app.core.auth import get_current_user
from app.database import get_db, SessionLocal
from app.models import AuditLog

# 🔁 Rollen-Aliases
ROLE_ALIASES = {
    "backoffice": "hr",
    "hr": "hr",
    "management": "management",
    "admin": "management",
    "support": "admin",
}

def normalize_role(role: str) -> str:
    """Wandelt z.B. 'backoffice' → 'hr' um"""
    return ROLE_ALIASES.get(role.lower(), role.lower())


def require_roles(allowed_roles: Union[str, List[str]]):
    """
    Decorator zur Rollenprüfung mit integriertem Audit-Logging.
    Erwartet, dass der Route ein 'user' via Depends(get_current_user) übergeben wird.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    allowed_normalized = {normalize_role(r) for r in allowed_roles}

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            request: Request = kwargs.get("request")
            db = kwargs.get("db")

            if user is None:
                raise HTTPException(
                    status_code=500,
                    detail="Missing 'user' in route — please include user: dict = Depends(get_current_user)",
                )

            # Rolle aus Abteilung oder Keycloak-Rollen bestimmen
            if isinstance(user, dict):
                role = user.get("department") or user.get("role")
                keycloak_roles = set(user.get("roles", []))
                email = user.get("email", "unknown")
            else:
                role = getattr(user, "department", None)
                keycloak_roles = set(getattr(user, "roles", []))
                email = getattr(user, "email", "unknown")

            normalized_user_role = normalize_role(role) if role else None
            normalized_user_roles = {normalize_role(r) for r in keycloak_roles}

            allowed = (
                normalized_user_role in allowed_normalized
                or allowed_normalized.intersection(normalized_user_roles)
            )

            # 🚫 Zugriff verweigert → Audit-Eintrag + HTTP 403
            if not allowed:
                try:
                    if not db:
                        db = SessionLocal()
                    log = AuditLog(
                        id=uuid.uuid4(),
                        user_email=email,
                        role=",".join(normalized_user_roles) or (normalized_user_role or "none"),
                        action="ACCESS_DENIED",
                        resource=request.url.path if request else func.__name__,
                        details=f"Required: {allowed_normalized} | Actual: {normalized_user_roles or normalized_user_role}",
                        created_at=datetime.utcnow(),
                    )
                    db.add(log)
                    db.commit()
                except Exception as e:
                    print(f"[AUDIT] Fehler beim Loggen: {e}")
                finally:
                    if db:
                        db.close()

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Allowed: {allowed_normalized} | Your roles: {normalized_user_roles or normalized_user_role}",
                )

            # ✅ Zugriff erlaubt → weiter
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
