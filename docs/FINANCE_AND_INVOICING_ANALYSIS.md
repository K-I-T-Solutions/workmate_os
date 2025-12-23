# WorkmateOS Finance & Invoice/Billing Functionality - Comprehensive Overview

**Last Updated:** December 22, 2025

## Executive Summary

The WorkmateOS system has a well-structured **Finance & Invoicing module** (Phase 2) with comprehensive invoice creation, payment tracking, expense management, and financial reporting capabilities. The implementation includes database models, API endpoints, PDF generation, and planning for UI components.

---

## 1. INVOICE MANAGEMENT

### 1.1 Database Models
**Location:** `/backend/app/modules/backoffice/invoices/models.py`

#### Invoice Model
- **Purpose:** Manages customer invoices and quotes
- **Key Fields:**
  - `invoice_number` (str, unique): Auto-generated (RE-2025-0001, AN-2025-0001, etc.)
  - `total` (Decimal): Total amount including VAT
  - `subtotal` (Decimal): Amount without VAT
  - `tax_amount` (Decimal): VAT amount
  - `status` (str): draft, sent, paid, partial, overdue, cancelled
  - `document_type` (str): invoice, quote, credit_note, order_confirmation
  - `issued_date`, `due_date` (Date): Invoice and due dates
  - `pdf_path` (str, optional): Path to generated PDF
  - `customer_id` (FK): Required customer reference
  - `project_id` (FK, optional): Associated project
  - `notes`, `terms` (Text, optional): Internal notes and payment terms

- **Key Methods:**
  - `recalculate_totals()`: Recalculates subtotal, tax, and total from line items
  - `update_status_from_payments()`: Auto-updates status based on payment progress
  - `is_overdue` (property): Boolean check if past due date and unpaid
  - `paid_amount` (property): Sum of all payments
  - `outstanding_amount` (property): Remaining balance to pay
  - `is_paid` (property): Boolean check if fully paid
  - `days_until_due` (property): Days remaining (negative = overdue)
  - `payment_rate` (property): Percentage paid (0-100)

- **Relationships:**
  - `customer` (many-to-one): CRM Customer
  - `project` (many-to-one, optional): Project
  - `line_items` (one-to-many): Invoice line items (cascade delete)
  - `payments` (one-to-many): Payment entries (cascade delete)
  - `expenses` (one-to-many): Associated expenses (cascade delete)

- **Constraints:**
  - All monetary values >= 0
  - Due date must be >= issued date
  - Status must be valid enum value
  - Invoice number is unique

#### InvoiceLineItem Model
- **Purpose:** Individual line items on invoices
- **Key Fields:**
  - `position` (int): Sort order on invoice
  - `description` (str): Service/product description
  - `quantity` (Decimal): Amount/count
  - `unit` (str): Unit of measure (Hours, Pieces, m², etc.)
  - `unit_price` (Decimal): Price per unit (net)
  - `tax_rate` (Decimal): VAT percentage (0-100)
  - `discount_percent` (Decimal): Discount percentage (0-100)
  - `invoice_id` (FK): Parent invoice

- **Key Calculations:**
  - `subtotal`: quantity × unit_price
  - `discount_amount`: subtotal × (discount_percent / 100)
  - `subtotal_after_discount`: subtotal - discount_amount
  - `tax_amount`: subtotal_after_discount × (tax_rate / 100)
  - `total`: subtotal_after_discount + tax_amount

#### Payment Model
- **Purpose:** Track all payment receipts for invoices
- **Key Fields:**
  - `amount` (Decimal): Payment amount (> 0)
  - `payment_date` (Date): When payment was received
  - `method` (str): cash, bank_transfer, credit_card, debit_card, paypal, sepa, other
  - `reference` (str, optional): Transaction ID or purpose
  - `note` (str, optional): Internal note
  - `invoice_id` (FK): Associated invoice

- **Triggers:**
  - Auto-updates invoice status after create/update/delete via SQLAlchemy events

#### NumberSequence Model
- **Purpose:** Manages invoice number sequences by document type and year
- **Fields:**
  - `doc_type` (str): Document type (invoice, quote, credit_note, cancellation)
  - `year` (int): Year for sequence
  - `current_number` (int): Last issued sequential number
