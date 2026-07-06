# WorkmateOS — CLAUDE.md

Internes ERP/OS-System für K.I.T. Solutions. Vollstack-Anwendung mit FastAPI Backend und Next.js 14 Frontend.

---

## Projekt-Überblick

- **Version:** 4.0.0
- **Stack:** FastAPI 0.115+ · PostgreSQL 16 · SQLAlchemy 2.0 · Next.js 14 · TypeScript · Tailwind CSS 4 · Base UI
- **Auth:** Keycloak OIDC (JWT RS256, PKCE)
- **Storage:** Nextcloud WebDAV (pluggable: local / S3)
- **Package Manager Frontend:** pnpm
- **Deployment:** Docker Compose (Dev) · GitHub Actions → workmate-01 (Prod)

---

## Verzeichnisstruktur

```
workmate_os/
├── backend/              # FastAPI App
│   ├── app/
│   │   ├── main.py       # App-Entrypoint, alle Router registriert
│   │   ├── core/         # Auth, DB, Storage, Email, Audit, Config
│   │   └── modules/      # Hauptmodule (siehe unten)
│   ├── alembic/          # DB-Migrationen
│   └── tests/            # pytest Tests
├── ui-v3/                # Next.js 14 Frontend (aktiv)
│   ├── app/              # Next.js App Router (Seiten)
│   ├── components/       # UI-Komponenten
│   │   ├── providers/    # Auth-Provider, Theme
│   │   ├── ui/           # Base UI Komponenten (Combobox, Select etc.)
│   │   └── [modul]/      # Modul-spezifische Komponenten
│   ├── lib/              # API-Client, Auth-Session, Utilities
│   └── types/            # TypeScript Definitionen
├── infra/                # docker-compose.yml, .env, .env.prod
├── docs/                 # Architektur, Roadmap, Daily Reports
└── Makefile              # Dev-Commands
```

---

## Module

| Modul | Pfad | Beschreibung |
|-------|------|--------------|
| `employees` | `modules/employees/` | Mitarbeiterverwaltung, Rollen, Abteilungen |
| `admin` | `modules/admin/` | Audit-Log, System-Settings |
| `dashboards` | `modules/dashboards/` | Dashboards, Notifications, User-Settings |
| `documents` | `modules/documents/` | Datei-Upload (Nextcloud WebDAV) |
| `reminders` | `modules/reminders/` | Erinnerungen |
| `crm` | `modules/backoffice/crm/` | Kunden, Kontakte, Activity-Timeline |
| `projects` | `modules/backoffice/projects/` | Projekte, Team-Zuordnung, Budget |
| `time_tracking` | `modules/backoffice/time_tracking/` | Stundenerfassung, billable/non-billable, customer_id |
| `invoices` | `modules/backoffice/invoices/` | Rechnungen, PDF, E-Mail-Versand |
| `finance` | `modules/backoffice/finance/` | Transaktionen, Bankintegration via n8n |
| `products` | `modules/backoffice/products/` | Produkt-/Leistungskatalog |
| `hr` | `modules/hr/` | Urlaub, Recruiting, Vergütung, Training, Onboarding |
| `support` | `modules/support/` | Ticket-System |
| `knowledge` | `modules/knowledge/` | Wiki / Knowledge Base |
| `email_intake` | `modules/email_intake/` | E-Mail → Ticket (n8n/IMAP Webhook) |

Jedes Modul folgt dem gleichen Muster: `routes.py · models.py · schemas.py · crud.py`

---

## Core Services

### Auth (`app/core/auth/`)
- `auth.py` — `get_current_user()`, JWKS-Cache, RS256/HS256 Token-Validierung
- `keycloak.py` — Auto-Provisioning neuer User beim Login, Rollen-Sync
- `roles.py` — `require_permissions()` Decorator, Wildcard-Matching (`*`, `backoffice.*`)
- `role_mapping.py` — Keycloak Realm-Rollen → WorkmateOS Rollen-Namen
- `routes.py` — Login/Callback/Me/Logout Endpoints; `get_employee_from_token` Dependency

### Rollen (K.I.T. Org-Konzept)

| Rolle | Permissions |
|-------|-------------|
| Admin | `["*"]` |
| Geschäftsführung | `employees.*, hr.*, backoffice.*, documents.*, admin.read` |
| CTO | `backoffice.projects/time/crm.read, documents.*, kb.*` |
| CFO | `backoffice.finance.*, invoices.*, crm.read` |
| Head of Events | `backoffice.crm.*, projects.*, time_tracking.write` |
| Mitarbeiter | `hr.view, backoffice.time_tracking.write, documents.read` |
| Marketing | `backoffice.crm.read, documents.read` |

Keycloak Realm-Rollen: `workmate-admin`, `workmate-geschaeftsfuehrung`, `workmate-cto`, `workmate-cfo`, `workmate-head-of-events`, `workmate-mitarbeiter`, `workmate-marketing`

### Database (`app/core/settings/database.py`)
```python
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker()
get_db() -> Generator[Session]
generate_uuid() -> UUID
```

### Storage (`app/core/storage/`)
Factory Pattern. Backends: `local.py`, `nextcloud.py`. Wechsel via `STORAGE_BACKEND` env.

### Email (`app/core/email/service.py`)
SMTP-basiert, HTML-Templates für Willkommen, Passwort-Reset, Rechnungen, Tickets.

### Audit (`app/core/audit/audit.py`)
Zentrale `AuditLog`-Tabelle. Auto-Logging für Permission-Denials und CRUD-Operationen.

