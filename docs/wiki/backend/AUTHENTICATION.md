---
layout: default
title: Authentication & RBAC
parent: Backend
grand_parent: Wiki
nav_order: 1
---

# 🔐 Authentication & RBAC — WorkmateOS

**Letzte Aktualisierung:** Juli 2026  
**Autor:** Joshua Kuhrau

---

## Übersicht

WorkmateOS nutzt **Keycloak** als Identity Provider mit OIDC/PKCE. Das System unterstützt:

- ✅ Single Sign-On (SSO) via Keycloak Realm `kit`
- ✅ PKCE-Flow (kein Client Secret im Browser)
- ✅ Automatisches Employee-Provisioning beim ersten Login
- ✅ Role-based Access Control (RBAC) mit Wildcard-Permissions
- ✅ RS256 JWT-Validierung via JWKS
- ✅ Automatische Employee-Code-Generierung (KIT-0001, KIT-0002, …)

---

## Auth-Flow

```
Browser                Keycloak               Backend (FastAPI)
  │                       │                          │
  │── Login-Redirect ────▶│                          │
  │◀─ Auth-Code ──────────│                          │
  │── Token-Request ─────▶│                          │
  │◀─ access_token (RS256)│                          │
  │                       │                          │
  │── GET /api/auth/me ───────────────────────────▶  │
  │   (Bearer: access_token)                         │
  │                   validate RS256 via JWKS        │
  │                   lookup Employee by uuid_keycloak│
  │◀─ { permissions: [...] } ─────────────────────── │
```

**Frontend:** PKCE implementiert in `ui-v3/lib/auth/pkce.ts`. Token wird in `localStorage` gespeichert. Beim App-Start ruft `auth-provider.tsx` `/api/auth/me` ab und lädt die Permissions.

---

## Backend-Komponenten

| Datei | Beschreibung |
|-------|--------------|
| `app/core/auth/auth.py` | `get_current_user()` Dependency, JWKS-Cache, RS256/HS256 Decoder |
| `app/core/auth/routes.py` | Endpoints: `/auth/me`, `/auth/login`, `/auth/callback`, `/auth/logout`; `get_employee_from_token` Dependency |
| `app/core/auth/keycloak.py` | Auto-Provisioning: `get_or_create_user()`, Employee-Code-Generator |
| `app/core/auth/role_mapping.py` | Keycloak Realm-Rollen → WorkmateOS Rollen-Namen |
| `app/core/auth/roles.py` | `require_permissions()` Decorator, Wildcard-Matching |
| `app/core/auth/service.py` | `AuthService`: HS256 Token-Erstellung (lokaler Fallback), Passwort-Hashing |

---

## Token-Validierung

Keycloak-Tokens sind **RS256** signiert. Der Backend-Decoder (`auth.py`) erkennt den Algorithmus am JWT-Header:

```python
header = pyjwt.get_unverified_header(token)
alg = header.get("alg")   # "RS256" oder "HS256"
```

- **RS256 (Keycloak):** Validierung via JWKS (`/realms/kit/protocol/openid-connect/certs`)
- **HS256 (lokal):** Validierung via `JWT_SECRET_KEY` (nur für Tests/lokale Tokens)

JWKS wird gecacht (`_JWKS_CACHE`). Bei unbekanntem `kid` wird der Cache automatisch erneuert.

---

## Keycloak Realm-Rollen → WorkmateOS

Das Mapping ist in `role_mapping.py` definiert:

| Keycloak Rolle | WorkmateOS Rolle |
|----------------|-----------------|
| `workmate-admin` | Admin |
| `workmate-geschaeftsfuehrung` | Geschäftsführung |
| `workmate-cto` | CTO |
| `workmate-cfo` | CFO |
| `workmate-head-of-events` | Head of Events |
| `workmate-mitarbeiter` | Mitarbeiter |
| `workmate-marketing` | Marketing |

Alte Rollen bleiben als Fallback gemappt (`workmate-ceo` → Geschäftsführung etc.).

Bei mehreren Rollen gewinnt die höchste Priorität (Admin > Geschäftsführung > … > Marketing).

---

## RBAC — Permission System

### Permission-Namensschema

```
modul.action          # Core-Module (employees, hr, documents, …)
backoffice.modul.action   # Backoffice-Module (crm, projects, invoices, …)
```

