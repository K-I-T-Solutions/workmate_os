# 🔧 Backend Wiki - WorkmateOS

**WorkmateOS Backend-Dokumentation**

Diese Dokumentation beschreibt die Backend-Architektur, Module und APIs von WorkmateOS.

---

## 📚 Dokumentations-Übersicht

| Dokument | Status | Beschreibung |
|----------|--------|--------------|
| **[Authentication & SSO](./AUTHENTICATION.md)** | ✅ Vollständig | Zitadel SSO, OAuth2, Role Mapping, Permissions |
| **[Admin Panel](./ADMIN_PANEL.md)** | ✅ Vollständig | System-Administration, User/Department/Role Management |
| **[Module Übersicht](./MODULE_UEBERSICHT.md)** | ✅ Vollständig | Alle Backend-Module (CRM, Projects, Invoices, etc.) |
| **[API Reference](./API_REFERENCE.md)** | ⏳ TODO | Alle REST Endpoints mit Beispielen |
| **[Datenbank Schema](./DATABASE.md)** | ⏳ TODO | Datenbank-Modelle, Migrations, Best Practices |

---

## 🏗️ Backend-Architektur

### Tech Stack

- **Framework:** FastAPI (Python 3.13)
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL 16
- **Migrations:** Alembic
- **Authentication:** Zitadel (OAuth2/OIDC)
- **API Docs:** Swagger/OpenAPI

### Verzeichnis-Struktur

```
backend/
├── app/
│   ├── core/                   # Core-Funktionalität
│   │   ├── auth/               # Authentication (Zitadel, Roles)
│   │   ├── audit/              # Audit Logging
│   │   └── settings/           # Config, Database
│   │
│   ├── modules/                # Business-Module
│   │   ├── employees/          # Mitarbeiter-Verwaltung
│   │   ├── documents/          # Dokumenten-Management
│   │   ├── reminders/          # Erinnerungen
│   │   ├── dashboards/         # Dashboard-Daten
│   │   ├── system/             # System-Services
│   │   └── backoffice/         # Backoffice-Module
│   │       ├── crm/            # Customer Relationship
│   │       ├── projects/       # Projekt-Management
│   │       ├── invoices/       # Rechnungswesen
│   │       ├── finance/        # Ausgaben
│   │       ├── time_tracking/  # Zeiterfassung
│   │       └── chat/           # Messaging
│   │
│   ├── models.py               # Model-Exporte (für Alembic)
│   └── main.py                 # FastAPI-App
│
├── alembic/                    # Database Migrations
├── tests/                      # Unit & Integration Tests
└── requirements.txt            # Python Dependencies
```

---

## 🔐 Authentication

WorkmateOS nutzt **Zitadel** als Identity Provider mit OAuth2/OIDC.

**Vollständige Dokumentation:** [→ AUTHENTICATION.md](./AUTHENTICATION.md)

**Quick Start:**
- SSO-Login über Zitadel
- Role-based Access Control (RBAC)
- Wildcard Permissions (`*`, `backoffice.*`)
- Automatisches Employee Onboarding

---

## 📦 Module

### Core-Module

