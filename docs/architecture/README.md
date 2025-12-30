# 🏗️ Architektur-Dokumentation

**System-Architektur und Design-Entscheidungen**

---

## 📋 Dokumente

### [System-Übersicht](./system_overview.md)
High-level Architektur von WorkmateOS mit:
- Tech Stack
- Komponenten-Übersicht
- Datenflüsse
- Deployment-Architektur

---

## 🔧 Tech Stack

**Frontend:**
- Vue 3 (Composition API)
- TypeScript
- Vite
- Pinia (State Management)

**Backend:**
- FastAPI (Python 3.13)
- SQLAlchemy 2.0
- PostgreSQL 16
- Alembic (Migrations)

**Authentication:**
- Zitadel (OAuth2/OIDC)

**Deployment:**
- Docker
- Docker Compose
- GitHub Actions (CI/CD)

---

## 🌐 System-Komponenten

```
┌─────────────────────────────────────────────────────────┐
│                    WorkmateOS                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────┐             │
│  │              │         │              │             │
│  │   Frontend   │────────▶│   Backend    │             │
│  │   (Vue 3)    │  REST   │   (FastAPI)  │             │
│  │              │◀────────│              │             │
│  └──────────────┘         └──────┬───────┘             │
│         │                        │                     │
│         │                        ▼                     │
│         │                 ┌──────────────┐             │
│         │                 │              │             │
│         │                 │  PostgreSQL  │             │
│         │                 │              │             │
│         │                 └──────────────┘             │
│         │                                              │
│         ▼                                              │
│  ┌──────────────┐                                      │
│  │              │                                      │
│  │   Zitadel    │                                      │
│  │   (SSO)      │                                      │
│  │              │                                      │
│  └──────────────┘                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Siehe auch

- [Backend Architektur](../wiki/backend/README.md)
- [Frontend Architektur](../wiki/frontend/architecture.md)
- [Datenbank Schema](../wiki/core/core_erm.dbml)

---

**Letzte Aktualisierung:** 30. Dezember 2025
