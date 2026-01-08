---
layout: default
title: Phase 4 HR Implementation Plan
parent: Roadmap
nav_order: 7
---

# Phase 4: HR Module - Implementierungsplan

**Status:** 20% Complete
**Zeitraum:** Januar 2026 - Februar 2026
**Ziel:** Vollständiges HR-Modul mit Leave Management, Recruiting, Onboarding und Analytics

---

## Executive Summary

Das HR-Modul befindet sich aktuell bei **20% Fertigstellung**. Die Grundstruktur und das Leave Management System sind implementiert, aber Frontend-Integration, weitere Submodule und Dokumentation fehlen noch.

**Abgeschlossen (v3.0.1 - 2026-01-08):**
- ✅ HR-Modul-Grundstruktur
- ✅ Leave Management Backend (Models, Schemas, CRUD, Routes)
- ✅ Database Migrations (Employees, Leave Requests, Leave Balances)
- ✅ HR-Rollen (hr_admin, hr_manager, hr_recruiter)
- ✅ Backend-Integration in main.py

**Geschätzter Restaufwand:** 40-50 Stunden
**Geschätzte Dauer:** 2-3 Wochen

---

## Aktueller Stand (20%)

### ✅ Bereits implementiert (v3.0.1)

#### 1. HR-Modul-Struktur (100%)
```
backend/app/modules/hr/
  ├── leave/              # ✅ Leave Management vollständig
  │   ├── models.py       # Employee, LeaveRequest, LeaveBalance
  │   ├── schemas.py      # Pydantic Schemas
  │   ├── crud.py         # CRUD Operations
  │   ├── routes.py       # FastAPI Router
  │   └── __init__.py
  ├── recruiting/         # 🔲 Platzhalter
  ├── onboarding/         # 🔲 Platzhalter
  ├── training/           # 🔲 Platzhalter
  ├── compensation/       # 🔲 Platzhalter
  ├── documents/          # 🔲 Platzhalter
  ├── analytics/          # 🔲 Platzhalter
  ├── permissions.py      # ✅ HR Permission Helpers
  ├── enums.py            # ✅ HR Enums (LeaveType, LeaveStatus, etc.)
  ├── utils.py            # ✅ HR Utility Functions
  └── __init__.py         # ✅ Main Router
```

#### 2. Database Migrations (100%)
- ✅ `2026_01_08_1556-a8904a298e14_add_hr_leave_management_module.py`
- ✅ `2026_01_08_1611-578d03552aae_add_hr_leave_management_tables_complete.py`

**Tabellen:**
- `hr_employees` - Mitarbeiter-Stammdaten
- `hr_leave_requests` - Urlaubsanträge
- `hr_leave_balances` - Urlaubskontingente

#### 3. HR-Rollen & Permissions (100%)
```python
# backend/app/core/auth/roles.py
ROLE_ALIASES = {
    "hr.admin": "hr_admin",        # Vollzugriff auf HR-Modul
    "hr.manager": "hr_manager",    # Genehmigungen & Übersichten
    "hr.recruiter": "hr_recruiter" # Recruiting & Onboarding
}
```

#### 4. Leave Management Backend (100%)

**Models:**
- `Employee` - Mitarbeiter-Daten (Name, Email, Department, Hire Date)
- `LeaveRequest` - Urlaubsanträge (Type, Start, End, Status, Reason)
- `LeaveBalance` - Urlaubskontingente (Year, Type, Total, Used, Available)

**API Endpoints:**
- `POST /api/hr/employees` - Mitarbeiter anlegen
- `GET /api/hr/employees` - Mitarbeiter auflisten
- `GET /api/hr/employees/{id}` - Mitarbeiter abrufen
- `PUT /api/hr/employees/{id}` - Mitarbeiter aktualisieren
- `DELETE /api/hr/employees/{id}` - Mitarbeiter löschen
- `POST /api/hr/leave-requests` - Urlaubsantrag erstellen
- `GET /api/hr/leave-requests` - Urlaubsanträge auflisten
- `PUT /api/hr/leave-requests/{id}` - Antrag aktualisieren
- `GET /api/hr/leave-balances` - Urlaubskontingente abrufen

