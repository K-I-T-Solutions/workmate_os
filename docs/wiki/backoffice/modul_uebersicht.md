---
layout: default
title: Modul-Übersicht
parent: Backoffice
grand_parent: Wiki
nav_order: 1
---

# Backoffice Module - Detaillierte Übersicht

## 1. CRM (Customer Relationship Management)

### Beschreibung
Das CRM-Modul ist das Herzstück der Kundenverwaltung. Es ermöglicht die zentrale Verwaltung aller Kundenbeziehungen, Kontakte und zugehöriger Aktivitäten.

### Hauptfunktionen
- **Kundenverwaltung**: Stammdatenpflege mit Name, E-Mail, Telefon, Adresse, Steuernummer
- **Kundentypen**: Unterscheidung zwischen B2B/B2C
- **Kontaktpersonen**: Mehrere Ansprechpartner pro Kunde mit Position und Kontaktdaten
- **Kundenhistorie**: Übersicht über alle Aktivitäten, Projekte, Rechnungen
- **CRM-Dashboard**: KPIs, aktive Kunden, Umsatzstatistiken

### API-Endpunkte
```
GET    /api/backoffice/crm/customers       → Alle Kunden
GET    /api/backoffice/crm/customers/:id   → Einzelner Kunde
POST   /api/backoffice/crm/customers       → Neuer Kunde
PUT    /api/backoffice/crm/customers/:id   → Kunde aktualisieren
DELETE /api/backoffice/crm/customers/:id   → Kunde löschen

GET    /api/backoffice/crm/contacts        → Alle Kontakte
GET    /api/backoffice/crm/contacts/:id    → Einzelner Kontakt
POST   /api/backoffice/crm/contacts        → Neuer Kontakt
PUT    /api/backoffice/crm/contacts/:id    → Kontakt aktualisieren
DELETE /api/backoffice/crm/contacts/:id    → Kontakt löschen

GET    /api/backoffice/crm/stats           → CRM-Statistiken
GET    /api/backoffice/crm/activities      → CRM-Aktivitäten
```

### Datenmodell
```typescript
interface Customer {
  id: string;
  name: string;
  type: "B2B" | "B2C";
  email: string | null;
  phone: string | null;
  tax_id: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
}

interface Contact {
  id: string;
  customer_id: string;
  firstname: string;
  lastname: string;
  email: string | null;
  phone: string | null;
  position: string | null;
  created_at: string;
  updated_at: string;
}
```

### UI-Module
- `ui/src/modules/crm/CrmApp.vue` - Hauptkomponente
- `ui/src/modules/crm/pages/CustomersListPage.vue` - Kundenliste
- `ui/src/modules/crm/pages/CustomerDetailPage.vue` - Kundendetails
- `ui/src/modules/crm/pages/ContactsListPage.vue` - Kontaktliste
- `ui/src/modules/crm/pages/CrmDashboardPage.vue` - CRM-Dashboard

### Status
✅ **Produktiv** - Vollständig implementiert (Backend + Frontend)
- Backend: `backend/app/modules/backoffice/crm/`
- Frontend: `ui/src/modules/crm/`

---

## 2. Projektmanagement

### Beschreibung
Verwaltung von Kundenprojekten mit Status-Tracking, Zeiterfassung und Team-Zuordnung.

### Hauptfunktionen
- **Projektverwaltung**: Titel, Beschreibung, Start-/Enddatum
- **Status-Tracking**: Geplant, In Bearbeitung, Abgeschlossen, Abgebrochen
- **Kundenzuordnung**: Verknüpfung mit CRM-Kunden
- **Abteilungszuordnung**: Zuständige Abteilung
- **Projektübersicht**: Dashboard mit allen aktiven Projekten

### API-Endpunkte
```
GET    /api/backoffice/projects            → Alle Projekte
GET    /api/backoffice/projects/:id        → Einzelnes Projekt
POST   /api/backoffice/projects            → Neues Projekt
PUT    /api/backoffice/projects/:id        → Projekt aktualisieren
DELETE /api/backoffice/projects/:id        → Projekt löschen
GET    /api/backoffice/projects/:id/stats  → Projekt-Statistiken
```

### Datenmodell
```typescript
interface Project {
  id: string;
  customer_id: string;
  department_id: string;
  title: string;
  status: "planned" | "in_progress" | "completed" | "cancelled";
  start_date: string;
  end_date: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}
```

