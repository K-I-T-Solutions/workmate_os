# Finance & Invoicing Module - Documentation Index

This directory contains comprehensive documentation of the WorkmateOS Finance and Invoicing functionality.

## Documentation Files

### 1. FINANCE_AND_INVOICING_ANALYSIS.md (603 lines)
**Comprehensive Deep Dive**

The most detailed document covering:
- Complete Invoice Management features and models
- Expense Management & Finance Tracking
- Database Schema & Migrations
- Integration with other modules (CRM, Projects, Documents)
- Current implementation status (fully vs. partially implemented)
- API Response Examples
- Testing approach
- Configuration & Company Details
- File structure summary
- Recommended next steps
- Known limitations
- Key technical decisions

**When to use:** Reading this when you need complete understanding of what exists, how it works, and what's missing.

---

### 2. FINANCE_QUICK_REFERENCE.md (184 lines)
**Quick Lookup Guide**

Fast-reference for:
- Implementation checklist (what's done, what's not)
- Key API paths
- Database entity relationships
- Important numbers & formats
- File locations table
- Computed properties reference
- Calculation formulas
- Invoice status flow
- Company hardcoded details
- Recent git changes
- Testing location
- Next priorities

**When to use:** Quick lookups, presentations, remembering paths or constants.

---

### 3. FINANCE_CODE_ARCHITECTURE.md (505 lines)
**Technical Architecture Document**

Detailed technical deep-dive:
- Complete Module Structure (file tree with descriptions)
- Data Flow Diagrams (creation, payment, filtering)
- Database Schema (CREATE TABLE statements)
- Validation Layers (4-layer validation flow)
- Model Properties & Computed Fields
- API Endpoint Matrix (all 22 endpoints)
- Error Handling Strategy
- Testing Strategy
- Performance Considerations
- Security Considerations
- Deployment Notes

**When to use:** When developing new features, optimizing, or understanding technical architecture.

---

## Key Statistics

- **Total Documentation Lines:** 1,292
- **Files Generated:** 3
- **Date Created:** December 22, 2025
- **Invoices Module:** ~500 LOC models + ~600 LOC routes + ~200 LOC CRUD + ~100 LOC PDF
- **Finance Module:** ~60 LOC models + ~160 LOC routes + ~160 LOC CRUD
- **API Endpoints:** 22 total (18 invoice, 6 finance)
- **Database Tables:** 5 (invoices, invoice_line_items, payments, number_sequences, expenses)

---

## Quick Navigation

### If You Want to...

**...understand what exists**
→ Start with FINANCE_AND_INVOICING_ANALYSIS.md Section 5

**...quickly look up an API endpoint**
→ Check FINANCE_CODE_ARCHITECTURE.md API Endpoint Matrix

**...find where code lives**
→ See FINANCE_QUICK_REFERENCE.md File Locations table

**...understand the data model**
→ Read FINANCE_CODE_ARCHITECTURE.md Database Schema & FINANCE_AND_INVOICING_ANALYSIS.md Section 1

**...see how to create an invoice (code flow)**
→ Check FINANCE_CODE_ARCHITECTURE.md Data Flow Diagram

**...understand validation**
→ See FINANCE_CODE_ARCHITECTURE.md Validation Layers

**...plan next features**
→ Read FINANCE_AND_INVOICING_ANALYSIS.md Section 10 (Recommended Next Steps)

**...understand current limitations**
→ Check FINANCE_AND_INVOICING_ANALYSIS.md Section 12

**...see the payment flow**
→ Look at FINANCE_CODE_ARCHITECTURE.md Data Flow Diagram

**...understand performance optimizations**
→ See FINANCE_CODE_ARCHITECTURE.md Performance Considerations

---

## Implementation Status Summary

### Fully Implemented
- Invoice creation with line items
- Automatic invoice numbering
- Payment tracking & recording
- Invoice status management with auto-updates
- Professional PDF generation
- Expense tracking with categories
- Financial KPIs
- Full REST API with pagination & filters
- Database validation & constraints
- Multiple document types support

### Not Yet Implemented
- Frontend UI components
- Payment gateway integration
- Advanced financial reports
- Accounting features
- Email notifications
- Overdue reminders
- Multi-currency support
- Audit trail
- Custom templates
- Batch operations

---

## File Locations (Quick Reference)

