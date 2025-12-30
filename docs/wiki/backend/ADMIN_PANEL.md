# 🛠️ Admin Panel Dokumentation

**System-Administration & Verwaltung**

**Status:** ✅ Phase 3 (80% Complete)
**Version:** 2.0
**Letzte Aktualisierung:** 30. Dezember 2025

---

## 📋 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Frontend-Komponenten](#frontend-komponenten)
   - [AdminApp Container](#adminapp-container)
   - [EmployeesPage](#employeespage)
   - [DepartmentsPage](#departmentspage)
   - [RolesPage](#rolespage)
   - [AuditLogPage](#auditlogpage)
   - [SystemSettingsPage](#systemsettingspage)
3. [Backend-APIs](#backend-apis)
   - [Employees API](#employees-api)
   - [Departments API](#departments-api)
   - [Roles API](#roles-api)
   - [Audit Log API](#audit-log-api-coming-soon)
   - [System Settings API](#system-settings-api-coming-soon)
4. [Berechtigungen](#berechtigungen)
5. [Features & Status](#features--status)

---

## Übersicht

Das **Admin Panel** ist das zentrale Verwaltungs-Interface für WorkmateOS. Es bietet System-Administratoren umfassende Kontrollmöglichkeiten über:

- **Mitarbeiter-Verwaltung** - CRUD-Operationen, Suche, Filterung
- **Abteilungs-Verwaltung** - Organisations-Struktur
- **Rollen & Berechtigungen** - Zugriffskontrolle, SSO-Mapping
- **Audit-Log** - System-Ereignisse & Änderungen (In Entwicklung)
- **System-Einstellungen** - Globale Konfiguration (In Entwicklung)

**Zugriff:** Nur für Benutzer mit Admin-Rolle (Permission: `admin.*` oder `*`)

---

## Frontend-Komponenten

### AdminApp Container

**Datei:** `ui/src/modules/admin/AdminApp.vue`

**Beschreibung:**
Container-Komponente mit Tab-Navigation für alle Admin-Funktionen.

**Struktur:**
```vue
<template>
  <div class="admin-app">
    <div class="admin-header">
      <h1>System Administration</h1>
    </div>

    <div class="admin-tabs">
      <!-- 5 Tabs für die verschiedenen Admin-Bereiche -->
    </div>

    <div class="admin-content">
      <!-- Dynamischer Content basierend auf aktivem Tab -->
    </div>
  </div>
</template>
```

**Tabs:**

| ID | Label | Icon | Komponente |
|----|-------|------|-----------|
| `employees` | Mitarbeiter | Users | EmployeesPage.vue |
| `departments` | Abteilungen | Building2 | DepartmentsPage.vue |
| `roles` | Rollen & Berechtigungen | Shield | RolesPage.vue |
| `settings` | System-Einstellungen | Settings | SystemSettingsPage.vue |
| `audit` | Audit-Log | FileText | AuditLogPage.vue |

**Features:**
- ✅ Tab-Navigation
- ✅ Responsive Design (Mobile: Nur Icons)
- ✅ Lazy-Loading der Tab-Komponenten

---

### EmployeesPage

**Datei:** `ui/src/modules/admin/pages/EmployeesPage.vue`

**Beschreibung:**
Tabellen-basierte Verwaltung aller Mitarbeiter mit Suche, Filterung und Pagination.

**Features:**

- ✅ **Suche** - In Name, Email, Employee Code
- ✅ **Pagination** - 20 Mitarbeiter pro Seite
- ✅ **Sortierung** - Nach allen Spalten
- ✅ **Status-Anzeige** - Active/Inactive Badge
- ✅ **CRUD-Operationen** - Erstellen, Bearbeiten, Löschen
- ✅ **Responsive** - Tabelle scrollt horizontal auf mobilen Geräten

**Tabellen-Spalten:**

| Spalte | Datentyp | Beschreibung |
|--------|----------|-------------|
| Code | String | Employee Code (z.B. `KIT-0001`) |
| Name | String | Vor- und Nachname |
| Email | String | E-Mail-Adresse |
| Abteilung | String | Department Name |
| Rolle | String | Role Name |
| Status | Badge | active, inactive, on_leave |
| Aktionen | Buttons | Bearbeiten, Löschen |

**API-Integration:**

```typescript
// Liste abrufen
GET /api/employees?skip=0&limit=20&search=Joshua

// Mitarbeiter löschen
DELETE /api/employees/{id}
```

**UI-States:**

- **Loading** - "Lade Mitarbeiter..."
- **Empty** - "Keine Mitarbeiter gefunden" + Icon
- **Data** - Tabelle mit Daten
- **Error** - Alert-Dialog bei Fehler

**Dialoge:**
- ⏳ **Create Dialog** - TODO: Formular noch nicht implementiert
- ⏳ **Edit Dialog** - TODO: Formular noch nicht implementiert

---

### DepartmentsPage

**Datei:** `ui/src/modules/admin/pages/DepartmentsPage.vue`

**Beschreibung:**
Card-basierte Darstellung aller Abteilungen mit Manager-Zuordnung.

**Features:**

- ✅ **Grid-Layout** - Responsive Cards (min 320px)
- ✅ **Manager-Anzeige** - Zugeordneter Abteilungsleiter
- ✅ **CRUD-Operationen** - Erstellen, Bearbeiten, Löschen
- ✅ **Hover-Effekt** - Highlight bei Mouse-Over

**Card-Struktur:**

```
┌─────────────────────────────┐
│ 🏢 IT-Abteilung             │
│ [Code: IT-001]              │
│                             │
│ Verwaltung der IT-Infrastr. │
│                             │
│ 👤 Leiter: Joshua Phu       │
│                             │
│          [✏️ Bearbeiten] [🗑️] │
└─────────────────────────────┘
```

**API-Integration:**

```typescript
// Liste abrufen
GET /api/departments

// Abteilung löschen
DELETE /api/departments/{id}
```

**Validierung:**
- Department Name ist erforderlich
- Department Code ist optional
- Manager ist optional (Employee FK)

---

### RolesPage

**Datei:** `ui/src/modules/admin/pages/RolesPage.vue`

**Beschreibung:**
Verwaltung von Rollen und deren Berechtigungen mit Zitadel-Integration.

**Features:**

- ✅ **Grid-Layout** - Responsive Cards (min 400px)
- ✅ **Permissions-Anzeige** - Liste aller zugewiesenen Berechtigungen
- ✅ **Zitadel-Integration** - Anzeige der Zitadel Role ID
- ✅ **Color-Coding** - Unterschiedliche Farben für System-Rollen
- ✅ **System-Rollen-Schutz** - Admin, CEO, Manager, Employee können nicht gelöscht werden

**Card-Struktur:**

```
┌─────────────────────────────────┐
│ 🛡️ Admin                    [✏️] │
│                                 │
│ 🔑 BERECHTIGUNGEN               │
│ ┌─┐ ┌─────────┐ ┌──────────┐  │
│ │*│ │employees│ │backoffice│  │
│ └─┘ └─────────┘ └──────────┘  │
│                                 │
│ Zitadel Role ID:                │
│ 273844991234567890              │
└─────────────────────────────────┘
```

**Rollen-Farben:**

| Rolle | Farbe | Hex |
|-------|-------|-----|
| Admin | Rot | `#dc3545` |
| CEO | Lila | `#6f42c1` |
| Manager | Blau | `#007bff` |
| Employee | Grün | `#28a745` |
| Custom | Primary | Variable |

**Permissions-System:**

```typescript
// Beispiel Permissions
permissions_json: [
  "*",                    // Wildcard: Voller Zugriff
  "employees.*",          // Alle Employee-Operationen
  "backoffice.crm.read",  // Nur CRM lesen
  "backoffice.*"          // Alle Backoffice-Operationen
]
```

**API-Integration:**

```typescript
// Liste abrufen
GET /api/roles

// Rolle löschen (nur Custom-Rollen)
DELETE /api/roles/{id}
```

**Siehe auch:**
→ [AUTHENTICATION.md](./AUTHENTICATION.md#role-mapping) für Details zum Role Mapping

---

### AuditLogPage

**Datei:** `ui/src/modules/admin/pages/AuditLogPage.vue`

**Status:** ⏳ **Frontend implementiert, Backend fehlt noch**

**Beschreibung:**
Tabellen-basierte Anzeige aller System-Ereignisse und Änderungen mit umfangreicher Filterung.

**Features:**

- ✅ **Umfangreiche Filter**
  - Benutzer-Filter (Dropdown)
  - Aktions-Filter (create, update, delete, login, logout)
  - Ressourcen-Filter (employee, department, role, customer, invoice, project)
  - Datum-Range (Von/Bis)
- ✅ **Pagination** - 50 Einträge pro Seite
- ✅ **Detail-Dialog** - Klick auf Zeile zeigt vollständige Details
- ✅ **Action-Badges** - Farbcodierte Aktionen
- ✅ **Mock-Daten** - Frontend funktioniert mit generierten Test-Daten

**Tabellen-Spalten:**

| Spalte | Datentyp | Beschreibung |
|--------|----------|-------------|
| Zeitstempel | DateTime | Format: "31.12.2025, 14:30:45" |
| Benutzer | String | Name des handelnden Users |
| Aktion | Badge | create, update, delete, login, logout |
| Ressource | Code + String | Typ und Name der Ressource |
| Details | String | Kurzbeschreibung der Änderung |
| IP-Adresse | String | IP des Clients |

**Action-Badges:**

| Aktion | Farbe | Icon | Beschreibung |
|--------|-------|------|--------------|
| create | Grün | Plus | Neuer Datensatz erstellt |
| update | Blau | Pencil | Datensatz geändert |
| delete | Rot | Trash2 | Datensatz gelöscht |
| login | Grau | LogIn | Benutzer-Login |
| logout | Grau | LogOut | Benutzer-Logout |

**Detail-Dialog:**

```
┌─────────────────────────────────────┐
│ Audit-Log Details              [✕]  │
├─────────────────────────────────────┤
│ Zeitstempel:   31.12.2025, 14:30:45 │
│ Benutzer:      Joshua Phu            │
│                (joshua@example.com)  │
│ Aktion:        Geändert              │
│ Ressource:     employee - Max Muster│
│ IP-Adresse:    192.168.1.100        │
│ Details:                             │
│ ┌─────────────────────────────────┐ │
│ │ {                               │ │
│ │   "field": "email",             │ │
│ │   "old": "old@example.com",     │ │
│ │   "new": "new@example.com"      │ │
│ │ }                               │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Backend-Anforderungen (TODO):**

```typescript
// Geplantes API-Endpoint
GET /api/audit-logs?skip=0&limit=50&user_id={uuid}&action=update&resource_type=employee&date_from=2025-01-01&date_to=2025-12-31

Response: {
  "total": 250,
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2025-12-30T14:30:45Z",
      "user_id": "uuid",
      "user_name": "Joshua Phu",
      "user_email": "joshua@example.com",
      "action": "update",
      "resource_type": "employee",
      "resource_id": "uuid",
      "resource_name": "Max Mustermann",
      "details": "Email geändert",
      "ip_address": "192.168.1.100",
      "changes": {
        "field": "email",
        "old": "old@example.com",
        "new": "new@example.com"
      }
    }
  ]
}
```

**Aktueller Workaround:**
Frontend generiert Mock-Daten mit `generateMockLogs()` Funktion.

---

### SystemSettingsPage

**Datei:** `ui/src/modules/admin/pages/SystemSettingsPage.vue`

**Status:** ⏳ **Frontend implementiert, Backend fehlt noch**

**Beschreibung:**
Formular-basierte Konfiguration globaler System-Einstellungen.

**Features:**

- ✅ **4 Kategorien** - Firmeninformationen, Lokalisierung, Arbeitszeiten, System
- ✅ **Speichern-Button** - Mit Loading-State
- ✅ **Success-Message** - Toast-Notification nach erfolgreichem Speichern
- ✅ **LocalStorage-Fallback** - Daten werden aktuell im Browser gespeichert

**Einstellungs-Kategorien:**

#### 1. Firmeninformationen

| Feld | Typ | Beispiel |
|------|-----|----------|
| Firmenname | Text | K.I.T IT-Solutions |
| Rechtsform | Text | GmbH |
| Steuernummer | Text | DE123456789 |
| Handelsregisternummer | Text | HRB 12345 |
| Straße & Hausnummer | Text | Musterstraße 123 |
| PLZ | Text | 56068 |
| Stadt | Text | Koblenz |
| Land | Text | Deutschland |
| E-Mail | Email | info@kit-it-koblenz.de |
| Telefon | Tel | +49 261 ... |
| Website | URL | https://kit-it-koblenz.de |

#### 2. Lokalisierung

| Feld | Typ | Optionen | Standard |
|------|-----|----------|----------|
| Standard-Zeitzone | Select | Europe/Berlin, Europe/London, ... | Europe/Berlin |
| Standard-Sprache | Select | de, en, fr | de |
| Währung | Select | EUR, USD, GBP | EUR |
| Datumsformat | Select | DD.MM.YYYY, MM/DD/YYYY, YYYY-MM-DD | DD.MM.YYYY |

#### 3. Arbeitszeiten

| Feld | Typ | Beschreibung | Standard |
|------|-----|--------------|----------|
| Arbeitsstunden pro Tag | Number | 1-24 Stunden | 8 |
| Arbeitstage pro Woche | Number | 1-7 Tage | 5 |
| Urlaubstage pro Jahr | Number | 0-365 Tage | 30 |
| Samstag ist Wochenende | Checkbox | Boolean | true |
| Sonntag ist Wochenende | Checkbox | Boolean | true |

#### 4. System

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| Wartungsmodus aktiv | Checkbox | System für normale User nicht verfügbar |
| Selbstregistrierung erlauben | Checkbox | User können sich selbst registrieren |
| E-Mail-Verifizierung erforderlich | Checkbox | User müssen E-Mail bestätigen |

**Backend-Anforderungen (TODO):**

```typescript
// Geplantes API-Endpoint
GET /api/settings
Response: {
  "company_name": "K.I.T IT-Solutions",
  "company_legal": "GmbH",
  ...
  "default_timezone": "Europe/Berlin",
  "default_language": "de",
  ...
}

PUT /api/settings
Body: {
  // Alle Settings-Felder
}
Response: {
  "message": "Settings updated successfully"
}
```

**Aktueller Workaround:**
Settings werden in `localStorage` unter dem Key `system_settings` gespeichert.

**Success-Message:**

```
┌──────────────────────────────────────┐
│ ✅ Einstellungen erfolgreich gespeichert! │
└──────────────────────────────────────┘
(Wird nach 3 Sekunden automatisch ausgeblendet)
```

---

## Backend-APIs

### Employees API

**Router:** `backend/app/modules/employees/routes.py`
**Prefix:** `/api/employees`
**Tags:** `Employees`

#### Endpoints:

##### GET `/api/employees`

**Beschreibung:** Liste aller Mitarbeiter mit Filterung und Pagination

**Query-Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `skip` | int | 0 | Anzahl zu überspringender Datensätze |
| `limit` | int | 100 | Max. Anzahl zurückzugebender Datensätze (max 500) |
| `search` | string | null | Suche in Name, Email, Employee Code |
| `department_id` | UUID | null | Filter nach Abteilung |
| `role_id` | UUID | null | Filter nach Rolle |
| `status` | string | null | Filter nach Status (active, inactive, on_leave) |

**Response:**

```json
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "employees": [
    {
      "id": "uuid",
      "employee_code": "KIT-0001",
      "first_name": "Joshua",
      "last_name": "Phu",
      "email": "joshua@example.com",
      "phone": "+49 261 ...",
      "status": "active",
      "department": {
        "id": "uuid",
        "name": "IT-Abteilung",
        "code": "IT-001"
      },
      "role": {
        "id": "uuid",
        "name": "Admin",
        "permissions_json": ["*"]
      },
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-12-30T14:30:00Z"
    }
  ]
}
```

---

##### GET `/api/employees/{employee_id}`

**Beschreibung:** Einzelnen Mitarbeiter abrufen

**Response:** Siehe `EmployeeResponse` Schema oben

---

##### GET `/api/employees/code/{employee_code}`

**Beschreibung:** Mitarbeiter anhand Employee Code abrufen

**Beispiel:** `GET /api/employees/code/KIT-0001`

**Response:** Siehe `EmployeeResponse` Schema

---

##### POST `/api/employees`

**Beschreibung:** Neuen Mitarbeiter anlegen

**Request Body:**

```json
{
  "employee_code": "KIT-0042",
  "first_name": "Max",
  "last_name": "Mustermann",
  "email": "max@example.com",
  "phone": "+49 123 456789",
  "department_id": "uuid",
  "role_id": "uuid",
  "status": "active"
}
```

**Validierung:**
- ✅ `employee_code` muss unique sein
- ✅ `email` muss unique sein
- ✅ `first_name`, `last_name`, `email` sind Pflichtfelder

**Status Code:** `201 Created`

**Response:** Erstellter Employee

**Errors:**

- `400 Bad Request` - Employee Code oder Email bereits vergeben
- `422 Unprocessable Entity` - Validierungsfehler

---

##### PUT `/api/employees/{employee_id}`

**Beschreibung:** Mitarbeiter aktualisieren

**Request Body:**

```json
{
  "first_name": "Max Updated",
  "email": "new@example.com",
  "status": "inactive"
}
```

**Hinweis:** Alle Felder sind optional. Nur angegebene Felder werden aktualisiert.

**Validierung:**
- ✅ Email muss unique sein (außer bei gleichem Mitarbeiter)

**Response:** Aktualisierter Employee

---

##### DELETE `/api/employees/{employee_id}`

**Beschreibung:** Mitarbeiter löschen (Soft Delete)

**Hinweis:** Setzt `status = 'inactive'` statt Datensatz zu löschen

**Status Code:** `204 No Content`

---

### Departments API

**Router:** `backend/app/modules/employees/routes.py`
**Prefix:** `/api/departments`
**Tags:** `Departments`

#### Endpoints:

##### GET `/api/departments`

**Beschreibung:** Liste aller Abteilungen

**Query-Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `skip` | int | 0 | Anzahl zu überspringender Datensätze |
| `limit` | int | 100 | Max. Anzahl zurückzugebender Datensätze |

**Response:**

```json
[
  {
    "id": "uuid",
    "name": "IT-Abteilung",
    "code": "IT-001",
    "description": "Verwaltung der IT-Infrastruktur",
    "manager_id": "uuid",
    "manager": {
      "id": "uuid",
      "first_name": "Joshua",
      "last_name": "Phu"
    },
    "created_at": "2025-01-10T09:00:00Z",
    "updated_at": "2025-12-20T12:00:00Z"
  }
]
```

---

##### GET `/api/departments/{department_id}`

**Beschreibung:** Einzelne Abteilung abrufen

**Response:** Siehe `DepartmentResponse` Schema oben

---

##### POST `/api/departments`

**Beschreibung:** Neue Abteilung anlegen

**Request Body:**

```json
{
  "name": "Marketing",
  "code": "MKT-001",
  "description": "Marketing & Communications",
  "manager_id": "uuid"
}
```

**Validierung:**
- ✅ `name` ist Pflichtfeld
- ✅ `code` ist optional aber sollte unique sein
- ✅ `manager_id` ist optional (FK zu Employee)

**Status Code:** `201 Created`

---

##### PUT `/api/departments/{department_id}`

**Beschreibung:** Abteilung aktualisieren

**Request Body:**

```json
{
  "name": "Marketing & Sales",
  "description": "Updated description"
}
```

**Hinweis:** Nur angegebene Felder werden aktualisiert

---

### Roles API

**Router:** `backend/app/modules/employees/routes.py`
**Prefix:** `/api/roles`
**Tags:** `Roles`

#### Endpoints:

##### GET `/api/roles`

**Beschreibung:** Liste aller Rollen

**Query-Parameter:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `skip` | int | 0 | Anzahl zu überspringender Datensätze |
| `limit` | int | 100 | Max. Anzahl zurückzugebender Datensätze |

**Response:**

```json
[
  {
    "id": "uuid",
    "name": "Admin",
    "description": "System Administrator mit vollem Zugriff",
    "permissions_json": ["*"],
    "keycloak_id": "273844991234567890",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-12-30T10:00:00Z"
  },
  {
    "id": "uuid",
    "name": "Manager",
    "description": "Manager mit Backoffice-Zugriff",
    "permissions_json": [
      "employees.read",
      "backoffice.*"
    ],
    "keycloak_id": "273844991234567891",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-12-15T14:00:00Z"
  }
]
```

---

##### GET `/api/roles/{role_id}`

**Beschreibung:** Einzelne Rolle abrufen

**Response:** Siehe `RoleResponse` Schema oben

---

##### POST `/api/roles`

**Beschreibung:** Neue Rolle anlegen

**Request Body:**

```json
{
  "name": "Projektleiter",
  "description": "Leitung von Projekten",
  "permissions_json": [
    "projects.*",
    "time_tracking.*",
    "invoices.read"
  ],
  "keycloak_id": "273844991234567892"
}
```

**Validierung:**
- ✅ `name` ist Pflichtfeld
- ✅ `permissions_json` ist Array von Permission-Strings
- ✅ `keycloak_id` ist optional (Zitadel Role ID)

**Permission-Syntax:**

```
*                     # Voller Zugriff
employees.*           # Alle Employee-Operationen
employees.read        # Nur lesen
backoffice.*          # Alle Backoffice-Module
backoffice.crm.*      # Nur CRM-Modul
```

**Siehe auch:** [AUTHENTICATION.md - Wildcard Permissions](./AUTHENTICATION.md#wildcard-permissions)

**Status Code:** `201 Created`

---

##### PUT `/api/roles/{role_id}`

**Beschreibung:** Rolle aktualisieren

**Request Body:**

```json
{
  "description": "Updated description",
  "permissions_json": [
    "projects.*",
    "time_tracking.*",
    "invoices.*"
  ]
}
```

**Hinweis:** Nur angegebene Felder werden aktualisiert

---

### Audit Log API (Coming Soon)

**Status:** ⏳ **Backend noch nicht implementiert**

**Geplanter Prefix:** `/api/audit-logs`
**Geplante Tags:** `Audit`

#### Geplante Endpoints:

##### GET `/api/audit-logs`

**Query-Parameter:**

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `skip` | int | Pagination offset |
| `limit` | int | Max. Anzahl (Standard: 50) |
| `user_id` | UUID | Filter nach User |
| `action` | string | Filter nach Aktion (create, update, delete, login, logout) |
| `resource_type` | string | Filter nach Ressourcen-Typ |
| `date_from` | date | Von Datum (ISO 8601) |
| `date_to` | date | Bis Datum (ISO 8601) |

**Geplante Response:**

```json
{
  "total": 250,
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2025-12-30T14:30:45Z",
      "user_id": "uuid",
      "user_name": "Joshua Phu",
      "user_email": "joshua@example.com",
      "action": "update",
      "resource_type": "employee",
      "resource_id": "uuid",
      "resource_name": "Max Mustermann",
      "details": "Email geändert",
      "ip_address": "192.168.1.100",
      "changes": {
        "field": "email",
        "old": "old@example.com",
        "new": "new@example.com"
      }
    }
  ]
}
```

**Implementierungs-Anforderungen:**

1. **Datenbank-Modell** erstellen (`audit_logs` Tabelle)
2. **Audit-Middleware** für automatisches Logging
3. **CRUD-Endpoints** implementieren
4. **Retention-Policy** (z.B. Logs älter als 1 Jahr löschen)

**Siehe auch:** Roadmap → [Phase 3: SSO & Admin](../../roadmap/README.md#phase-3-sso--admin-in-progress)

---

### System Settings API (Coming Soon)

**Status:** ⏳ **Backend noch nicht implementiert**

**Geplanter Prefix:** `/api/settings`
**Geplante Tags:** `Settings`

#### Geplante Endpoints:

##### GET `/api/settings`

**Beschreibung:** Alle System-Einstellungen abrufen

**Geplante Response:**

```json
{
  "company_name": "K.I.T IT-Solutions",
  "company_legal": "GmbH",
  "tax_number": "DE123456789",
  "registration_number": "HRB 12345",
  "address_street": "Musterstraße 123",
  "address_zip": "56068",
  "address_city": "Koblenz",
  "address_country": "Deutschland",
  "company_email": "info@kit-it-koblenz.de",
  "company_phone": "+49 261 ...",
  "company_website": "https://kit-it-koblenz.de",

  "default_timezone": "Europe/Berlin",
  "default_language": "de",
  "default_currency": "EUR",
  "date_format": "DD.MM.YYYY",

  "working_hours_per_day": 8,
  "working_days_per_week": 5,
  "vacation_days_per_year": 30,
  "weekend_saturday": true,
  "weekend_sunday": true,

  "maintenance_mode": false,
  "allow_registration": false,
  "require_email_verification": true
}
```

---

##### PUT `/api/settings`

**Beschreibung:** System-Einstellungen aktualisieren

**Request Body:** Alle oder einzelne Settings-Felder

**Validierung:**
- Email-Format validieren
- URL-Format validieren
- Numerische Felder in gültigem Bereich

**Response:**

```json
{
  "message": "Settings updated successfully"
}
```

**Implementierungs-Anforderungen:**

1. **Datenbank-Modell** erstellen (`system_settings` Tabelle)
2. **CRUD-Endpoints** implementieren
3. **Validierung** für alle Felder
4. **Caching** für bessere Performance

---

## Berechtigungen

**Admin-Zugriff erforderlich:**

Der Zugriff auf das Admin Panel ist nur für Benutzer mit folgenden Permissions möglich:

```typescript
// Voller Admin-Zugriff
permissions: ["*"]

// Oder spezifische Admin-Permission
permissions: ["admin.*"]

// Oder spezifische Unterbereiche
permissions: [
  "admin.employees.*",
  "admin.departments.*",
  "admin.roles.*",
  "admin.audit.*",
  "admin.settings.*"
]
```

**Permission-Prüfung im Frontend:**

```typescript
import { useAuth } from '@/composables/useAuth';

const { hasPermission } = useAuth();

// Prüfen ob User Admin ist
if (!hasPermission('admin.*') && !hasPermission('*')) {
  // Kein Zugriff
}
```

**Permission-Prüfung im Backend:**

```python
from app.core.auth.permissions import require_permissions

@router.get("/employees")
@require_permissions("admin.employees.read", "admin.*", "*")
def list_employees(...):
    ...
```

**Siehe auch:** [AUTHENTICATION.md - Wildcard Permissions](./AUTHENTICATION.md#wildcard-permissions)

---

## Features & Status

### ✅ Implementiert (Phase 3)

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| AdminApp Container | ✅ | - | 100% |
| Mitarbeiter-Verwaltung | ✅ | ✅ | 100% |
| Abteilungs-Verwaltung | ✅ | ✅ | 100% |
| Rollen-Verwaltung | ✅ | ✅ | 100% |
| Zitadel Role Mapping | ✅ | ✅ | 100% |
| Wildcard Permissions | ✅ | ✅ | 100% |
| Responsive Design | ✅ | - | 100% |

### ⏳ In Entwicklung

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Audit-Log UI | ✅ | ❌ | 50% (Mock-Daten) |
| System-Settings UI | ✅ | ❌ | 50% (localStorage) |
| Employee Create/Edit Dialog | ❌ | ✅ | 50% |
| Department Create/Edit Dialog | ❌ | ✅ | 50% |
| Role Create/Edit Dialog | ❌ | ✅ | 50% |

### 📅 Geplant (Phase 4)

| Feature | Beschreibung | Priorität |
|---------|--------------|-----------|
| Audit-Log Backend | Datenbank-Modell + APIs | Hoch |
| System-Settings Backend | Datenbank-Modell + APIs | Hoch |
| Formular-Dialoge | Create/Edit-Formulare für alle Entitäten | Mittel |
| Bulk-Operationen | Mehrere Employees gleichzeitig bearbeiten | Niedrig |
| CSV-Import/Export | Daten im-/exportieren | Niedrig |
| Advanced Filters | Mehr Filteroptionen für alle Tabellen | Niedrig |

---

## Technische Details

### Frontend-Technologien

- **Framework:** Vue 3 (Composition API)
- **TypeScript:** Vollständige Type-Safety
- **Icons:** Lucide Vue Next
- **HTTP-Client:** Axios (via `apiClient`)
- **Styling:** Scoped CSS mit CSS Variables

### Backend-Technologien

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic v2
- **Database:** PostgreSQL 16

### API-Patterns

Alle APIs folgen REST-Prinzipien:

- `GET` - Liste / Einzelobjekt abrufen
- `POST` - Neues Objekt erstellen (201 Created)
- `PUT` - Objekt aktualisieren
- `DELETE` - Objekt löschen (204 No Content)

**Pagination:**

```
GET /api/employees?skip=20&limit=20
```

**Filtering:**

```
GET /api/employees?department_id={uuid}&status=active
```

**Searching:**

```
GET /api/employees?search=Joshua
```

---

## Code-Beispiele

### Frontend: Employee löschen

```typescript
async function deleteEmployee(emp: any) {
  if (!confirm(`Mitarbeiter ${emp.first_name} ${emp.last_name} wirklich löschen?`)) {
    return;
  }

  try {
    await apiClient.delete(`/api/employees/${emp.id}`);
    await fetchEmployees(); // Liste neu laden
  } catch (error) {
    console.error('Failed to delete employee:', error);
    alert('Fehler beim Löschen');
  }
}
```

### Frontend: Rollen laden

```typescript
async function fetchRoles() {
  loading.value = true;
  try {
    const response = await apiClient.get('/api/roles');
    roles.value = response.data;
  } catch (error) {
    console.error('Failed to fetch roles:', error);
  } finally {
    loading.value = false;
  }
}
```

### Backend: Employee mit Filtern

```python
@employee_router.get("", response_model=schemas.EmployeeListResponse)
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    department_id: Optional[UUID] = Query(None),
    role_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    employees, total = crud.get_employees(
        db,
        skip=skip,
        limit=limit,
        search=search,
        department_id=department_id,
        role_id=role_id,
        status=status
    )

    return {
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "employees": employees
    }
```

---

## Siehe auch

- [AUTHENTICATION.md](./AUTHENTICATION.md) - SSO, OAuth2, Role Mapping
- [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md) - Alle Backend-Module
- [Roadmap Phase 3](../../roadmap/README.md#phase-3-sso--admin-in-progress)
- [System-Übersicht](../../architecture/system_overview.md)

---

**Letzte Aktualisierung:** 30. Dezember 2025
**Dokumentations-Status:** ✅ Vollständig (90%)
**Nächste Schritte:** Audit Log Backend, System Settings Backend, Formular-Dialoge
