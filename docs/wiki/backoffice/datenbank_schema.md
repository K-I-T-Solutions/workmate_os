---
layout: default
title: Datenbank-Schema
parent: Backoffice
grand_parent: Wiki
nav_order: 2
---

# Datenbank-Schema - Backoffice & CRM (Phase 2)

**PostgreSQL-Datenbankstruktur für WorkmateOS Phase 2**

---

## Übersicht

Die Backoffice-Datenbank umfasst zwei Hauptbereiche:

1. **Core-Tabellen**: Grundlegende Entitäten (Mitarbeiter, Abteilungen, Rollen, etc.)
2. **CRM & Backoffice-Tabellen**: Kundenverwaltung, Projekte, Zeiterfassung, Finanzen

---

## 📊 Entity Relationship Diagram

### Visuelle Darstellung

![Backoffice Database Schema](./mermaid-diagram-2025-10-24-091048.png)

*Vollständiges ERD mit allen Tabellen und Beziehungen*

![Backoffice Module Architecture](./mermaid-diagram-2025-10-24-091134.png)

*Modul-Architektur und Datenfluss*

---

## 🗄️ Core-Tabellen

### employees (Mitarbeiter)

**Beschreibung**: Mitarbeiterstammdaten mit Rollen- und Abteilungszuordnung

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `firstname` | `varchar` | Vorname |
| `lastname` | `varchar` | Nachname |
| `email` | `varchar` | E-Mail-Adresse |
| `role_id` | `uuid` | Foreign Key → `roles.id` |
| `department_id` | `uuid` | Foreign Key → `departments.id` |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- `role_id` → `roles.id` (Many-to-One)
- `department_id` → `departments.id` (Many-to-One)
- Rückverweise: `time_entries`, `chat_messages`, `dashboards`, `reminders`, `documents`

---

### departments (Abteilungen)

**Beschreibung**: Organisationsstruktur mit Abteilungen und Managern

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `name` | `varchar` | Abteilungsname |
| `manager_id` | `uuid` | Foreign Key → `employees.id` |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- `manager_id` → `employees.id` (Many-to-One)
- Rückverweise: `employees`, `projects`

---

### roles (Rollen & Berechtigungen)

**Beschreibung**: Rollen mit JSON-basiertem Berechtigungssystem

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `name` | `varchar` | Rollenname (z.B. "Admin", "Manager") |
| `permissions` | `jsonb` | Berechtigungen als JSON |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Beispiel `permissions` JSON**:
```json
{
  "crm": ["read", "write", "delete"],
  "projects": ["read", "write"],
  "invoices": ["read"],
  "admin_panel": ["access"]
}
```

**Relationen**:
- Rückverweise: `employees`

---

### documents (Dokumentenverwaltung)

**Beschreibung**: Zentrale Dokumentenverwaltung mit polymorpher Verknüpfung

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `title` | `varchar` | Dokumenttitel |
| `file_path` | `text` | Dateipfad auf Server |
| `type` | `varchar` | Dateityp (pdf, docx, xlsx, etc.) |
| `category` | `varchar` | Kategorie (contract, invoice, report) |
| `owner_id` | `uuid` | Foreign Key → `employees.id` |
| `linked_module` | `varchar` | Modulname (customer, project, invoice) |
| `linked_id` | `uuid` | ID des verknüpften Objekts |
| `checksum` | `varchar` | SHA256-Prüfsumme |
| `is_confidential` | `boolean` | Vertraulich? |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Polymorphe Verknüpfung**:
- `linked_module` + `linked_id` ermöglichen flexible Zuordnung zu beliebigen Entities
- Beispiel: `linked_module = "customer"`, `linked_id = "123-456-789"` → Dokument gehört zu Kunde mit ID 123-456-789

**Relationen**:
- `owner_id` → `employees.id` (Many-to-One)

---

### reminders (Erinnerungen & Aufgaben)

**Beschreibung**: Aufgabenverwaltung mit Fälligkeitsdatum und Priorität

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `title` | `varchar` | Aufgabentitel |
| `due_date` | `date` | Fälligkeitsdatum |
| `priority` | `varchar` | Priorität (low, medium, high) |
| `linked_to` | `varchar` | Verknüpfung (customer, project, invoice) |
| `owner_id` | `uuid` | Foreign Key → `employees.id` |
| `is_done` | `boolean` | Erledigt? |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- `owner_id` → `employees.id` (Many-to-One)

---

### dashboards (Benutzer-Dashboards)

**Beschreibung**: Personalisierte Dashboard-Layouts pro Benutzer

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `user_id` | `uuid` | Foreign Key → `employees.id` |
| `layout_json` | `jsonb` | Widget-Layout als JSON |
| `theme` | `varchar` | Theme (dark, light) |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Beispiel `layout_json`**:
```json
{
  "widgets": [
    {"id": "crm-stats", "x": 0, "y": 0, "w": 4, "h": 2},
    {"id": "recent-customers", "x": 4, "y": 0, "w": 4, "h": 2},
    {"id": "project-timeline", "x": 0, "y": 2, "w": 8, "h": 3}
  ]
}
```