- **Format:** RE-2025-0001, AN-2025-0001, GS-2025-0001, ST-2025-0001
- **Features:** Atomic counter with FOR UPDATE locking for concurrency safety

### 1.2 API Endpoints

**Base Path:** `/api/backoffice/invoices`

#### List & Filter
- `GET /` - List invoices with pagination and filters
  - Query params: `skip`, `limit`, `status`, `customer_id`, `project_id`, `date_from`, `date_to`
  - Returns: `InvoiceListResponse` with pagination metadata

- `GET /statistics` - Invoice statistics
  - Returns: Total count, total revenue, outstanding amount, overdue count, counts by status

#### Single Invoice Operations
- `GET /{invoice_id}` - Get single invoice with all relations
- `GET /by-number/{invoice_number}` - Get invoice by invoice number
- `POST /` - Create new invoice (with automatic PDF generation option)
- `PATCH /{invoice_id}` - Update invoice (status, notes, terms only)
- `PATCH /{invoice_id}/status` - Update status only
- `POST /{invoice_id}/recalculate` - Recalculate totals from line items
- `DELETE /{invoice_id}` - Delete invoice (cascade: line items, payments, PDF)

#### PDF Operations
- `GET /{invoice_id}/pdf` - Download invoice PDF (auto-generates if missing)
- `POST /{invoice_id}/regenerate-pdf` - Regenerate PDF (e.g., after template change)

#### Bulk Operations
- `POST /bulk/status-update` - Update status for multiple invoices
  - Returns: success_count, failed_count, failed_ids

#### Payment Management
- `POST /{invoice_id}/payments` - Add payment (auto-updates invoice status)
- `GET /{invoice_id}/payments` - List payments for invoice
- `GET /payments/{payment_id}` - Get single payment
- `PATCH /payments/{payment_id}` - Update payment
- `DELETE /payments/{payment_id}` - Delete payment (auto-updates invoice status)

### 1.3 Schemas & Validation

**Location:** `/backend/app/modules/backoffice/invoices/schemas.py`

- `InvoiceStatus` enum: draft, sent, paid, partial, overdue, cancelled
- `PaymentMethod` enum: cash, bank_transfer, credit_card, debit_card, paypal, sepa, other
- `DocumentType` enum: invoice, quote, credit_note, order_confirmation

**Request/Response Schemas:**
- `InvoiceCreate`: For creating invoices (requires min. 1 line item)
- `InvoiceUpdate`: For partial updates
- `InvoiceResponse`: Full invoice response with computed fields
- `InvoiceListResponse`: Paginated list with page/pages calculations
- `InvoiceStatisticsResponse`: KPI data
- `PaymentCreate`, `PaymentUpdate`, `PaymentResponse`: Payment operations
- `InvoiceLineItemCreate`, `InvoiceLineItemResponse`: Line item operations
- `BulkStatusUpdate`, `BulkUpdateResponse`: Bulk operations
- `InvoiceFilterParams`: Query parameter validation

**Validations:**
- Decimal conversion for monetary values
- Date validation (due_date >= issued_date)
- Status enum validation
- Minimum 1 line item required on creation

### 1.4 CRUD Operations

**Location:** `/backend/app/modules/backoffice/invoices/crud.py`

**Create:**
- Automatic or manual invoice number generation
- Validates customer exists
- Validates project exists (if provided)
- Creates line items with automatic positioning
- Auto-recalculates totals
- Optional synchronous PDF generation
- Registers PDF as Document

**Read:**
- Get invoices with optional filters (status, customer, project, date range)
- Count with same filters
- Get single invoice with all relations eager-loaded
- Get invoice by number

**Update:**
- Update status, notes, terms only
- Validate new status
- Recalculate totals from line items

**Delete:**
- Cascade delete line items and payments
- Delete PDF file from filesystem

**Statistics:**
- Total count
- Total revenue (paid invoices only)
- Outstanding amount (unpaid + partial)
- Count of overdue, draft, sent, paid, cancelled

### 1.5 PDF Generation

**Location:** `/backend/app/modules/backoffice/invoices/pdf_generator.py`

