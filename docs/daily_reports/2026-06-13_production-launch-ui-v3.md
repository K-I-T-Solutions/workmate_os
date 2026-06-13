# Daily Report — 2026-06-13

**Projekt:** WorkmateOS  
**Autor:** Joshua Kuhrau  
**Branch-Basis:** `main` / Deploy: Production (workmate.kit-it-koblenz.de)

---

## Zusammenfassung

Vollständiger Produktions-Launch von WorkmateOS UI v3. Backend-Instabilität durch Alembic-Migrationsfehler behoben, CI/CD-Pipeline repariert, und anschließend mehrere UI-Features nachgezogen.

---

## Erledigte Aufgaben

### Backend — Alembic Migrations-Fix

**Problem:** Produktions-Backend steckte in einer Restart-Loop.  
**Ursache:** Zwei Migrationsdateien teilten dieselbe Revision-ID `f1a2b3c4d5e6`:
- `2026_03_20_1100-..._add_invoice_reminders.py`
- `2026_04_21_1000-..._ticketing_foundation.py`

Das erzeugte einen logischen Cycle im Alembic-Revisions-Baum.

**Lösung:**
- `ticketing_foundation` erhielt eine neue eindeutige ID: `c1d2e3f4a5b6`
- `add_pipeline_stage` zeigt wieder korrekt auf `f1a2b3c4d5e6` (add_invoice_reminders)
- `add_workmate_id_to_employees` zeigt auf die neue ID `c1d2e3f4a5b6`
- `alembic/versions/` aus `.dockerignore` entfernt (Migrations-Dateien wieder im Image)

**Finaler Revisions-Chain:**  
`email_intake → add_invoice_reminders (f1a2b3c4d5e6) → pipeline_stage → ticket_reporter → remove_sevdesk → ticketing_foundation (c1d2e3f4a5b6) → workmate_id → customer_id (d1e2f3a4b5c6)`

---

### CI/CD — GitHub Actions Pipeline

**Problem:** Deploy-Workflow schlug fehl durch:
- Fehlerhafter Docker-Injection-Ansatz für Migrations-Dateien
- Frontend-Healthcheck ignorierte 307-Redirect (`/` → `/login`)
- `curl` nicht verfügbar im Alpine-Container (Next.js Image)

**Lösung:**
- Injection-Step entfernt; Migrations-Dateien sind direkt im Image
- Healthcheck auf `/login` mit `curl -L` (Redirect folgen)
- Docker-Compose Healthcheck auf `wget --spider -q http://127.0.0.1:3000`

---

### Frontend — NEXT_PUBLIC Umgebungsvariablen

**Problem:** `NEXT_PUBLIC_*` Variablen waren leer in Production → `Invalid URL` und `Unexpected token '<'` in der Browser-Konsole.  
**Ursache:** `.env.local` wird durch rsync ausgeschlossen; Variablen werden zur Build-Zeit eingebakent.

**Lösung:** `ui-v3/.env.production` erstellt mit:
- `NEXT_PUBLIC_KEYCLOAK_URL`, `NEXT_PUBLIC_KEYCLOAK_REALM`, `NEXT_PUBLIC_KEYCLOAK_CLIENT_ID`
- `NEXT_PUBLIC_API_BASE`, `NEXT_PUBLIC_APP_URL`

---

### UI — Theme-System (4 Varianten)

Farbschema-Auswahl wie in UI v1. Implementierung:

| Theme | Hintergrund | Akzent |
|---|---|---|
| Standard | Schwarz (`#111111`) | Electric Blue |
| Anthrazit | Anthrazit (`#232223`) | Orange (`#FF9100`) |
| Midnight | Reines Schwarz (OLED) | Electric Blue |
| Hell | Weiß (`#f8f9fa`) | Dunkelblau |

- CSS Custom Properties via `:root[data-theme="..."]` (Spezifität 0,1,1)
- localStorage-Persistenz (`workmate-theme`)
- Anti-FOUC Inline-Script in `<head>`
- Erreichbar über Einstellungen → Erscheinungsbild

