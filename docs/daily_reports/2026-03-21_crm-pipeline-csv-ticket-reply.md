---
layout: default
title: CRM Pipeline, CSV-Import & Ticket E-Mail-Reply
parent: Daily Reports
nav_order: 11
---

# Daily Report – 21. März 2026

## CRM Pipeline-Ansicht, CSV-Import & Ticket E-Mail-Reply

---

### CRM – Pipeline-Ansicht (Kanban)

#### Backend
- Alembic Migration `a1b2c3d4e5f7`: `pipeline_stage VARCHAR(50) DEFAULT 'new_lead'` an `customers`-Tabelle + Index
- `PipelineStage` Enum: `new_lead → qualified → proposal → negotiation → won | lost`
- `get_pipeline_customers(db)` → gruppiert alle Kunden nach Stage
- `update_pipeline_stage(db, customer_id, stage)` → Stage-Wechsel
- `GET /backoffice/crm/pipeline` — Pipeline-Daten (stage → Kunden)
- `PATCH /backoffice/crm/customers/{id}/pipeline-stage` — Stage updaten

#### Frontend
- `PipelineStage` Type + `pipeline_stage` am `Customer`-Interface
- `crm.service.ts`: `getPipeline()`, `updatePipelineStage()`
- `useCustomers.ts`: `loadPipeline()`, optimistisches Stage-Update
- `useCrmNavigation.ts`: View `"pipeline"` + `goPipeline()`
- Neue Seite `CrmPipelinePage.vue`: 6-Spalten-Kanban, natives HTML5 Drag & Drop (kein externes Package), Farb-Kodierung je Stage, Trophy/Ban-Quickaction-Buttons
- `CrmApp.vue`: Pipeline-View eingebunden
- `CustomersListPage.vue`: "Pipeline"-Button im Header

---

### CRM – CSV-Import

#### Backend
- Neue Datei `csv_import.py`: `import_customers_csv(db, file_bytes, skip_duplicates, dry_run)`
  - Auto-Delimiter-Erkennung (`;` oder `,`)
  - Encoding-Fallback (UTF-8-SIG → Latin-1)
  - Pflichtfeld-Validierung (`name`)
  - Duplikaterkennung per E-Mail
  - Rückgabe: `ImportResult(imported, skipped, errors, preview)`
- `POST /backoffice/crm/customers/import-csv` mit `dry_run` und `skip_duplicates` Query-Params
- `CsvImportResponse` Schema

#### Frontend
- `CsvImportResult` Interface in `customer.ts`
- `crm.service.ts`: `importCsvDryRun()`, `importCsv()`
- `CustomersListPage.vue`: 3-Schritt-Import-Modal
  - Step 1: Datei-Upload (Drag & Drop + File-Picker)
  - Step 2: Vorschau der ersten 5 Zeilen (dry_run=true)
  - Step 3: Bestätigung mit Import-Zusammenfassung

---

### Support – Ticket E-Mail-Reply

#### Backend
- Alembic Migration `b2c3d4e5f6a7`: `reporter_email VARCHAR(255)` an `support_tickets`
- `reporter_email` Feld am Support-Ticket-Model + Schemas (`TicketCreate`, `TicketUpdate`, `TicketResponse`)
- `TicketReplyRequest` Schema (`body: str`)
- `send_ticket_reply()` Funktion im EmailService (Jinja2-Templates `ticket_reply.html` / `.txt`)
- `POST /api/support/tickets/{id}/reply`:
  - Prüft ob `reporter_email` vorhanden
  - Sendet E-Mail via SMTP
  - Speichert Antwort als öffentlichen Kommentar
- `email_intake/service.py`: trägt `reporter_email` beim automatischen Ticket-Erstellen ein

#### Frontend
- `TicketDetailPage.vue`: `reporterEmail` Computed (DB-Feld + Regex-Fallback aus mailto-Link)
- Reply-Modal: Fehlerhinweis (`replyError`), Erfolgs-Banner (`replySent`), Send-Button deaktiviert ohne E-Mail

---

### Produktions-Deploy-Fix

- `backend/entrypoint.prod.sh`: führt `alembic upgrade head` vor uvicorn aus
- `backend/Dockerfile.prod`: entrypoint statt CMD, healthcheck start-period auf 60s erhöht
- `.github/workflows/deploy-production.yml`: expliziter Migrations-Schritt nach Container-Start

---

### Commits

| Hash | Beschreibung |
|---|---|
| `1e691ca` | DATEV-Export (EXTF Buchungsstapel) |
| `c74f5cf` | Mahnwesen (Dunning) mit 3 Mahnstufen |
| `3c8aa80` | Rechnung per E-Mail direkt aus WorkmateOS |
| `abd8bfe` | Email-Design auf K.I.T. Rebrand 2026 |
| `afac7e8` | SMTP Credentials als GitHub Secrets |
| *(heute)* | CRM Pipeline + CSV-Import + Ticket Reply + Deploy-Fix |