**Features:**
- Document type templates (invoice, quote, credit_note, order_confirmation)
- Custom colors per document type
- Company branding (K.I.T. Solutions)
- Watermark support (company logo)
- SEPA QR code generation for payments
- German number formatting (1.234,50 €)
- Line item table with calculations
- Bank details (IBAN, BIC)
- Terms and conditions
- Professional invoice layout

**File Naming:** `KIT-RE-{sequence}.pdf`
**Storage:** `/root/workmate_os_uploads/invoices/`

---

## 2. EXPENSE MANAGEMENT & FINANCE TRACKING

### 2.1 Database Models

**Location:** `/backend/app/modules/backoffice/finance/models.py`

#### Expense Model
- **Purpose:** Track project costs and expenses
- **Key Fields:**
  - `title` (str): Expense name
  - `category` (str enum): travel, material, software, hardware, consulting, marketing, office, training, other
  - `amount` (Decimal): Expense amount (> 0)
  - `description` (str): Detailed description
  - `receipt_path` (str, optional): Path to receipt/document
  - `note` (str, optional): Additional notes
  - `is_billable` (bool): Can be charged to customer
  - `project_id` (FK, optional): Associated project
  - `invoice_id` (FK, optional): If already invoiced

- **Key Methods:**
  - `is_invoiced` (property): Boolean check if assigned to invoice

- **Relationships:**
  - `project` (many-to-one, optional): Project
  - `invoice` (many-to-one, optional): Invoice if invoiced

- **Constraints:**
  - Amount must be > 0

### 2.2 API Endpoints

**Base Path:** `/api/backoffice/finance`

#### Expense CRUD
- `POST /expenses` - Create expense
- `GET /expenses` - List expenses with filters and pagination
  - Query params: `title`, `category`, `project_id`, `invoice_id`, `from_date`, `to_date`, `limit`, `offset`
- `GET /expenses/{expense_id}` - Get single expense
- `PATCH /expenses/{expense_id}` - Update expense
- `DELETE /expenses/{expense_id}` - Delete expense

#### Financial KPIs
- `GET /kpis/expenses` - Get expense KPIs
  - Query params: `title`, `category`, `project_id`, `from_date`, `to_date`
  - Returns: Total expenses, breakdown by category

### 2.3 Schemas & Validation

**Location:** `/backend/app/modules/backoffice/finance/schemas.py`

- `ExpenseCreate`: For creating expenses
- `ExpenseUpdate`: For partial updates (all fields optional)
- `ExpenseRead`: Full expense response
- `ExpenseListResponse`: Paginated list
- `ExpenseKpiRequest`: Optional KPI request parameters
- `ExpenseKpiResponse`: Total and breakdown by category

**Validations:**
- Amount must be > 0
- Category must be valid enum

### 2.4 CRUD Operations

**Location:** `/backend/app/modules/backoffice/finance/crud.py` (named service.py)

**Create:**
- Creates expense with all fields
- Category enum handling

**Read:**
- List with title, category, project, invoice, and date range filters
- Pagination support (limit, offset)
- Returns total count with items

**Update:**
- Partial updates (exclude_unset=True)
- Category enum handling
- All fields except ID optional

**Delete:**
- Hard delete (v0.1)

**KPIs:**
- Calculates total expense amount
- Groups by category with sum per category
- Supports same filters as list (title, category, project, date range)

---

## 3. DATABASE SCHEMA MIGRATION

**Location:** `/backend/alembic/versions/`

**Migration Files:**
1. `2025_10_24_1224-0c0b8f566bc5_fix_invoice_expense_relationship.py`
   - Establishes Invoice-Expense relationship

2. `2025_10_24_1331-452a56fe4f4d_add_invoices_and_payments_tables.py`
   - Creates invoices, invoice_line_items, payments tables
   - Creates indexes for filtering and lookups

3. `2025_11_19_1707-c87120e6a54d_add_document_type_to_invoices.py`
   - Adds document_type column to invoices table