### Status
✅ **Vollständig** - Backend + Frontend implementiert
- Backend: `backend/app/modules/backoffice/projects/` ✅
- Frontend: `ui/src/modules/projects/` ✅
  - ProjectsDashboardPage.vue
  - ProjectsListPage.vue
  - ProjectDetailPage.vue
  - ProjectFormPage.vue
- API-Endpunkte: Alle CRUD-Operationen verfügbar
- Features: Filter nach Kunde, Pagination, Status-Management

---

## 3. Zeiterfassung

### Beschreibung
Erfassung von Arbeitszeiten pro Mitarbeiter und Projekt mit automatischer Dauerberechnung.

### Hauptfunktionen
- **Zeitbuchung**: Start-/Endzeit mit automatischer Berechnung
- **Projektbezug**: Jede Zeitbuchung einem Projekt zugeordnet
- **Notizen**: Beschreibung der durchgeführten Tätigkeit
- **Mitarbeiterübersicht**: Zeitbuchungen pro Mitarbeiter
- **Projektübersicht**: Gesamtzeit pro Projekt
- **Zeitberichte**: Export & Auswertungen

### API-Endpunkte
```
GET    /api/backoffice/time-entries               → Alle Zeiteinträge
GET    /api/backoffice/time-entries/:id           → Einzelner Zeiteintrag
POST   /api/backoffice/time-entries               → Neuer Zeiteintrag
PUT    /api/backoffice/time-entries/:id           → Zeiteintrag aktualisieren
DELETE /api/backoffice/time-entries/:id           → Zeiteintrag löschen
GET    /api/backoffice/time-entries/by-project/:id → Nach Projekt
GET    /api/backoffice/time-entries/by-employee/:id → Nach Mitarbeiter
```

### Datenmodell
```typescript
interface TimeEntry {
  id: string;
  employee_id: string;
  project_id: string;
  start_time: string;      // ISO 8601 Timestamp
  end_time: string | null; // Null = läuft noch
  duration: string;        // PostgreSQL interval (z.B. "02:30:00")
  note: string | null;
  created_at: string;
  updated_at: string;
}
```

### Status
✅ **Vollständig** - Backend + Frontend implementiert
- Backend: `backend/app/modules/backoffice/time_tracking/` ✅
- Frontend: `ui/src/modules/time-tracking/` ✅
  - TimeTrackingDashboard.vue
  - TimeEntriesListPage.vue
  - TimeEntryDetailPage.vue
  - TimeEntryFormPage.vue (mit Start/Stop Timer)
- API-Prefix: `/api/backoffice/time-tracking`
- Features: Automatische Dauer-Berechnung, Mitarbeiter & Projekt-Filter

---

## 4. Rechnungsmanagement

### Beschreibung
Erstellung und Verwaltung von Kundenrechnungen mit PDF-Export und Zahlungsverfolgung.

### Hauptfunktionen
- **Rechnungserstellung**: Automatisch aus Projekten/Zeiteinträgen
- **PDF-Generierung**: Rechnungs-PDFs mit Firmenlogo
- **Status-Tracking**: Entwurf, Versendet, Bezahlt, Überfällig
- **Fälligkeitsdatum**: Automatische Berechnung
- **Kundenzuordnung**: Verknüpfung mit CRM
- **Projektzuordnung**: Projektbezogene Rechnungen

### API-Endpunkte
```
# LIST & FILTERS
GET    /api/backoffice/invoices             → Alle Rechnungen (mit Pagination & Filtern)
GET    /api/backoffice/invoices/statistics  → Statistiken (Umsatz, offene Forderungen)
GET    /api/backoffice/invoices/:id         → Einzelne Rechnung
GET    /api/backoffice/invoices/by-number/:invoice_number → Nach Rechnungsnummer

# CREATE & UPDATE
POST   /api/backoffice/invoices             → Neue Rechnung (mit Line Items)
PATCH  /api/backoffice/invoices/:id         → Rechnung aktualisieren
PATCH  /api/backoffice/invoices/:id/status  → Nur Status ändern
POST   /api/backoffice/invoices/:id/recalculate → Totals neu berechnen

# DELETE
DELETE /api/backoffice/invoices/:id         → Rechnung löschen (mit Cascade)

# PDF OPERATIONS
GET    /api/backoffice/invoices/:id/pdf     → PDF herunterladen (auto-generate falls fehlt)
POST   /api/backoffice/invoices/:id/regenerate-pdf → PDF neu generieren

# BULK OPERATIONS
POST   /api/backoffice/invoices/bulk/status-update → Status für mehrere Rechnungen

# PAYMENTS (siehe Zahlungsmanagement)
POST   /api/backoffice/invoices/:id/payments → Zahlung hinzufügen
GET    /api/backoffice/invoices/:id/payments → Alle Zahlungen einer Rechnung
```

