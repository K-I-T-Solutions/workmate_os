"""
Keycloak to Workmate OS Role Mapping
Maps Keycloak roles to Workmate OS internal roles
"""
from typing import Optional

# Mapping: Keycloak role name -> Workmate OS role name
KEYCLOAK_ROLE_MAPPING = {
    # Keycloak role (case-insensitive) -> Workmate role
    "workmate-admin": "Admin",
    "workmate-ceo": "CEO",
    "workmate-manager": "Manager",
    "workmate-employee": "Employee",

    # Direct role names (as configured in Keycloak)
    "admin": "Admin",
    "ceo": "CEO",
    "manager": "Manager",
    "employee": "Employee",
}

# Default role if no role is assigned in Keycloak
DEFAULT_ROLE = "Employee"

# Role priority (highest priority first)
# Used when a user has multiple roles in Keycloak
ROLE_PRIORITY = [
    "Admin",
    "CEO",
    "Manager",
    "Employee",
]


def map_keycloak_roles(keycloak_roles: dict[str, str | None]) -> tuple[Optional[str], Optional[str]]:
    """
    Map Keycloak roles to a single Workmate OS role

    Args:
        keycloak_roles: Dict of role names from Keycloak {role_name: None}

    Returns:
        Tuple of (Workmate OS role name, role key) or (None, None)
    """
    if not keycloak_roles:
        return (DEFAULT_ROLE, None)

    mapped_roles = []
    role_id_mapping = {}

    for role_name, role_id in keycloak_roles.items():
        role_lower = role_name.lower().strip()

        if role_lower in KEYCLOAK_ROLE_MAPPING:
            workmate_role = KEYCLOAK_ROLE_MAPPING[role_lower]
            mapped_roles.append(workmate_role)
            role_id_mapping[workmate_role] = role_id

    if not mapped_roles:
        return (DEFAULT_ROLE, None)

    # Return highest priority role
    for priority_role in ROLE_PRIORITY:
        if priority_role in mapped_roles:
            return (priority_role, role_id_mapping.get(priority_role))

    first_role = mapped_roles[0]
    return (first_role, role_id_mapping.get(first_role))


def extract_roles_from_token(token_payload: dict) -> dict[str, str | None]:
    """
    Extract roles from Keycloak token payload

    Keycloak sends roles in:
    - realm_access.roles (realm-level roles, list of strings)
    - resource_access.{client_id}.roles (client-level roles, list of strings)

    Args:
        token_payload: Decoded JWT token payload

    Returns:
        Dict mapping role_name -> None
    """
    roles = {}

    # 1. Extract realm roles: realm_access.roles
    realm_access = token_payload.get("realm_access", {})
    if isinstance(realm_access, dict):
        for role_name in realm_access.get("roles", []):
            roles[role_name] = None

    # 2. Extract client roles: resource_access.{client}.roles
    resource_access = token_payload.get("resource_access", {})
    if isinstance(resource_access, dict):
        for client_id, client_data in resource_access.items():
            if isinstance(client_data, dict):
                for role_name in client_data.get("roles", []):
                    roles[role_name] = None

    return roles