| Modul | Beschreibung | Dokumentation |
|-------|--------------|---------------|
| **Employees** | Mitarbeiter, Abteilungen, Rollen | [ADMIN_PANEL.md](./ADMIN_PANEL.md) / [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#employees-module) |
| **Documents** | Dokumenten-Upload & Management | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#documents-module) |
| **Reminders** | Erinnerungen & Benachrichtigungen | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#reminders-module) |
| **Dashboards** | Dashboard-Konfiguration | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#dashboards-module) |
| **System** | Infrastruktur-Services | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#system-module) |

### Backoffice-Module

| Modul | Beschreibung | Dokumentation |
|-------|--------------|---------------|
| **CRM** | Kunden & Kontakte | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#crm-module) |
| **Projects** | Projekt-Management | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#projects-module) |
| **Invoices** | Rechnungserstellung | [Finance DE](../finance/de/) / [Finance EN](../finance/en/) |
| **Finance** | Ausgaben-Management | [Finance DE](../finance/de/) / [Finance EN](../finance/en/) |
| **Time Tracking** | Zeiterfassung | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#time-tracking-module) |
| **Chat** | Messaging-System | [MODULE_UEBERSICHT.md](./MODULE_UEBERSICHT.md#chat-module) |

---

## 🌐 API-Struktur

Alle Module folgen einer **konsistenten API-Struktur**:

```
/api/{module}/
├── GET    /                # List (mit Pagination & Filtern)
├── POST   /                # Create
├── GET    /{id}            # Read
├── PUT    /{id}            # Update
├── DELETE /{id}            # Delete
└── ...    (custom endpoints)
```

**Beispiel - CRM:**
```
GET    /api/customers               # Liste aller Kunden
POST   /api/customers               # Neuen Kunden anlegen
GET    /api/customers/{id}          # Kunden abrufen
PUT    /api/customers/{id}          # Kunden bearbeiten
DELETE /api/customers/{id}          # Kunden löschen
GET    /api/customers/{id}/contacts # Kontakte eines Kunden
```

---

## 🗄️ Datenbank

### Schema-Design

- **Core-Schema:** [core_erm.dbml](../core/core_erm.dbml)
- **Backoffice-Schema:** [workmateos_phase2.dbml](../backoffice/workmateos_phase2.dbml)

### Migrations

Migrations werden mit **Alembic** verwaltet:

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Dokumentation:** ⏳ TODO - DATABASE.md

---

## 🔍 API-Dokumentation

### Swagger UI

**Entwicklung:** http://localhost:8000/docs
**Production:** https://api.workmate.kit-it-koblenz.de/docs

### Authentifizierung in Swagger

1. Klicke auf "Authorize" 🔓
2. Gib Access Token ein: `Bearer {your_token}`
3. Klicke "Authorize"
4. API-Calls werden automatisch authentifiziert

---

## 🧪 Testing

**Test-Framework:** Pytest

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_auth.py::test_login
```

**Dokumentation:** ⏳ TODO - TESTING.md

---

## 🚀 Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code-Struktur pro Modul

Jedes Modul folgt diesem Pattern:

```
module_name/
├── __init__.py          # Exports
├── models.py            # SQLAlchemy Models
├── schemas.py           # Pydantic Schemas (Request/Response)
├── crud.py              # Database Operations
├── routes.py            # FastAPI Endpoints
└── README.md (optional) # Modul-Dokumentation
```

---

## 📊 Performance & Monitoring

### Logging

WorkmateOS nutzt Python's `logging` mit strukturiertem Logging:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("User logged in", extra={"user_id": user.id, "email": user.email})
logger.error("Database error", exc_info=True)
```

### Metrics (TODO)

- Prometheus für Metriken
- Grafana für Dashboards
- Sentry für Error Tracking

---

## 🔒 Sicherheit

### Best Practices

- ✅ **HTTPS only** in Production
- ✅ **JWT Token Validation** bei jedem Request
- ✅ **Role-based Access Control** (RBAC)
- ✅ **SQL Injection Prevention** durch SQLAlchemy ORM
- ✅ **CORS** konfiguriert für Frontend-Domain
- ⏳ **Rate Limiting** (TODO)
- ⏳ **Input Validation** mit Pydantic

**Dokumentation:** ⏳ TODO - SICHERHEIT.md

---

## 📝 Beiträge zur Dokumentation

Diese Dokumentation lebt! Wenn du etwas hinzufügst:

1. Halte dich an die **bestehende Struktur**
2. Füge **Code-Beispiele** hinzu
3. Aktualisiere den **Changelog** am Ende
4. Verlinke auf **verwandte Dokumente**

---

## 🔗 Links

- [Frontend-Dokumentation](../frontend/README.md)
- [Core-System Docs](../core/README.md)
- [Finance-Dokumentation](../finance/README.md)
- [Architecture Blueprint](../../architecture/system_overview.md)

---

**Letzte Aktualisierung:** 30. Dezember 2025
**Maintainer:** K.I.T Solutions Team

