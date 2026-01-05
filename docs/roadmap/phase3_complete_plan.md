---
layout: default
title: Phase 3 Complete Plan - SSO, Admin, HR & Support
parent: Roadmap
nav_order: 6
---

# Phase 3: SSO, Admin, HR & Support - Vollständiger Implementierungsplan

**Status:** 30% Complete → 100% Complete
**Zeitraum:** Q4 2025 - Q1 2026
**Ziel:** Vollständiges Admin-System mit HR-Management und Support-Ticketing

---

## Executive Summary

Phase 3 umfasst **vier Hauptbereiche:**

1. **SSO & Admin** (80% fertig) - Zitadel SSO, Role Mapping, Admin Panel
2. **HR-Modul** (0% fertig) - Leave Management, Sick Notes, Applications
3. **Support-System** (0% fertig) - Ticket-System, Helpdesk
4. **Backend-Infrastruktur** (50% fertig) - Audit Log API, System Settings API

**Gesamtstatus:** ~30% Complete
**Geschätzter Aufwand:** 4-6 Wochen
**Geschätzte Dauer:** 1-1.5 Monate

---

## Teil 1: SSO & Admin (80% Complete)

### ✅ Bereits implementiert

- Zitadel SSO Integration (OAuth2)
- Role Mapping & Wildcard Permissions
- Admin Panel Frontend (5 Pages)
- Admin Backend APIs (Employees, Departments, Roles)

### ⏳ Noch zu tun (20%)

#### 1.1 Audit Log Backend API

**Zeitaufwand:** 3-4 Stunden

**Aufgaben:**
- API Router erstellen (`/api/audit-logs`)
- Service mit Filterung & Pagination
- Frontend anpassen (Mock-Daten entfernen)

**Details:** Siehe separates Dokument `phase3_implementation_plan.md`

#### 1.2 System Settings Backend

**Zeitaufwand:** 4-5 Stunden

**Aufgaben:**
- Datenbank-Modell erstellen
- Alembic Migration
- API Router (`GET/PUT /api/settings`)
- Frontend anpassen (localStorage entfernen)

**Details:** Siehe separates Dokument `phase3_implementation_plan.md`

---

## Teil 2: HR-Modul (0% Complete)

**Zeitaufwand:** 2-3 Wochen

### Features-Übersicht

1. **Leave Management (Urlaubsverwaltung)**
2. **Sick Leave Tracking (Krankmeldungen)**
3. **Applications Management (Bewerbungsverwaltung)**
4. **Team Calendar (Teamkalender)**

---

### 2.1 Leave Management

**Ziel:** Digitale Urlaubsanträge und Genehmigungen

#### Datenbank-Modell

**Tabelle:** `leave_requests`

```python
class LeaveRequest(Base, UUIDMixin):
    """Urlaubsanträge."""
    __tablename__ = "leave_requests"

    employee_id = Column(UUID, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)  # vacation, sick, parental, unpaid
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_count = Column(Integer, nullable=False)  # Arbeitstage
    status = Column(String(20), nullable=False, default="pending")  # pending, approved, rejected
    reason = Column(Text)
    approver_id = Column(UUID, ForeignKey("employees.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approver_id])
```

#### API Endpoints

- `POST /api/hr/leave` - Urlaubsantrag erstellen
- `GET /api/hr/leave` - Liste aller Anträge (gefiltert nach Employee)
- `GET /api/hr/leave/{id}` - Einzelnen Antrag abrufen
- `PUT /api/hr/leave/{id}` - Antrag bearbeiten (nur wenn pending)
- `DELETE /api/hr/leave/{id}` - Antrag löschen (nur wenn pending)
- `POST /api/hr/leave/{id}/approve` - Antrag genehmigen (Manager only)
- `POST /api/hr/leave/{id}/reject` - Antrag ablehnen (Manager only)

#### Frontend-Komponenten

**Dateien:**
- `ui/src/modules/hr/pages/LeaveOverview.vue` - Übersicht aller Anträge
- `ui/src/modules/hr/pages/LeaveRequest.vue` - Antrag erstellen/bearbeiten
- `ui/src/modules/hr/pages/LeaveCalendar.vue` - Kalender-Ansicht
- `ui/src/modules/hr/components/LeaveCard.vue` - Einzelner Antrag (Card)
- `ui/src/modules/hr/components/LeaveForm.vue` - Formular

