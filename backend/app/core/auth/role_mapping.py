"""
Keycloak to WorkmateOS Role Mapping
Mappt Keycloak Realm-Rollen auf interne WorkmateOS-Rollen.

Keycloak-Rollen (Realm Level) die angelegt sein müssen:
  workmate-admin
  workmate-geschaeftsfuehrung
  workmate-cto
  workmate-cfo
  workmate-head-of-events
  workmate-mitarbeiter
  workmate-marketing
"""
from typing import Optional

KEYCLOAK_ROLE_MAPPING: dict[str, str] = {
    # Bevorzugte Keycloak-Rollennamen (workmate-Präfix)
    "workmate-admin":               "Admin",
    "workmate-geschaeftsfuehrung":  "Geschäftsführung",
    "workmate-cto":                 "CTO",
    "workmate-cfo":                 "CFO",
    "workmate-head-of-events":      "Head of Events",
    "workmate-mitarbeiter":         "Mitarbeiter",
    "workmate-marketing":           "Marketing",

    # Direktnamen (lowercase) als Fallback
    "admin":                "Admin",
    "geschaeftsfuehrung":   "Geschäftsführung",
    "cto":                  "CTO",
    "cfo":                  "CFO",
    "head-of-events":       "Head of Events",
    "mitarbeiter":          "Mitarbeiter",
    "marketing":            "Marketing",

    # Rückwärtskompatibilität – alte Keycloak-Rollen vor Umstrukturierung
    "workmate-ceo":         "Geschäftsführung",
    "workmate-manager":     "Mitarbeiter",
    "workmate-employee":    "Mitarbeiter",
    "ceo":                  "Geschäftsführung",
    "manager":              "Mitarbeiter",
    "employee":             "Mitarbeiter",
}

# Fallback wenn kein Keycloak-Rolle gemappt werden kann
DEFAULT_ROLE = "Mitarbeiter"

# Priorität bei mehreren Rollen (höchste zuerst)
ROLE_PRIORITY = [
    "Admin",
    "Geschäftsführung",
    "CTO",
    "CFO",
    "Head of Events",
    "Mitarbeiter",
    "Marketing",
]


def map_keycloak_roles(keycloak_roles: dict[str, str | None]) -> tuple[Optional[str], Optional[str]]:
    """
    Mappt Keycloak-Rollen auf eine einzelne WorkmateOS-Rolle.
    Bei mehreren Rollen gewinnt die höchste Priorität.
    """
    if not keycloak_roles:
        return (DEFAULT_ROLE, None)

    mapped_roles: list[str] = []
    role_id_mapping: dict[str, str | None] = {}

    for role_name, role_id in keycloak_roles.items():
        role_key = role_name.lower().strip()
        if role_key in KEYCLOAK_ROLE_MAPPING:
            workmate_role = KEYCLOAK_ROLE_MAPPING[role_key]
            mapped_roles.append(workmate_role)
            role_id_mapping[workmate_role] = role_id

    if not mapped_roles:
        return (DEFAULT_ROLE, None)

    for priority_role in ROLE_PRIORITY:
        if priority_role in mapped_roles:
            return (priority_role, role_id_mapping.get(priority_role))

    first_role = mapped_roles[0]
    return (first_role, role_id_mapping.get(first_role))


def extract_roles_from_token(token_payload: dict) -> dict[str, str | None]:
    """
    Extrahiert Rollen aus dem Keycloak JWT-Payload.

    Keycloak sendet Rollen in:
    - realm_access.roles  (Realm-Level, Liste von Strings)
    - resource_access.{client_id}.roles  (Client-Level, Liste von Strings)
    """
    roles: dict[str, str | None] = {}

    realm_access = token_payload.get("realm_access", {})
    if isinstance(realm_access, dict):
        for role_name in realm_access.get("roles", []):
            roles[role_name] = None

    resource_access = token_payload.get("resource_access", {})
    if isinstance(resource_access, dict):
        for client_data in resource_access.values():
            if isinstance(client_data, dict):
                for role_name in client_data.get("roles", []):
                    roles[role_name] = None

    return roles
