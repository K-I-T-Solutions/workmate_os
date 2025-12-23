# Finance & Invoicing Module - Code Architecture

## Module Structure

```
workmate_os/
├── backend/app/modules/backoffice/
│   ├── invoices/
│   │   ├── __init__.py
│   │   ├── models.py                  # SQLAlchemy ORM models
│   │   │   ├── Invoice               # Main invoice model
│   │   │   ├── InvoiceLineItem       # Line items
│   │   │   ├── Payment               # Payment receipts
│   │   │   └── NumberSequence        # Invoice numbering
│   │   ├── schemas.py                # Pydantic validation
│   │   │   ├── InvoiceStatus enum
│   │   │   ├── PaymentMethod enum
│   │   │   ├── DocumentType enum
│   │   │   ├── InvoiceCreate/Update/Response
│   │   │   ├── PaymentCreate/Update/Response
│   │   │   ├── InvoiceLineItemCreate/Response
│   │   │   ├── InvoiceStatisticsResponse
│   │   │   └── BulkStatusUpdate
│   │   ├── routes.py                 # FastAPI endpoints
│   │   │   ├── list_invoices()       # GET /
│   │   │   ├── get_statistics()      # GET /statistics
│   │   │   ├── get_invoice()         # GET /{id}
│   │   │   ├── create_invoice()      # POST /
│   │   │   ├── update_invoice()      # PATCH /{id}
│   │   │   ├── delete_invoice()      # DELETE /{id}
│   │   │   ├── download_invoice_pdf()# GET /{id}/pdf
│   │   │   ├── add_payment()         # POST /{id}/payments
│   │   │   ├── bulk_update_status()  # POST /bulk/status-update
│   │   │   └── ... (more endpoints)
│   │   ├── crud.py                   # Database operations
│   │   │   ├── get_invoices()        # Read with filters
│   │   │   ├── create_invoice()      # Create with line items
│   │   │   ├── update_invoice()      # Update status/notes
│   │   │   ├── delete_invoice()      # Delete cascade
│   │   │   ├── recalculate_invoice_totals()
│   │   │   ├── get_invoice_statistics()
│   │   │   ├── _generate_invoice_number()
│   │   │   ├── _generate_next_number()
│   │   │   ├── _validate_customer_exists()
│   │   │   ├── _validate_invoice_number_unique()
│   │   │   └── _generate_and_save_pdf()
│   │   ├── payments_crud.py          # Payment-specific operations
│   │   │   ├── create_payment()      # Create with validation
│   │   │   ├── get_payment()         # Single payment
│   │   │   ├── get_payments()        # List payments
│   │   │   ├── update_payment()      # Update payment
│   │   │   └── delete_payment()      # Delete payment
│   │   ├── pdf_generator.py          # PDF generation
│   │   │   ├── generate_invoice_pdf()
│   │   │   ├── format_eur()          # German currency formatting
│   │   │   ├── draw_logo_watermark()
│   │   │   ├── DOCUMENT_TYPES        # Template config
│   │   │   ├── COMPANY_*             # Company constants
│   │   │   ├── BANK_*                # Bank constants
│   │   │   └── ... (rendering functions)
│   │   └── templates/               # (Empty, for future)
│   │
│   └── finance/
│       ├── __init__.py
│       ├── models.py                 # SQLAlchemy ORM models
│       │   └── Expense               # Expense/cost tracking
│       ├── schemas.py                # Pydantic validation
│       │   ├── ExpenseCreate/Update/Read
│       │   ├── ExpenseListResponse
│       │   ├── ExpenseKpiResponse
│       │   └── ExpenseCategory enum
│       ├── router.py                 # FastAPI endpoints
│       │   ├── create_expense_endpoint()      # POST /expenses
│       │   ├── list_expenses_endpoint()       # GET /expenses
│       │   ├── get_expense_endpoint()         # GET /expenses/{id}
│       │   ├── update_expense_endpoint()      # PATCH /expenses/{id}
│       │   ├── delete_expense_endpoint()      # DELETE /expenses/{id}
│       │   └── get_expense_kpis_endpoint()    # GET /kpis/expenses
│       └── crud.py (service.py)     # Database operations
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
│   └── test_invoice.py              # Integration tests
│
└── backend/app/main.py              # Router registration
    ├── app.include_router(invoices_router, ...)
    └── app.include_router(finance_routes.router, ...)
```