**UI-Features:**
- Kalender-Picker für Start/End-Datum
- Automatische Berechnung der Arbeitstage
- Status-Badges (Pending, Approved, Rejected)
- Approve/Reject-Buttons für Manager
- Filter nach Status, Mitarbeiter, Zeitraum
- Export zu iCal (für externe Kalender)

#### Business Logic

**Validierungen:**
- Start-Datum darf nicht in der Vergangenheit liegen
- End-Datum muss nach Start-Datum sein
- Überschneidungen mit existierenden Anträgen prüfen
- Verfügbare Urlaubstage prüfen (Employee.vacation_days_available)

**Genehmigungsworkflow:**
1. Employee erstellt Antrag → Status: `pending`
2. Manager erhält Notification
3. Manager genehmigt → Status: `approved`, Urlaubstage werden abgezogen
4. Manager lehnt ab → Status: `rejected`, Rejection-Reason erforderlich

**Notifications:**
- E-Mail an Manager bei neuem Antrag
- E-Mail an Employee bei Genehmigung/Ablehnung
- Push-Notification (wenn Mobile App vorhanden)

---

### 2.2 Sick Leave Tracking

**Ziel:** Digitale Krankmeldungen mit Attest-Upload

#### Datenbank-Modell

**Tabelle:** `sick_leaves`

```python
class SickLeave(Base, UUIDMixin):
    """Krankmeldungen."""
    __tablename__ = "sick_leaves"

    employee_id = Column(UUID, ForeignKey("employees.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # optional bei unbekannter Dauer
    days_count = Column(Integer)
    certificate_required = Column(Boolean, default=False)  # ab 3 Tagen
    certificate_uploaded = Column(Boolean, default=False)
    certificate_document_id = Column(UUID, ForeignKey("documents.id"))
    status = Column(String(20), default="active")  # active, ended, extended
    notes = Column(Text)

    # Relationships
    employee = relationship("Employee", back_populates="sick_leaves")
    certificate = relationship("Document")
```

#### API Endpoints

- `POST /api/hr/sick-leave` - Krankmeldung erstellen
- `GET /api/hr/sick-leave` - Liste aller Krankmeldungen
- `GET /api/hr/sick-leave/{id}` - Einzelne Krankmeldung
- `PUT /api/hr/sick-leave/{id}` - Krankmeldung aktualisieren
- `POST /api/hr/sick-leave/{id}/extend` - Krankmeldung verlängern
- `POST /api/hr/sick-leave/{id}/end` - Krankmeldung beenden
- `POST /api/hr/sick-leave/{id}/upload-certificate` - Attest hochladen

#### Frontend-Komponenten

**Dateien:**
- `ui/src/modules/hr/pages/SickLeaveOverview.vue` - Übersicht
- `ui/src/modules/hr/pages/SickLeaveForm.vue` - Meldung erstellen
- `ui/src/modules/hr/components/SickLeaveCard.vue` - Einzelne Meldung

**UI-Features:**
- Schnell-Meldung (nur Start-Datum)
- Attest-Upload (Drag & Drop)
- Status-Anzeige (Aktiv, Beendet)
- Automatische Erinnerung für Attest (ab Tag 3)
- Verlängern-Button
- Beenden-Button (mit Rückkehr-Datum)

#### Business Logic

**Validierungen:**
- Start-Datum darf nicht in der Zukunft liegen
- Attest erforderlich ab Tag 3
- Keine Überschneidungen mit Urlaubsanträgen

**Automatisierungen:**
- E-Mail an Manager bei neuer Krankmeldung
- Erinnerung an Employee für Attest-Upload (Tag 3)
- Erinnerung an Manager bei fehlendem Attest (Tag 5)
- Automatische Zählung der Krankheitstage pro Jahr

---

### 2.3 Applications Management

**Ziel:** Bewerbungsverwaltung und Recruiting-Prozess

#### Datenbank-Modell

**Tabelle:** `applications`

```python
class Application(Base, UUIDMixin):
    """Bewerbungen."""
    __tablename__ = "applications"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(50))
    position = Column(String(200), nullable=False)
    status = Column(String(50), default="new")  # new, screening, interview, offer, hired, rejected
    source = Column(String(100))  # linkedin, website, referral, etc.
    cv_document_id = Column(UUID, ForeignKey("documents.id"))
    cover_letter = Column(Text)
    expected_salary = Column(Numeric(10, 2))
    earliest_start_date = Column(Date)
    assigned_to = Column(UUID, ForeignKey("employees.id"))  # HR Manager
    notes = Column(Text)

    # Relationships
    cv = relationship("Document")
    assigned_user = relationship("Employee")
    interviews = relationship("Interview", back_populates="application")
```

