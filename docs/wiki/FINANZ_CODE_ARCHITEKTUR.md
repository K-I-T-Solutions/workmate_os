# Finanz- & Rechnungsmodul - Code-Architektur

## Modulstruktur

```
workmate_os/
├── backend/app/modules/backoffice/
│   ├── invoices/
│   │   ├── __init__.py
│   │   ├── models.py                  # SQLAlchemy ORM-Modelle
│   │   │   ├── Invoice               # Haupt-Rechnungsmodell
│   │   │   ├── InvoiceLineItem       # Positionen
│   │   │   ├── Payment               # Zahlungseingänge
│   │   │   └── NumberSequence        # Rechnungsnummerierung
│   │   ├── schemas.py                # Pydantic-Validierung
│   │   │   ├── InvoiceStatus enum
│   │   │   ├── PaymentMethod enum
│   │   │   ├── DocumentType enum
│   │   │   ├── InvoiceCreate/Update/Response
│   │   │   ├── PaymentCreate/Update/Response
│   │   │   ├── InvoiceLineItemCreate/Response
│   │   │   ├── InvoiceStatisticsResponse
│   │   │   └── BulkStatusUpdate
│   │   ├── routes.py                 # FastAPI-Endpoints
│   │   │   ├── list_invoices()       # GET /
│   │   │   ├── get_statistics()      # GET /statistics
│   │   │   ├── get_invoice()         # GET /{id}
│   │   │   ├── create_invoice()      # POST /
│   │   │   ├── update_invoice()      # PATCH /{id}
│   │   │   ├── delete_invoice()      # DELETE /{id}
│   │   │   ├── download_invoice_pdf()# GET /{id}/pdf
│   │   │   ├── add_payment()         # POST /{id}/payments
│   │   │   ├── bulk_update_status()  # POST /bulk/status-update
│   │   │   └── ... (weitere Endpoints)
│   │   ├── crud.py                   # Datenbankoperationen
│   │   │   ├── get_invoices()        # Lesen mit Filtern
│   │   │   ├── create_invoice()      # Erstellen mit Positionen
│   │   │   ├── update_invoice()      # Update Status/Notizen
│   │   │   ├── delete_invoice()      # Kaskadierendes Löschen
│   │   │   ├── recalculate_invoice_totals()
│   │   │   ├── get_invoice_statistics()
│   │   │   ├── _generate_invoice_number()
│   │   │   ├── _generate_next_number()
│   │   │   ├── _validate_customer_exists()
│   │   │   ├── _validate_invoice_number_unique()
│   │   │   └── _generate_and_save_pdf()
│   │   ├── payments_crud.py          # Zahlungsspezifische Operationen
│   │   │   ├── create_payment()      # Erstellen mit Validierung
│   │   │   ├── get_payment()         # Einzelne Zahlung
│   │   │   ├── get_payments()        # Zahlungen auflisten
│   │   │   ├── update_payment()      # Zahlung aktualisieren
│   │   │   └── delete_payment()      # Zahlung löschen
│   │   ├── pdf_generator.py          # PDF-Generierung
│   │   │   ├── generate_invoice_pdf()
│   │   │   ├── format_eur()          # Deutsche Währungsformatierung
│   │   │   ├── draw_logo_watermark()
│   │   │   ├── DOCUMENT_TYPES        # Vorlagenkonfiguration
│   │   │   ├── COMPANY_*             # Firmenkonstanten
│   │   │   ├── BANK_*                # Bankkonstanten
│   │   │   └── ... (Rendering-Funktionen)
│   │   └── templates/               # (Leer, für Zukunft)
│   │
│   └── finance/
│       ├── __init__.py
│       ├── models.py                 # SQLAlchemy ORM-Modelle
│       │   └── Expense               # Ausgaben-/Kostenverfolgung
│       ├── schemas.py                # Pydantic-Validierung
│       │   ├── ExpenseCreate/Update/Read
│       │   ├── ExpenseListResponse
│       │   ├── ExpenseKpiResponse
│       │   └── ExpenseCategory enum
│       ├── router.py                 # FastAPI-Endpoints
│       │   ├── create_expense_endpoint()      # POST /expenses
│       │   ├── list_expenses_endpoint()       # GET /expenses
│       │   ├── get_expense_endpoint()         # GET /expenses/{id}
│       │   ├── update_expense_endpoint()      # PATCH /expenses/{id}
│       │   ├── delete_expense_endpoint()      # DELETE /expenses/{id}
│       │   └── get_expense_kpis_endpoint()    # GET /kpis/expenses
│       └── crud.py (service.py)     # Datenbankoperationen
│           ├── create_expense()
│           ├── get_expense()
│           ├── list_expenses()
│           ├── update_expense()
│           ├── delete_expense()
│           └── get_expense_kpis()
│
├── backend/alembic/versions/
│   ├── 2025_10_24_1224-..._fix_invoice_expense_relationship.py
│   ├── 2025_10_24_1331-..._add_invoices_and_payments_tables.py
│   └── 2025_11_19_1707-..._add_document_type_to_invoices.py
│
├── backend/tests/
│   └── test_invoice.py              # Integrationstests
│
└── backend/app/main.py              # Router-Registrierung
    ├── app.include_router(invoices_router, ...)
    └── app.include_router(finance_routes.router, ...)
```