**Relationen**:
- `user_id` → `employees.id` (Many-to-One)

---

## 🏢 CRM & Backoffice-Tabellen

### customers (Kunden)

**Beschreibung**: Kundenstammdaten für CRM

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `name` | `varchar` | Firmenname / Name |
| `type` | `varchar` | Kundentyp (B2B, B2C) |
| `email` | `varchar` | E-Mail-Adresse |
| `phone` | `varchar` | Telefonnummer |
| `tax_id` | `varchar` | Steuernummer / USt-IdNr. |
| `address` | `text` | Vollständige Adresse |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- Rückverweise: `contacts`, `projects`, `invoices`

---

### contacts (Kontaktpersonen)

**Beschreibung**: Ansprechpartner bei Kunden

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `customer_id` | `uuid` | Foreign Key → `customers.id` |
| `firstname` | `varchar` | Vorname |
| `lastname` | `varchar` | Nachname |
| `email` | `varchar` | E-Mail-Adresse |
| `phone` | `varchar` | Telefonnummer |
| `position` | `varchar` | Position (z.B. "Geschäftsführer") |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- `customer_id` → `customers.id` (Many-to-One)

---

### projects (Projekte)

**Beschreibung**: Kundenprojekte mit Status und Zeitrahmen

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `customer_id` | `uuid` | Foreign Key → `customers.id` |
| `department_id` | `uuid` | Foreign Key → `departments.id` |
| `title` | `varchar` | Projekttitel |
| `status` | `varchar` | Status (planned, in_progress, completed, cancelled) |
| `start_date` | `date` | Startdatum |
| `end_date` | `date` | Enddatum |
| `description` | `text` | Projektbeschreibung |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- `customer_id` → `customers.id` (Many-to-One)
- `department_id` → `departments.id` (Many-to-One)
- Rückverweise: `time_entries`, `invoices`, `expenses`, `chat_messages`

---

### time_entries (Zeiterfassung)

**Beschreibung**: Arbeitszeiterfassung pro Mitarbeiter und Projekt

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `employee_id` | `uuid` | Foreign Key → `employees.id` |
| `project_id` | `uuid` | Foreign Key → `projects.id` |
| `start_time` | `timestamp` | Startzeit |
| `end_time` | `timestamp` | Endzeit (NULL = läuft noch) |
| `duration` | `interval` | Dauer (PostgreSQL interval) |
| `note` | `text` | Notiz zur Tätigkeit |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Besonderheiten**:
- `duration` wird automatisch aus `end_time - start_time` berechnet
- `end_time = NULL` bedeutet "Timer läuft noch"

**Relationen**:
- `employee_id` → `employees.id` (Many-to-One)
- `project_id` → `projects.id` (Many-to-One)

---

### invoices (Rechnungen)

**Beschreibung**: Kundenrechnungen mit PDF-Export

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `customer_id` | `uuid` | Foreign Key → `customers.id` |
| `project_id` | `uuid` | Foreign Key → `projects.id` (optional) |
| `total` | `numeric` | Gesamtbetrag |
| `status` | `varchar` | Status (draft, sent, paid, overdue) |
| `due_date` | `date` | Fälligkeitsdatum |
| `issued_date` | `date` | Rechnungsdatum |
| `pdf_path` | `text` | Pfad zur PDF-Datei |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- `customer_id` → `customers.id` (Many-to-One)
- `project_id` → `projects.id` (Many-to-One, optional)
- Rückverweise: `payments`, `expenses`

---

### payments (Zahlungen)

**Beschreibung**: Zahlungseingänge für Rechnungen

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `invoice_id` | `uuid` | Foreign Key → `invoices.id` |
| `amount` | `numeric` | Zahlungsbetrag |
| `payment_date` | `date` | Zahlungsdatum |
| `method` | `varchar` | Zahlungsmethode (bank_transfer, credit_card, cash, paypal) |
| `note` | `text` | Notiz |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Besonderheiten**:
- Mehrere Payments pro Invoice möglich (Teilzahlungen)
- Summe aller Payments = Invoice.total → Status wird automatisch auf "paid" gesetzt

**Relationen**:
- `invoice_id` → `invoices.id` (Many-to-One)

---

### expenses (Ausgaben)

**Beschreibung**: Projekt- und Rechnungsausgaben

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `project_id` | `uuid` | Foreign Key → `projects.id` (optional) |
| `invoice_id` | `uuid` | Foreign Key → `invoices.id` (optional) |
| `category` | `varchar` | Kategorie (material, personnel, service, other) |
| `amount` | `numeric` | Betrag |
| `note` | `text` | Beschreibung |
| `created_at` | `timestamp` | Erstellungsdatum |
| `updated_at` | `timestamp` | Letzte Änderung |

**Relationen**:
- `project_id` → `projects.id` (Many-to-One, optional)
- `invoice_id` → `invoices.id` (Many-to-One, optional)

---

