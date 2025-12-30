---
layout: default
title: Zitadel Setup
parent: Setup
nav_order: 1
---

# Zitadel Rollen-Konfiguration für Workmate OS

## Übersicht

Workmate OS unterstützt automatisches Rollen-Mapping von Zitadel. Wenn ein User sich per SSO einloggt, wird seine Rolle automatisch aus Zitadel übernommen.

## Verfügbare Rollen in Workmate OS

| Workmate Rolle | Beschreibung | Priorität |
|----------------|--------------|-----------|
| Admin | Voller System-Zugriff | 1 (höchste) |
| CEO | Chief Executive Officer | 2 |
| Manager | Abteilungsleiter | 3 |
| Employee | Standard-Mitarbeiter | 4 (Standard) |

## Schritt 1: Project in Zitadel erstellen (falls noch nicht vorhanden)

1. Gehe zu **Zitadel Console** → **K.I.T. Organization**
2. Klicke auf **Projects** im Menü
3. Falls noch kein Project existiert:
   - Klicke auf **New Project**
   - Name: `Workmate OS`
   - Save

## Schritt 2: Rollen im Project definieren

1. Öffne dein **Workmate OS Project**
2. Gehe zu **Roles**
3. Füge folgende Rollen hinzu:

### Rollen erstellen:

Klicke auf **New Role** und erstelle:

| Role Key | Display Name | Description |
|----------|--------------|-------------|
| `workmate-admin` | Workmate Admin | Full system administrator |
| `workmate-ceo` | Workmate CEO | Chief Executive Officer |
| `workmate-manager` | Workmate Manager | Department Manager |
| `workmate-employee` | Workmate Employee | Standard Employee |

**Wichtig:** Die Role Keys müssen exakt so geschrieben werden (kleinbuchstaben mit Bindestrich).

## Schritt 3: Application mit Project verknüpfen

1. Gehe zu deiner Application (Client ID: `353229597984227349`)
2. Stelle sicher, dass sie mit dem **Workmate OS Project** verknüpft ist
3. Falls nicht:
   - Gehe zu **Applications** → Deine App
   - **Assign to Project**: Wähle "Workmate OS"

## Schritt 4: Rollen-Claims in Token aktivieren

1. Gehe zu deine Application → **Token Settings** (oder **OIDC Configuration**)
2. Aktiviere:
   - ✅ **Add project roles to access token**
   - ✅ **Add project roles to ID token**
3. Save

## Schritt 5: Rollen zu Usern zuweisen

### Einem User Rollen zuweisen:

1. Gehe zu **Users** in der K.I.T. Organization
2. Wähle den User aus (z.B. joshua@kit-it-koblenz.de)
3. Klicke auf **Authorizations** oder **Project Grants**
4. Klicke **New Authorization**
5. Wähle:
   - **Project**: Workmate OS
   - **Roles**: Wähle eine oder mehrere Rollen (z.B. `workmate-admin`)
6. Save

**Hinweis:** Wenn ein User mehrere Rollen hat, wird automatisch die höchste Priorität verwendet:
- Admin > CEO > Manager > Employee

## Schritt 6: Testen

1. Logge dich aus Workmate OS aus
2. Klicke auf **Mit SSO anmelden**
3. Logge dich mit deinem Zitadel-Account ein
4. Prüfe nach dem Login deine Rolle:
   - Gehe zu **Profil** oder
   - Prüfe in der Datenbank: `SELECT email, role_id FROM employees WHERE email = 'deine@email.de';`

## Rollen-Mapping anpassen

Falls du andere Rollennamen in Zitadel verwenden möchtest, kannst du das Mapping anpassen:

**Datei:** `/backend/app/core/auth/role_mapping.py`

```python
ZITADEL_ROLE_MAPPING = {
    # Deine eigenen Mapping-Regeln
    "my-custom-admin": "Admin",
    "my-custom-employee": "Employee",
    # ...
}
```

## Standard-Rolle

Wenn ein User **keine Rolle** in Zitadel hat, wird automatisch die Rolle **Employee** zugewiesen.

Du kannst die Standard-Rolle ändern in:

**Datei:** `/backend/app/core/auth/role_mapping.py`

```python
DEFAULT_ROLE = "Employee"  # Ändere zu "Manager" oder einer anderen Rolle
```

## Troubleshooting

### Rolle wird nicht übernommen

1. **Prüfe Backend-Logs:**
   ```bash
   docker logs workmate_backend --tail 50 | grep "Zitadel roles"
   ```

2. **Prüfe ob Rollen im Token sind:**
   - Die Logs zeigen: `[DEBUG get_or_create_user] Zitadel roles: [...]`
   - Falls leer: Rollen-Claims sind nicht im Token aktiviert

3. **Prüfe Rollen-Mapping:**
   - Logs zeigen: `[DEBUG get_or_create_user] Mapped to Workmate role: Admin`
   - Falls `None`: Rolle nicht im Mapping definiert

### User hat falsche Rolle

1. Logge dich aus und wieder ein (Rollen werden bei jedem Login aktualisiert)
2. Prüfe in Zitadel, welche Rollen dem User zugewiesen sind
3. Prüfe ob das Mapping korrekt ist

## Beispiel: Token mit Rollen

So sieht ein Zitadel Token mit Rollen aus:

```json
{
  "iss": "https://auth.intern.phudevelopement.xyz",
  "sub": "353230006945579029",
  "email": "joshua@kit-it-koblenz.de",
  "urn:zitadel:iam:org:project:roles": {
    "workmate-admin": "353229597984227349",
    "workmate-manager": "353229597984227349"
  }
}
```

In diesem Fall wird der User die Rolle **Admin** bekommen (höchste Priorität).