#### 5. Version & Integration (100%)
- ✅ Version auf 3.0.1 erhöht (backend + ui)
- ✅ HR Router in `main.py` registriert
- ✅ Import-Pfade in Core-Modulen korrigiert

**Commit:** `3cc546d` - feat(hr): Add HR Leave Management Module (v3.0.1)

---

## Was fehlt noch? (80%)

### 1. HR Frontend (0%) - **PRIORITÄT HOCH**

**Status:** Komplett fehlend

**Was fehlt:**
- ❌ Vue-Module-Struktur für HR
- ❌ HR Dashboard Page
- ❌ Leave Management UI (Anträge, Genehmigungen, Übersicht)
- ❌ Employee Management UI
- ❌ API-Integration mit Backend
- ❌ HR Navigation in DockNav

**Geplante Struktur:**
```
ui/src/modules/hr/
  ├── pages/
  │   ├── HRDashboard.vue          # Übersicht
  │   ├── LeaveManagement.vue      # Urlaubsverwaltung
  │   ├── LeaveRequestForm.vue     # Antrag erstellen
  │   ├── LeaveApprovals.vue       # Genehmigungen (Manager)
  │   ├── EmployeeList.vue         # Mitarbeiter-Übersicht
  │   └── EmployeeDetails.vue      # Mitarbeiter-Details
  ├── components/
  │   ├── LeaveRequestCard.vue
  │   ├── LeaveBalanceWidget.vue
  │   ├── EmployeeCard.vue
  │   └── LeaveCalendar.vue
  └── api/
      └── hrApi.ts                 # API-Client für HR-Modul
```

**Implementierungs-Schritte:**

1. **HR Dashboard erstellen**
   - Übersicht über Urlaubsanträge (eigene + Team)
   - Urlaubskalender-Widget
   - Quick Actions (Antrag erstellen, Genehmigungen)
   - Urlaubskontingent-Anzeige

2. **Leave Management UI**
   - Formular für neue Urlaubsanträge
   - Liste aller Anträge (mit Filter: Status, Type, Date Range)
   - Detail-View für Anträge
   - Genehmigen/Ablehnen-Funktion (für Manager)

3. **Employee Management UI**
   - Tabelle mit Mitarbeiter-Liste
   - Suchfunktion
   - CRUD-Funktionen (nur für hr_admin)
   - Employee-Detail-Page mit Urlaubshistorie

4. **HR API Client**
   ```typescript
   // ui/src/modules/hr/api/hrApi.ts
   export const hrApi = {
     // Employees
     getEmployees: () => apiClient.get('/api/hr/employees'),
     getEmployee: (id: string) => apiClient.get(`/api/hr/employees/${id}`),
     createEmployee: (data: EmployeeCreate) => apiClient.post('/api/hr/employees', data),
     updateEmployee: (id: string, data: EmployeeUpdate) => apiClient.put(`/api/hr/employees/${id}`, data),
     deleteEmployee: (id: string) => apiClient.delete(`/api/hr/employees/${id}`),

     // Leave Requests
     getLeaveRequests: (filters?: LeaveFilters) => apiClient.get('/api/hr/leave-requests', { params: filters }),
     createLeaveRequest: (data: LeaveRequestCreate) => apiClient.post('/api/hr/leave-requests', data),
     updateLeaveRequest: (id: string, data: LeaveRequestUpdate) => apiClient.put(`/api/hr/leave-requests/${id}`, data),
     approveLeaveRequest: (id: string) => apiClient.post(`/api/hr/leave-requests/${id}/approve`),
     rejectLeaveRequest: (id: string, reason: string) => apiClient.post(`/api/hr/leave-requests/${id}/reject`, { reason }),

     // Leave Balances
     getLeaveBalances: (employeeId?: string) => apiClient.get('/api/hr/leave-balances', { params: { employee_id: employeeId } }),
   };
   ```

5. **Navigation aktualisieren**
   ```typescript
   // ui/src/components/DockNav.vue
   const menuItems = [
     // ...
     {
       name: 'HR',
       icon: 'mdi-account-multiple',
       route: '/hr',
       permission: 'hr.*'
     }
   ];
   ```

**Zeitaufwand:** 15-20 Stunden

---

### 2. Recruiting Submodul (0%) - **PRIORITÄT MITTEL**

**Status:** Nur Platzhalter vorhanden