**Key Indexes:**
- `ix_invoices_customer_id`: Fast customer lookups
- `ix_invoices_project_id`: Fast project lookups
- `ix_invoices_status`: Fast status filtering
- `ix_invoices_issued_date`, `ix_invoices_due_date`: Date filtering
- `ix_invoices_invoice_number`: Number lookups
- `ix_invoice_line_items_invoice_id`, `ix_invoice_line_items_position`: Line item ordering
- `ix_payments_invoice_id`, `ix_payments_payment_date`, `ix_payments_method`: Payment lookups
- `ix_expenses_*`: Similar indexes for expense filtering

---

## 4. INTEGRATION WITH OTHER MODULES

### 4.1 CRM Integration
- Invoices require a Customer (CRM module)
- Customer has back_populates relationship to invoices
- Customer.invoices accesses all their invoices

### 4.2 Project Integration
- Invoices can optionally link to Projects
- Expenses can optionally link to Projects
- Projects track associated invoices and expenses

### 4.3 Document Management
- Invoice PDFs registered as Documents
- Document category: "Rechnungen"
- Linked module: "invoices"
- Stored with metadata for search/organization

### 4.4 Time Tracking Integration
- Future potential: Link time entries to invoice line items
- Current: Manual entry of hours/services on invoices

---

## 5. CURRENT STATE & IMPLEMENTATION LEVEL

### Fully Implemented
- **Invoice Creation & Management**
  - Full CRUD operations
  - Automatic number generation with yearly sequence reset
  - Multiple document types support
  - PDF generation with branding
  
- **Payment Processing**
  - Record payment receipts
  - Track payment methods
  - Auto-update invoice status based on payments
  - Partial payment support

- **Financial Reporting**
  - Invoice statistics (counts, totals, outstanding)
  - Expense KPIs (totals by category)
  - Status-based reporting
  - Date range filtering

- **Expense Tracking**
  - Expense creation and management
  - Category-based organization
  - Billable flag for customer charging
  - Receipt/document attachment support

- **Validation & Integrity**
  - Proper constraints on database level
  - Pydantic schema validation
  - Relationship validation (customer/project exists)
  - Unique invoice number enforcement

- **PDF Generation**
  - Professional invoice templates
  - Multi-document type support
  - QR code for SEPA payments
  - Watermarking support
  - German formatting

### Partially Implemented / Planned
- **UI Components**
  - No current UI components in `/ui/src/modules/`
  - Only CRM and Dashboard modules have UI
  - Invoice/Finance UI needs development

- **Payment Gateway Integration**
  - No real payment processing (Stripe, PayPal, etc.)
  - Manual payment entry only
  - Future: Webhook integration for auto-reconciliation

- **Advanced Financial Reports**
  - No P&L statements
  - No tax reports
  - No cash flow forecasting
  - No profitability analysis by project

- **Accounting Features**
  - No double-entry bookkeeping
  - No journal entries
  - No ledger/chart of accounts
  - No depreciation tracking

- **Multi-currency Support**
  - Currently German-only formatting
  - No currency field on invoices
  - Assumes EUR

---

## 6. API RESPONSE EXAMPLES

### Create Invoice (200+ lines example in test file)
```json
{
  "invoice_number": "RE-2025-0001",
  "issued_date": "2025-12-22",
  "due_date": "2026-01-05",
  "customer_id": "uuid...",
  "project_id": "uuid...",
  "status": "draft",
  "total": 2145.50,
  "subtotal": 1800.00,
  "tax_amount": 342.00,
  "line_items": [
    {
      "position": 1,
      "description": "IT-Support",
      "quantity": 2,
      "unit": "Hours",
      "unit_price": 85.00,
      "tax_rate": 19.0,
      "discount_percent": 0.0,
      "subtotal": 170.00,
      "tax_amount": 32.30,
      "total": 202.30
    }
  ],
  "payments": [],
  "paid_amount": 0,
  "outstanding_amount": 2145.50,
  "is_paid": false,
  "is_overdue": false
}
```

### Invoice Statistics
```json
{
  "total_count": 42,
  "total_revenue": 150000.00,
  "outstanding_amount": 25000.00,
  "overdue_count": 3,
  "draft_count": 5,
  "sent_count": 12,
  "paid_count": 20,
  "cancelled_count": 2
}
```

---

## 7. TESTING

**Location:** `/backend/tests/test_invoice.py`

