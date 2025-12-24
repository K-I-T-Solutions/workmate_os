
<p align="center">
  <img src="/assets/workmate_white_transparent.png#gh-light-mode-only" width="420" alt="K.I.T. Workmate Logo">
</p>

<h3 align="center">The internal toolkit.</h3>

<p align="center">
  <a href="https://github.com/K-I-T-Solutions/workmate_os"><img src="https://img.shields.io/badge/Version-v1.0.0-green?style=flat-square&logo=git" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Framework-Vue%203-42b883?style=flat-square&logo=vue.js" /></a>
  <a href="#"><img src="https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Auth-Keycloak-ff9100?style=flat-square&logo=keycloak" /></a>
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

| Modul | Beschreibung | Status |
|:--|:--|:--:|
| 👤 **HR / Personalverwaltung** | Mitarbeiterdaten, Verträge & Personalakten zentral verwalten | ✅ |
| 🕒 **Zeiterfassung** | Start/Stop-Erfassung, Tages- & Monatsübersicht, Export | ✅ |
| 💼 **CRM** | Kundenverwaltung mit automatischer Kundennummer & Creator-Tracking | ✅ |
| 📁 **Projekte** | Projektmanagement mit Kunden-Verknüpfung, Status & Filterung | ✅ |
| 🧾 **Rechnungen** | Rechnungserstellung mit optionaler Rechnungsnummer | ✅ |
| 💰 **Finanzen** | Zahlungen, Cashflow & Financial Reports | ✅ |
| 💬 **Chat** | Interne Team-Kommunikation | ✅ |
| 📁 **DMS / Dokumentenverwaltung** | Sicherer Upload, Tagging & Zugriff nach Rollen | ✅ |
| 🔔 **Reminder / Fristen-System** | Automatische Erinnerungen & Statusfarben | ✅ |
| 📊 **Dashboard & KPIs** | Kennzahlen, Status & Aktivitätsübersicht | ✅ |
| 🧠 **Systemverwaltung** | Rollen, Berechtigungen & Audit-Logs | ✅ |

---

## 🧠 Tech-Stack

| Bereich | Technologie |
|:--|:--|
| Frontend | Vue 3 + Vite + Tailwind CSS 4 |
| Backend | FastAPI + SQLAlchemy + PostgreSQL 16 |
| Authentifizierung | JWT-basierte Authentifizierung |
| Infrastruktur | Docker Compose + Traefik (Reverse Proxy & SSL) |
| Design | Custom Dark Theme + K.I.T. Solutions Branding |
| CI/CD | GitHub Actions (automatisches Deployment) |

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

> “Work smarter, not harder – mit Workmate OS wird’s endlich Realität.” 🧩

---

💡 **Tipp:**  
Lege deine Logos in dein Repo unter:  

/assets/workmate_white_transparent.png
/assets/workmate_dark_transparent.png
/assets/workmate_favicon.ico

und passe im README die Pfade an (`assets/...` statt nur Dateiname).

---
