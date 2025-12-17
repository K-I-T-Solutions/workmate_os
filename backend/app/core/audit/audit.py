# app/core/audit.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app import models
import json
import logging

logger = logging.getLogger(__name__)

# Optional: actions/ressourcen whitelisten (hilft gegen Tippfehler im Code)
ALLOWED_ACTIONS = {
    "create", "update", "delete", "approve", "reject",
    "upload", "download", "complete", "snooze",
    "hr_export", "hr_update", "hr_review", "hr_sync",
}
# Prefix-Konventionen helfen später beim Filtern
ALLOWED_RESOURCE_PREFIXES = ("document:", "employee:", "reminder:", "vacation:", "sick_leave:", "hr_")

Jsonable = Union[str, Dict[str, Any]]

def _safe_json(details: Jsonable) -> str:
    """Konvertiert dict → JSON (verlustfrei), string bleibt string."""
    if isinstance(details, str):
        return details
    try:
        # default=str verhindert Crashes bei nicht-serialisierbaren Objekten (z. B. datetimes)
        return json.dumps(details, ensure_ascii=False, default=str)
    except Exception as e:
        # Fallback: best-effort string
        logger.warning("audit details could not be JSON-serialized: %s", e)
        return str(details)

def _normalize_resource(resource: str) -> str:
    return resource.strip()

def _normalize_action(action: str) -> str:
    return action.strip().lower()

def log_action(
    db: Session,
    user: Optional[dict],
    action: str,
    resource: str,
    details: Jsonable = "",
    *,
    strict: bool = False,          # wenn True → bei Fehler raise statt nur loggen
    max_details_len: int = 4000,   # Sicherheitsgrenze für sehr große Payloads
) -> None:
    """
    Fügt einen Audit-Log-Eintrag hinzu (ohne eigenen Commit).
    - bleibt in der laufenden Transaktion (db.flush())
    - fällt nie leise aus (loggt Fehler), optional strict
    - normalisiert action/resource, serialisiert details robust

    Args:
        db: aktive SQLAlchemy Session
        user: dict mit mind. {"email", "role"} (kann None sein → wird zu 'system')
        action: z.B. 'upload', 'update', 'hr_export'
        resource: z.B. 'document:<uuid>' oder 'hr_reports'
        details: Kontextinfos (str oder dict)
        strict: bei True Exceptions nicht schlucken
        max_details_len: Details werden auf diese Länge gekürzt (DB-Constraints/GDPR)
    """
    try:
        norm_action = _normalize_action(action)
        norm_resource = _normalize_resource(resource)

        # Optionale Leitplanke gegen Zahlendreher/Tippfehler
        if ALLOWED_ACTIONS and norm_action not in ALLOWED_ACTIONS:
            logger.warning("audit action '%s' not in ALLOWED_ACTIONS (continuing)", norm_action)

        if ALLOWED_RESOURCE_PREFIXES and not norm_resource.startswith(ALLOWED_RESOURCE_PREFIXES):
            logger.warning("audit resource '%s' does not match expected prefixes %s (continuing)",
                           norm_resource, ALLOWED_RESOURCE_PREFIXES)

        # User-Fallbacks (z. B. Systemjobs)
        user_email = (user or {}).get("email") or "system@workmate"
        user_role  = (user or {}).get("role")  or "system"

        # Details sicher serialisieren + sanft begrenzen
        serialized = _safe_json(details)
        if serialized and len(serialized) > max_details_len:
            serialized = serialized[:max_details_len - 3] + "..."

        log = models.AuditLog(
            user_email=user_email,
            role=user_role,
            action=norm_action,
            resource=norm_resource,
            details=serialized,
            created_at=datetime.now(timezone.utc),  # tz-aware
        )

        db.add(log)
        db.flush()  # keine eigene Transaktion eröffnen
        logger.info("📝 audit: %s → %s", norm_action, norm_resource)

    except Exception as e:
        logger.error("⚠️ audit log failed (%s → %s): %s", action, resource, e, exc_info=True)
        if strict:
            raise
        # bewusst kein rollback hier – das gehört dem Call-Scope
