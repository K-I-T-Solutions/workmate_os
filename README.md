
<p align="center">
  <img src="/assets/workmate_white_transparent.png#gh-light-mode-only" width="420" alt="K.I.T. Workmate Logo">
</p>

<h3 align="center">The internal toolkit.</h3>

<p align="center">
  <a href="https://github.com/K-I-T-Solutions/workmate_os"><img src="https://img.shields.io/badge/Version-v4.0.0-blue?style=flat-square&logo=git" /></a>
  <a href="https://k-i-t-solutions.github.io/workmate_os/"><img src="https://img.shields.io/badge/Docs-Online-success?style=flat-square&logo=readthedocs" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Phase-4%20(100%25)-brightgreen?style=flat-square&logo=github" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Framework-Vue%203-42b883?style=flat-square&logo=vue.js" /></a>
  <a href="#"><img src="https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Auth-Zitadel%20SSO-5469d4?style=flat-square&logo=oauth" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Dockerized-Yes-0db7ed?style=flat-square&logo=docker" /></a>
</p>

---

# 🧠 Workmate OS  
**Das modulare Betriebssystem für deinen Büroalltag.**  
Kompakt. Schnell. Intuitiv. – powered by **Joshua Phu Kuhrau / K.I.T. Solutions**

---

## 🚀 Überblick

**Workmate OS** ist eine modulare Verwaltungsplattform für alle organisatorischen Aufgaben.  
Von Personal über Kunden bis zu Tickets, Finanzen und Dokumentenverwaltung – alles läuft zentral, sicher und integriert.  

Ziel ist es, Verwaltungsarbeit **endlich einfach und modern** zu machen:  
✅ weniger Klicks, 🧩 mehr Übersicht, ⚡ maximale Performance.

---

## 🧩 Module

### ✅ Phase 1 & 2: Core & Backoffice (100%)

| Modul | Beschreibung | Status |
|:--|:--|:--:|
| 👤 **Employees** | Mitarbeiter, Abteilungen, Rollen mit SSO-Integration | ✅ |
| 📁 **Documents** | Dokumenten-Upload mit Checksum-Validierung | ✅ |
| 🔔 **Reminders** | Erinnerungen mit polymorphen Verknüpfungen | ✅ |
| 📊 **Dashboards** | Personalisierbare User-Dashboards | ✅ |
| 💼 **CRM** | Customer & Contact Management mit Activity Tracking | ✅ |
| 📁 **Projects** | Projekt-Management mit Budget-Tracking | ✅ |
| 🧾 **Invoices** | Rechnungserstellung mit PDF-Generierung | ✅ |
| 💰 **Finance** | Ausgaben-Management & Belege | ✅ |
| 🕒 **Time Tracking** | Zeiterfassung mit billable/non-billable Hours | ✅ |
| 💬 **Chat** | Messaging-System (in Development) | ✅ |

### ✅ Phase 3: SSO & Admin (100%)

| Modul | Beschreibung | Status |
|:--|:--|:--:|
| 🔐 **Keycloak SSO** | OAuth2/OIDC Integration | ✅ |
| 🛡️ **Role Mapping** | Keycloak → Backend Role Sync | ✅ |
| 🎯 **Wildcard Permissions** | Flexible Permission System (*, backoffice.*) | ✅ |
| 🛠️ **Admin Panel** | 5 Admin-Seiten (Users, Depts, Roles, Audit, Settings) | ✅ |
| 📋 **Audit Log** | System Events Tracking mit User-Enrichment | ✅ |
| ⚙️ **System Settings** | Global Configuration (Frontend + Backend) | ✅ |
| 👤 **User Settings** | Persönliche Einstellungen (Sprache, Zeitzone) | ✅ |
| 📊 **CRM Activity Timeline** | Automatisches Logging aller CRM-Operationen | ✅ |

### ✅ Phase 4: HR & Support (100%)

| Modul | Beschreibung | Status |
|:--|:--|:--:|
| 🏖️ **HR Self-Service** | Urlaubsanträge, Saldo, Genehmigungsworkflow | ✅ |
| 👥 **HR Recruiting** | Job Postings, Bewerbungs-Pipeline mit Rating | ✅ |
| 🎫 **Support Tickets** | Ticket-System mit Kommentaren, internen Notizen | ✅ |
| 📚 **Knowledge Base** | Interne Wiki mit Markdown, Suche, Voting | ✅ |

### 📅 Phase 5: Enterprise (Planned)

| Modul | Beschreibung | Status |
|:--|:--|:--:|
| 🏦 **Banking API** | Kontoauszüge automatisch importieren | 📅 |
| 💼 **Elster Integration** | Deutsche Steuerverwaltung | 📅 |
| 📱 **Mobile App** | React Native / Flutter App | 📅 |

---

## 🧠 Tech-Stack