---

## Datenfluss-Diagramm

### Rechnungserstellungs-Ablauf

```
Benutzeranfrage (API)
    ↓
routes.py::create_invoice()
    ↓
[Validierung]
    ├─ Kunde existiert?
    └─ Projekt existiert?
    ↓
crud.py::create_invoice()
    ├─ Rechnungsnummer generieren (NumberSequence)
    ├─ Invoice-Objekt erstellen
    ├─ InvoiceLineItem-Objekte erstellen
    ├─ recalculate_totals() auf Invoice
    ├─ In Datenbank speichern (commit)
    └─ Optional: PDF generieren
        └─ pdf_generator.py::generate_invoice_pdf()
    ↓
Antwort (InvoiceResponse-Schema)
```

### Zahlungsablauf

```
Benutzeranfrage (API)
    ↓
routes.py::add_payment()
    ↓
payments_crud.py::create_payment()
    ├─ Rechnung existiert?
    ├─ Betrag <= outstanding_amount?
    ├─ Payment-Objekt erstellen
    ├─ In Datenbank speichern
    └─ Rechnungsstatus aktualisieren
        └─ Invoice.update_status_from_payments()
    ↓
SQLAlchemy Event (after_insert)
    └─ Rechnungsstatus automatisch aktualisieren
    ↓
Antwort (PaymentResponse-Schema)
```

### Listen- & Filterablauf

```
Benutzeranfrage (API)
    ↓
routes.py::list_invoices()
    │
    └─ Query-Filter aufbauen:
        ├─ Status-Filter?
        ├─ customer_id-Filter?
        ├─ project_id-Filter?
        ├─ date_from/date_to?
        └─ skip/limit Pagination?
    ↓
crud.py::get_invoices()
    ├─ Filter auf Query anwenden
    ├─ Nach issued_date desc sortieren
    ├─ Offset + Limit
    ├─ Beziehungen Eager-laden (customer, line_items, payments)
    └─ Query ausführen
    ↓
Antwort (InvoiceListResponse-Schema)
```

---

## Datenbankschema-Beziehungen

```
CREATE TABLE invoices (
    id UUID PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE,
    customer_id UUID FOREIGN KEY → customers.id,
    project_id UUID FOREIGN KEY → projects.id,
    total DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    status VARCHAR(50),
    document_type VARCHAR(50),
    issued_date DATE,
    due_date DATE,
    pdf_path TEXT,
    notes TEXT,
    terms TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CHECK (total >= 0),
    CHECK (subtotal >= 0),
    CHECK (status IN (...)),
    INDEX (customer_id),
    INDEX (project_id),
    INDEX (status),
    INDEX (invoice_number)
);

CREATE TABLE invoice_line_items (
    id UUID PRIMARY KEY,
    invoice_id UUID FOREIGN KEY → invoices.id CASCADE,
    position INT,
    description TEXT,
    quantity DECIMAL(10,2),
    unit VARCHAR(50),
    unit_price DECIMAL(10,2),
    tax_rate DECIMAL(5,2),
    discount_percent DECIMAL(5,2),
    CHECK (quantity > 0),
    INDEX (invoice_id, position)
);

CREATE TABLE payments (
    id UUID PRIMARY KEY,
    invoice_id UUID FOREIGN KEY → invoices.id CASCADE,
    amount DECIMAL(10,2),
    payment_date DATE,
    method VARCHAR(50),
    reference VARCHAR(100),
    note TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CHECK (amount > 0),
    INDEX (invoice_id),
    INDEX (payment_date),
    INDEX (method)
);

CREATE TABLE number_sequences (
    id UUID PRIMARY KEY,
    doc_type VARCHAR(50),
    year INT,
    current_number INT,
    UNIQUE (doc_type, year)
);

CREATE TABLE expenses (
    id UUID PRIMARY KEY,
    title VARCHAR(50),
    category VARCHAR(50),
    amount DECIMAL(10,2),
    description TEXT,
    receipt_path TEXT,
    note TEXT,
    is_billable BOOLEAN,
    project_id UUID FOREIGN KEY → projects.id,
    invoice_id UUID FOREIGN KEY → invoices.id,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CHECK (amount > 0),
    INDEX (project_id),
    INDEX (invoice_id),
    INDEX (category)
);
```