---

## Data Flow Diagram

### Invoice Creation Flow

```
User Request (API)
    ↓
routes.py::create_invoice()
    ↓
[Validation]
    ├─ Customer exists?
    └─ Project exists?
    ↓
crud.py::create_invoice()
    ├─ Generate invoice number (NumberSequence)
    ├─ Create Invoice object
    ├─ Create InvoiceLineItem objects
    ├─ recalculate_totals() on Invoice
    ├─ Save to database (commit)
    └─ Optional: Generate PDF
        └─ pdf_generator.py::generate_invoice_pdf()
    ↓
Response (InvoiceResponse schema)
```

### Payment Flow

```
User Request (API)
    ↓
routes.py::add_payment()
    ↓
payments_crud.py::create_payment()
    ├─ Invoice exists?
    ├─ Amount <= outstanding_amount?
    ├─ Create Payment object
    ├─ Save to database
    └─ Update Invoice status
        └─ Invoice.update_status_from_payments()
    ↓
SQLAlchemy Event (after_insert)
    └─ Auto-update invoice status
    ↓
Response (PaymentResponse schema)
```

### List & Filter Flow

```
User Request (API)
    ↓
routes.py::list_invoices()
    │
    └─ Build query filters:
        ├─ status filter?
        ├─ customer_id filter?
        ├─ project_id filter?
        ├─ date_from/date_to?
        └─ skip/limit pagination?
    ↓
crud.py::get_invoices()
    ├─ Apply filters to query
    ├─ Order by issued_date desc
    ├─ Offset + Limit
    ├─ Eager load relations (customer, line_items, payments)
    └─ Execute query
    ↓
Response (InvoiceListResponse schema)
```

---

## Database Schema Relationships

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

## Validation Layers

```
┌─────────────────────────────────────────┐
│         API Request                     │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Pydantic Schema Validation            │
│   (schemas.py)                          │
│   ├─ Type checking                      │
│   ├─ Decimal conversion                 │
│   ├─ Date validation                    │
│   ├─ Enum validation                    │
│   └─ Min/max constraints                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   CRUD Validation (crud.py)             │
│   ├─ Customer exists?                   │
│   ├─ Project exists?                    │
│   ├─ Invoice number unique?             │
│   ├─ Payment amount <= outstanding?     │
│   └─ Status transition valid?           │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Database Constraints                  │
│   ├─ CHECK constraints                  │
│   ├─ FOREIGN KEY constraints            │
│   ├─ UNIQUE constraints                 │
│   └─ NOT NULL constraints               │
└────────────┬────────────────────────────┘
             │
        (Success or 400/422/409 Error)
```

---

## Model Properties & Computed Fields

### Invoice Model

```python
# Database Fields
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

# Computed Properties (real-time calculations)
- paid_amount: Decimal          # SUM(payments.amount)
- outstanding_amount: Decimal   # total - paid_amount
- is_paid: bool                 # outstanding_amount <= 0
- is_overdue: bool              # today > due_date AND not paid
- days_until_due: Optional[int] # (due_date - today).days
- payment_rate: float           # (paid_amount / total) * 100

# Methods
- recalculate_totals()          # Recalc from line items
- update_status_from_payments() # Auto-update status
```

### InvoiceLineItem Model

```python
# Database Fields
- id: UUID
- invoice_id: UUID
- position: int
- description: str
- quantity: Decimal
- unit: str
- unit_price: Decimal
- tax_rate: Decimal
- discount_percent: Decimal

# Computed Properties
- subtotal: Decimal             # quantity * unit_price
- discount_amount: Decimal      # subtotal * (discount_percent / 100)
- subtotal_after_discount: Decimal # subtotal - discount_amount
- tax_amount: Decimal           # subtotal_after_discount * (tax_rate / 100)
- total: Decimal                # subtotal_after_discount + tax_amount
```

### Expense Model

```python
# Database Fields
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

# Computed Properties
- is_invoiced: bool             # invoice_id is not None
```

---