| Bereich | Technologie |
|:--|:--|
| Frontend | Vue 3 + TypeScript + Vite + Pinia |
| Backend | FastAPI (Python 3.13) + SQLAlchemy 2.0 + PostgreSQL 16 |
| Authentifizierung | Zitadel SSO (OAuth2/OIDC) + JWT |
| Infrastruktur | Docker Compose + Nginx (Reverse Proxy & SSL) |
| Design | Custom Dark Theme + K.I.T. Solutions Branding |
| CI/CD | GitHub Actions (automatisches Deployment) |

---

## 📚 Dokumentation

**Umfassende Online-Dokumentation:** [https://k-i-t-solutions.github.io/workmate_os/](https://k-i-t-solutions.github.io/workmate_os/)

**Quick Links:**
- 🏗️ [System-Architektur](https://k-i-t-solutions.github.io/workmate_os/architecture/system_overview) - Visuelle Diagramme & Flows
- 🔐 [Authentication & SSO](https://k-i-t-solutions.github.io/workmate_os/wiki/backend/AUTHENTICATION) - Zitadel Integration Guide
- 🛠️ [Admin Panel](https://k-i-t-solutions.github.io/workmate_os/wiki/backend/ADMIN_PANEL) - Admin Interface Docs
- 📦 [Backend Module](https://k-i-t-solutions.github.io/workmate_os/wiki/backend/MODULE_UEBERSICHT) - Alle 11 Module
- 🎨 [Frontend](https://k-i-t-solutions.github.io/workmate_os/wiki/frontend/) - Vue 3 Architektur
- 💰 [Finance](https://k-i-t-solutions.github.io/workmate_os/wiki/finance/) - Rechnungswesen (DE/EN)
- 🗺️ [Roadmap](https://k-i-t-solutions.github.io/workmate_os/roadmap/) - Development Phasen

---

## 🌐 Production

Die Anwendung läuft produktiv auf:

* 🖥️ **Frontend:** [https://workmate.kit-it-koblenz.de](https://workmate.kit-it-koblenz.de)
* 🌐 **API:** [https://api.workmate.kit-it-koblenz.de](https://api.workmate.kit-it-koblenz.de)
* 📚 **API Docs:** [https://api.workmate.kit-it-koblenz.de/docs](https://api.workmate.kit-it-koblenz.de/docs)

**Deployment:**
- Automatisches Deployment via GitHub Actions bei Push auf `main`
- Docker Compose mit Traefik Reverse Proxy
- Let's Encrypt SSL-Zertifikate
- Vollständig containerisiert (PostgreSQL, Backend, Frontend)

---

## 🛠️ Entwicklung

```bash
# Backend starten
make backend-up

# Frontend starten
make ui-up

# Gesamtes Dev-System
make dev-up
```

**Branch-Strategie:**
- `main` - Production-Branch (automatisches Deployment)
- `dev` - Development-Branch für neue Features
- Feature-Branches → PR zu `dev` → PR zu `main`

**📖 Siehe auch:** [Setup Guide](docs/setup/README.md) für detaillierte Installationsanweisungen

---

## 🌍 Vision

Workmate OS ist Teil der **K.I.T. Solutions-Philosophie**:

> *Ethische, offene und nachhaltige IT – für Menschen, nicht gegen sie.*

Das Ziel ist ein vollständig offenes, selbst-hostbares System für moderne Unternehmensverwaltung.
Von kleinen Teams bis zu Organisationen, die Wert auf **Datenschutz, Effizienz und Ästhetik** legen.

---

## 💡 Autor & Credits

**Joshua Phu Kuhrau**
*Fachinformatiker – Systemintegration*
K.I.T. Solutions • Koblenz, Deutschland
🌐 [kit-it-koblenz.de](https://kit-it-koblenz.de)

---

## 📊 Development Progress

```
Phase 1: Core System         ████████████████ 100% ✅
Phase 2: Backoffice          ████████████████ 100% ✅
Phase 3: SSO & Admin         ████████████████ 100% ✅
Phase 4: HR & Support        ████████████████ 100% ✅
Phase 5: Enterprise          ░░░░░░░░░░░░░░░░   0% 📅

Overall Documentation        ██████████████░░  85% 📚
```

**Current Version:** v4.0.0 — Phase 4 abgeschlossen
**Next Sprint:** Phase 5 (Banking API, Elster Integration, Mobile App)

---

> "Work smarter, not harder – mit Workmate OS wird's endlich Realität." 🧩

---

<p align="center">
  <strong>Weitere Infos:</strong><br>
  <a href="https://k-i-t-solutions.github.io/workmate_os/">📚 Dokumentation</a> •
  <a href="docs/roadmap/README.md">🗺️ Roadmap</a> •
  <a href="docs/architecture/system_overview.md">🏗️ Architektur</a> •
  <a href="https://kit-it-koblenz.de">🌐 K.I.T. Solutions</a>
</p>

---