---

## Validierungsebenen

```
┌─────────────────────────────────────────┐
│         API-Anfrage                     │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Pydantic-Schema-Validierung           │
│   (schemas.py)                          │
│   ├─ Typprüfung                         │
│   ├─ Decimal-Konvertierung              │
│   ├─ Datumsvalidierung                  │
│   ├─ Enum-Validierung                   │
│   └─ Min/Max-Constraints                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   CRUD-Validierung (crud.py)            │
│   ├─ Kunde existiert?                   │
│   ├─ Projekt existiert?                 │
│   ├─ Rechnungsnummer eindeutig?         │
│   ├─ Zahlungsbetrag <= offen?           │
│   └─ Status-Übergang gültig?            │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Datenbank-Constraints                 │
│   ├─ CHECK-Constraints                  │
│   ├─ FOREIGN KEY-Constraints            │
│   ├─ UNIQUE-Constraints                 │
│   └─ NOT NULL-Constraints               │
└────────────┬────────────────────────────┘
             │
        (Erfolg oder 400/422/409 Fehler)
```

---

## Modell-Eigenschaften & Berechnete Felder

### Invoice-Modell

```python
# Datenbankfelder
- id: UUID
- invoice_number: str
- customer_id: UUID
- project_id: Optional[UUID]
- total: Decimal
- subtotal: Decimal
- tax_amount: Decimal
- status: str
- document_type: str
- issued_date: Optional[date]
- due_date: Optional[date]
- pdf_path: Optional[str]
- notes: Optional[str]
- terms: Optional[str]

# Berechnete Eigenschaften (Echtzeit-Berechnungen)
- paid_amount: Decimal          # SUM(payments.amount)
- outstanding_amount: Decimal   # total - paid_amount
- is_paid: bool                 # outstanding_amount <= 0
- is_overdue: bool              # heute > due_date UND nicht bezahlt
- days_until_due: Optional[int] # (due_date - heute).days
- payment_rate: float           # (paid_amount / total) * 100

# Methoden
- recalculate_totals()          # Neu berechnen aus Positionen
- update_status_from_payments() # Status automatisch aktualisieren
```

### InvoiceLineItem-Modell

```python
# Datenbankfelder
- id: UUID
- invoice_id: UUID
- position: int
- description: str
- quantity: Decimal
- unit: str
- unit_price: Decimal
- tax_rate: Decimal
- discount_percent: Decimal

# Berechnete Eigenschaften
- subtotal: Decimal             # quantity * unit_price
- discount_amount: Decimal      # subtotal * (discount_percent / 100)
- subtotal_after_discount: Decimal # subtotal - discount_amount
- tax_amount: Decimal           # subtotal_after_discount * (tax_rate / 100)
- total: Decimal                # subtotal_after_discount + tax_amount
```

### Expense-Modell

```python
# Datenbankfelder
- id: UUID
- title: str
- category: str (enum)
- amount: Decimal
- description: str
- receipt_path: Optional[str]
- note: Optional[str]
- is_billable: bool
- project_id: Optional[UUID]
- invoice_id: Optional[UUID]

# Berechnete Eigenschaften
- is_invoiced: bool             # invoice_id is not None
```

---

## API-Endpoint-Matrix