---

## Development Commands

```bash
make dev-up               # Services starten
make dev-down             # Services stoppen
make dev-rebuild          # Rebuild & Restart
make backend-rebuild      # Nur Backend rebuilden
make dev-logs             # Live Logs
make shell                # Backend-Shell (bash im Container)
make db-shell             # PostgreSQL CLI

make migrate-create MSG='Beschreibung'  # Neue Migration erstellen
make migrate-auto MSG='Beschreibung'    # Migration erstellen & anwenden
make migrate-up                          # Alle Migrationen anwenden
make migrate-down                        # Eine Migration zurückrollen
make migrate-current                     # Aktuelle Revision anzeigen
make migrate-history                     # Migrations-History

make seed                 # Demo-Daten laden
make db-reset             # DB komplett zurücksetzen (DESTRUKTIV)
```

---

## Umgebungsvariablen

Konfiguration in `infra/.env` (Dev) und `infra/.env.prod` (Prod).

| Variable | Beispiel | Beschreibung |
|----------|---------|--------------|
| `DATABASE_URL` | `postgresql+psycopg2://...` | PostgreSQL-Verbindung |
| `KEYCLOAK_URL` | `https://login.kit-it-koblenz.de` | Keycloak Server (extern) |
| `KEYCLOAK_INTERNAL_URL` | `http://keycloak:8080` | Keycloak intern (Docker-Netz) |
| `KEYCLOAK_REALM` | `kit` | Realm-Name |
| `KEYCLOAK_CLIENT_ID` | `workmate-backend` | Client-ID |
| `STORAGE_BACKEND` | `nextcloud` | `nextcloud` \| `local` \| `s3` |
| `NEXTCLOUD_URL` | `https://cloud.../dav/...` | WebDAV-URL |
| `SMTP_*` | — | E-Mail-Konfiguration |
| `JWT_SECRET_KEY` | — | Fallback für lokale HS256-Tokens |

---

## Datenbank & Migrationen

- **ORM:** SQLAlchemy 2.0 (declarative, `Base`)
- **IDs:** UUID v4 überall
- **Migrations:** Alembic, Dateiformat `YYYY_MM_DD_HHMM-{rev}_{slug}`, Timezone: `Europe/Berlin`
- **Neue Migration immer** nach Modell-Änderung via `make migrate-auto`

---

## Tests

```bash
# Im Backend-Container
cd backend
pytest tests/
pytest tests/test_email_intake.py -v
```

- Framework: `pytest` + `pytest-asyncio`
- DB: SQLite In-Memory für Unit-Tests
- Dependency Overrides: `app.dependency_overrides[get_db] = test_db_session`

---

## API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc:       `http://localhost:8000/redoc`
- Health:      `http://localhost:8000/health`
- System Info: `http://localhost:8000/system/info`

Alle Modul-Routen unter `/api/...`. Prefix wird in `main.py` gesetzt.

---

## Frontend (ui-v3)

```bash
cd ui-v3
pnpm install
pnpm dev          # Next.js Dev-Server auf :3000
pnpm build        # TypeScript-Check + Build
```

Umgebungsvariablen (Next.js):
- `NEXT_PUBLIC_API_BASE` — API-URL
- `NEXT_PUBLIC_KEYCLOAK_URL`, `NEXT_PUBLIC_KEYCLOAK_REALM`, `NEXT_PUBLIC_KEYCLOAK_CLIENT_ID`

Auth-Flow: PKCE via `lib/auth/pkce.ts`, Token in localStorage, Permissions von `/api/auth/me`.

---

## Konventionen

- **Backend:** Kommentare auf Deutsch, Docstrings optional
- **Schemas:** Pydantic v2 (`model_config = ConfigDict(from_attributes=True)`)
- **Permissions:** `@require_permissions(["modul.action"])` Decorator auf Route-Ebene
- **Neue Module:** Gleiches Muster wie bestehende (`routes / models / schemas / crud`) + Router in `main.py` registrieren
- **Migrationen:** Immer nach Modell-Änderungen, niemals manuell SQL schreiben
- **UUID:** `generate_uuid()` aus `app.core.settings.database` verwenden
- **Git:** Feature-Branch → dev → PR auf main; niemals direkt auf main committen

---

## Produktions-URLs

| Service | URL |
|---------|-----|
| Frontend | `https://workmate.kit-it-koblenz.de` |
| API | `https://api.workmate.kit-it-koblenz.de` |
| Docs | `https://api.workmate.kit-it-koblenz.de/docs` |
| Health | `https://api.workmate.kit-it-koblenz.de/health` |
| Keycloak | `https://login.kit-it-koblenz.de` |

---

## Aktueller Stand (Phase 4 abgeschlossen)

- Phase 1–4: ✅ Core, Backoffice, SSO/Admin, HR & Support
- Phase 5: geplant — Banking API, Elster, Mobile App

## Agents

Spezialisierte Sub-Agenten verfügbar:

| Agent | Invoke für |
|-------|-----------|
| `frontend-builder` | Next.js Komponenten, Composables, Pages, Design-System |
| `backend-builder` | FastAPI-Routen, SQLAlchemy-Modelle, Pydantic-Schemas, CRUD, Alembic-Migrationen, Permissions |
| `api-sync` | OpenAPI-Schema exportieren, TypeScript-Typen generieren (`make openapi-sync`) |

Claude wählt den passenden Agent automatisch oder du rufst ihn explizit: *"Nutze api-sync um die Typen zu aktualisieren"*
