---
layout: default
title: SevDesk/FinTS entfernt, Claude Agents, Repo-Housekeeping
parent: Daily Reports
nav_order: 13
---

# Daily Report – 13. April 2026

## SevDesk & FinTS entfernt · Claude Agents · Repo-Housekeeping

---

### Claude Sub-Agenten eingerichtet

Drei spezialisierte Agenten in `.claude/` angelegt:

| Agent | Aufgabe |
|-------|---------|
| `backend-builder.md` | FastAPI-Routen, SQLAlchemy-Modelle, Pydantic-Schemas, CRUD, Alembic, Permissions |
| `api-sync.md` | OpenAPI-Schema exportieren → TypeScript-Typen generieren |
| `CLAUDE.md` | Projekt-Dokumentation mit Agents-Tabelle |

Dazu verdrahtet:
- `ui/package.json`: Script `api:generate` (`openapi-typescript`)
- `Makefile`: Targets `openapi-export`, `openapi-codegen`, `openapi-sync`

---

### UI Design-Konsistenz Audit & Bereinigung

Vollständiger Audit aller 86 Vue-Dateien. Fünf kritische Probleme behoben:

**K-1 — `kit-card` vereinheitlicht**
- `base.css` auf echte CSS-Variablen umgestellt
- 125× `kit-card` im Einsatz (vorher: 3+ konkurrierende Ad-hoc-Patterns)

**K-2 + K-3 — Badge-System implementiert**
- `badge-green / amber / red / blue / cyan / gray` in `base.css` definiert
- Bootstrap Light-Theme Farben (`#d4edda`, `#f8d7da`) aus Admin entfernt

**K-4 — Toast-System eingebunden**
- `useToast` + `ToastContainer` in `AppLayout.vue` eingebunden
- `api/client.ts` verdrahtet
- 17× `alert()` in 8 Dateien durch `toast.success/error/warning` ersetzt

**K-5 — Error-States ergänzt**
- 23 Seiten mit `error` ref + try/catch + Template-Block nachgerüstet
- User sieht bei API-Fehlern jetzt Hinweis + "Erneut versuchen" Button

---

### Finance Modul — Bestandsaufnahme

Vollständige Analyse des Buchhaltungs-Moduls dokumentiert in `docs/finance-module-status.md`.

**Kernaussage:**
- Rechnungssystem: 85% — solide für Agenturen/Freiberufler
- Buchhaltungslogik: 20% — keine doppelte Buchführung, kein Kontenrahmen
- Bankintegration: 60% — n8n + CSV-Import ✅, FinTS ❌

---

### SevDesk & FinTS/PSD2 entfernt

SevDesk wird nicht genutzt, FinTS funktioniert nicht mit den vorhandenen Banken. Einziger Integrationskanal bleibt der n8n-Webhook.

**Backend entfernt:**
- `SevDeskConfig`, `SevDeskInvoiceMapping`, `SevDeskBankAccountMapping`, `SevDeskSyncHistory`, `SevDeskSyncStatus`
- Alle `SevDesk*` / `FinTs*` / `Psd2*` Schemas
- `FINTS_*` / `PSD2_*` / `SEVDESK_*` Fehlercodes
- `PSD2_ENVIRONMENT` aus `config.py`
- FinTS aus `requirements.txt`

**Alembic Migration:** `2026_04_13_2313-e8aae60dde48` — dropped `sevdesk_config`, `sevdesk_sync_history`, `sevdesk_invoice_mappings`, `sevdesk_bank_account_mappings`

**Frontend entfernt:**
- `useSevDesk.ts` gelöscht
- PSD2-Typen, -Funktionen und -UI aus `useBanking.ts`, `banking.service.ts`, `BankAccountsPage`, `BankTransactionsPage`

**Stripe bleibt** vollständig erhalten.

---

### Repo-Housekeeping

- Veraltete Branches gelöscht: `feat/pdf-generator-rebrand`, `fix/pdf-description-wrap` (beide 0 eigene Commits, bereits in `main` enthalten)
- Aktive Branches: `main`, `dev`
- Git-Workflow festgelegt: **commit → `dev` pushen → PR `dev → main` → merge** (kein direkter Push auf `main`)

---

### Commits heute

| Hash | Message |
|------|---------|
| `62bae8a` | refactor(ui): Design-Konsistenz Audit – Card, Badge, Toast, Error-States |
| `1ba9e26` | refactor(finance): SevDesk und FinTS/PSD2 vollständig entfernen |

---

### Offene Punkte

| # | Problem | Prio |
|---|---------|------|
| M-1 | `any` in TypeScript — 70+ Stellen | Moderat |
| M-3 | 5 Modale ohne Backdrop-Click/Escape | Moderat |
| M-5 | 14× `console.log` in Production-Code | Moderat |
| M-6 | Dateiname `useInvocies.ts` (Tippfehler) | Klein |