**Tabelle:** `interviews`

```python
class Interview(Base, UUIDMixin):
    """Interviews."""
    __tablename__ = "interviews"

    application_id = Column(UUID, ForeignKey("applications.id"), nullable=False)
    interview_date = Column(DateTime, nullable=False)
    interviewer_id = Column(UUID, ForeignKey("employees.id"), nullable=False)
    type = Column(String(50), default="phone")  # phone, video, onsite
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled
    feedback = Column(Text)
    rating = Column(Integer)  # 1-5

    # Relationships
    application = relationship("Application", back_populates="interviews")
    interviewer = relationship("Employee")
```

#### API Endpoints

**Applications:**
- `POST /api/hr/applications` - Bewerbung erstellen (auch öffentlich für Bewerbungsformular)
- `GET /api/hr/applications` - Liste aller Bewerbungen
- `GET /api/hr/applications/{id}` - Einzelne Bewerbung
- `PUT /api/hr/applications/{id}` - Bewerbung aktualisieren
- `PUT /api/hr/applications/{id}/status` - Status ändern
- `DELETE /api/hr/applications/{id}` - Bewerbung löschen

**Interviews:**
- `POST /api/hr/applications/{id}/interviews` - Interview anlegen
- `GET /api/hr/applications/{id}/interviews` - Interviews für Bewerbung
- `PUT /api/hr/interviews/{id}` - Interview aktualisieren
- `POST /api/hr/interviews/{id}/feedback` - Feedback hinzufügen

#### Frontend-Komponenten

**Dateien:**
- `ui/src/modules/hr/pages/ApplicationsOverview.vue` - Kanban-Board
- `ui/src/modules/hr/pages/ApplicationDetail.vue` - Detail-Ansicht
- `ui/src/modules/hr/pages/ApplicationForm.vue` - Bewerbungsformular
- `ui/src/modules/hr/components/ApplicationCard.vue` - Bewerbungs-Card
- `ui/src/modules/hr/components/InterviewScheduler.vue` - Interview planen

**UI-Features:**
- Kanban-Board (New → Screening → Interview → Offer → Hired/Rejected)
- Drag & Drop für Status-Änderungen
- CV-Viewer (PDF-Preview)
- Interview-Timeline
- Notes & Feedback-Bereich
- E-Mail-Templates für Absagen/Zusagen

#### Business Logic

**Application Workflow:**
1. Bewerbung eingeht → Status: `new`
2. HR screent → Status: `screening`
3. Interview geplant → Status: `interview`
4. Angebot gemacht → Status: `offer`
5. Eingestellt → Status: `hired` (Employee wird angelegt)
6. Abgelehnt → Status: `rejected` (mit Grund)

**Notifications:**
- E-Mail an HR-Team bei neuer Bewerbung
- E-Mail an Candidate bei Status-Änderung
- Calendar-Invite für Interviews

---

### 2.4 Team Calendar

**Ziel:** Zentrale Übersicht über Abwesenheiten und Ressourcen

#### Features

- **Monatsansicht** - Alle Abwesenheiten auf einen Blick
- **Teamansicht** - Abwesenheiten nach Abteilung gruppiert
- **Ressourcenplanung** - Verfügbare Mitarbeiter pro Tag
- **Konflikt-Erkennung** - Warnung bei zu vielen Abwesenheiten
- **Export** - iCal, Google Calendar, Outlook

#### Frontend-Komponente

**Datei:** `ui/src/modules/hr/pages/TeamCalendar.vue`

**UI-Libraries:**
- FullCalendar (Vue 3 Integration)
- Oder: Custom Calendar mit CSS Grid

**Datenquellen:**
- Leave Requests (approved)
- Sick Leaves (active)
- Public Holidays (aus Settings)

---

### HR-Modul: Implementierungs-Schritte

1. **Woche 1: Leave Management** (5 Tage)
   - Tag 1: Datenbank-Modell + Migration
   - Tag 2: Backend APIs (CRUD + Approval)
   - Tag 3: Frontend (Overview + Form)
   - Tag 4: Business Logic (Validierung, Workflow)
   - Tag 5: Testing & Integration

