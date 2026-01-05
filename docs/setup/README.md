---
layout: default
title: Setup
nav_order: 3
has_children: true
---

# ⚙️ Setup & Konfiguration

**Installation und Konfiguration von WorkmateOS**

---

## 📋 Setup-Anleitungen

### [Zitadel SSO Setup](./zitadel_setup.md)
Vollständige Anleitung zur Konfiguration von Zitadel als Identity Provider:
- Zitadel Installation
- Application erstellen
- Rollen konfigurieren
- Backend-Integration
- Frontend-Integration

---

## 🚀 Quick Start

### Development Setup

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
cd ui
npm install
npm run dev
```

**3. Database:**
```bash
docker-compose up -d postgres
```

---

## 🔧 Konfiguration

### Environment Variables

**Backend (`.env`):**
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/workmate
ZITADEL_ISSUER=https://zitadel.example.com
ZITADEL_CLIENT_ID=your-client-id
ZITADEL_CLIENT_SECRET=your-secret
```

**Frontend (`ui/.env`):**
```bash
VITE_API_URL=http://localhost:8000
VITE_ZITADEL_ISSUER=https://zitadel.example.com
VITE_ZITADEL_CLIENT_ID=your-client-id
```

---

## 📚 Siehe auch

- [Backend Module](../wiki/backend/MODULE_UEBERSICHT.md)
- [Frontend Architektur](../wiki/frontend/architecture.md)
- [System-Architektur](../architecture/system_overview.md)

---

**Letzte Aktualisierung:** 30. Dezember 2025
