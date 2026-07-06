
<p align="center">
  <img src="assets/workmate_white_transparent.png#gh-light-mode-only" width="420" alt="K.I.T. Workmate Logo">
  <img src="assets/workmate_dark_transparent.png#gh-dark-mode-only" width="420" alt="K.I.T. Workmate Logo">
</p>

<h3 align="center">The internal toolkit.</h3>

<p align="center">
  <a href="https://github.com/K-I-T-Solutions/workmate_os/releases/tag/v4.0"><img src="https://img.shields.io/badge/Version-v4.0-orange?style=flat-square&logo=git" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Framework-Next.js%2014-000000?style=flat-square&logo=next.js" /></a>
  <a href="#"><img src="https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Auth-Keycloak-ff9100?style=flat-square&logo=keycloak" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Dockerized-Yes-0db7ed?style=flat-square&logo=docker" /></a>
</p>

---

# WorkmateOS

**Das modulare Betriebssystem für deinen Büroalltag.**
Kompakt. Schnell. Intuitiv. – powered by **K.I.T. Solutions**

---

## Überblick

WorkmateOS ist eine modulare Verwaltungsplattform für alle organisatorischen Aufgaben eines modernen Unternehmens. Von Personal über Kunden bis zu Tickets, Finanzen und Dokumenten – alles läuft zentral, sicher und integriert unter einem Dach.

---

## Module

| Modul | Beschreibung |
|:--|:--|
| **Dashboard** | Kennzahlen, Status & Aktivitätsübersicht |
| **CRM** | Kunden, Kontakte, Pipeline (Kanban), CSV-Import |
| **Rechnungen** | Erstellen, PDF-Export, E-Mail-Versand, DATEV-Export |
| **Projekte** | Projektverwaltung mit Kundenzuordnung |
| **Finanzen** | Transaktionen via n8n-Webhook, Mahnwesen (3 Stufen) |
| **HR** | Mitarbeiterdaten, Urlaub & Abwesenheiten |
| **Support-Tickets** | Ticket-Verwaltung mit E-Mail-Reply direkt aus WorkmateOS |
| **Email Intake** | IMAP-Postfach → automatische Tickets via n8n |
| **Knowledge Base** | Internes Wiki für Teams |
| **Dokumente** | Sicherer Upload mit Kundenzuordnung |
| **Zeiterfassung** | Start/Stop mit Genehmigungsworkflow |
| **Admin** | Rollen, Abteilungen, Benutzerverwaltung |

---

## Tech-Stack

| Bereich | Technologie |
|:--|:--|
| Frontend | Next.js 14 · TypeScript · Tailwind CSS 4 · Base UI |
| Backend | FastAPI · SQLAlchemy · PostgreSQL · Alembic |
| Auth | Keycloak 26 (OIDC, PKCE, RBAC) |
| Infrastruktur | Docker Compose · Traefik (Prod) · Caddy (Dev) |
| Automatisierung | n8n (Email Intake, Transaktionen) |

---

## Entwicklung

```bash
# Gesamtes Dev-System starten
make dev-up

# Datenbank-Migrationen
make db-migrate
```

Lokale Umgebung (nach `make dev-up`):

- **UI:** https://workmate.test
- **API:** https://api.workmate.test
- **API Docs:** https://api.workmate.test/docs
- **Login:** https://login.workmate.test

---

## Deployment

Produktions-Deploy läuft via GitHub Actions auf `workmate-01` (Hetzner):

```bash
# Manuell deployen
./deploy.sh
```

Voraussetzungen: `.env` mit Keycloak- und DB-Credentials, Docker Compose auf dem Server.

---

## Vision

WorkmateOS ist Teil der **K.I.T. Solutions-Philosophie**:

> *Ethische, offene und nachhaltige IT – für Menschen, nicht gegen sie.*

Ziel ist ein vollständig self-hostbares System für moderne Unternehmensverwaltung – von kleinen Teams bis zu wachsenden Organisationen, die Wert auf Datenschutz, Effizienz und ein sauberes UX legen.

---

## Autor

**Joshua Phu Kuhrau**
K.I.T. Solutions · Koblenz
[kit-it-koblenz.de](https://kit-it-koblenz.de)