Beispiele: `hr.view`, `backoffice.crm.read`, `backoffice.invoices.write`

### Wildcard-Matching

```python
check_permission(user_perms, required):
    if "*" in user_perms → True          # Admin
    if required in user_perms → True     # Exakter Treffer
    if "backoffice.*" in user_perms
       and required.startswith("backoffice.") → True   # Wildcard-Präfix
```

### Route-Absicherung (Backend)

```python
@router.get("/customers")
@require_permissions(["backoffice.crm.read"])
async def list_customers(...):
    ...
```

### Frontend-Guards

```typescript
// Auth-Provider
const hasPermission = (required: string): boolean => {
  if (perms.includes("*")) return true
  if (perms.includes(required)) return true
  return perms.some(p => p.endsWith(".*") && required.startsWith(p.slice(0, -1)))
}

// Sidebar-Eintrag
{ label: "CRM", permission: "backoffice.crm.read" }

// Action-Button
{hasPermission("backoffice.crm.write") && <Button>Anlegen</Button>}
```

---

## Rollen & Permissions

| Rolle | Permissions |
|-------|-------------|
| **Admin** | `["*"]` |
| **Geschäftsführung** | `employees.*, hr.*, backoffice.*, documents.*, reminders.*, support.*, kb.*, dashboards.*, admin.read` |
| **CTO** | `employees.read, hr.view, backoffice.projects.*, backoffice.time_tracking.*, backoffice.crm.read, backoffice.products.read, backoffice.invoices.read, backoffice.finance.read, documents.*, support.*, kb.*, reminders.*, dashboards.read` |
| **CFO** | `employees.read, hr.view, backoffice.finance.*, backoffice.invoices.*, backoffice.crm.read, backoffice.projects.read, backoffice.time_tracking.view, backoffice.products.read, documents.read, reminders.*, dashboards.read` |
| **Head of Events** | `hr.view, backoffice.crm.*, backoffice.projects.*, backoffice.time_tracking.write, backoffice.invoices.read, backoffice.products.read, documents.read, reminders.*, support.view, dashboards.read` |
| **Mitarbeiter** | `hr.view, backoffice.time_tracking.write, documents.read, reminders.*, dashboards.read` |
| **Marketing** | `hr.view, backoffice.crm.read, documents.read, reminders.read, dashboards.read` |

---

## Auto-Provisioning

Wenn sich ein Nutzer zum ersten Mal via Keycloak anmeldet und noch kein Employee-Eintrag existiert, legt `keycloak.py`'s `get_or_create_user()` automatisch einen an:

- Employee-Code wird sequentiell generiert: `KIT-0001`, `KIT-0002`, …
- `uuid_keycloak` wird gesetzt (Keycloak `sub`)
- Rolle wird aus dem JWT-Token gemappt
- Fehlende Daten (Name, E-Mail) werden aus dem Token übernommen

---

## Konfiguration

```env
KEYCLOAK_URL=https://login.kit-it-koblenz.de         # Externer Issuer (muss mit JWT iss matchen)
KEYCLOAK_INTERNAL_URL=http://keycloak:8080            # Intern (Docker-Netz, für JWKS)
KEYCLOAK_REALM=kit
KEYCLOAK_CLIENT_ID=workmate-backend
KEYCLOAK_CLIENT_SECRET=...                            # Nur für Backend-zu-Keycloak Admin-API
JWT_SECRET_KEY=...                                    # Fallback für lokale HS256-Tokens
```

---

## Troubleshooting

| Problem | Ursache | Lösung |
|---------|---------|--------|
| `401` bei `/api/auth/me` | Token abgelaufen oder falscher Realm | Neu einloggen; KEYCLOAK_URL prüfen |
| Sidebar leer nach Login | Permissions kommen nicht aus `/api/auth/me` | Browser-Cache leeren, neu anmelden |
| `Unknown key ID` im Log | JWKS-Cache veraltet | Cache wird automatisch erneuert; ggf. Backend neu starten |
| Employee nicht gefunden | `uuid_keycloak` in DB falsch | DB prüfen: `SELECT uuid_keycloak FROM employees WHERE email = '...'` |
| Rolle wird nicht übernommen | Keycloak Realm-Rolle nicht in `role_mapping.py` | Mapping ergänzen und deployen |