### Datenmodell
```typescript
interface Invoice {
  id: string;
  customer_id: string;
  project_id: string | null;
  total: number;
  status: "draft" | "sent" | "paid" | "overdue";
  due_date: string;
  issued_date: string;
  pdf_path: string | null;
  created_at: string;
  updated_at: string;
}
```

### Status
✅ **Vollständig** - Backend + Frontend mit Advanced Features!
- Backend: `backend/app/modules/backoffice/invoices/` ✅
- Frontend: `ui/src/modules/invoices/` ✅
  - InvoicesDashboardPage.vue
  - InvoicesListPage.vue (mit Filtern)
  - InvoiceDetailPage.vue (mit PDF-Anzeige)
  - InvoiceFormPage.vue (mit Line Items)
  - CustomerSelect.vue
  - ProjectSelect.vue
- **Backend Features:**
  - ✅ PDF-Generierung (sync/async mit Background Tasks)
  - ✅ Line Items System mit Auto-Positionierung
  - ✅ Pagination & Multi-Filter (Status, Kunde, Projekt, Datumsbereich)
  - ✅ Statistik-Dashboard (Umsatz, Forderungen, Überfällige)
  - ✅ Bulk Status-Updates
  - ✅ Auto-Recalculate Totals
  - ✅ Payment Integration (siehe Zahlungsmanagement)
- Files: `routes.py`, `crud.py`, `pdf_generator.py`, `payments_crud.py`

---

## 5. Zahlungsmanagement

### Beschreibung
Verwaltung von Zahlungseingängen für Rechnungen.

### Hauptfunktionen
- **Zahlungserfassung**: Betrag, Datum, Zahlungsart
- **Rechnungszuordnung**: Verknüpfung mit Rechnung
- **Teilzahlungen**: Mehrere Zahlungen pro Rechnung möglich
- **Zahlungshistorie**: Übersicht aller Zahlungen
- **Automatische Status-Updates**: Rechnung als "bezahlt" markieren

### API-Endpunkte
```
# Payment Management (über Invoices-Route)
POST   /api/backoffice/invoices/:id/payments → Zahlung hinzufügen (mit Auto-Status)
GET    /api/backoffice/invoices/:id/payments → Alle Zahlungen einer Rechnung
GET    /api/backoffice/invoices/payments/:payment_id → Einzelne Zahlung
PATCH  /api/backoffice/invoices/payments/:payment_id → Zahlung aktualisieren
DELETE /api/backoffice/invoices/payments/:payment_id → Zahlung löschen
```

### Datenmodell
```typescript
interface Payment {
  id: string;
  invoice_id: string;
  amount: number;
  payment_date: string;
  method: "bank_transfer" | "credit_card" | "cash" | "paypal" | "other";
  note: string | null;
  created_at: string;
  updated_at: string;
}
```

### Status
✅ **Vollständig** - In Invoices-Modul integriert (Backend + Frontend)
- Backend: `backend/app/modules/backoffice/invoices/payments_crud.py` ✅
- Frontend: In `ui/src/modules/invoices/` integriert ✅
  - Zahlungen werden in InvoiceDetailPage.vue angezeigt
  - Zahlungsformular in Invoice-Modul
- **Features:**
  - ✅ Teilzahlungen unterstützt
  - ✅ Auto-Status-Update (paid/partial bei vollständiger/teilweiser Zahlung)
  - ✅ Validierung (Betrag ≤ outstanding_amount)
  - ✅ CRUD-Operationen komplett

---

## 6. Ausgabenverwaltung

### Beschreibung
Erfassung und Verwaltung von Projekt- und Rechnungsausgaben.

### Hauptfunktionen
- **Ausgabenerfassung**: Kategorie, Betrag, Beschreibung
- **Projekt-/Rechnungszuordnung**: Verknüpfung mit Projekten oder Rechnungen
- **Kategorisierung**: Material, Personal, Dienstleistung, Sonstiges
- **Ausgabenberichte**: Auswertung nach Projekt/Zeitraum
- **Kostenanalyse**: Projekt-Profitabilität