2. **Woche 2: Sick Leave + Applications** (5 Tage)
   - Tag 1-2: Sick Leave (Backend + Frontend)
   - Tag 3-4: Applications (Backend + Frontend)
   - Tag 5: Testing & Integration

3. **Woche 3: Team Calendar + Polish** (5 Tage)
   - Tag 1-2: Team Calendar
   - Tag 3: Notifications & E-Mails
   - Tag 4: Documentation
   - Tag 5: Final Testing & Deployment

**Total: 3 Wochen**

---

## Teil 3: Support-System (0% Complete)

**Zeitaufwand:** 1-2 Wochen

### Features-Übersicht

1. **Ticket-System** - Support-Anfragen verwalten
2. **Knowledge Base** - Self-Service-Artikel
3. **Internal Chat** - Echtzeit-Support (optional)

---

### 3.1 Ticket-System

**Ziel:** Interne und externe Support-Anfragen verwalten

#### Datenbank-Modell

**Tabelle:** `tickets`

```python
class Ticket(Base, UUIDMixin):
    """Support-Tickets."""
    __tablename__ = "tickets"

    ticket_number = Column(String(20), unique=True, nullable=False)  # AUTO-12345
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="open")  # open, in_progress, waiting, resolved, closed
    priority = Column(String(50), default="medium")  # low, medium, high, urgent
    category = Column(String(100))  # technical, billing, hr, general

    # Requester (kann Employee oder externer User sein)
    requester_type = Column(String(50), nullable=False)  # employee, customer, anonymous
    requester_id = Column(UUID)  # Employee oder Customer ID
    requester_email = Column(String(100), nullable=False)
    requester_name = Column(String(200))

    # Assignment
    assigned_to = Column(UUID, ForeignKey("employees.id"))
    assigned_at = Column(DateTime)

    # Timestamps
    first_response_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)

    # Relationships
    assignee = relationship("Employee")
    comments = relationship("TicketComment", back_populates="ticket")
    attachments = relationship("Document", secondary="ticket_attachments")
```

**Tabelle:** `ticket_comments`

```python
class TicketComment(Base, UUIDMixin):
    """Kommentare/Antworten auf Tickets."""
    __tablename__ = "ticket_comments"

    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    author_type = Column(String(50), nullable=False)  # employee, customer, system
    author_id = Column(UUID)
    author_name = Column(String(200))
    author_email = Column(String(100))
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Nur für Mitarbeiter sichtbar

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
```

#### API Endpoints

**Tickets:**
- `POST /api/support/tickets` - Ticket erstellen (öffentlich)
- `GET /api/support/tickets` - Liste aller Tickets (Employee only)
- `GET /api/support/tickets/{id}` - Einzelnes Ticket
- `PUT /api/support/tickets/{id}` - Ticket aktualisieren
- `PUT /api/support/tickets/{id}/status` - Status ändern
- `PUT /api/support/tickets/{id}/assign` - Ticket zuweisen
- `DELETE /api/support/tickets/{id}` - Ticket löschen

**Comments:**
- `POST /api/support/tickets/{id}/comments` - Kommentar hinzufügen
- `GET /api/support/tickets/{id}/comments` - Kommentare abrufen

**Public Endpoints (ohne Auth):**
- `POST /api/public/support/tickets` - Öffentliches Ticket-Formular
- `GET /api/public/support/tickets/{id}?token={token}` - Ticket-Status prüfen

#### Frontend-Komponenten

**Dateien:**
- `ui/src/modules/support/pages/TicketOverview.vue` - Ticket-Liste
- `ui/src/modules/support/pages/TicketDetail.vue` - Ticket-Detail mit Kommentaren
- `ui/src/modules/support/pages/TicketForm.vue` - Neues Ticket
- `ui/src/modules/support/components/TicketCard.vue` - Ticket-Card
- `ui/src/modules/support/components/CommentThread.vue` - Kommentar-Thread

**UI-Features:**
- Ticket-Liste mit Filterung (Status, Priority, Category, Assigned)
- Ticket-Detail mit Timeline
- Kommentar-Editor (Markdown-Support)
- Datei-Anhänge (Drag & Drop)
- Status-Änderung per Dropdown
- Schnell-Actions (Assign to me, Mark as resolved)
- Öffentliches Ticket-Formular (für externe Anfragen)

#### Business Logic

