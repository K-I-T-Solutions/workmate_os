"""
Zitadel to Workmate OS Role Mapping
Maps Zitadel roles/groups to Workmate OS internal roles
"""
from typing import Optional

# Mapping: Zitadel role name -> Workmate OS role name
ZITADEL_ROLE_MAPPING = {
    # Zitadel role (case-insensitive) -> Workmate role
    "workmate-admin": "Admin",
    "workmate-ceo": "CEO",
    "workmate-manager": "Manager",
    "workmate-employee": "Employee",

    # Alternative mappings (falls du andere Namen verwendest)
    "admin": "Admin",
    "ceo": "CEO",
    "manager": "Manager",
    "employee": "Employee",
}

# Default role if no role is assigned in Zitadel
DEFAULT_ROLE = "Employee"

# Role priority (highest priority first)
# Used when a user has multiple roles in Zitadel
ROLE_PRIORITY = [
    "Admin",
    "CEO",
    "Manager",
    "Employee",
]


def map_zitadel_roles(zitadel_roles: dict[str, str]) -> tuple[Optional[str], Optional[str]]:
    """
    Map Zitadel roles to a single Workmate OS role

    Args:
        zitadel_roles: Dict of role names from Zitadel {role_name: role_id}

    Returns:
        Tuple of (Workmate OS role name, Zitadel role ID) or (None, None)
    """
    if not zitadel_roles:
        return (DEFAULT_ROLE, None)

    # Normalize roles (lowercase) and map them
    mapped_roles = []
    role_id_mapping = {}  # Maps workmate_role -> zitadel_role_id

    for zitadel_role_name, zitadel_role_id in zitadel_roles.items():
        zitadel_role_lower = zitadel_role_name.lower().strip()

        # Check if role exists in mapping
        if zitadel_role_lower in ZITADEL_ROLE_MAPPING:
            workmate_role = ZITADEL_ROLE_MAPPING[zitadel_role_lower]
            mapped_roles.append(workmate_role)
            # Store the ID for this mapped role
            role_id_mapping[workmate_role] = zitadel_role_id

    if not mapped_roles:
        # No matching roles found, use default
        return (DEFAULT_ROLE, None)

    # Return highest priority role and its Zitadel ID
    for priority_role in ROLE_PRIORITY:
        if priority_role in mapped_roles:
            zitadel_id = role_id_mapping.get(priority_role)
            return (priority_role, zitadel_id)

    # Fallback: return first mapped role
    first_role = mapped_roles[0]
    return (first_role, role_id_mapping.get(first_role))


def extract_roles_from_token(token_payload: dict) -> dict[str, str]:
    """
    Extract roles from Zitadel token payload

    Zitadel can send roles in different claims:
    - urn:zitadel:iam:org:project:roles (project roles)
    - urn:zitadel:iam:org:project:{project_id}:roles
    - roles (generic)

    Zitadel role format can be:
    - Simple dict: {"role_name": "project_id"}
    - Nested dict: {"role_name": {"grant_id": "org_domain"}}

    Args:
        token_payload: Decoded JWT token payload

    Returns:
        Dict mapping role_name -> role_id (grant_id from nested structure)
    """
    roles = {}

    # Check common role claims
    possible_claims = [
        "roles",  # Generic
        "urn:zitadel:iam:org:project:roles",  # Project roles
    ]

    for claim in possible_claims:
        if claim in token_payload:
            claim_value = token_payload[claim]

            # Roles can be a dict {role_name: ...} or a list
            if isinstance(claim_value, dict):
                for role_name, role_data in claim_value.items():
                    # Check if role_data is nested dict or simple string
                    if isinstance(role_data, dict):
                        # Nested format: {"grant_id": "org_domain"}
                        # Extract the grant_id (first key)
                        grant_ids = list(role_data.keys())
                        role_id = grant_ids[0] if grant_ids else None
                        roles[role_name] = role_id
                    else:
                        # Simple format: just the ID as string
                        roles[role_name] = role_data
            elif isinstance(claim_value, list):
                # List format: just role names (no IDs)
                for role_name in claim_value:
                    roles[role_name] = None

    # Also check for custom claims with "roles" in the key
    for key, value in token_payload.items():
        if "role" in key.lower() and key not in possible_claims:
            if isinstance(value, dict):
                for role_name, role_data in value.items():
                    if isinstance(role_data, dict):
                        grant_ids = list(role_data.keys())
                        role_id = grant_ids[0] if grant_ids else None
                        roles[role_name] = role_id
                    else:
                        roles[role_name] = role_data
            elif isinstance(value, list):
                for role_name in value:
                    roles[role_name] = None

    return roles