**Neue Dateien:** `ui-v3/lib/theme/use-theme.ts`, `ui-v3/components/providers/theme-provider.tsx`

---

### UI — Favicon (Workmate Rebrand 2026)

Favicon-Set komplett auf neue Rebrand-Assets umgestellt.

**Quelle:** `/mnt/data/docs/K.I.T/3_Assets/Logos/Workmate_Rebrand_2026/LOGOS_TRANSPARENT/WORKMATE _ OS.png`

- Transparentes WM-Logo (kein dunkler Hintergrund)
- Vor Skalierung mit `-fuzz 10% -trim` zugeschnitten → schärfer bei kleinen Größen
- Erzeugte Varianten: `favicon.ico` (16/32/48px), `icon-dark/light-32x32.png`, `apple-icon.png` (180px), `favicon-192.png`, `favicon-512.png`, `workmate-logo.png` (400px, Login + Sidebar)
- `icon.svg` als SVG-Fallback

---

### UI — Breadcrumb: Name statt UUID

**Problem:** Detailseiten zeigten die UUID aus der URL im Breadcrumb.

**Lösung:** `PageTitleContext` + `usePageTitle(title)` Hook.

- Detail-Komponenten setzen den Titel sobald Daten geladen sind
- `shell-layout.tsx` liest den Context und gibt `pageTitle` an `<Topbar>` weiter

| Seite | Breadcrumb-Wert |
|---|---|
| Kunden-Detail | `customer.name` |
| Projekt-Detail | `project.title` |
| Rechnung-Detail | `invoice.invoice_number` |
| Ticket-Detail | `ticket.title` |
| Mitarbeiter-Detail | `first_name last_name` |
| Wiki-Artikel | `article.title` |

**Neue Datei:** `ui-v3/lib/page-title-context.tsx`

---

## Commits heute

| Hash | Beschreibung |
|---|---|
| `2169d72` | feat(ui-v3): Breadcrumb zeigt Namen statt UUID auf Detailseiten |
| `7a0e427` | fix(ui-v3): Favicon-Icons trimmen für schärfere Darstellung bei kleinen Größen |
| `feeddd8` | fix(ui-v3): Favicon auf transparentes WM-Logo umstellen |
| `60ae054` | feat(ui-v3): Favicon & App-Icons auf Workmate Rebrand 2026 aktualisieren |
| `0ad765e` | feat(ui-v3): Theme-System mit 4 Farbvarianten implementieren |
| `a99232e` | fix(ci): Frontend-Healthcheck auf /login mit -L Redirect-Folgen |
| `d463cca` | fix(alembic): Duplikate Revision-ID f1a2b3c4d5e6 auflösen |
| `c769938` | fix(ui-v3): NEXT_PUBLIC env-Variablen für Production-Build setzen |
| `8363649` | fix(alembic): Revisions-Cycle beheben durch korrekten down_revision-Zeiger |
| `36637c1` | fix(backend): alembic/versions aus Docker-Image ausschließen |
| `e5a5925` | fix(infra): Alembic-Volume-Mount, Next.js Frontend, Node.js 24 Actions |
| `f06060f` | feat(ui-v3): WorkmateOS UI v3 – vollständiges Frontend (Initial Commit) |
| `e329343` | feat(documents): customer_id FK + Alembic-Migration für kundenbezogene Dokumente |

---

## PRs (heute gemergt)

- PR #42 — Favicon Workmate Rebrand 2026
- PR #43 — Favicon auf transparentes WM-Logo
- PR #44 — Favicon trimmen
- PR #45 — Breadcrumb Namen statt UUID

---

## Status

**Production:** Live und stabil  
**URL:** https://workmate.kit-it-koblenz.de  
**Backend:** https://api.workmate.kit-it-koblenz.de  
**Keycloak:** https://login.kit-it-koblenz.de (Realm: kit)
