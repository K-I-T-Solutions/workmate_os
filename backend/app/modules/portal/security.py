# app/modules/portal/security.py
"""
Kundenportal – Session-Tokens und Auth-Dependency.

WICHTIG: Portal-Sessions werden mit einem EIGENEN, abgeleiteten Schlüssel signiert.
Der interne HS256-Pfad in app.core.auth.auth prüft kein `aud` – mit dem gleichen
JWT_SECRET_KEY wäre ein Portal-Token sonst als Mitarbeiter-Token gültig.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.settings.config import settings
from app.core.settings.database import get_db
from app.modules.backoffice.crm.models import Contact

PORTAL_AUDIENCE = "workmate-portal"
PORTAL_ALGORITHM = "HS256"

_bearer = HTTPBearer(auto_error=False)


def _signing_key() -> str:
    return hmac.new(
        settings.JWT_SECRET_KEY.encode(), b"workmate-portal-session-v1", hashlib.sha256
    ).hexdigest()


def generate_link_token() -> str:
    return secrets.token_urlsafe(32)


def hash_link_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session_token(contact: Contact) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.PORTAL_SESSION_HOURS)
    payload = {
        "sub": str(contact.id),
        "cid": str(contact.customer_id),
        "typ": "portal",
        "aud": PORTAL_AUDIENCE,
        "iat": datetime.now(timezone.utc),
        "exp": expires,
    }
    return pyjwt.encode(payload, _signing_key(), algorithm=PORTAL_ALGORITHM), expires


@dataclass
class PortalSession:
    contact: Contact
    customer_id: UUID

    @property
    def actor_id(self) -> str:
        return f"portal:{self.contact.id}"


def get_portal_session(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> PortalSession:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Portal-Sitzung ungültig oder abgelaufen",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if creds is None:
        raise unauthorized
    try:
        payload = pyjwt.decode(
            creds.credentials,
            _signing_key(),
            algorithms=[PORTAL_ALGORITHM],
            audience=PORTAL_AUDIENCE,
        )
    except pyjwt.InvalidTokenError:
        raise unauthorized
    if payload.get("typ") != "portal":
        raise unauthorized

    try:
        contact_id = UUID(payload["sub"])
        customer_id = UUID(payload["cid"])
    except (KeyError, ValueError):
        raise unauthorized

    # Zugang wird bei jedem Request geprüft → Entzug wirkt sofort
    contact = db.get(Contact, contact_id)
    if not contact or not contact.portal_enabled or contact.customer_id != customer_id:
        raise unauthorized
    return PortalSession(contact=contact, customer_id=customer_id)