### API-Endpunkte
```
# CRUD
GET    /api/backoffice/finance/expenses     → Alle Ausgaben (mit Pagination & Filtern)
GET    /api/backoffice/finance/expenses/:id → Einzelne Ausgabe
POST   /api/backoffice/finance/expenses     → Neue Ausgabe
PATCH  /api/backoffice/finance/expenses/:id → Ausgabe aktualisieren
DELETE /api/backoffice/finance/expenses/:id → Ausgabe löschen

# STATISTICS
GET    /api/backoffice/finance/expenses/kpis → KPI-Dashboard (Gesamt, Kategorien, Trends)

# FILTER-PARAMETER
# - title (string)
# - category (material|personnel|service|other)
# - project_id (UUID)
# - invoice_id (UUID)
# - from_date / to_date (date range)
# - limit / offset (pagination)
```

### Datenmodell
```typescript
interface Expense {
  id: string;
  project_id: string | null;
  invoice_id: string | null;
  category: "material" | "personnel" | "service" | "other";
  amount: number;
  note: string | null;
  created_at: string;
  updated_at: string;
}
```

### Status
✅ **Vollständig** - Backend + Frontend implementiert
- Backend: `backend/app/modules/backoffice/finance/` ✅
- Frontend: `ui/src/modules/expenses/` + `ui/src/modules/finance/` ✅
  - **Expenses-Modul:**
    - ExpensesDashboardPage.vue
    - ExpensesListPage.vue (mit Filtern)
    - ExpenseFormPage.vue
  - **Finance-Modul:**
    - FinanceDashboardPage.vue (Übersicht)
- **Backend Features:**
  - ✅ KPI-Dashboard (Gesamt, pro Kategorie, Trends)
  - ✅ Multi-Filter (Titel, Kategorie, Projekt, Rechnung, Datumsbereich)
  - ✅ Pagination
  - ✅ Kategorie-basierte Auswertungen
- Files: `routes.py`, `crud.py`, `schemas.py`, `models.py`

---

## 7. Projekt-Chat

### Beschreibung
Projektbezogene Team-Kommunikation mit Nachrichtenverlauf.

### Hauptfunktionen
- **Projektkommunikation**: Chat-Nachrichten pro Projekt
- **Nachrichtenverlauf**: Chronologische Anzeige
- **Team-Benachrichtigungen**: Bei neuen Nachrichten
- **Dateien teilen**: Anhänge zu Nachrichten (über Documents-Modul)
- **Echtzeit-Updates**: WebSocket-basiert

### API-Endpunkte
```
# REST API
GET    /api/backoffice/chat/projects/:project_id/messages → Nachrichten eines Projekts (Pagination)
POST   /api/backoffice/chat/projects/:project_id/messages → Neue Nachricht (mit Broadcast)

# WEBSOCKET (Echtzeit)
WS     /api/backoffice/chat/ws/projects/:project_id → WebSocket-Verbindung

# PARAMETER
# - limit (default: 50, max: 200)
# - offset (default: 0)

# WEBSOCKET EVENTS
# - "new_message" → Broadcast wenn neue Nachricht erstellt wird
# - "pong" → Echo-Response für Keep-Alive
```

### Datenmodell
```typescript
interface ChatMessage {
  id: string;
  project_id: string;
  author_id: string;
  message: string;
  created_at: string;
}
```

### Status
✅ **Backend Ready** - WebSocket-basiertes Echtzeit-Chat implementiert!
- Backend: `backend/app/modules/backoffice/chat/` ✅
- Frontend: ⏳ Geplant für Phase 2.4
- **Features:**
  - ✅ **WebSocket-Support** mit Connection Manager
  - ✅ **Broadcast-System** (neue Nachrichten an alle Clients)
  - ✅ REST-API für Nachrichtenverlauf (Pagination)
  - ✅ Auto-Connect/Disconnect-Management
  - ✅ Pro-Projekt-Channels
- Files: `routes.py`, `crud.py`, `schemas.py`, `models.py`
- **Implementation:** ConnectionManager mit Dict[project_id, Set[WebSocket]]

---

## Core-Module (Shared)

Diese Module werden von allen Backoffice-Modulen verwendet:

### Employees (Mitarbeiter)
- Mitarbeiterstammdaten
- Rollen- und Abteilungszuordnung
- Siehe: [Core-Dokumentation](../core/entities.md)