| Component | Path |
|-----------|------|
| Invoice Models | `backend/app/modules/backoffice/invoices/models.py` |
| Invoice API Endpoints | `backend/app/modules/backoffice/invoices/routes.py` |
| Invoice Database Ops | `backend/app/modules/backoffice/invoices/crud.py` |
| Payment Database Ops | `backend/app/modules/backoffice/invoices/payments_crud.py` |
| PDF Generation | `backend/app/modules/backoffice/invoices/pdf_generator.py` |
| Expense Models | `backend/app/modules/backoffice/finance/models.py` |
| Finance API Endpoints | `backend/app/modules/backoffice/finance/router.py` |
| Finance Database Ops | `backend/app/modules/backoffice/finance/crud.py` |
| Validation Schemas | `backend/app/modules/backoffice/{invoices,finance}/schemas.py` |
| Database Migrations | `backend/alembic/versions/` (3 files) |
| Integration Tests | `backend/tests/test_invoice.py` |
| Main App Router Setup | `backend/app/main.py` (lines 22-24, 100-102) |

---

## Database Tables

```
1. invoices
   - Main invoice records
   - Tracks: number, status, totals, dates, customer, project
   - 11 indexed columns
   
2. invoice_line_items
   - Individual line items per invoice
   - Tracks: description, quantity, unit, price, tax, discount
   - Cascade deleted with invoice
   
3. payments
   - Payment receipts for invoices
   - Tracks: amount, date, method, reference
   - Triggers auto-status update on invoice
   
4. number_sequences
   - Manages invoice number generation
   - Per document type (invoice, quote, credit_note, etc.)
   - Per year (yearly reset)
   - Atomic counter with FOR UPDATE locking
   
5. expenses
   - Project costs and expenses
   - Tracks: category, amount, billable flag
   - Links to project and invoice
```

---

## API Endpoints (Complete List)

### Invoices (18 endpoints)

**List & Statistics:**
- GET /api/backoffice/invoices/ - List with filters/pagination
- GET /api/backoffice/invoices/statistics - Get KPIs

**Single Invoice:**
- GET /api/backoffice/invoices/{id} - Get by ID
- GET /api/backoffice/invoices/by-number/{num} - Get by number
- POST /api/backoffice/invoices/ - Create new
- PATCH /api/backoffice/invoices/{id} - Update
- PATCH /api/backoffice/invoices/{id}/status - Update status only
- POST /api/backoffice/invoices/{id}/recalculate - Recalculate totals
- DELETE /api/backoffice/invoices/{id} - Delete

**PDF Operations:**
- GET /api/backoffice/invoices/{id}/pdf - Download PDF
- POST /api/backoffice/invoices/{id}/regenerate-pdf - Regenerate PDF

**Bulk Operations:**
- POST /api/backoffice/invoices/bulk/status-update - Bulk status update

**Payments (6 endpoints):**
- POST /api/backoffice/invoices/{id}/payments - Create payment
- GET /api/backoffice/invoices/{id}/payments - List payments
- GET /api/backoffice/invoices/payments/{id} - Get payment
- PATCH /api/backoffice/invoices/payments/{id} - Update payment
- DELETE /api/backoffice/invoices/payments/{id} - Delete payment

### Finance (6 endpoints)

**Expenses:**
- POST /api/backoffice/finance/expenses - Create
- GET /api/backoffice/finance/expenses - List with filters
- GET /api/backoffice/finance/expenses/{id} - Get single
- PATCH /api/backoffice/finance/expenses/{id} - Update
- DELETE /api/backoffice/finance/expenses/{id} - Delete

**KPIs:**
- GET /api/backoffice/finance/kpis/expenses - Get expense totals by category

---

## Key Models & Their Properties

### Invoice
```
Database Fields:
- invoice_number (str, unique)
- customer_id (FK, required)
- project_id (FK, optional)
- total, subtotal, tax_amount (Decimal)
- status (enum: draft/sent/paid/partial/overdue/cancelled)
- document_type (enum: invoice/quote/credit_note/order_confirmation)
- issued_date, due_date (Date, optional)
- pdf_path (str, optional)

Computed Properties:
- paid_amount (sum of payments)
- outstanding_amount (total - paid)
- is_paid (bool)
- is_overdue (bool)
- payment_rate (0-100%)
- days_until_due (int, can be negative)

Methods:
- recalculate_totals() - Recalc from line items
- update_status_from_payments() - Auto-update status
```