| Methode | Pfad | Handler | Zweck |
|--------|------|---------|---------|
| GET | `/invoices/` | `list_invoices()` | Liste mit Filtern/Pagination |
| GET | `/invoices/statistics` | `get_statistics()` | KPI-Daten |
| GET | `/invoices/{id}` | `get_invoice()` | Einzelne abrufen |
| GET | `/invoices/by-number/{num}` | `get_invoice_by_number()` | Nach Nummer |
| POST | `/invoices/` | `create_invoice()` | Neue erstellen |
| PATCH | `/invoices/{id}` | `update_invoice()` | Aktualisieren |
| PATCH | `/invoices/{id}/status` | `update_invoice_status()` | Nur Status |
| POST | `/invoices/{id}/recalculate` | `recalculate_totals()` | Summen neu berechnen |
| DELETE | `/invoices/{id}` | `delete_invoice()` | Löschen |
| GET | `/invoices/{id}/pdf` | `download_invoice_pdf()` | PDF herunterladen |
| POST | `/invoices/{id}/regenerate-pdf` | `regenerate_pdf()` | PDF neu generieren |
| POST | `/invoices/bulk/status-update` | `bulk_update_status()` | Bulk-Update |
| POST | `/invoices/{id}/payments` | `add_payment()` | Zahlung erstellen |
| GET | `/invoices/{id}/payments` | `list_invoice_payments()` | Zahlungen auflisten |
| GET | `/invoices/payments/{id}` | `get_payment()` | Zahlung abrufen |
| PATCH | `/invoices/payments/{id}` | `update_payment()` | Zahlung aktualisieren |
| DELETE | `/invoices/payments/{id}` | `delete_payment()` | Zahlung löschen |
| POST | `/finance/expenses` | `create_expense_endpoint()` | Erstellen |
| GET | `/finance/expenses` | `list_expenses_endpoint()` | Liste |
| GET | `/finance/expenses/{id}` | `get_expense_endpoint()` | Einzelne abrufen |
| PATCH | `/finance/expenses/{id}` | `update_expense_endpoint()` | Aktualisieren |
| DELETE | `/finance/expenses/{id}` | `delete_expense_endpoint()` | Löschen |
| GET | `/finance/kpis/expenses` | `get_expense_kpis_endpoint()` | KPI-Daten |

---

## Fehlerbehandlungs-Strategie

```python
# CRUD-Funktionen verwenden try/except-Muster:

try:
    # Validierung
    if not customer_exists(customer_id):
        raise HTTPException(404, "Kunde nicht gefunden")

    # Datenbankoperation
    invoice = models.Invoice(...)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

except HTTPException:
    db.rollback()
    raise  # HTTP-Exceptions erneut werfen

except Exception as e:
    db.rollback()
    raise HTTPException(500, f"Fehlgeschlagen: {str(e)}")
```

---

## Test-Strategie

### Unit-Tests (Geplant)
- Modell-Validierung
- Eigenschaftsberechnungen
- CRUD-Operationen
- PDF-Generierung

### Integrationstests (Aktuell)
- `test_invoice.py`: End-to-End-API-Tests
  - Rechnungserstellung
  - PDF-Generierung
  - Zahlungsablauf
  - Status-Updates

### Manuelles Testen
- API-Endpoints via curl/Postman
- Visuelle PDF-Inspektion
- Datenbank-Abfragen

---

## Performance-Überlegungen

1. **Eager Loading:** Beziehungen mit `selectinload()` geladen um N+1 zu vermeiden
2. **Indizierung:** Alle FK- und Filterspalten indiziert
3. **Pagination:** Begrenzt auf max. 500 Einträge pro Anfrage
4. **Query-Optimierung:** Spezifische SELECT-Abfragen, keine vollständigen Objekt-Loads
5. **PDF-Generierung:** Optionale Background-Task-Unterstützung
6. **Decimal-Arithmetik:** Verwendet Decimal-Typ für Genauigkeit (nicht float)
7. **Atomare Zähler:** FOR UPDATE Sperre bei Nummernsequenzen

---

## Sicherheits-Überlegungen

1. **Validierung:** Alle Eingaben validiert (Schema + CRUD)
2. **Typ-Sicherheit:** Decimal/UUID-Typen durchgehend verwendet
3. **SQL-Injection:** ORM-Schutz via parametrisierte Abfragen
4. **Kaskadierendes Löschen:** Ordentlich konfiguriert zur Wahrung referenzieller Integrität
5. **Dateipfade:** PDFs serverseitig gespeichert, nicht unter Benutzerkontrolle
6. **Constraints:** Constraints auf Datenbankebene durchgesetzt

---

## Deployment-Hinweise

### Erforderliche Tabellen
- invoices
- invoice_line_items
- payments
- number_sequences
- expenses

### Erforderliche Migrationen
- 2025_10_24_1224-..._fix_invoice_expense_relationship.py
- 2025_10_24_1331-..._add_invoices_and_payments_tables.py
- 2025_11_19_1707-..._add_document_type_to_invoices.py

### Dateisystem
- PDF-Speicher: `/root/workmate_os_uploads/invoices/`
- Schreibberechtigungen sicherstellen
- Backup-Strategie für PDFs

### Konfiguration
- Firmendetails in `pdf_generator.py` (fest kodiert)
- Dokumentvorlagen in DOCUMENT_TYPES dict
- Bankdetails in BANK_*-Konstanten
- Diese vor Produktions-Deployment aktualisieren