**Ticket-Workflow:**
1. Ticket erstellt → Status: `open`, E-Mail an Support-Team
2. Mitarbeiter nimmt an → Status: `in_progress`, assigned_to gesetzt
3. Wartet auf Rückmeldung → Status: `waiting`
4. Lösung bereitgestellt → Status: `resolved`, resolved_at gesetzt
5. Ticket geschlossen → Status: `closed`, closed_at gesetzt

**SLA (Service Level Agreement):**
- **First Response:** 4 Stunden für high/urgent, 24h für medium/low
- **Resolution Time:** 24h für urgent, 48h für high, 7 Tage für medium/low

**Notifications:**
- E-Mail an Requester bei Status-Änderung
- E-Mail an Assignee bei neuem Kommentar
- Slack-Notification bei urgent Tickets (optional)

---

### 3.2 Knowledge Base

**Ziel:** Self-Service-Artikel für häufige Fragen

#### Datenbank-Modell

**Tabelle:** `kb_articles`

```python
class KBArticle(Base, UUIDMixin):
    """Knowledge-Base-Artikel."""
    __tablename__ = "kb_articles"

    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)  # SEO-friendly URL
    content = Column(Text, nullable=False)  # Markdown
    category = Column(String(100))
    tags = Column(JSON)  # ["email", "password", "login"]
    is_published = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    author_id = Column(UUID, ForeignKey("employees.id"))

    # Relationships
    author = relationship("Employee")
```

#### API Endpoints

- `POST /api/kb/articles` - Artikel erstellen (Employee only)
- `GET /api/kb/articles` - Liste aller Artikel (öffentlich)
- `GET /api/kb/articles/{slug}` - Einzelner Artikel (öffentlich)
- `PUT /api/kb/articles/{id}` - Artikel aktualisieren
- `DELETE /api/kb/articles/{id}` - Artikel löschen

#### Frontend-Komponenten

**Dateien:**
- `ui/src/modules/support/pages/KnowledgeBase.vue` - Artikel-Übersicht
- `ui/src/modules/support/pages/ArticleView.vue` - Artikel-Ansicht
- `ui/src/modules/support/pages/ArticleEditor.vue` - Artikel erstellen/bearbeiten

**UI-Features:**
- Kategorie-Navigation
- Volltext-Suche
- Markdown-Rendering
- Syntax-Highlighting für Code
- "War dieser Artikel hilfreich?" Voting

---

### 3.3 Internal Chat (Optional)

**Ziel:** Echtzeit-Support-Chat zwischen Employees

**Hinweis:** Bereits ein Chat-Modul in Phase 2 implementiert?
Wenn ja, für Support-Team erweitern.

