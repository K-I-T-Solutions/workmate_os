---
layout: default
title: UI Design-Konsistenz Audit & Bereinigung
parent: Daily Reports
nav_order: 12
---

# Daily Report – 6. April 2026

## UI Design-Konsistenz Audit & vollständige Bereinigung

---

### Kontext

Vollständiger Frontend-Audit (86 Vue-Dateien, 9 Composables, alle CSS-Dateien) mit anschließender systematischer Bereinigung aller kritischen Probleme. Ziel: einheitliches Design-System, keine Ad-hoc-Styles, saubere UX-Patterns.

---

### Claude-Agents eingerichtet

Drei spezialisierte Sub-Agenten in `.claude/` angelegt:

- **`backend-builder.md`** — FastAPI-Routen, SQLAlchemy-Modelle, Pydantic-Schemas, CRUD, Alembic-Migrationen, Permissions
- **`api-sync.md`** — OpenAPI-Schema exportieren, TypeScript-Typen generieren
- **`CLAUDE.md`** — Projekt-Dokumentation aktualisiert mit Agents-Tabelle

Dazu verdrahtet:
- `ui/package.json`: Script `api:generate` ergänzt (`openapi-typescript`)
- `Makefile`: Targets `openapi-export`, `openapi-codegen`, `openapi-sync`

---

### K-1: `kit-card` — Card-Pattern vereinheitlicht

**Problem:** `.kit-card` war in `base.css` definiert aber nirgendwo genutzt. Stattdessen 3+ konkurrierende Ad-hoc-Patterns (Tailwind-Opacity, Backdrop-Blur, hardcodierte Hex-Werte).

**Lösung:**
- `base.css`: `.kit-card` auf tatsächliche CSS-Variablen aus `tokens.css` umgestellt
- 11 Vue-Dateien auf `kit-card` migriert
- 16 weitere waren bereits korrekt
- Resultat: **125× `kit-card`** im Einsatz, 1 verbleibendes Ad-hoc-Pattern

**Betroffene Module:** Admin, CRM, Expenses, Finance, HR, Invoices, Knowledge, Projects, Support, Time-Tracking

---

### K-2 + K-3: Badge/Status-System implementiert & Bootstrap-Farben entfernt

**Problem:** 4 konkurrierende Badge-Systeme, Admin-Modul nutzte Bootstrap Light-Theme Farben (`#d4edda`, `#f8d7da`, `#fff3cd`) die im Dark-Theme brechen.

**Lösung:**
- `base.css`: Vollständiges Badge-System definiert:
  - `.badge` — Base-Klasse
  - `.badge-green` / `.badge-amber` / `.badge-red` / `.badge-blue` / `.badge-cyan` / `.badge-gray`
- Status-Mapping vereinheitlicht (aktiv→green, offen→amber, überfällig→red, versendet→blue)
- 6 Dateien migriert: `EmployeeListPage`, `BankAccountsPage`, `LeaveDetailPage`, `LeaveManagementPage`, `CustomerDetailPage`, `ApplicationsPage`
- Bootstrap-Farben vollständig entfernt

---

### K-4: Toast-System eingebunden & alert() ersetzt

**Problem:** 34 `alert()`/`confirm()` Aufrufe statt Design-konformer Notifications. `useToast` war bereits implementiert aber nie eingebunden.

**Lösung:**
- `AppLayout.vue`: `<ToastContainer />` eingebunden
- `api/client.ts`: `showUserNotification` TODO-Stub verdrahtet → ruft jetzt `useToast().error()` auf
- **17× `alert()`** in 8 Dateien ersetzt:

| Datei | Ersetzt |
|-------|---------|
| `admin/EmployeesPage.vue` | 6× |
| `admin/RolesPage.vue` | 3× (TODO-Stubs entfernt) |
| `admin/DepartmentsPage.vue` | 2× |
| `admin/SystemSettingsPage.vue` | 1× |
| `hr/LeaveManagementPage.vue` | 2× |
| `hr/EmployeeListPage.vue` | 3× |
| `finance/BankTransactionsPage.vue` | 1× |
| `invoices/InvoiceDetailPage.vue` | 1× |

---

### K-5: Error-States in 23 Seiten ergänzt

**Problem:** 36 Seiten hatten Loading-State aber keinen sichtbaren Fehler-State — bei API-Fehlern sah der User eine leere Seite ohne Erklärung.

**Lösung:** Einheitliches Pattern in allen betroffenen Seiten:
- `error` ref + try/catch/finally in Fetch-Funktionen
- Error-Template Block: roter Hinweistext + "Erneut versuchen" Button
- `console.error()` durch `error.value = '...'` ersetzt

**23 Dateien geändert**, 8 hatten Error-State bereits via Composable:

| Modul | Dateien |
|-------|---------|
| Admin | AuditLogPage, DepartmentsPage, RolesPage, EmployeesPage |
| Expenses | ExpensesDashboardPage, ExpensesListPage |
| Finance | FinanceDashboardPage |
| HR | ApplicationsPage, EmployeeDetailPage, EmployeeListPage, HRDashboardPage, LeaveApprovalsPage, LeaveDetailPage, LeaveManagementPage, RecruitingPage |
| Knowledge | KBHomePage |
| Projects | ProjectsDashboardPage, ProjectDetailPage |
| Support | TicketDetailPage, TicketsListPage |
| CRM | CustomerDetailPage |
| Layouts | SettingsPage, UserProfilePage |

---

### Technische Notiz

`vue-tsc` (v3.1.2) crasht mit `TypeError: Cannot read properties of undefined (reading 'fileName')` in `@volar/typescript@2.4.23` — pre-existierender Toolchain-Bug mit Node.js v25, unabhängig von heutigen Änderungen. Vite-Build selbst ist grün (1994 Module, ~1.7s).

---

### Offene Punkte (für morgen)

| # | Problem | Umfang |
|---|---------|--------|
| M-1 | `any` in TypeScript — 70+ Stellen | 20+ Dateien |
| M-3 | 5 Modale ohne Backdrop-Click/Escape | 5 Dateien |
| M-5 | `console.log` in Production-Code | 14 Stellen |
| M-6 | Dateiname `useInvocies.ts` (Tippfehler) | 1 Datei |
| N-2 | `rounded-xl` vs `rounded-lg` gemischt | 20+ Dateien |

---

### Geänderte Dateien (Gesamt)

39 Dateien, 787 Insertions, 621 Deletions
