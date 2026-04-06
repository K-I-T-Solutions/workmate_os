# WorkmateOS — CLAUDE.md

Internes ERP/OS-System für K.I.T. Solutions. Vollstack-Anwendung mit FastAPI Backend und Vue 3 Frontend.

---

## Projekt-Überblick

- **Version:** 4.0.0
- **Stack:** FastAPI 0.115+ · PostgreSQL 16 · SQLAlchemy 2.0 · Vue 3 · TypeScript · Tailwind CSS 4
- **Auth:** Keycloak OIDC (JWT RS256)
- **Storage:** Nextcloud WebDAV (pluggable: local / S3)
- **Package Manager Frontend:** pnpm
- **Deployment:** Docker Compose (Dev) · Render.com / Fly.io (Prod)

---

## Verzeichnisstruktur

```
workmate_os/
├── backend/              # FastAPI App
│   ├── app/
│   │   ├── main.py       # App-Entrypoint, alle Router registriert
│   │   ├── core/         # Auth, DB, Storage, Email, Audit, Config
│   │   └── modules/      # 13 Hauptmodule (siehe unten)
│   ├── alembic/          # DB-Migrationen
│   └── tests/            # pytest Tests
├── ui/                   # Vue 3 Frontend
│   └── src/
│       ├── modules/      # Seiten pro Modul
│       ├── services/     # API-Client (Axios), Navigation
│       ├── composables/  # Vue Hooks
│       └── types/        # TypeScript Definitionen
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
| `documents` | `modules/documents/` | Datei-Upload (Storage-Backend) |
| `reminders` | `modules/reminders/` | Erinnerungen |
| `crm` | `modules/backoffice/crm/` | Kunden, Kontakte, Activity-Timeline |
| `projects` | `modules/backoffice/projects/` | Projekte, Team-Zuordnung, Budget |
| `time_tracking` | `modules/backoffice/time_tracking/` | Stundenerfassung, billable/non-billable |
| `invoices` | `modules/backoffice/invoices/` | Rechnungen, PDF, ZUGFeRD/Factur-X |
| `finance` | `modules/backoffice/finance/` | Transaktionen, Bankintegration via n8n |
| `products` | `modules/backoffice/products/` | Produkt-/Leistungskatalog |
| `chat` | `modules/backoffice/chat/` | Internes Messaging |
| `hr` | `modules/hr/` | Urlaub, Recruiting, Vergütung, Training |
| `support` | `modules/support/` | Ticket-System |
| `knowledge` | `modules/knowledge/` | Wiki / Knowledge Base |
| `email_intake` | `modules/email_intake/` | E-Mail → Ticket (n8n/IMAP Webhook) |

Jedes Modul folgt dem gleichen Muster: `routes.py · models.py · schemas.py · crud.py`

---

## Core Services

### Auth (`app/core/auth/`)
- `auth.py` — `get_current_user()`, JWT-Validierung, JWKS-Cache
- `keycloak.py` — Admin API, User/Role-Sync
- `roles.py` — `require_permissions()` Decorator, Wildcard-Matching (`*`, `backoffice.*`)
- `routes.py` — Login/Callback/Me/Logout Endpoints

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
| `KEYCLOAK_URL` | `https://login.intern...` | Keycloak Server |
| `KEYCLOAK_REALM` | `kit` | Realm-Name |
| `KEYCLOAK_CLIENT_ID` | `workmate-backend` | Client-ID |
| `STORAGE_BACKEND` | `nextcloud` | `nextcloud` \| `local` \| `s3` |
| `NEXTCLOUD_URL` | `https://cloud.../dav/...` | WebDAV-URL |
| `SMTP_*` | — | E-Mail-Konfiguration |
| `JWT_SECRET_KEY` | — | Fallback für lokale Tokens |
| `PSD2_ENVIRONMENT` | `sandbox` | `sandbox` \| `production` |

---

## Datenbank & Migrationen

- **ORM:** SQLAlchemy 2.0 (declarative, `Base`)
- **IDs:** UUID v4 überall
- **Migrations:** Alembic, Dateiformat `YYYY_MM_DD_HHMM-{rev}_{slug}`, Timezone: `Europe/Berlin`
- **Neue Migration immer** nach Modeländerung via `make migrate-auto`

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

## Frontend

```bash
cd ui
pnpm install
pnpm dev          # Vite Dev-Server auf :5173
pnpm build        # TypeScript-Check + Build
```

Umgebungsvariablen (Vite):
- `VITE_API_BASE` — API-URL
- `VITE_KEYCLOAK_URL`, `VITE_KEYCLOAK_REALM`, `VITE_KEYCLOAK_CLIENT_ID`

TypeScript-Typen werden via `openapi-typescript` aus dem OpenAPI-Spec generiert (`assets/openapi.yaml`).

---

## Konventionen

- **Backend:** Alles auf Deutsch (Kommentare, Variablennamen bei Bedarf), Docstrings optional
- **Schemas:** Pydantic v2 (`model_config = ConfigDict(from_attributes=True)`)
- **Permissions:** `@require_permissions(["modul.action"])` Decorator auf Route-Ebene
- **Neue Module:** Gleiches Muster wie bestehende (`routes / models / schemas / crud`) + Router in `main.py` registrieren
- **Migrationen:** Immer nach Modell-Änderungen, niemals manuell SQL schreiben
- **UUID:** `generate_uuid()` aus `app.core.settings.database` verwenden

---

## Produktions-URLs

| Service | URL |
|---------|-----|
| Frontend | `https://workmate.kit-it-koblenz.de` |
| API | `https://api.workmate.kit-it-koblenz.de` |
| Docs | `https://api.workmate.kit-it-koblenz.de/docs` |
| Health | `https://api.workmate.kit-it-koblenz.de/health` |

---

## Aktueller Stand (Phase 4 abgeschlossen)

- Phase 1–4: ✅ Core, Backoffice, SSO/Admin, HR & Support
- Phase 5: geplant — Banking API, Elster, Mobile App


## Agents

Spezialisierte Sub-Agenten verfügbar:

| Agent | Invoke für |
|-------|-----------|
| `frontend-builder` | Vue Components, Composables, Views, Design-System |
| `backend-builder` | FastAPI-Routen, SQLAlchemy-Modelle, Pydantic-Schemas, CRUD, Alembic-Migrationen, Permissions |
| `api-sync` | OpenAPI-Schema exportieren, TypeScript-Typen generieren (`make openapi-sync`) |

Claude wählt den passenden Agent automatisch oder du rufst ihn explizit: *"Nutze api-sync um die Typen zu aktualisieren"*
