"""
API-Key Authentifizierung für Email Intake Endpoints
-----------------------------------------------------
Separater Auth-Mechanismus für Service-Accounts (z. B. n8n).
Prüft `Authorization: Bearer <key>` gegen die api_keys-Tabelle.
"""
from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.settings.database import get_db
from app.modules.email_intake.models import ApiKey
from app.modules.email_intake.service import authenticate_api_key

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)

REQUIRED_SCOPE = "email:ingest"


def require_api_key(
    creds: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db=Depends(get_db),
) -> ApiKey:
    """
    FastAPI-Dependency: Prüft ob ein gültiger API-Key mit Scope 'email:ingest'
    im Authorization-Header übergeben wurde.

    Raises:
        401 wenn kein Token vorhanden
        401 wenn Token ungültig oder inaktiv
        403 wenn Scope fehlt
    """
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kein API-Key angegeben. Header: Authorization: Bearer <key>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = authenticate_api_key(db, creds.credentials, required_scope=REQUIRED_SCOPE)

    if api_key is None:
        logger.warning("Ungültiger oder inaktiver API-Key verwendet")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger oder inaktiver API-Key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("API-Key '%s' authentifiziert", api_key.name)
    return api_key
