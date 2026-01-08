"""
HR Module Permissions
RBAC-Berechtigungen für das HR-Modul.
"""
from enum import Enum


class HRPermission(str, Enum):
    """
    HR-Berechtigungen für Role-Based Access Control.

    Hierarchie:
    - hr_admin: Voller Zugriff auf alle HR-Module
    - hr_manager: Manager mit Genehmigungsrechten
    - hr_recruiter: Nur Recruiting
    - employee: Self-Service nur
    """

    # ============================================================================
    # RECRUITING
    # ============================================================================
    RECRUITING_VIEW = "hr.recruiting.view"
    RECRUITING_MANAGE = "hr.recruiting.manage"
    APPLICATIONS_VIEW = "hr.applications.view"
    APPLICATIONS_MANAGE = "hr.applications.manage"

    # ============================================================================
    # ONBOARDING
    # ============================================================================
    ONBOARDING_VIEW = "hr.onboarding.view"
    ONBOARDING_MANAGE = "hr.onboarding.manage"

    # ============================================================================
    # LEAVE MANAGEMENT
    # ============================================================================
    LEAVE_VIEW_ALL = "hr.leave.view_all"
    LEAVE_APPROVE = "hr.leave.approve"
    LEAVE_MANAGE = "hr.leave.manage"

    # ============================================================================
    # TRAINING
    # ============================================================================
    TRAINING_VIEW = "hr.training.view"
    TRAINING_MANAGE = "hr.training.manage"

    # ============================================================================
    # COMPENSATION (hochsensibel)
    # ============================================================================
    COMPENSATION_VIEW_ALL = "hr.compensation.view_all"
    COMPENSATION_MANAGE = "hr.compensation.manage"

    # ============================================================================
    # DOCUMENTS
    # ============================================================================
    DOCUMENTS_VIEW_ALL = "hr.documents.view_all"
    DOCUMENTS_MANAGE = "hr.documents.manage"

    # ============================================================================
    # ANALYTICS
    # ============================================================================
    ANALYTICS_VIEW = "hr.analytics.view"
    ANALYTICS_EXPORT = "hr.analytics.export"

    # ============================================================================
    # SELF-SERVICE (alle Mitarbeiter)
    # ============================================================================
    SELF_VIEW = "hr.self.view"
    SELF_UPDATE = "hr.self.update"


# ============================================================================
# ROLLE-BERECHTIGUNG MAPPING
# ============================================================================

ROLE_PERMISSIONS = {
    "hr_admin": [
        # Vollzugriff auf alle HR-Module
        HRPermission.RECRUITING_VIEW,
        HRPermission.RECRUITING_MANAGE,
        HRPermission.APPLICATIONS_VIEW,
        HRPermission.APPLICATIONS_MANAGE,
        HRPermission.ONBOARDING_VIEW,
        HRPermission.ONBOARDING_MANAGE,
        HRPermission.LEAVE_VIEW_ALL,
        HRPermission.LEAVE_APPROVE,
        HRPermission.LEAVE_MANAGE,
        HRPermission.TRAINING_VIEW,
        HRPermission.TRAINING_MANAGE,
        HRPermission.COMPENSATION_VIEW_ALL,
        HRPermission.COMPENSATION_MANAGE,
        HRPermission.DOCUMENTS_VIEW_ALL,
        HRPermission.DOCUMENTS_MANAGE,
        HRPermission.ANALYTICS_VIEW,
        HRPermission.ANALYTICS_EXPORT,
        HRPermission.SELF_VIEW,
        HRPermission.SELF_UPDATE,
    ],

    "hr_manager": [
        # Team-HR-Operationen verwalten
        HRPermission.RECRUITING_VIEW,
        HRPermission.APPLICATIONS_VIEW,
        HRPermission.APPLICATIONS_MANAGE,
        HRPermission.ONBOARDING_VIEW,
        HRPermission.LEAVE_VIEW_ALL,
        HRPermission.LEAVE_APPROVE,
        HRPermission.TRAINING_VIEW,
        HRPermission.TRAINING_MANAGE,
        HRPermission.DOCUMENTS_VIEW_ALL,
        HRPermission.ANALYTICS_VIEW,
        HRPermission.SELF_VIEW,
        HRPermission.SELF_UPDATE,
    ],

    "hr_recruiter": [
        # Recruiting-fokussierte Berechtigungen
        HRPermission.RECRUITING_VIEW,
        HRPermission.RECRUITING_MANAGE,
        HRPermission.APPLICATIONS_VIEW,
        HRPermission.APPLICATIONS_MANAGE,
        HRPermission.SELF_VIEW,
        HRPermission.SELF_UPDATE,
    ],

    "employee": [
        # Nur Self-Service
        HRPermission.SELF_VIEW,
        HRPermission.SELF_UPDATE,
    ]
}


def get_role_permissions(role: str) -> list[HRPermission]:
    """
    Gibt die Berechtigungen für eine Rolle zurück.

    Args:
        role: Rollenname (z.B. "hr_admin", "hr_manager")

    Returns:
        Liste der Berechtigungen für diese Rolle
    """
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user_role: str, required_permission: HRPermission) -> bool:
    """
    Prüft, ob eine Rolle eine bestimmte Berechtigung hat.

    Args:
        user_role: Rolle des Benutzers
        required_permission: Erforderliche Berechtigung

    Returns:
        True wenn Berechtigung vorhanden, sonst False
    """
    role_perms = get_role_permissions(user_role)
    return required_permission in role_perms
