---
layout: default
title: Phase 4 komplett – HR, Recruiting, Support, Knowledge Base
parent: Daily Reports
nav_order: 10
---

# Daily Report - 12. März 2026

## Phase 3 & 4 Abschluss + Bugfixes

---

### Phase 3 – SSO & Admin (100% ✅)

#### Audit Log Backend
- `GET /api/audit-logs` mit User-Enrichment (`user_name`, `user_email`)
- `resource_type` als Alias für `entity_type` (Frontend-Kompatibilität)
- AuditLog-Actions erweitert: `call`, `email`, `message`, `note`, `ticket_*`, `login`, `logout`, `upload`
- Migration `a3f8c12d9e01`

#### User Settings
- `GET/PUT /api/users/{id}/settings` — persönliche Einstellungen (Sprache, Zeitzone)
- `UserSettingsUpdate` Schema, CRUD in Dashboards-Modul

#### CRM Activity Timeline
- CRM CRUD (Customer, Contact) schreibt automatisch AuditLog-Einträge
- `GET /api/backoffice/crm/customers/{id}/activities` — merged manuelle + Audit-Events als `system`-Activities
- `GET /api/backoffice/crm/activities/latest` — unified für beide Dashboards
- Frontend: `ActivityType` um `"system"` erweitert, Activity-Icon in CustomerDetailPage, CrmDashboardPage, DashboardPage

---

### Phase 4 – HR, Support, Knowledge Base (100% ✅)

#### HR Self-Service
- `MyLeavePage.vue` — Urlaubssaldo-Widget, eigene Anträge, Antrag stellen + stornieren
- Self-Service Endpoints (`/my-requests`, `/my-balance`, `/cancel`)
- Tab "Mein Urlaub" als Default-Tab in HRApp

#### HR Detailseiten
- `EmployeeDetailPage.vue` — Gravatar, Tabs (Überblick / Urlaub), Urlaubskonto-Widget, Leave-History
- `LeaveDetailPage.vue` — Detailansicht statt Modal, Employee separat geladen, Gravatar
- `LeaveApprovalsPage.vue` — Refactored: Gravatar, kompakte Cards, Employee separat geladen
- Gravatar in `EmployeeListPage.vue` Karten

#### HR Recruiting
- Backend: `JobPosting` + `Application` Models, vollständige REST API
- Migration `b9f1e4c8a2d3`: `hr_job_postings` + `hr_applications`
- `RecruitingPage.vue`: Stellenübersicht, Status-Filter, Veröffentlichen/Schließen/Archivieren
- `ApplicationsPage.vue`: Pipeline mit Statusvorschritt, Stern-Rating (1–5), Gravatar

#### Support Tickets
- Backend: `Ticket` + `TicketComment`, auto-Ticketnummer (`TKT-XXXXX`)
- Migration `c7d2f3e4b5a6`: `support_tickets` + `support_ticket_comments`
- `TicketsListPage.vue`: Liste mit Suche, Status/Priorität-Filter, Create-Form
- `TicketDetailPage.vue`: Kommentar-Timeline, interne Notizen, Status-Workflow, Gravatar
- App im Dock (Position 8, LifeBuoy-Icon)

#### Knowledge Base
- Backend: `KBCategory` + `KBArticle`, Volltextsuche, View-Counter, Helpful-Voting, Slugify
- Migration `d8e3f5c6b7a8`: `kb_categories` + `kb_articles`
- `KBHomePage.vue`: Kategorie-Grid mit Farb-Picker, Suche, letzte Artikel
- `KBCategoryPage.vue`: Artikelliste, Status-Filter, Artikel anlegen
- `KBArticlePage.vue`: Inline-Bearbeitung (Markdown), Helpful/Not-Helpful Voting
- App im Dock (Position 9, BookOpen-Icon)

---

### Bugfixes

| # | Problem | Fix |
|---|---------|-----|
| 1 | `KBArticle.category_id` ohne ForeignKey → ORM-Mapper-Crash beim Start | `ForeignKey("kb_categories.id")` ergänzt, DB-Spalte von VARCHAR zu UUID migriert |
| 2 | CRM Activities: `db.commit()` nach `log_audit()` fehlte → Einträge wurden zurückgerollt | `db.commit()` nach jedem `log_audit()`-Call ergänzt |
| 3 | Audit-Log Response: `user_name`/`user_email` fehlten | Employee-Lookup im Service, `AdminAuditLogResponse` Schema |
| 4 | `gpg-agent allow-loopback-pinentry` doppelt eingetragen → Commit-Fehler | `gpg-agent.conf` bereinigt |

---

### UI/UX Verbesserungen

- **Home-Button** in jeder Window-Titelleiste (navigiert zu `/app`)
- `kit-input` Klasse einheitlich in allen neuen Formularen
- Gravatar konsistent in HR-Modul (Mitarbeiterliste, Genehmigungen, Leave-Detail, Recruiting)
- Detailseiten-Ästhetik vereinheitlicht (Back-Button, Card-Grid, Badges)

---

### Versionierung

| Branch | Version | Status |
|--------|---------|--------|
| `main` | v3.0.0 | Phase 3 abgeschlossen |
| `dev`  | –       | Phase 4 komplett, PR ausstehend |

**Nächster Schritt:** PR `dev → main`, Version auf `4.0.0` bumpen, Phase 5 planen (Banking API, Elster, Mobile App)
