# 📦 Backend Module Übersicht - WorkmateOS

**Vollständige Dokumentation aller Backend-Module**

**Status:** ✅ Vollständig
**Letzte Aktualisierung:** 30. Dezember 2025
**Autor:** K.I.T Solutions Team

---

## 📋 Inhaltsverzeichnis

### Core Module
1. [Employees Module](#employees-module) - Mitarbeiter, Abteilungen, Rollen
2. [Documents Module](#documents-module) - Dokumenten-Management
3. [Reminders Module](#reminders-module) - Erinnerungen & Benachrichtigungen
4. [Dashboards Module](#dashboards-module) - Dashboard-Verwaltung
5. [System Module](#system-module) - Infrastruktur-Services

### Backoffice Module
6. [CRM Module](#crm-module) - Customer Relationship Management
7. [Projects Module](#projects-module) - Projekt-Management
8. [Invoices Module](#invoices-module) - Rechnungswesen
9. [Finance Module](#finance-module) - Ausgaben-Verwaltung
10. [Time Tracking Module](#time-tracking-module) - Zeiterfassung
11. [Chat Module](#chat-module) - Messaging-System

---

## Modul-Übersicht

| Modul | Typ | Models | API Prefix | Status |
|-------|-----|--------|------------|--------|
| Employees | Core | Department, Role, Employee | `/api/employees`, `/api/departments`, `/api/roles` | ✅ Produktiv |
| Documents | Core | Document | `/api/documents` | ✅ Produktiv |
| Reminders | Core | Reminder | `/api/reminders` | ✅ Produktiv |
| Dashboards | Core | Dashboard, OSPreferences, UserSettings | `/api/dashboards` | ✅ Produktiv |
| System | Core | InfraService | - | ✅ Produktiv |
| CRM | Backoffice | Customer, Contact, Activity | `/api/customers`, `/api/contacts` | ✅ Produktiv |
| Projects | Backoffice | Project | `/api/projects` | ✅ Produktiv |
| Invoices | Backoffice | Invoice, InvoiceLineItem, Payment | `/api/invoices` | ✅ Produktiv |
| Finance | Backoffice | Expense | `/api/expenses` | ✅ Produktiv |
| Time Tracking | Backoffice | TimeEntry | `/api/time-entries` | ✅ Produktiv |
| Chat | Backoffice | ChatMessage | `/api/messages` | ✅ Produktiv |

---

# Core Module

---

## Employees Module

**Pfad:** `app/modules/employees/`
**Zweck:** Verwaltung von Mitarbeitern, Abteilungen und Rollen (Core-Entities)

### Datenmodelle

#### 1. Department

Organisationseinheiten wie IT, HR, Finance, etc.

**Tabelle:** `departments`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `name` | String | Abteilungsname (z.B. "IT", "HR") |
| `code` | String | Kurz-Code (z.B. "IT", "FIN") |
| `description` | Text | Beschreibung der Abteilung |
| `manager_id` | UUID (FK) | Abteilungsleiter (Employee) |
| `created_at` | Timestamp | Erstellungsdatum |

**Relationships:**
- `employees` → Liste aller Mitarbeiter in dieser Abteilung
- `manager` → Abteilungsleiter (Employee)

**API Endpoints:**
```
GET    /api/departments        # Liste aller Abteilungen
POST   /api/departments        # Neue Abteilung erstellen
GET    /api/departments/{id}   # Abteilung abrufen
PUT    /api/departments/{id}   # Abteilung aktualisieren
DELETE /api/departments/{id}   # Abteilung löschen
```

---

#### 2. Role

System-Rollen mit Berechtigungen (RBAC).

**Tabelle:** `roles`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `name` | String | Rollenname (z.B. "Admin", "Manager") |
| `description` | Text | Beschreibung der Rolle |
| `keycloak_id` | String | Zitadel Role ID (für SSO-Mapping) |
| `permissions_json` | JSONB | Array von Permissions (z.B. `["*"]`, `["backoffice.*"]`) |

**Relationships:**
- `employees` → Liste aller Mitarbeiter mit dieser Rolle

**Beispiel-Daten:**
```json
{
  "name": "Admin",
  "permissions_json": ["*"],
  "keycloak_id": "zitadel-role-admin-123"
}
```

**API Endpoints:**
```
GET    /api/roles        # Liste aller Rollen
POST   /api/roles        # Neue Rolle erstellen
GET    /api/roles/{id}   # Rolle abrufen
PUT    /api/roles/{id}   # Rolle aktualisieren
DELETE /api/roles/{id}   # Rolle löschen (nur wenn keine Employees)
```

---

#### 3. Employee

Zentrale Mitarbeiter-Entity mit allen Personal-Informationen.

**Tabelle:** `employees`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **Identifikation** | | |
| `id` | UUID | Primary Key |
| `employee_code` | String (unique) | Mitarbeiter-Code (z.B. "KIT-0001") |
| `uuid_keycloak` | String | Zitadel User ID (für SSO) |
| **Persönliche Daten** | | |
| `first_name` | String | Vorname |
| `last_name` | String | Nachname |
| `gender` | String | Geschlecht (male, female, diverse, other) |
| `birth_date` | Date | Geburtsdatum |
| `nationality` | String | Staatsangehörigkeit |
| `photo_url` | String | Pfad zum Profilbild |
| `bio` | Text | Biografie / Beschreibung |
| **Kontakt** | | |
| `email` | String (unique) | E-Mail-Adresse |
| `phone` | String | Telefonnummer |
| **Adresse** | | |
| `address_street` | String | Straße & Hausnummer |
| `address_zip` | String | Postleitzahl |
| `address_city` | String | Stadt |
| `address_country` | String | Land |
| **Organisation** | | |
| `department_id` | UUID (FK) | Zugehörige Abteilung |
| `role_id` | UUID (FK) | Zugewiesene Rolle |
| `reports_to` | UUID (FK) | Vorgesetzter (Employee) |
| **Beschäftigung** | | |
| `employment_type` | String | fulltime, parttime, intern, external |
| `hire_date` | Date | Einstellungsdatum |
| `termination_date` | Date | Kündigungsdatum |
| `status` | String | active, inactive, on_leave |
| **Präferenzen** | | |
| `timezone` | String | Zeitzone (default: Europe/Berlin) |
| `language` | String | Sprache (default: de) |
| `theme` | String | UI-Theme (default: catppuccin-frappe) |
| `notifications_enabled` | Boolean | Benachrichtigungen aktiviert |
| **Externe Services** | | |
| `matrix_username` | String | Matrix Chat Username |
| **Timestamps** | | |
| `created_at` | Timestamp | Erstellt am |
| `updated_at` | Timestamp | Zuletzt geändert |
| `last_login` | Timestamp | Letzter Login |

**Relationships:**
- `department` → Abteilung
- `role` → Zugewiesene Rolle
- `supervisor` → Vorgesetzter (Employee)
- `documents` → Liste aller Dokumente
- `reminders` → Liste aller Erinnerungen
- `dashboards` → Personalisierte Dashboards
- `chat_messages` → Chat-Nachrichten
- `os_preferences` → OS-Einstellungen
- `user_settings` → Benutzer-Einstellungen
- `notifications` → Benachrichtigungen
- `activity_entries` → Aktivitätsverlauf

**API Endpoints:**
```
GET    /api/employees              # Liste mit Pagination & Filtern
POST   /api/employees              # Neuen Mitarbeiter anlegen
GET    /api/employees/{id}         # Mitarbeiter abrufen
PUT    /api/employees/{id}         # Mitarbeiter aktualisieren
DELETE /api/employees/{id}         # Mitarbeiter löschen
GET    /api/employees/me           # Aktuell eingeloggter User
GET    /api/employees/{id}/documents  # Dokumente eines Mitarbeiters
```

**Query Parameter:**
```
GET /api/employees?skip=0&limit=20&status=active&department_id={uuid}&search=Joshua
```

**Validierungen:**
- `employee_code` muss unique sein
- `email` muss unique und valid sein
- `status` muss einer der erlaubten Werte sein
- `employment_type` muss einer der erlaubten Werte sein

---

## Documents Module

**Pfad:** `app/modules/documents/`
**Zweck:** Zentrales Dokumenten-Management für File-Uploads

### Datenmodelle

#### Document

Zentrale Datei-Speicherung mit Referenzsystem.

**Tabelle:** `documents`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `title` | String | Dokumenten-Titel |
| `file_path` | String | Pfad zur Datei (z.B. `/uploads/docs/...`) |
| `type` | String | Dateityp (pdf, image, doc, etc.) |
| `category` | String | Kategorie (Krankmeldung, Vertrag, Rechnung) |
| `owner_id` | UUID (FK) | Besitzer (Employee) |
| `linked_module` | String | Ursprungs-Modul (HR, Finance, etc.) |
| `uploaded_at` | Timestamp | Upload-Zeitpunkt |
| `checksum` | String | Datei-Prüfsumme (SHA256) |
| `is_confidential` | Boolean | Vertraulich (DSGVO) |

**Relationships:**
- `owner` → Besitzer (Employee)

**API Endpoints:**
```
GET    /api/documents           # Liste aller Dokumente (gefiltert nach Permissions)
POST   /api/documents           # Dokument hochladen
GET    /api/documents/{id}      # Dokument-Metadaten abrufen
GET    /api/documents/{id}/download  # Datei herunterladen
PUT    /api/documents/{id}      # Metadaten aktualisieren
DELETE /api/documents/{id}      # Dokument löschen
```

**Upload-Beispiel:**
```python
# POST /api/documents
# Content-Type: multipart/form-data

{
  "file": <binary>,
  "title": "Arbeitsvertrag Joshua Phu",
  "category": "Vertrag",
  "is_confidential": true
}
```

**Validierungen:**
- Datei-Größe max. 50MB
- Erlaubte Dateitypen: pdf, png, jpg, docx, xlsx
- Checksum wird automatisch berechnet
- Duplicate detection via checksum

---

## Reminders Module

**Pfad:** `app/modules/reminders/`
**Zweck:** Universelles Erinnerungs- und Benachrichtigungssystem

### Datenmodelle

#### Reminder

Erinnerungen mit polymorphem Entity-Linking.

**Tabelle:** `reminders`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `title` | String | Erinnerungs-Titel |
| `description` | Text | Beschreibung |
| `due_date` | Date | Fälligkeitsdatum |
| `priority` | String | low, medium, high, critical |
| `linked_entity_type` | String | Verknüpfter Entity-Typ (z.B. "Document", "Invoice") |
| `linked_entity_id` | UUID | ID des verknüpften Entities |
| `owner_id` | UUID (FK) | Besitzer (Employee) |
| `status` | String | open, done, overdue |
| `created_at` | Timestamp | Erstellungsdatum |
| `notified` | Boolean | Notification bereits gesendet |

**Relationships:**
- `owner` → Besitzer (Employee)

**API Endpoints:**
```
GET    /api/reminders           # Liste aller Erinnerungen (current user)
POST   /api/reminders           # Neue Erinnerung erstellen
GET    /api/reminders/{id}      # Erinnerung abrufen
PUT    /api/reminders/{id}      # Erinnerung aktualisieren
DELETE /api/reminders/{id}      # Erinnerung löschen
PATCH  /api/reminders/{id}/complete  # Als erledigt markieren
```

**Beispiel - Polymorphe Verknüpfung:**
```json
{
  "title": "Rechnung RE-2025-001 bezahlen",
  "linked_entity_type": "Invoice",
  "linked_entity_id": "uuid-invoice-123",
  "due_date": "2025-01-15",
  "priority": "high"
}
```

**Background Jobs:**
- Täglicher Cronjob prüft überfällige Reminders
- Automatische Notifications per Email/Push

---

## Dashboards Module

**Pfad:** `app/modules/dashboards/`
**Zweck:** Personalisierte Dashboards und Benutzer-Einstellungen

### Datenmodelle

#### Dashboard

Benutzer-definierte Dashboard-Konfigurationen.

**Tabelle:** `dashboards`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `owner_id` | UUID (FK) | Besitzer (Employee) |
| `name` | String | Dashboard-Name |
| `config_json` | JSONB | Widget-Konfiguration |
| `is_default` | Boolean | Standard-Dashboard |
| `created_at` | Timestamp | Erstellungsdatum |

**Relationships:**
- `owner` → Besitzer (Employee)

**Beispiel-Config:**
```json
{
  "widgets": [
    {
      "type": "time_tracker",
      "position": {"x": 0, "y": 0, "w": 6, "h": 4}
    },
    {
      "type": "upcoming_reminders",
      "position": {"x": 6, "y": 0, "w": 6, "h": 4}
    }
  ]
}
```

**API Endpoints:**
```
GET    /api/dashboards          # Liste aller Dashboards (current user)
POST   /api/dashboards          # Neues Dashboard erstellen
GET    /api/dashboards/{id}     # Dashboard abrufen
PUT    /api/dashboards/{id}     # Dashboard aktualisieren
DELETE /api/dashboards/{id}     # Dashboard löschen
```

---

## System Module

**Pfad:** `app/modules/system/`
**Zweck:** Infrastruktur-Services und technische Integrationen

### Datenmodelle

#### InfraService

Technische Services wie Datenbanken, Keycloak, Matrix, etc.

**Tabelle:** `infra_services`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `name` | String | Service-Name |
| `type` | String | database, auth, mail, chat, storage, external_api |
| `connection_url` | String | Verbindungs-URL |
| `status` | String | active, inactive, error |
| `last_sync` | Timestamp | Letzte Synchronisation |
| `managed_by` | UUID (FK) | Verantwortlicher Admin (Employee) |

**Relationships:**
- `manager` → Verantwortlicher (Employee)

**Verwendung:**
- Überwachung externer Services
- Health-Checks
- Admin-Dashboard für Infrastruktur

---

# Backoffice Module

---

## CRM Module

**Pfad:** `app/modules/backoffice/crm/`
**Zweck:** Customer Relationship Management (Kunden & Kontakte)

### Datenmodelle

#### 1. Customer

Kunden / Organisationen.

**Tabelle:** `customers`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **Identifikation** | | |
| `id` | UUID | Primary Key |
| `customer_number` | String (unique) | Kundennummer (z.B. "KIT-CUS-000001") |
| `name` | String | Kundenname / Firmenname |
| `type` | String | creator, individual, business, government |
| **Kontakt** | | |
| `email` | String | Haupt-E-Mail |
| `phone` | String | Telefonnummer |
| `website` | String | Webseite |
| **Business** | | |
| `tax_id` | String | Steuernummer / USt-IdNr |
| **Adresse** | | |
| `street` | String | Straße & Hausnummer |
| `zip_code` | String | PLZ |
| `city` | String | Stadt |
| `country` | String | Land (default: Deutschland) |
| **Meta** | | |
| `notes` | Text | Interne Notizen |
| `status` | String | active, inactive, lead, blocked |
| `created_at` | Timestamp | Erstellt am |
| `updated_at` | Timestamp | Aktualisiert am |

**Relationships:**
- `contacts` → Liste aller Ansprechpartner
- `projects` → Liste aller Projekte
- `invoices` → Liste aller Rechnungen

**Properties:**
```python
@property
def full_address(self) -> str:
    """Vollständige Adresse als String"""

@property
def primary_contact(self) -> Contact:
    """Hauptansprechpartner"""

@property
def total_revenue(self) -> Decimal:
    """Gesamtumsatz (alle paid invoices)"""

@property
def outstanding_amount(self) -> Decimal:
    """Offene Forderungen"""

@property
def active_projects_count(self) -> int:
    """Anzahl aktiver Projekte"""
```

**API Endpoints:**
```
GET    /api/customers              # Liste mit Filtern
POST   /api/customers              # Neuen Kunden anlegen
GET    /api/customers/{id}         # Kunde abrufen
PUT    /api/customers/{id}         # Kunde aktualisieren
DELETE /api/customers/{id}         # Kunde löschen
GET    /api/customers/{id}/contacts    # Kontakte eines Kunden
GET    /api/customers/{id}/projects    # Projekte eines Kunden
GET    /api/customers/{id}/invoices    # Rechnungen eines Kunden
GET    /api/customers/{id}/statistics  # Umsatz-Statistiken
```

**Validierungen:**
- `customer_number` muss unique sein
- `status` muss einer der erlaubten Werte sein
- `type` muss einer der erlaubten Werte sein

---

#### 2. Contact

Ansprechpartner eines Kunden.

**Tabelle:** `contacts`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `customer_id` | UUID (FK) | Zugehöriger Kunde |
| `firstname` | String | Vorname |
| `lastname` | String | Nachname |
| `email` | String | E-Mail |
| `phone` | String | Telefon |
| `mobile` | String | Mobilnummer |
| `position` | String | Position im Unternehmen |
| `department` | String | Abteilung |
| `is_primary` | Boolean | Hauptansprechpartner (nur einer pro Customer) |
| `notes` | Text | Notizen |
| `created_at` | Timestamp | Erstellt am |
| `updated_at` | Timestamp | Aktualisiert am |

**Relationships:**
- `customer` → Zugehöriger Kunde

**Properties:**
```python
@property
def full_name(self) -> str:
    """Vorname + Nachname"""

@property
def display_name(self) -> str:
    """Name mit Position (z.B. 'Max Mustermann (Geschäftsführer)')"""
```

**API Endpoints:**
```
GET    /api/contacts           # Alle Kontakte (gefiltert)
POST   /api/contacts           # Neuen Kontakt erstellen
GET    /api/contacts/{id}      # Kontakt abrufen
PUT    /api/contacts/{id}      # Kontakt aktualisieren
DELETE /api/contacts/{id}      # Kontakt löschen
```

**Constraints:**
- Nur **ein** `is_primary=true` pro Customer (PostgreSQL Partial Unique Index)

---

#### 3. Activity

CRM-Aktivitäten (Calls, Meetings, Emails).

**Tabelle:** `crm_activities`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `customer_id` | UUID (FK) | Zugehöriger Kunde |
| `contact_id` | UUID (FK) | Optional: Zugehöriger Kontakt |
| `type` | String | call, meeting, email, note |
| `description` | Text | Beschreibung der Aktivität |
| `occurred_at` | Timestamp | Zeitpunkt der Aktivität |
| `created_at` | Timestamp | Erstellt am |

**Relationships:**
- `customer` → Kunde
- `contact` → Kontakt (optional)

**API Endpoints:**
```
GET    /api/activities           # Alle Aktivitäten
POST   /api/activities           # Neue Aktivität erstellen
GET    /api/customers/{id}/activities  # Aktivitäten eines Kunden
```

---

## Projects Module

**Pfad:** `app/modules/backoffice/projects/`
**Zweck:** Projekt-Management mit Budget, Zeiterfassung und Abrechnung

### Datenmodelle

#### Project

Projekte für Kunden mit Zeiterfassung und Budgetverwaltung.

**Tabelle:** `projects`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **Identifikation** | | |
| `id` | UUID | Primary Key |
| `customer_id` | UUID (FK) | Zugehöriger Kunde |
| `project_number` | String (unique) | Projektnummer (z.B. "PRJ-2025-001") |
| `title` | String | Projekttitel |
| **Organisation** | | |
| `department_id` | UUID (FK) | Zugehörige Abteilung |
| `project_manager_id` | UUID (FK) | Projektmanager (Employee) |
| **Status & Priorität** | | |
| `status` | String | planning, active, on_hold, completed, cancelled |
| `priority` | String | low, medium, high, urgent |
| **Zeitplan** | | |
| `start_date` | Date | Projektstartdatum |
| `end_date` | Date | Geplantes Projektende |
| `deadline` | Date | Finale Deadline |
| **Finanzen** | | |
| `budget` | Decimal(10,2) | Gesamtbudget in EUR |
| `hourly_rate` | Decimal(10,2) | Standard-Stundensatz |
| **Inhalt** | | |
| `description` | Text | Projektbeschreibung |
| `notes` | Text | Interne Notizen |
| **Timestamps** | | |
| `created_at` | Timestamp | Erstellt am |
| `updated_at` | Timestamp | Aktualisiert am |

**Relationships:**
- `customer` → Kunde
- `department` → Abteilung
- `project_manager` → Projektmanager
- `time_entries` → Zeiterfassungen
- `invoices` → Rechnungen
- `expenses` → Ausgaben
- `chat_messages` → Chat-Nachrichten

**Properties:**
```python
@property
def is_active(self) -> bool:
    """Prüft ob Projekt aktiv ist"""

@property
def is_overdue(self) -> bool:
    """Prüft ob Projekt überfällig ist"""

@property
def days_until_deadline(self) -> int:
    """Tage bis Deadline (negativ = überfällig)"""

@property
def total_hours_tracked(self) -> Decimal:
    """Summe aller erfassten Stunden"""

@property
def billable_hours(self) -> Decimal:
    """Summe abrechenbarer Stunden"""

@property
def total_revenue(self) -> Decimal:
    """Umsatz aus bezahlten Rechnungen"""

@property
def total_expenses(self) -> Decimal:
    """Summe aller Ausgaben"""

@property
def budget_utilization(self) -> float:
    """Budget-Auslastung in %"""

@property
def profit_margin(self) -> Decimal:
    """Gewinnmarge (Umsatz - Kosten)"""

@property
def completion_percentage(self) -> float:
    """Fertigstellungsgrad basierend auf Zeitraum"""
```

**API Endpoints:**
```
GET    /api/projects              # Liste aller Projekte
POST   /api/projects              # Neues Projekt erstellen
GET    /api/projects/{id}         # Projekt abrufen
PUT    /api/projects/{id}         # Projekt aktualisieren
DELETE /api/projects/{id}         # Projekt löschen
GET    /api/projects/{id}/time-entries   # Zeiterfassungen
GET    /api/projects/{id}/invoices       # Rechnungen
GET    /api/projects/{id}/expenses       # Ausgaben
GET    /api/projects/{id}/statistics     # Statistiken
```

**Validierungen:**
- `budget` muss >= 0 sein
- `hourly_rate` muss >= 0 sein
- `end_date` muss >= `start_date` sein
- `status` muss einer der erlaubten Werte sein

---

## Invoices Module

**Pfad:** `app/modules/backoffice/invoices/`
**Zweck:** Rechnungserstellung und Zahlungsmanagement

**📚 Vollständige Dokumentation:** Siehe [FINANCE_DOCUMENTATION_INDEX.md](../../FINANCE_DOCUMENTATION_INDEX.md)

### Datenmodelle

#### 1. Invoice

Kundenrechnungen und Angebote.

**Tabelle:** `invoices`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `customer_id` | UUID (FK) | Kunde |
| `project_id` | UUID (FK) | Optional: Projekt |
| `invoice_number` | String (unique) | Rechnungsnummer (z.B. "RE-2025-001") |
| `document_type` | String | invoice, quote |
| `status` | String | draft, sent, paid, partial, overdue, cancelled |
| `total` | Decimal(10,2) | Gesamtbetrag inkl. MwSt |
| `subtotal` | Decimal(10,2) | Zwischensumme ohne MwSt |
| `tax_amount` | Decimal(10,2) | MwSt-Betrag |
| `issued_date` | Date | Rechnungsdatum |
| `due_date` | Date | Fälligkeitsdatum |
| `pdf_path` | String | Pfad zur PDF-Rechnung |
| `notes` | Text | Interne Notizen |
| `terms` | Text | Zahlungsbedingungen |
| `created_at` | Timestamp | Erstellt am |
| `updated_at` | Timestamp | Aktualisiert am |

**Relationships:**
- `customer` → Kunde
- `project` → Projekt (optional)
- `line_items` → Rechnungspositionen
- `payments` → Zahlungseingänge

**Properties:**
```python
@property
def outstanding_amount(self) -> Decimal:
    """Offener Betrag (total - sum(payments))"""

@property
def is_fully_paid(self) -> bool:
    """Ist vollständig bezahlt?"""

@property
def days_overdue(self) -> int:
    """Tage überfällig (0 wenn nicht überfällig)"""
```

**Methods:**
```python
def recalculate_totals(self):
    """Berechnet total/subtotal/tax_amount aus line_items neu"""

def add_line_item(self, description, quantity, unit_price, tax_rate):
    """Fügt Rechnungsposition hinzu und aktualisiert Summen"""
```

**API Endpoints:**
```
GET    /api/invoices              # Liste aller Rechnungen
POST   /api/invoices              # Neue Rechnung erstellen
GET    /api/invoices/{id}         # Rechnung abrufen
PUT    /api/invoices/{id}         # Rechnung aktualisieren
DELETE /api/invoices/{id}         # Rechnung löschen
POST   /api/invoices/{id}/finalize  # Rechnung finalisieren (PDF generieren)
GET    /api/invoices/{id}/pdf     # PDF herunterladen
POST   /api/invoices/{id}/send    # Rechnung per Email versenden
```

---

#### 2. InvoiceLineItem

Rechnungspositionen.

**Tabelle:** `invoice_line_items`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `invoice_id` | UUID (FK) | Zugehörige Rechnung |
| `position` | Integer | Sortierung |
| `description` | String | Positionsbeschreibung |
| `quantity` | Decimal(10,2) | Menge |
| `unit_price` | Decimal(10,2) | Einzelpreis |
| `tax_rate` | Decimal(5,2) | Steuersatz (19.00 = 19%) |
| `total` | Decimal(10,2) | Gesamtpreis (berechnet) |

**Properties:**
```python
@property
def subtotal(self) -> Decimal:
    """Zwischensumme (quantity * unit_price)"""

@property
def tax_amount(self) -> Decimal:
    """Steuerbetrag"""
```

---

#### 3. Payment

Zahlungseingänge.

**Tabelle:** `payments`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `invoice_id` | UUID (FK) | Zugehörige Rechnung |
| `amount` | Decimal(10,2) | Zahlungsbetrag |
| `payment_date` | Date | Zahlungsdatum |
| `payment_method` | String | cash, bank_transfer, credit_card, etc. |
| `reference` | String | Zahlungsreferenz / Transaktions-ID |
| `notes` | Text | Notizen |
| `created_at` | Timestamp | Erstellt am |

**Relationships:**
- `invoice` → Rechnung

**API Endpoints:**
```
GET    /api/payments              # Alle Zahlungen
POST   /api/payments              # Zahlung erfassen
GET    /api/invoices/{id}/payments  # Zahlungen einer Rechnung
```

---

## Finance Module

**Pfad:** `app/modules/backoffice/finance/`
**Zweck:** Ausgaben-Management

### Datenmodelle

#### Expense

Ausgaben/Kosten für Projekte oder allgemein.

**Tabelle:** `expenses`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `project_id` | UUID (FK) | Optional: Projekt |
| `employee_id` | UUID (FK) | Verantwortlicher Employee |
| `category` | String | travel, material, software, etc. |
| `description` | Text | Beschreibung der Ausgabe |
| `amount` | Decimal(10,2) | Betrag |
| `expense_date` | Date | Ausgabedatum |
| `receipt_url` | String | Pfad zum Beleg (Foto/PDF) |
| `is_reimbursed` | Boolean | Erstattet? |
| `notes` | Text | Notizen |
| `created_at` | Timestamp | Erstellt am |

**Relationships:**
- `project` → Projekt (optional)
- `employee` → Employee

**API Endpoints:**
```
GET    /api/expenses              # Liste aller Ausgaben
POST   /api/expenses              # Neue Ausgabe erfassen
GET    /api/expenses/{id}         # Ausgabe abrufen
PUT    /api/expenses/{id}         # Ausgabe aktualisieren
DELETE /api/expenses/{id}         # Ausgabe löschen
PATCH  /api/expenses/{id}/reimburse  # Als erstattet markieren
```

---

## Time Tracking Module

**Pfad:** `app/modules/backoffice/time_tracking/`
**Zweck:** Zeiterfassung für Projekte

### Datenmodelle

#### TimeEntry

Arbeitszeit-Erfassung pro Employee und Projekt.

**Tabelle:** `time_entries`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `employee_id` | UUID (FK) | Mitarbeiter |
| `project_id` | UUID (FK) | Projekt (optional für interne Zeit) |
| `start_time` | Timestamp | Start-Zeitpunkt |
| `end_time` | Timestamp | End-Zeitpunkt (optional für laufende Timer) |
| `duration_minutes` | Integer | Dauer in Minuten (berechnet oder manuell) |
| `billable` | Boolean | Abrechenbar? |
| `hourly_rate` | Decimal(10,2) | Stundensatz für diesen Eintrag |
| `note` | Text | Was wurde gearbeitet? |
| `task_type` | String | development, meeting, support, documentation |
| `is_approved` | Boolean | Vom Manager genehmigt? |
| `is_invoiced` | Boolean | Bereits abgerechnet? |
| `created_at` | Timestamp | Erstellt am |
| `updated_at` | Timestamp | Aktualisiert am |

**Relationships:**
- `employee` → Employee
- `project` → Projekt

**Properties:**
```python
@property
def duration_hours(self) -> float:
    """Dauer in Stunden (Dezimal)"""
```

**API Endpoints:**
```
GET    /api/time-entries          # Liste aller Einträge
POST   /api/time-entries          # Neuen Eintrag erfassen
GET    /api/time-entries/{id}     # Eintrag abrufen
PUT    /api/time-entries/{id}     # Eintrag aktualisieren
DELETE /api/time-entries/{id}     # Eintrag löschen
POST   /api/time-entries/start    # Timer starten
POST   /api/time-entries/{id}/stop  # Timer stoppen
GET    /api/time-entries/current  # Aktuell laufender Timer
GET    /api/employees/{id}/time-entries  # Einträge eines Mitarbeiters
GET    /api/projects/{id}/time-entries   # Einträge eines Projekts
```

**Query Parameter:**
```
GET /api/time-entries?employee_id={uuid}&project_id={uuid}&start_date=2025-01-01&end_date=2025-01-31&billable=true
```

---

## Chat Module

**Pfad:** `app/modules/backoffice/chat/`
**Zweck:** Projekt-bezogenes Messaging-System

### Datenmodelle

#### ChatMessage

Nachrichten im Kontext von Projekten.

**Tabelle:** `chat_messages`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | UUID | Primary Key |
| `project_id` | UUID (FK) | Zugehöriges Projekt |
| `author_id` | UUID (FK) | Autor (Employee) |
| `content` | Text | Nachrichten-Inhalt |
| `is_system_message` | Boolean | System-Nachricht (z.B. "Projekt erstellt") |
| `created_at` | Timestamp | Erstellt am |
| `updated_at` | Timestamp | Bearbeitet am |

**Relationships:**
- `project` → Projekt
- `author` → Employee

**API Endpoints:**
```
GET    /api/messages              # Alle Nachrichten (gefiltert)
POST   /api/messages              # Neue Nachricht senden
GET    /api/projects/{id}/messages  # Nachrichten eines Projekts
DELETE /api/messages/{id}         # Nachricht löschen (nur eigene)
```

**WebSocket Support:**
```
WS /ws/projects/{project_id}/chat
```
Real-time Messaging für Live-Updates.

---

## 🔧 Entwickler-Hinweise

### Konsistente Patterns

Alle Module folgen diesen Patterns:

#### 1. Datenmodelle
```python
from app.core.settings.database import Base
from app.core.misc.mixins import UUIDMixin, TimestampMixin

class MyModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "my_models"

    # Fields...

    # Relationships...

    # Properties...

    def __repr__(self):
        return f"<MyModel(id={self.id}, ...)>"
```

#### 2. Enums
```python
from enum import Enum

class MyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

#### 3. API Routes
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/my-models", tags=["MyModels"])

@router.get("/")
async def list_items(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    # Implementation...

@router.post("/")
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    # Implementation...
```

#### 4. Schemas (Pydantic)
```python
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
```

### Code-Qualität

**Validierungen:**
- SQLAlchemy CheckConstraints für Daten-Integrität
- Pydantic Schemas für Request/Response Validation
- Business-Logic in Models (Properties & Methods)

**Performance:**
- Indizes auf FK und häufig gefilterten Feldern
- Lazy Loading für große Relationships
- Pagination für alle List-Endpoints

**Sicherheit:**
- RBAC via Permissions (siehe [AUTHENTICATION.md](./AUTHENTICATION.md))
- SQL Injection Prevention durch ORM
- Input Validation durch Pydantic

---

## 📊 Statistiken

**Gesamt:**
- 11 Module
- 25+ Models
- 100+ API Endpoints
- 50+ Relationships

**Code-Metriken:**
- Lines of Code: ~15.000+
- Test Coverage: ⏳ TODO
- API Response Time: <100ms (avg)

---

## 📝 Changelog

| Datum | Modul | Änderung |
|-------|-------|----------|
| 30.12.2025 | Alle | Initiale Dokumentation erstellt |
| 30.12.2025 | CRM | CustomerStatus Enum hinzugefügt |
| 30.12.2025 | Projects | Budget-Properties erweitert |
| 30.12.2025 | Invoices | recalculate_totals() Method |

---

## 🔗 Siehe auch

- [Authentication & SSO](./AUTHENTICATION.md) - Permission System
- [API Reference](./API_REFERENCE.md) (TODO) - Alle Endpoints im Detail
- [Finance Documentation](../../FINANCE_DOCUMENTATION_INDEX.md) - Rechnungswesen
- [Database Schema](../core/core_erm.dbml) - ER-Diagramm

---

**Letzte Aktualisierung:** 30. Dezember 2025
**Maintainer:** K.I.T Solutions Team
**Feedback:** GitHub Issues oder direkter Kontakt