## API Endpoint Matrix

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/invoices/` | `list_invoices()` | List with filters/pagination |
| GET | `/invoices/statistics` | `get_statistics()` | KPI data |
| GET | `/invoices/{id}` | `get_invoice()` | Get single |
| GET | `/invoices/by-number/{num}` | `get_invoice_by_number()` | By number |
| POST | `/invoices/` | `create_invoice()` | Create new |
| PATCH | `/invoices/{id}` | `update_invoice()` | Update |
| PATCH | `/invoices/{id}/status` | `update_invoice_status()` | Status only |
| POST | `/invoices/{id}/recalculate` | `recalculate_totals()` | Recalc totals |
| DELETE | `/invoices/{id}` | `delete_invoice()` | Delete |
| GET | `/invoices/{id}/pdf` | `download_invoice_pdf()` | Download PDF |
| POST | `/invoices/{id}/regenerate-pdf` | `regenerate_pdf()` | Regenerate PDF |
| POST | `/invoices/bulk/status-update` | `bulk_update_status()` | Bulk update |
| POST | `/invoices/{id}/payments` | `add_payment()` | Create payment |
| GET | `/invoices/{id}/payments` | `list_invoice_payments()` | List payments |
| GET | `/invoices/payments/{id}` | `get_payment()` | Get payment |
| PATCH | `/invoices/payments/{id}` | `update_payment()` | Update payment |
| DELETE | `/invoices/payments/{id}` | `delete_payment()` | Delete payment |
| POST | `/finance/expenses` | `create_expense_endpoint()` | Create |
| GET | `/finance/expenses` | `list_expenses_endpoint()` | List |
| GET | `/finance/expenses/{id}` | `get_expense_endpoint()` | Get single |
| PATCH | `/finance/expenses/{id}` | `update_expense_endpoint()` | Update |
| DELETE | `/finance/expenses/{id}` | `delete_expense_endpoint()` | Delete |
| GET | `/finance/kpis/expenses` | `get_expense_kpis_endpoint()` | KPI data |

---

## Error Handling Strategy

```python
# CRUD functions use try/except pattern:

try:
    # Validation
    if not customer_exists(customer_id):
        raise HTTPException(404, "Customer not found")
    
    # Database operation
    invoice = models.Invoice(...)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
except HTTPException:
    db.rollback()
    raise  # Re-raise HTTP exceptions
    
except Exception as e:
    db.rollback()
    raise HTTPException(500, f"Failed: {str(e)}")
```

---

## Testing Strategy

### Unit Tests (Planned)
- Model validation
- Property calculations
- CRUD operations
- PDF generation

### Integration Tests (Current)
- `test_invoice.py`: End-to-end API testing
  - Invoice creation
  - PDF generation
  - Payment flow
  - Status updates

### Manual Testing
- API endpoints via curl/Postman
- PDF visual inspection
- Database queries

---

## Performance Considerations

1. **Eager Loading:** Relationships loaded with `selectinload()` to avoid N+1
2. **Indexing:** All FK and filter columns indexed
3. **Pagination:** Limited to 500 items max per request
4. **Query Optimization:** Specific SELECT queries, not full object loads
5. **PDF Generation:** Optional background task support
6. **Decimal Arithmetic:** Using Decimal type for accuracy (not float)
7. **Atomic Counters:** FOR UPDATE locking on number sequences

---

## Security Considerations

1. **Validation:** All inputs validated (schema + CRUD)
2. **Type Safety:** Decimal/UUID types used throughout
3. **SQL Injection:** ORM protection via parameterized queries
4. **Cascade Deletes:** Properly configured to maintain referential integrity
5. **File Paths:** PDFs stored server-side, not in user control
6. **Constraints:** Database-level constraints enforced

---

## Deployment Notes

### Required Tables
- invoices
- invoice_line_items
- payments
- number_sequences
- expenses

### Required Migrations
- 2025_10_24_1224-..._fix_invoice_expense_relationship.py
- 2025_10_24_1331-..._add_invoices_and_payments_tables.py
- 2025_11_19_1707-..._add_document_type_to_invoices.py

### File System
- PDF storage: `/root/workmate_os_uploads/invoices/`
- Ensure write permissions
- Backup strategy for PDFs

### Configuration
- Company details in `pdf_generator.py` (hardcoded)
- Document templates in DOCUMENT_TYPES dict
- Bank details in BANK_* constants
- Update these before production deployment

