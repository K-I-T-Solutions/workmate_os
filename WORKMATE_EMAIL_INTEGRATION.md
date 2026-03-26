# Task: WorkmateOS – E-Mail Integration (n8n → API)

## Kontext

WorkmateOS ist ein FastAPI/PostgreSQL/Vue.js-basiertes ERP/CRM-System von K.I.T. Solutions.
Drei mailcow-Postfächer sollen per n8n (IMAP Polling) Tickets und Kontakte in WorkmateOS erstellen:

- `support@kit-it-koblenz.de` → Ticket (Typ: Support)
- `kontakt@kit-it-koblenz.de` → Kontakt matchen/anlegen + Ticket (Typ: Anfrage)
- `info@kit-it-koblenz.de`    → Kontakt matchen/anlegen + Ticket (Typ: Info)

---

## Deine Aufgabe

Implementiere folgende Komponenten in WorkmateOS:

### 1. Datenbankmodell (PostgreSQL / SQLAlchemy)

Erstelle oder erweitere folgende Tabellen, falls noch nicht vorhanden:

**`contacts`**
```
id, email (unique), name, phone, company, created_at, updated_at
```

**`tickets`**
```
id, subject, body, from_email, from_name, source (enum: email/web/manual),
mailbox (enum: support/kontakt/info), ticket_type (enum: support/anfrage/info),
status (enum: open/in_progress/closed), contact_id (FK → contacts, nullable),
created_at, updated_at
```

Nutze Alembic für die Migration. Erstelle eine neue Migrationsdatei.

---

### 2. FastAPI Endpoints

Erstelle `app/routers/email_intake.py` mit folgenden Endpoints:

#### POST `/api/v1/email/ingest`

Nimmt eine eingehende E-Mail entgegen und:
1. Matched oder erstellt einen Kontakt anhand der `from_email`
2. Erstellt ein Ticket mit korrektem `ticket_type` basierend auf `mailbox`
3. Verknüpft Ticket mit Kontakt
4. Gibt Ticket-ID und Contact-ID zurück

**Request Body (JSON):**
```json
{
  "subject": "string",
  "body": "string",
  "from_email": "string",
  "from_name": "string",
  "mailbox": "support | kontakt | info",
  "received_at": "ISO8601 datetime (optional)"
}
```

**Response:**
```json
{
  "ticket_id": "int",
  "contact_id": "int",
  "contact_created": "bool",
  "ticket_type": "string",
  "status": "open"
}
```

#### GET `/api/v1/email/tickets`

Listet alle Tickets. Query-Parameter: `mailbox`, `status`, `limit`, `offset`.

#### GET `/api/v1/email/tickets/{ticket_id}`

Gibt ein einzelnes Ticket mit zugehörigem Kontakt zurück.

#### GET `/api/v1/contacts?email={email}`

Sucht einen Kontakt per E-Mail. Wird von n8n vor dem Ingest genutzt (optional, da Ingest das intern macht).

---

### 3. Authentifizierung

- Nutze den bestehenden Auth-Mechanismus in WorkmateOS (Bearer Token / API Key)
- Erstelle einen dedizierten **Service-Account / API-Key** für n8n mit dem Scope `email:ingest`
- Der Key soll in der DB gespeichert werden (Tabelle `api_keys` oder äquivalent)
- Gib den generierten Key am Ende aus (einmalig, danach gehasht gespeichert)

Falls noch kein API-Key-System existiert: Implementiere ein einfaches, sicheres System:
```
api_keys: id, name, key_hash (bcrypt), scopes (JSON array), active, created_at
```
Middleware prüft `Authorization: Bearer <key>` Header.

---

### 4. n8n Workflow (JSON Export)

Erstelle `n8n/email_intake_workflow.json` – einen vollständigen n8n-Workflow der:

1. **Trigger:** IMAP-Node (3 separate Trigger-Nodes, einer pro Postfach)
   - Host: `mail.kit-it-koblenz.de`, Port: `993`, SSL: true
   - Polling-Intervall: 60 Sekunden
   - Nach Abruf: E-Mail als gelesen markieren

2. **Set-Node:** Extrahiert `subject`, `body` (text/plain bevorzugt), `from_email`, `from_name`, setzt `mailbox`-Wert

3. **HTTP Request-Node:** POST an `https://workmate.kit-it-koblenz.de/api/v1/email/ingest`
   - Header: `Authorization: Bearer {{$credentials.workmateApiKey}}`
   - Body: JSON aus Set-Node

4. **IF-Node:** Prüft ob HTTP Status 200/201 → Error-Branch loggt in n8n

Nutze n8n Credentials für IMAP-Passwörter und den WorkmateOS API Key – **keine Hardcoded Credentials im Workflow**.

---

### 5. Dateien die erstellt/bearbeitet werden sollen

```
app/
  models/
    contact.py          (neu oder erweitern)
    ticket.py           (neu oder erweitern)
    api_key.py          (neu, falls nicht vorhanden)
  routers/
    email_intake.py     (neu)
  schemas/
    email_intake.py     (Pydantic Schemas, neu)
  services/
    email_intake.py     (Business Logic, neu)
  core/
    auth.py             (erweitern um API Key Auth)
alembic/versions/
  XXXX_add_email_intake_tables.py  (neu)
n8n/
  email_intake_workflow.json       (neu)
tests/
  test_email_intake.py             (neu, pytest)
```

---

### 6. Tests

Schreibe `tests/test_email_intake.py` mit pytest:
- POST `/api/v1/email/ingest` mit neuem Kontakt → prüfe Ticket + Contact erstellt
- POST mit bekannter E-Mail → prüfe Contact gematcht (nicht doppelt angelegt)
- POST mit falschem API Key → prüfe 401
- Je ein Test pro mailbox-Typ (support/kontakt/info) → prüfe korrekten ticket_type

---

## Hinweise

- Nutze den bestehenden Stack: FastAPI, SQLAlchemy (async wenn bereits so genutzt), PostgreSQL, Alembic
- Folge dem bestehenden Code-Stil im Projekt
- Kein Breaking Change an bestehenden Endpoints
- Alle neuen Endpoints unter `/api/v1/email/`
- Logging: Nutze das bestehende Logger-Setup, logge jeden Ingest mit ticket_id und contact_id
- Bei HTML-Mails: Extrahiere Plain-Text via `html2text` oder `BeautifulSoup` (pip-Dependency ergänzen)

## Starte mit

1. Lies die bestehende Projektstruktur (`app/`, `alembic/`, `requirements.txt`)
2. Prüfe welche Models/Auth bereits existieren
3. Implementiere dann schrittweise in der Reihenfolge: Models → Migration → Schemas → Service → Router → Tests → n8n Workflow
