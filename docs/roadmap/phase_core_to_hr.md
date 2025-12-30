---
layout: default
title: Phase Core to HR
parent: Roadmap
nav_order: 1
---

# 🧭 Workmate OS – Phaseplan: Core → HR

> Ziel: Erweiterung des bestehenden Core-Systems um das **HR-Modul**,
> inklusive Datenmodell, API-Struktur, UI-Komponenten und Dokumentation.

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

## 🧠 Phase 2 – HR-Konzept (Geplant: Montag–Dienstag nächste Woche)

**Ziele:**
- Definition der HR-Prozesse:
  - Urlaub (Leave Requests)
  - Krankmeldungen (Sick Notes)
  - Bewerbungen (Applications)
  - Teamkalender / Ressourcenübersicht
- Definition der Beziehungen zum Core:
  - `Employee ↔ LeaveRequest`
  - `Employee ↔ SickNote`
  - `Document ↔ SickNote`
- Erstellung eines **HR-Blueprints** (analog zu `architecture_blueprint.md`)
- Diagramm: **HR Data Flow** (Mermaid)
- ERM: **hr_erm.dbml**

**Deliverables:**
- `/docs/wiki/hr/README.md`
- `/docs/wiki/hr/hr_erm.md`
- `/docs/wiki/hr/flows.md`

---

## 🧱 Phase 3 – HR-Datenmodell (Woche 44)

**Ziele:**
- Tabellen: `leave_requests`, `sick_notes`, `applications`
- Modelle + Schemas im Backend:
  ```
  backend/app/modules/hr/
    ├── models.py
    ├── schemas.py
    ├── router.py
    ├── service.py
    └── __init__.py
  ```
- Verbindung mit Core-Entities (`Employee`, `Document`)
- FastAPI-Routen (CRUD)
  - `/api/hr/leave`
  - `/api/hr/sicknotes`
  - `/api/hr/applications`

**Deliverables:**
- Alembic-Migration (`alembic/versions/add_hr_tables.py`)
- `hr_erm.dbml` Diagramm
- Unit-Tests (`tests/test_hr.py`)

---

## 🖥 Phase 4 – HR-Frontend (Woche 45)

**Ziele:**
- Vue-Module-Struktur:
  ```
  ui/src/modules/hr/
    ├── pages/LeaveOverview.vue
    ├── pages/SickNote.vue
    ├── pages/Applications.vue
    └── components/HRCard.vue
  ```
- HR-Dashboard Integration:
  - Übersicht aller HR-Einträge im User-Dashboard
  - Neue HR-Kachel in DockNav (`"HR"`)
- API-Integration über `useApi()`

**Deliverables:**
- `ui/src/modules/hr/*`
- API-Anbindung getestet (`/api/hr/*`)
- Screenshot + Demo-Flow im Wiki

---

## 🧩 Phase 5 – HR-Dokumentation (Woche 46)

**Ziele:**
- Wiki-Seiten analog zum Core-Modul:
  ```
  docs/wiki/hr/
    ├── README.md
    ├── entities.md
    ├── flows.md
    ├── hr_erm.md
    ├── api_endpoints.md
  ```
- Ergänzung im Haupt-Wiki:
  - Verlinkung zwischen Core und HR
  - Neues Kapitel in `architecture_blueprint.md`

**Deliverables:**
- Vollständiges HR-Wiki-Bundle (`workmate_hr_wiki.zip`)
- Flow-Diagramme in Mermaid + DBML

---

## ⚙️ Phase 6 – Integration & Testing (Woche 47)

**Ziele:**
- End-to-End-Test: Core + HR
- Zugriffskontrolle über Keycloak (HR-spezifische Rollen)
- Reminder-Automatisierung:
  - z. B. „Krankmeldung ausläuft in 2 Tagen“
- Dokumentenverknüpfung prüfen (Uploads → SickNotes)

**Deliverables:**
- Integrationstest (`tests/test_hr_integration.py`)
- API Health Check `/api/hr/health`
- Wiki-Eintrag: „HR-System Integration Tests“

---

## 🚀 Gesamtziel

> Vollständig funktionales HR-Modul als erste Erweiterung des Core-Systems  
> inklusive DBML, API, UI, Doku, und interner Integration in Keycloak.