**Features:**
- Support-Channel (#support)
- @mentions für Support-Team
- Ticket aus Chat erstellen

---

### Support-System: Implementierungs-Schritte

1. **Woche 1: Ticket-System** (5 Tage)
   - Tag 1: Datenbank-Modell + Migration
   - Tag 2: Backend APIs
   - Tag 3-4: Frontend (Ticket-Liste, Detail, Form)
   - Tag 5: Notifications & Testing

2. **Woche 2: Knowledge Base + Polish** (optional, 3-5 Tage)
   - Tag 1-2: Knowledge Base (Backend + Frontend)
   - Tag 3: Public Ticket Form
   - Tag 4: Documentation
   - Tag 5: Testing & Deployment

**Total: 1-2 Wochen**

---

## Gesamtübersicht Phase 3

### Timeline

```
Woche 1:  Admin Backend fertigstellen (Audit Log, System Settings)
Woche 2:  HR Leave Management
Woche 3:  HR Sick Leave + Applications
Woche 4:  HR Team Calendar + Ticket-System Backend
Woche 5:  Ticket-System Frontend + Knowledge Base
Woche 6:  Testing, Documentation, Deployment
```

**Total: 6 Wochen**

### Aufwands-Breakdown

| Bereich | Aufwand | Status |
|---------|---------|--------|
| SSO & Admin (Audit Log, Settings) | 8-12h | 80% → 100% |
| HR Leave Management | 1 Woche | 0% → 100% |
| HR Sick Leave | 2-3 Tage | 0% → 100% |
| HR Applications | 2-3 Tage | 0% → 100% |
| HR Team Calendar | 2 Tage | 0% → 100% |
| Support Ticket-System | 1 Woche | 0% → 100% |
| Support Knowledge Base | 2-3 Tage | 0% → 100% |
| Testing & Documentation | 1 Woche | - |

**Total: 4-6 Wochen**

---

## Erfolgskriterien Phase 3

Phase 3 gilt als abgeschlossen, wenn:

### Admin
- [x] Zitadel SSO funktioniert
- [x] Role Mapping funktioniert
- [x] Wildcard Permissions funktionieren
- [x] Admin Panel Frontend ist vollständig
- [ ] Audit Log Backend API funktioniert
- [ ] System Settings Backend funktioniert

### HR
- [ ] Leave Requests können erstellt, genehmigt und abgelehnt werden
- [ ] Sick Leaves können erfasst und Atteste hochgeladen werden
- [ ] Applications können verwaltet und durch den Hiring-Prozess geführt werden
- [ ] Team Calendar zeigt alle Abwesenheiten korrekt an
- [ ] Notifications funktionieren (E-Mail bei Anträgen)

### Support
- [ ] Tickets können erstellt und zugewiesen werden
- [ ] Ticket-Kommentare funktionieren
- [ ] Status-Workflow funktioniert (open → resolved → closed)
- [ ] Öffentliches Ticket-Formular funktioniert
- [ ] Knowledge Base ist abrufbar

### Allgemein
- [ ] Alle APIs sind dokumentiert (OpenAPI/Swagger)
- [ ] Tests sind geschrieben und bestehen (min. 70% Coverage)
- [ ] Dokumentation ist vollständig
- [ ] Performance-Tests bestehen (>100 concurrent users)
- [ ] Security-Review durchgeführt

---

## Risiken & Mitigationen

### Risiko 1: Zu großer Scope

**Problem:** Phase 3 ist sehr umfangreich (Admin + HR + Support)

**Mitigation:**
- Priorisierung: Admin zuerst (kritisch), dann HR, dann Support
- MVP-Ansatz: Erst Kern-Features, dann Nice-to-Haves
- Optional: Support-System auf Phase 4 verschieben

### Risiko 2: Komplexe HR-Workflows

**Problem:** Leave-Approval und Sick-Leave-Tracking sind komplex

**Mitigation:**
- Klare Business-Rules dokumentieren (vor Implementierung)
- Schrittweiser Workflow (erst einfach, dann erweitern)
- Stakeholder-Feedback einholen (HR-Team)

### Risiko 3: Notifications & E-Mails

**Problem:** E-Mail-Versand kann fehleranfällig sein

**Mitigation:**
- E-Mail-Service abstrahieren (z.B. SendGrid, Mailgun)
- Queue-System für zuverlässigen Versand (Celery)
- Fallback: In-App-Notifications

---

## Alternativer Ansatz: Phasen-Aufteilung

Falls 6 Wochen zu lang sind, kann Phase 3 aufgeteilt werden:

### Phase 3A: Admin & HR (4 Wochen)
- Admin Backend (Audit Log, Settings)
- HR-Modul (Leave, Sick Leave, Applications, Calendar)

### Phase 3B: Support (2 Wochen)
- Ticket-System
- Knowledge Base

**Empfehlung:** Phase 3A zuerst, dann 3B basierend auf Bedarf

---

## Nächste Schritte

1. **Strategie-Entscheidung:** Vollständige Phase 3 (6 Wochen) oder Aufteilung?
2. **Priorisierung:** Welche Features sind MUST-HAVE?
3. **Team-Verfügbarkeit:** Reicht ein Entwickler oder Team benötigt?
4. **Stakeholder-Alignment:** HR-Team & Support-Team einbinden
5. **Start:** Admin Backend fertigstellen (1-2 Tage), dann HR

---

## Zusammenfassung

**Phase 3 bringt WorkmateOS auf Vollständigkeit:**
- 🔐 SSO & Admin (Fast fertig, nur Backend APIs fehlen)
- 👥 HR-Management (Leave, Sick Leave, Applications, Calendar)
- 🎫 Support-System (Tickets, Knowledge Base)

**Geschätzter Aufwand:** 4-6 Wochen
**Aktueller Status:** ~30% Complete
**Ziel:** Produktionsreifes System mit allen Kern-Features

**Priorität:**
1. Admin Backend fertigstellen (kritisch)
2. HR Leave Management (high value)
3. HR Sick Leave + Applications (medium value)
4. Support Ticket-System (medium value)
5. Knowledge Base (nice to have)

---

**Erstellt:** 05. Januar 2026
**Autor:** Claude Code & Joshua Phu Kuhrau
**Version:** 1.0 (Complete Plan)
**Status:** Ready for Implementation

🚀 **Let's build Phase 3: Admin, HR & Support!**