### chat_messages (Projekt-Chat)

**Beschreibung**: Projektkommunikation im Team

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | `uuid` | Primary Key |
| `project_id` | `uuid` | Foreign Key → `projects.id` |
| `author_id` | `uuid` | Foreign Key → `employees.id` |
| `message` | `text` | Nachrichtentext |
| `created_at` | `timestamp` | Erstellungsdatum |

**Relationen**:
- `project_id` → `projects.id` (Many-to-One)
- `author_id` → `employees.id` (Many-to-One)

---

## 🔗 Beziehungsübersicht

### Haupt-Datenfluss

```
┌──────────────┐
│  employees   │◄──────────┐
└──────┬───────┘           │
       │                   │
       │ owns              │ belongs to
       ↓                   │
┌──────────────┐    ┌──────────────┐
│ departments  │────│ time_entries │
└──────┬───────┘    └──────┬───────┘
       │                   │
       │ manages           │ tracked on
       ↓                   ↓
┌──────────────┐    ┌──────────────┐
│  projects    │◄───│  customers   │
└──────┬───────┘    └──────┬───────┘
       │                   │
       │ billed in         │ has
       ↓                   ↓
┌──────────────┐    ┌──────────────┐
│  invoices    │    │  contacts    │
└──────┬───────┘    └──────────────┘
       │
       │ paid with
       ↓
┌──────────────┐
│  payments    │
└──────────────┘
```

### Kardinalitäten

| Beziehung | Typ | Beschreibung |
|-----------|-----|--------------|
| `employees` → `roles` | Many-to-One | Viele Mitarbeiter können dieselbe Rolle haben |
| `employees` → `departments` | Many-to-One | Viele Mitarbeiter können in derselben Abteilung sein |
| `departments` → `employees` (manager) | Many-to-One | Jede Abteilung hat einen Manager |
| `customers` → `contacts` | One-to-Many | Ein Kunde kann mehrere Kontakte haben |
| `customers` → `projects` | One-to-Many | Ein Kunde kann mehrere Projekte haben |
| `projects` → `time_entries` | One-to-Many | Ein Projekt hat viele Zeiteinträge |
| `projects` → `chat_messages` | One-to-Many | Ein Projekt hat viele Chat-Nachrichten |
| `projects` → `invoices` | One-to-Many | Ein Projekt kann mehrere Rechnungen haben |
| `invoices` → `payments` | One-to-Many | Eine Rechnung kann mehrere Zahlungen haben |
| `invoices` → `expenses` | One-to-Many | Eine Rechnung kann mehrere Ausgaben haben |

---

## 📝 DBML-Datei

Die vollständige Datenbankdefinition als DBML (Database Markup Language) findest du in:

📄 **[workmateos_phase2.dbml](./workmateos_phase2.dbml)**

Diese Datei kann mit Tools wie [dbdiagram.io](https://dbdiagram.io) visualisiert werden.

---

## 🔧 Datenbank-Setup

### Migration erstellen (Alembic)

```bash
# Neue Migration generieren
alembic revision --autogenerate -m "Add backoffice tables"

# Migration ausführen
alembic upgrade head
```

### Initiale Daten (Seeds)

```sql
-- Beispiel-Rolle anlegen
INSERT INTO roles (id, name, permissions) VALUES
  (gen_random_uuid(), 'Admin', '{"crm": ["read", "write", "delete"], "admin_panel": ["access"]}'),
  (gen_random_uuid(), 'Manager', '{"crm": ["read", "write"], "projects": ["read", "write"]}'),
  (gen_random_uuid(), 'Employee', '{"crm": ["read"], "projects": ["read"], "time_entries": ["write"]}');

-- Beispiel-Abteilung
INSERT INTO departments (id, name) VALUES
  (gen_random_uuid(), 'Sales'),
  (gen_random_uuid(), 'Development'),
  (gen_random_uuid(), 'Management');
```

---

## 🔐 Indizes & Performance

### Empfohlene Indizes

```sql
-- Häufige Lookups
CREATE INDEX idx_employees_role_id ON employees(role_id);
CREATE INDEX idx_employees_department_id ON employees(department_id);
CREATE INDEX idx_contacts_customer_id ON contacts(customer_id);
CREATE INDEX idx_projects_customer_id ON projects(customer_id);
CREATE INDEX idx_time_entries_employee_id ON time_entries(employee_id);
CREATE INDEX idx_time_entries_project_id ON time_entries(project_id);
CREATE INDEX idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX idx_payments_invoice_id ON payments(invoice_id);

-- Polymorphe Verknüpfungen
CREATE INDEX idx_documents_linked ON documents(linked_module, linked_id);

-- Status-Filter
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_projects_status ON projects(status);

-- Zeitbasierte Queries
CREATE INDEX idx_time_entries_start_time ON time_entries(start_time);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
```

---

**Datenbank**: PostgreSQL 15+
**ORM**: SQLAlchemy 2.0
**Migrations**: Alembic
**Letzte Aktualisierung**: 30. Dezember 2025