### InvoiceLineItem
```
Database Fields:
- position (int, sort order)
- description (str)
- quantity, unit_price (Decimal)
- unit (str)
- tax_rate, discount_percent (Decimal)

Computed Properties:
- subtotal = quantity * unit_price
- discount_amount = subtotal * (discount_percent / 100)
- subtotal_after_discount = subtotal - discount_amount
- tax_amount = subtotal_after_discount * (tax_rate / 100)
- total = subtotal_after_discount + tax_amount
```

### Payment
```
Database Fields:
- amount (Decimal, > 0)
- payment_date (Date)
- method (enum: cash/bank_transfer/credit_card/etc.)
- reference (str, optional - transaction ID)
- note (str, optional)
- invoice_id (FK, required)

Triggers:
- Auto-updates invoice status on create/update/delete via SQLAlchemy events
```

### Expense
```
Database Fields:
- title (str)
- category (enum: travel/material/software/hardware/consulting/marketing/office/training/other)
- amount (Decimal, > 0)
- description (str)
- receipt_path (str, optional)
- note (str, optional)
- is_billable (bool)
- project_id (FK, optional)
- invoice_id (FK, optional)

Computed Properties:
- is_invoiced (bool) - if invoice_id is set
```

---

## Key Constants & Configurations

### Invoice Number Format
- Pattern: `PREFIX-YEAR-SEQNUM`
- Example: `RE-2025-0001`
- Prefixes:
  - RE = Invoice (Rechnung)
  - AN = Quote (Angebot)
  - GS = Credit Note (Gutschrift)
  - ST = Cancellation (Stornierung)

### Document Types
- invoice: Title "RECHNUNG", Color #ff9100
- quote: Title "ANGEBOT", Color #008cff
- credit_note: Title "GUTSCHRIFT", Color #5dcc5d
- order_confirmation: Title "AUFTRAGSBESTÄTIGUNG", Color #9933ff

### Payment Methods
- cash
- bank_transfer
- credit_card
- debit_card
- paypal
- sepa
- other

### Expense Categories
- travel
- material
- software
- hardware
- consulting
- marketing
- office
- training
- other

### Company Details (Hardcoded)
- **Name:** K.I.T. Solutions
- **Owner:** Joshua Phu Kuhrau
- **Address:** Dietzstr. 1, 56073 Koblenz, Germany
- **Email:** info@kit-it-koblenz.de
- **Phone:** Tel. 0162 / 2654262
- **Website:** https://kit-it-koblenz.de
- **IBAN:** DE94100110012706471170
- **BIC:** NTSBDEB1XX
- **Bank:** N26 Bank AG

---

## Recent Development History

**2025-10-24:** Initial implementation
- Created invoices module with full CRUD
- Implemented payment tracking
- Added PDF generation with ReportLab
- Created number sequencing system

**2025-11-19:** Multi-document support
- Added document_type field
- Extended PDF templates for quotes, credit notes, etc.

**2025-12-16:** Finance module expansion
- Added expenses/finance tracking
- Implemented expense KPIs
- Enhanced relationships between invoices and expenses

**2025-12-19:** Document management integration
- Integrated Nextcloud storage
- Enhanced document handling

**2025-12-22:** Documentation
- Created comprehensive documentation
- Architecture analysis
- Quick reference guides

---

## How to Navigate This Documentation

1. **First Time?** → Read FINANCE_AND_INVOICING_ANALYSIS.md Sections 1-3
2. **Need Quick Facts?** → Check FINANCE_QUICK_REFERENCE.md
3. **Implementing Features?** → Use FINANCE_CODE_ARCHITECTURE.md
4. **Need to Know What's Missing?** → See FINANCE_AND_INVOICING_ANALYSIS.md Sections 5 & 10
5. **Debugging Issues?** → Check FINANCE_CODE_ARCHITECTURE.md Error Handling & Validation Layers
6. **Deploying?** → Read FINANCE_CODE_ARCHITECTURE.md Deployment Notes

---

## Testing Your Changes

### Integration Tests
```bash
cd backend/tests
python test_invoice.py
```

### Manual API Testing
Use curl or Postman against:
- `https://api.workmate.intern.phudevelopement.xyz/api/backoffice/invoices/`

### Database Validation
Check migrations applied:
```bash
alembic history
```

---

## Contact & Support

For questions about the finance module:
1. Check the relevant documentation file
2. Review the code comments in the implementation files
3. Look at test_invoice.py for usage examples
4. Check recent git commits for changes

---

## License & Confidentiality

This documentation and code is proprietary to K.I.T. Solutions.

Created: December 22, 2025
Last Updated: December 22, 2025
Version: 1.0