- Integration test script against live API
- Tests invoice creation with line items
- Tests PDF generation
- Tests payment flow
- Manual testing approach (not pytest)

---

## 8. CONFIGURATION & CONSTANTS

### PDF Generator Constants
- **Company:** K.I.T. Solutions
- **Owner:** Joshua Phu Kuhrau
- **Address:** Dietzstr. 1, 56073 Koblenz, Germany
- **Email:** info@kit-it-koblenz.de
- **Website:** https://kit-it-koblenz.de
- **Phone:** Tel. 0162 / 2654262
- **Bank:** DE94100110012706471170 (N26 Bank AG)

### Document Type Configurations
| Type | Title | Color | Default Terms |
|------|-------|-------|----------------|
| invoice | RECHNUNG | #ff9100 | 14 days |
| quote | ANGEBOT | #008cff | 14 days valid |
| credit_note | GUTSCHRIFT | #5dcc5d | Offset against open items |
| order_confirmation | AUFTRAGSBESTÄTIGUNG | #9933ff | Please verify |

---

## 9. FILE STRUCTURE SUMMARY

```
backend/
├── alembic/versions/
│   ├── 2025_10_24_1224-..._fix_invoice_expense_relationship.py
│   ├── 2025_10_24_1331-..._add_invoices_and_payments_tables.py
│   └── 2025_11_19_1707-..._add_document_type_to_invoices.py
│
└── app/modules/backoffice/
    ├── invoices/
    │   ├── __init__.py
    │   ├── models.py (Invoice, InvoiceLineItem, Payment, NumberSequence)
    │   ├── schemas.py (Pydantic models)
    │   ├── routes.py (FastAPI endpoints)
    │   ├── crud.py (Database operations)
    │   ├── payments_crud.py (Payment operations)
    │   ├── pdf_generator.py (PDF generation)
    │   └── templates/ (empty, for future templates)
    │
    └── finance/
        ├── __init__.py
        ├── models.py (Expense)
        ├── schemas.py (Pydantic models)
        ├── router.py (FastAPI endpoints)
        ├── crud.py (service.py - Database operations)
        └── service.py (same as crud.py)

tests/
└── test_invoice.py (Integration test script)
```

---

## 10. RECOMMENDED NEXT STEPS

### Priority 1: UI Implementation
- Create invoice list page with filters and pagination
- Create invoice detail/edit page
- Create invoice creation form with line items
- Create payment entry form
- Add invoice status management UI
- Add PDF download button

### Priority 2: Payment Integration
- Integrate Stripe or PayPal
- Add payment webhooks for auto-reconciliation
- Add payment status updates
- Add payment history visualization

### Priority 3: Advanced Reporting
- Create P&L statement
- Add tax report generation
- Add cash flow forecasting
- Add profitability by project
- Export to accounting software (ELSTER, Datev format)

### Priority 4: Accounting Features
- Implement chart of accounts
- Add journal entries for manual bookkeeping
- Add ledger views
- Add trial balance reports
- Add depreciation tracking

### Priority 5: Financial Analysis
- Add financial dashboards
- Add trend analysis
- Add customer profitability
- Add project profitability
- Add forecast models

---

## 11. KEY TECHNICAL DECISIONS

1. **Automatic Invoice Numbering:** Yearly sequence per document type using atomic counter with FOR UPDATE locking
2. **Status Management:** Auto-updated via SQLAlchemy events when payments are added/removed
3. **Cascade Relationships:** Delete invoice cascades to line items, payments, and expenses
4. **PDF Generation:** ReportLab for professional templates, optional background task generation
5. **Validation:** Two-layer validation (schema + database constraints)
6. **Pagination:** Limit to 500 items max per request to prevent memory issues
7. **Decimal Arithmetic:** Uses Decimal type throughout for financial accuracy

---

## 12. KNOWN LIMITATIONS

1. No UI components yet (backend only)
2. No real payment processor integration (manual entry only)
3. Single currency (EUR assumed)
4. German language only for PDF output
5. No audit trail for invoice changes
6. No invoice templates (using fixed layout)
7. No email notification system
8. No reminders for overdue invoices
9. No late fees/interest calculation
10. No dunning management