### Departments (Abteilungen)
- Abteilungsstruktur
- Manager-Zuordnung
- Siehe: [Core-Dokumentation](../core/entities.md)

### Roles (Rollen)
- Rollenverwaltung
- Berechtigungen (JSON)
- Siehe: [Backend-Dokumentation](../backend/MODULE_UEBERSICHT.md)

### Documents (Dokumente)
- Dokumentenverwaltung
- Polymorphe Verknüpfung mit allen Modulen
- Siehe: [Core-Dokumentation](../core/entities.md)

### Reminders (Erinnerungen)
- Aufgaben & Erinnerungen
- Fälligkeitsdatum & Priorität
- Siehe: [Core-Dokumentation](../core/entities.md)

### Dashboards (Dashboards)
- Benutzerspezifische Layouts
- Widget-Konfiguration
- Siehe: [Core-Dokumentation](../core/entities.md)

---

## Modul-Integration

### Typischer Workflow

```
1. Kunde anlegen (CRM)
   ↓
2. Projekt erstellen & Kunde zuordnen (Projektmanagement)
   ↓
3. Zeit auf Projekt buchen (Zeiterfassung)
   ↓
4. Rechnung aus Zeiteinträgen generieren (Rechnungsmanagement)
   ↓
5. Zahlungseingang erfassen (Zahlungsmanagement)
   ↓
6. Ausgaben für Projekt erfassen (Ausgabenverwaltung)
   ↓
7. Projekt-Kommunikation (Chat)
```

### Datenfluss-Diagramm

```
┌──────────┐     ┌──────────┐     ┌─────────────┐
│   CRM    │────→│ Projekte │────→│Zeiterfassung│
│(Kunden)  │     │          │     │             │
└──────────┘     └──────────┘     └─────────────┘
                       │                  │
                       ↓                  ↓
                 ┌──────────┐      ┌──────────┐
                 │Rechnungen│←─────│Ausgaben  │
                 │          │      │          │
                 └──────────┘      └──────────┘
                       │
                       ↓
                 ┌──────────┐
                 │Zahlungen │
                 │          │
                 └──────────┘
```

---

## Technische Details

### Backend (FastAPI)
```
backend/src/modules/backoffice/
├── crm/
│   ├── router.py           # API-Endpunkte
│   ├── service.py          # Business Logic
│   ├── models.py           # SQLAlchemy Models
│   └── schemas.py          # Pydantic Schemas
├── projects/
├── time_tracking/
├── invoices/
├── payments/
├── expenses/
└── chat/
```

### Frontend (Vue 3)
```
ui/src/modules/
├── crm/                    # ✅ Implementiert
├── projects/               # 🔄 In Arbeit
├── time-tracking/          # ⏳ Geplant
├── invoices/               # ⏳ Geplant
├── payments/               # ⏳ Geplant
├── expenses/               # ⏳ Geplant
└── chat/                   # ⏳ Geplant
```

---

## Roadmap

### Phase 2.1 (✅ KOMPLETT ABGESCHLOSSEN!)
- ✅ **CRM** - Live in Produktion (Backend + Frontend)
- ✅ **Projekte** - Vollständig implementiert (Backend + Frontend)
- ✅ **Zeiterfassung** - Vollständig implementiert (Backend + Frontend)
- ✅ **Rechnungen** - Vollständig implementiert (Backend + Frontend mit PDF!)
- ✅ **Zahlungen** - Vollständig implementiert (in Invoices integriert)
- ✅ **Ausgaben/Finance** - Vollständig implementiert (Backend + Frontend)
- ✅ **Projekt-Chat Backend** - Vollständig implementiert (WebSocket!)

### Phase 2.2 (Aktuell)
- 🔄 **Projekt-Chat Frontend** - Nächste Priorität (WebSocket-Integration)
- ⏳ **Reporting & Analytics** - Geplant

### Phase 2.3 (Q2 2026)
- ⏳ **Advanced Features & Optimierungen**
- ⏳ **Mobile-Optimierung**

### Phase 2.4 (Q3 2026)
- ⏳ **AI-Features & Automatisierung**
- ⏳ **Advanced Reporting**

**🎉 Status: Backend & Frontend zu 100% fertig (außer Chat-Frontend)!**
**Nur noch fehlt: Projekt-Chat Frontend (alle anderen Module sind ready)**

---

**Letzte Aktualisierung**: 30. Dezember 2025