**Ziel:** Bewerbungsmanagement-System

**Geplante Features:**
- Job Postings (Stellenausschreibungen)
- Applicants (Bewerber)
- Application Process (Bewerbungsprozess)
- Interview Scheduling (Terminplanung)
- Offer Management (Vertragsangebote)

**Datenbank-Schema:**
```sql
hr_job_postings (
  id UUID PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  department_id UUID REFERENCES departments(id),
  description TEXT,
  requirements TEXT,
  location VARCHAR(100),
  employment_type VARCHAR(50), -- full-time, part-time, contract
  salary_range VARCHAR(100),
  status VARCHAR(50), -- draft, published, closed
  published_at TIMESTAMP,
  closed_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

hr_applicants (
  id UUID PRIMARY KEY,
  job_posting_id UUID REFERENCES hr_job_postings(id),
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  resume_url VARCHAR(500), -- Link zu CV/Lebenslauf
  cover_letter TEXT,
  status VARCHAR(50), -- applied, screening, interview, offer, hired, rejected
  applied_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

hr_interviews (
  id UUID PRIMARY KEY,
  applicant_id UUID REFERENCES hr_applicants(id),
  interviewer_id UUID REFERENCES hr_employees(id),
  scheduled_at TIMESTAMP,
  duration_minutes INT,
  location VARCHAR(200), -- office, video, phone
  notes TEXT,
  rating INT, -- 1-5
  status VARCHAR(50), -- scheduled, completed, cancelled
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

**API Endpoints:**
```
POST   /api/hr/recruiting/job-postings
GET    /api/hr/recruiting/job-postings
GET    /api/hr/recruiting/job-postings/{id}
PUT    /api/hr/recruiting/job-postings/{id}
DELETE /api/hr/recruiting/job-postings/{id}

POST   /api/hr/recruiting/applicants
GET    /api/hr/recruiting/applicants
GET    /api/hr/recruiting/applicants/{id}
PUT    /api/hr/recruiting/applicants/{id}
DELETE /api/hr/recruiting/applicants/{id}

POST   /api/hr/recruiting/interviews
GET    /api/hr/recruiting/interviews
PUT    /api/hr/recruiting/interviews/{id}
```

**Zeitaufwand:** 10-12 Stunden (Backend + Frontend)

---

### 3. Onboarding Submodul (0%) - **PRIORITÄT NIEDRIG**

**Status:** Nur Platzhalter vorhanden

**Ziel:** Onboarding-Prozess für neue Mitarbeiter

**Geplante Features:**
- Onboarding Checklists
- Document Collection (Verträge, Formulare)
- Equipment Assignment (Laptop, Handy, etc.)
- Training Assignments
- Buddy System

**Zeitaufwand:** 8-10 Stunden

---

### 4. Analytics Submodul (0%) - **PRIORITÄT NIEDRIG**

**Status:** Nur Platzhalter vorhanden

**Ziel:** HR-Kennzahlen und Reports

**Geplante Features:**
- Mitarbeiter-Statistiken (Headcount, Turnover)
- Urlaubsstatistiken (Usage, Patterns)
- Recruiting Metrics (Time to Hire, Application Funnel)
- Attendance Reports
- Export zu PDF/Excel

**Zeitaufwand:** 6-8 Stunden

---

### 5. HR Dokumentation (0%) - **PRIORITÄT HOCH**

**Status:** Komplett fehlend

**Was fehlt:**
- ❌ Wiki-Seiten für HR-Modul
- ❌ API-Dokumentation
- ❌ Flow-Diagramme (Mermaid)
- ❌ ERM-Diagramm (DBML)
- ❌ User Guide

**Geplante Struktur:**
```
docs/wiki/hr/
  ├── README.md                # HR-Modul-Übersicht
  ├── entities.md              # Datenmodell-Dokumentation
  ├── flows.md                 # Prozess-Flows (Mermaid)
  ├── hr_erm.md                # ERM-Diagramm
  ├── api_endpoints.md         # API-Referenz
  ├── leave_management.md      # Leave Management Guide
  ├── recruiting.md            # Recruiting Guide
  └── permissions.md           # HR-Berechtigungen
