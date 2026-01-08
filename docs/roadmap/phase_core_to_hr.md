---
layout: default
title: Phase Core to HR
parent: Roadmap
nav_order: 1
---

# 🧭 Workmate OS – Phaseplan: Core → HR

> Ziel: Erweiterung des bestehenden Core-Systems um das **HR-Modul**,
> inklusive Datenmodell, API-Struktur, UI-Komponenten und Dokumentation.

**Letztes Update:** 08. Januar 2026 (v3.0.1)
**Aktueller Stand:** Phase 3 ✅ | Phase 4 🔄 (20%)

📄 **Detaillierter Implementierungsplan:** [phase4_hr_implementation_plan.md](./phase4_hr_implementation_plan.md)

---

## 🧩 Phase 1 – Core Finalisierung (Status: ✅ Abgeschlossen)

**Ziele:**
- [x] Core-Datenmodell (DBML + Entities)
- [x] Infrastruktur & Reverse Proxy (Caddy, Cloudflare)
- [x] Health Checks (`/system/health`)
- [x] Core-Dokumentation & Wiki-Struktur
- [x] Core-Flows (Mermaid Diagramme)
- [x] ERM validiert und in dbdiagram.io eingebunden

**Deliverables:**
- `/docs/wiki/core/*`
- `/docs/core_erm.dbml`
- `backend/app/modules/core/*`
- `ui/src/modules/core/*`

---

## 🧠 Phase 2 – HR-Konzept (Status: ✅ Abgeschlossen)

**Ziele:**
- [x] Definition der HR-Prozesse:
  - [x] Urlaub (Leave Requests)
  - [x] Krankmeldungen (Sick Notes)
  - [x] Bewerbungen (Applications)
  - [x] Teamkalender / Ressourcenübersicht
- [x] Definition der Beziehungen zum Core:
  - `Employee ↔ LeaveRequest`
  - `Employee ↔ SickNote`
  - `Document ↔ SickNote`
- [x] HR-Modul-Struktur definiert
- [x] HR-Rollen-System entworfen

**Deliverables:**
- [x] HR-Modul-Architektur
- [x] Database Schema (Employees, Leave Requests, Leave Balances)
- [x] Submodule identifiziert (Leave, Recruiting, Onboarding, etc.)

---

## 🧱 Phase 3 – HR-Datenmodell (Status: ✅ Abgeschlossen - v3.0.1)

**Ziele:**
- [x] Tabellen: `hr_employees`, `hr_leave_requests`, `hr_leave_balances`
- [x] Modelle + Schemas im Backend:
  ```
  backend/app/modules/hr/
    ├── leave/
    │   ├── models.py       # Employee, LeaveRequest, LeaveBalance
    │   ├── schemas.py      # Pydantic Schemas
    │   ├── crud.py         # CRUD Operations
    │   ├── routes.py       # FastAPI Router
    │   └── __init__.py
    ├── permissions.py      # HR Permission Helpers
    ├── enums.py           # HR Enums
    ├── utils.py           # Utility Functions
    └── __init__.py        # Main Router
  ```
- [x] HR-Rollen implementiert (`hr_admin`, `hr_manager`, `hr_recruiter`)
- [x] FastAPI-Routen (CRUD)
  - `/api/hr/employees`
  - `/api/hr/leave-requests`
  - `/api/hr/leave-balances`

**Deliverables:**
- [x] 2 Alembic-Migrationen (2026-01-08)
- [x] HR-Modul-Struktur mit Submodulen
- [x] Version auf 3.0.1 erhöht

**Commit:** `3cc546d` - feat(hr): Add HR Leave Management Module (v3.0.1)
**Details:** Siehe `/docs/roadmap/phase4_hr_implementation_plan.md`

---

## 🖥 Phase 4 – HR-Frontend & Submodule (Status: 🔄 In Progress - 20%)

**Ziele:**
- [x] Backend-Grundstruktur (v3.0.1)
- [ ] Vue-Module-Struktur:
  ```
  ui/src/modules/hr/
    ├── pages/
    │   ├── HRDashboard.vue
    │   ├── LeaveManagement.vue
    │   ├── EmployeeList.vue
    │   └── EmployeeDetails.vue
    └── components/
        ├── LeaveRequestCard.vue
        ├── LeaveBalanceWidget.vue
        └── EmployeeCard.vue
  ```
- [ ] HR-Dashboard Integration
- [ ] API-Integration über `hrApi`
- [ ] Recruiting Submodul (Backend + Frontend)

**Deliverables:**
- [x] Backend-Struktur & Migrations
- [ ] `ui/src/modules/hr/*`
- [ ] API-Anbindung getestet
- [ ] Recruiting-Modul implementiert

**Status:** 20% Complete (nur Backend)
**Details:** Siehe `/docs/roadmap/phase4_hr_implementation_plan.md`

---

## 🧩 Phase 5 – HR-Dokumentation & Advanced Features

**Ziele:**
- [ ] Wiki-Seiten:
  ```
  docs/wiki/hr/
    ├── README.md
    ├── entities.md
    ├── flows.md
    ├── hr_erm.md
    ├── api_endpoints.md
    ├── leave_management.md
    ├── recruiting.md
    └── permissions.md
  ```
- [ ] Flow-Diagramme (Mermaid)
- [ ] ERM-Diagramm (DBML)
- [ ] Advanced Features:
  - [ ] Onboarding Submodul
  - [ ] Training & Development
  - [ ] Compensation Management
  - [ ] Analytics & Reporting

**Deliverables:**
- [ ] Vollständige HR-Dokumentation
- [ ] Flow-Diagramme in Mermaid + DBML
- [ ] Advanced Submodule implementiert

**Status:** Geplant für Q2 2026

---

## ⚙️ Phase 6 – Integration, Testing & Production

**Ziele:**
- [ ] End-to-End-Tests: Core + HR
- [ ] Zugriffskontrolle über Zitadel (HR-spezifische Rollen)
- [ ] Email-Benachrichtigungen:
  - Urlaubsantrag genehmigt/abgelehnt
  - Erinnerungen für auslaufende Urlaube
- [ ] Performance-Optimierung
- [ ] Security Audit

**Deliverables:**
- [ ] Integrationstests (`tests/test_hr_integration.py`)
- [ ] API Health Check `/api/hr/health`
- [ ] Production-Ready HR-Modul
- [ ] Release v3.2 oder v4.0

**Status:** Geplant für Q2 2026

---

## 🚀 Gesamtziel

> Vollständig funktionales HR-Modul als erste Erweiterung des Core-Systems  
> inklusive DBML, API, UI, Doku, und interner Integration in Keycloak.
