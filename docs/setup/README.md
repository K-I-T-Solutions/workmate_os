---
layout: default
title: Setup
nav_order: 3
has_children: true
---

# Setup & Konfiguration

**Installation und Konfiguration von WorkmateOS**

---

## Development Setup

```bash
# Gesamtes Dev-System starten
make dev-up

# Datenbank-Migrationen
make db-migrate
```

Lokale Umgebung nach `make dev-up`:

- **UI:** https://workmate.test
- **API:** https://api.workmate.test
- **API Docs:** https://api.workmate.test/docs
- **Login:** https://login.workmate.test (Keycloak)

---

## Manuell (ohne Make)

**1. Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**2. Frontend:**
```bash
cd ui-v3
npm install
npm run dev
```

**3. Datenbank:**
```bash
docker compose up -d postgres
```

---

## Environment Variables

**Backend (`.env`):**
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/workmate
KEYCLOAK_URL=https://login.kit-it-koblenz.de
KEYCLOAK_REALM=kit
KEYCLOAK_CLIENT_ID=workmate
KEYCLOAK_CLIENT_SECRET=your-secret
SMTP_HOST=your-smtp-host
SMTP_USER=your-smtp-user
SMTP_PASS=your-smtp-pass
```

**Frontend (`ui-v3/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=https://api.workmate.kit-it-koblenz.de
NEXTAUTH_URL=https://workmate.kit-it-koblenz.de
NEXTAUTH_SECRET=your-secret
KEYCLOAK_CLIENT_ID=workmate
KEYCLOAK_CLIENT_SECRET=your-secret
KEYCLOAK_ISSUER=https://login.kit-it-koblenz.de/realms/kit
```

---

## Production Deploy

Deploy läuft via GitHub Actions auf `workmate-01` (Hetzner). Manuell:

```bash
./deploy.sh
```

Alembic-Migrationen werden automatisch beim Deploy ausgeführt.

---

## Siehe auch

- [Backend Module](../wiki/backend/MODULE_UEBERSICHT.md)
- [Frontend Architektur](../wiki/frontend/architecture.md)
- [System-Architektur](../architecture/system_overview.md)

---

**Stand:** Juni 2026 · WorkmateOS v3.0