```

**Zeitaufwand:** 4-6 Stunden

---

## Implementierungs-Reihenfolge

### Phase 4.1: Frontend Foundation (Woche 1-2)

**Priorität: KRITISCH**

1. **Tag 1-2: HR Dashboard & Navigation** (8h)
   - HR-Modul in Vue Router einbinden
   - HR Dashboard Page erstellen
   - Navigation in DockNav hinzufügen
   - API-Client aufsetzen

2. **Tag 3-4: Leave Management UI** (10h)
   - LeaveRequestForm.vue - Antrag erstellen
   - LeaveManagement.vue - Anträge anzeigen
   - LeaveApprovals.vue - Genehmigungen (Manager)
   - API-Integration testen

3. **Tag 5: Employee Management UI** (6h)
   - EmployeeList.vue - Mitarbeiter-Tabelle
   - EmployeeDetails.vue - Detail-Page
   - CRUD-Funktionen implementieren

**Deliverables:**
- ✅ Funktionales HR-Frontend
- ✅ Leave Management vollständig nutzbar
- ✅ Employee Management vollständig nutzbar

---

### Phase 4.2: Recruiting & Dokumentation (Woche 3)

**Priorität: MITTEL**

1. **Tag 1-2: Recruiting Backend** (8h)
   - Models für Job Postings, Applicants, Interviews
   - Alembic Migration erstellen
   - CRUD-Services implementieren
   - API-Router erstellen

2. **Tag 3: Recruiting Frontend** (6h)
   - Job Postings UI
   - Applicants UI
   - Interview Scheduling

3. **Tag 4: HR Dokumentation** (6h)
   - Wiki-Seiten erstellen
   - API-Dokumentation schreiben
   - Flow-Diagramme (Mermaid)
   - ERM-Diagramm (DBML)

**Deliverables:**
- ✅ Recruiting-Modul funktional
- ✅ Vollständige HR-Dokumentation

---

### Phase 4.3: Onboarding, Analytics & Testing (Optional)

**Priorität: NIEDRIG**

Kann auf Phase 5 verschoben werden, falls Zeit knapp wird.

1. **Onboarding Submodul** (8-10h)
2. **Analytics Submodul** (6-8h)
3. **End-to-End Testing** (4h)
4. **Performance-Optimierung** (2h)

---

## Testing-Checkliste

### Leave Management

- [ ] Mitarbeiter können Urlaubsantrag erstellen
- [ ] Manager können Anträge genehmigen/ablehnen
- [ ] Urlaubskontingente werden korrekt berechnet
- [ ] Überschneidungen werden erkannt
- [ ] Email-Benachrichtigungen bei Statusänderungen
- [ ] Filterung & Suche funktioniert
- [ ] Pagination funktioniert

### Employee Management

- [ ] CRUD-Operationen funktionieren
- [ ] Suche & Filterung funktioniert
- [ ] Berechtigungen werden korrekt geprüft
- [ ] Mitarbeiter-Details werden korrekt angezeigt
- [ ] Urlaubshistorie wird angezeigt

### Recruiting

- [ ] Job Postings können erstellt/bearbeitet werden
- [ ] Bewerbungen können erfasst werden
- [ ] Interviews können geplant werden
- [ ] Bewerbungsstatus kann aktualisiert werden
- [ ] Benachrichtigungen funktionieren

### Permissions

- [ ] `hr_admin` hat vollen Zugriff
- [ ] `hr_manager` kann Anträge genehmigen
- [ ] `hr_recruiter` hat Zugriff auf Recruiting
- [ ] Normale User sehen nur ihre eigenen Daten
- [ ] Wildcard-Permissions funktionieren (`hr.*`)

---

## Risiken & Mitigationen

### Risiko 1: Komplexität der Urlaubsberechnung

**Problem:** Urlaubsberechnung ist komplex (gesetzliche Feiertage, Wochenenden, Übertrag)

**Mitigation:**
- Zunächst einfache Berechnung (Tage zwischen Start und End)
- Später: Integration mit Feiertags-API (z.B. Nager.Date)
- Konfigurierbare Berechnungsregeln in System Settings

### Risiko 2: Email-Benachrichtigungen

**Problem:** Email-System noch nicht vollständig implementiert

**Mitigation:**
- Phase 4.1: Email-Benachrichtigungen optional (In-App-Benachrichtigungen)
- Phase 4.2: SMTP-Integration hinzufügen
- Fallback: Benachrichtigungen im System anzeigen

### Risiko 3: Performance bei vielen Mitarbeitern

**Problem:** Große Firmen haben 100+ Mitarbeiter

**Mitigation:**
- Effiziente Indizes auf häufig abgefragte Spalten
- Pagination mit max. 50 Einträgen pro Seite
- Lazy Loading für Employee-Details
- Caching für häufig abgerufene Daten

---

## Erfolgskriterien

Phase 4 gilt als abgeschlossen, wenn:

- [x] HR-Modul-Grundstruktur existiert
- [x] Leave Management Backend ist implementiert
- [x] Database Migrations sind vorhanden
- [x] HR-Rollen sind registriert
- [ ] **HR Frontend ist vollständig implementiert**
- [ ] **Leave Management ist vollständig nutzbar**
- [ ] **Employee Management ist vollständig nutzbar**
- [ ] **Recruiting Submodul ist implementiert**
- [ ] **HR-Dokumentation ist vollständig**
- [ ] **Tests sind geschrieben und bestehen**

---

## Dokumentations-Updates

Nach Abschluss von Phase 4:

1. **docs/roadmap/README.md**
   - Phase 4 Status auf 100% setzen

2. **docs/roadmap/phase_core_to_hr.md**
   - Phase 3 als abgeschlossen markieren
   - Phase 4 & 5 Status aktualisieren

3. **docs/wiki/hr/**
   - Alle Wiki-Seiten erstellen
   - API-Dokumentation hinzufügen

4. **Daily Report erstellen**
   - `docs/daily_reports/2026-01-XX_phase4_hr_completion.md`

---

## Ausblick: Phase 5 - HR Advanced Features

Nach Abschluss von Phase 4 folgt **Phase 5: HR Advanced Features** (Q2 2026).

**Geplante Features:**

1. **Performance Management**
   - Performance Reviews (Mitarbeitergespräche)
   - Goal Setting (Zielvereinbarungen)
   - 360° Feedback

2. **Training & Development**
   - Training Catalog
   - Course Assignments
   - Certifications Management
   - Skill Matrix

3. **Compensation Management**
   - Salary Management
   - Bonus Calculations
   - Raise Requests
   - Payroll Export

4. **Time Tracking**
   - Clock In/Out
   - Timesheet Management
   - Overtime Tracking
   - Integration mit Leave Management

5. **Employee Self-Service**
   - Personal Data Management
   - Document Downloads (Payslips, Contracts)
   - Absence Calendar
   - Team Directory

**Geschätzter Aufwand Phase 5:** 6-8 Wochen

---

## Zusammenfassung

**Phase 4 HR Module Plan:**
- ✅ 20% bereits fertig (Backend-Grundstruktur, Leave Management Backend)
- 🔄 80% verbleibend (Frontend, Recruiting, Dokumentation)
- ⏱️ Geschätzter Aufwand: 40-50 Stunden
- 📅 Geschätzte Dauer: 2-3 Wochen
- 🎯 Ziel: Vollständig nutzbares HR-Modul mit Leave Management & Recruiting

**Prioritäten:**
1. **HR Frontend** (KRITISCH - ohne Frontend ist Backend nutzlos)
2. **HR Dokumentation** (HOCH - wichtig für Adoption)
3. **Recruiting Submodul** (MITTEL - kann verschoben werden)
4. **Onboarding & Analytics** (NIEDRIG - Nice-to-have)

**Nächste Schritte:**
1. Mit Phase 4.1 starten (HR Frontend Foundation)
2. Leave Management vollständig nutzbar machen
3. Employee Management UI fertigstellen
4. Recruiting-Modul implementieren
5. Dokumentation schreiben
6. Testing & Integration
7. Phase 4 als abgeschlossen markieren
8. Release v3.1 vorbereiten

---

**Erstellt:** 08. Januar 2026
**Autor:** Claude Code & Joshua Phu Kuhrau
**Version:** 1.0
**Status:** In Progress (20% Complete)

**Letzter Commit:** `3cc546d` - feat(hr): Add HR Leave Management Module (v3.0.1)

🚀 **Let's build the HR Module!**
