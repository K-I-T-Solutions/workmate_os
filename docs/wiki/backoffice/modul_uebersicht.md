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
🔄 **In Entwicklung** - Backend teilweise implementiert, Frontend geplant

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
⏳ **Geplant** - Phase 2 Roadmap

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
GET    /api/backoffice/invoices             → Alle Rechnungen
GET    /api/backoffice/invoices/:id         → Einzelne Rechnung
POST   /api/backoffice/invoices             → Neue Rechnung
PUT    /api/backoffice/invoices/:id         → Rechnung aktualisieren
DELETE /api/backoffice/invoices/:id         → Rechnung löschen
GET    /api/backoffice/invoices/:id/pdf     → PDF herunterladen
POST   /api/backoffice/invoices/:id/send    → Rechnung versenden
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
⏳ **Geplant** - Phase 2 Roadmap

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
GET    /api/backoffice/payments             → Alle Zahlungen
GET    /api/backoffice/payments/:id         → Einzelne Zahlung
POST   /api/backoffice/payments             → Neue Zahlung
PUT    /api/backoffice/payments/:id         → Zahlung aktualisieren
DELETE /api/backoffice/payments/:id         → Zahlung löschen
GET    /api/backoffice/payments/by-invoice/:id → Nach Rechnung
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
⏳ **Geplant** - Phase 2 Roadmap

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
GET    /api/backoffice/expenses             → Alle Ausgaben
GET    /api/backoffice/expenses/:id         → Einzelne Ausgabe
POST   /api/backoffice/expenses             → Neue Ausgabe
PUT    /api/backoffice/expenses/:id         → Ausgabe aktualisieren
DELETE /api/backoffice/expenses/:id         → Ausgabe löschen
GET    /api/backoffice/expenses/by-project/:id → Nach Projekt
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
⏳ **Geplant** - Phase 2 Roadmap

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
GET    /api/backoffice/chat/messages/:project_id  → Nachrichten eines Projekts
POST   /api/backoffice/chat/messages              → Neue Nachricht
DELETE /api/backoffice/chat/messages/:id          → Nachricht löschen
WS     /api/backoffice/chat/ws/:project_id        → WebSocket-Verbindung
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
⏳ **Geplant** - Phase 2 Roadmap

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

### Phase 2.1 (Q1 2026)
- ✅ CRM-Modul (Abgeschlossen)
- 🔄 Projektmanagement (In Arbeit)

### Phase 2.2 (Q2 2026)
- ⏳ Zeiterfassung
- ⏳ Rechnungsmanagement

### Phase 2.3 (Q3 2026)
- ⏳ Zahlungsmanagement
- ⏳ Ausgabenverwaltung

### Phase 2.4 (Q4 2026)
- ⏳ Projekt-Chat
- ⏳ Reporting & Analytics

---

**Letzte Aktualisierung**: 30. Dezember 2025
