# WorkmateOS Finance & Invoicing - Quick Reference

## Current Implementation Status

### Fully Implemented Features
- [x] Invoice creation with line items
- [x] Automatic invoice numbering (RE-2025-0001 format)
- [x] Payment tracking & recording
- [x] Invoice status management (draft, sent, paid, partial, overdue, cancelled)
- [x] Auto-status updates when payments received
- [x] Professional PDF generation with SEPA QR codes
- [x] Expense tracking with categories
- [x] Financial KPIs (totals, by-category breakdown)
- [x] Full REST API with pagination & filters
- [x] Database validation & constraints
- [x] Customer & Project integration
- [x] Multiple document types (invoice, quote, credit_note, order_confirmation)
- [x] Payment method tracking (cash, bank_transfer, credit_card, etc.)
- [x] Decimal arithmetic for financial accuracy

### Not Yet Implemented
- [ ] Frontend UI components
- [ ] Payment gateway integration (Stripe, PayPal)
- [ ] Advanced financial reports (P&L, tax, cash flow)
- [ ] Accounting features (ledger, journal, chart of accounts)
- [ ] Email notifications
- [ ] Overdue invoice reminders
- [ ] Multi-currency support
- [ ] Invoice audit trail
- [ ] Custom invoice templates
- [ ] Batch invoice operations

---

## Key API Paths

### Invoices
```
GET    /api/backoffice/invoices/
POST   /api/backoffice/invoices/
GET    /api/backoffice/invoices/statistics
GET    /api/backoffice/invoices/{invoice_id}
GET    /api/backoffice/invoices/{invoice_id}/pdf
PATCH  /api/backoffice/invoices/{invoice_id}
DELETE /api/backoffice/invoices/{invoice_id}
POST   /api/backoffice/invoices/{invoice_id}/payments
```

### Finance
```
GET    /api/backoffice/finance/expenses
POST   /api/backoffice/finance/expenses
GET    /api/backoffice/finance/kpis/expenses
```

---

## Database Models (Entity Relationship)

```
Customer ─────────→ Invoice ──────────→ InvoiceLineItem
                         ↓
                       Payment

Project ───→ Invoice
        ↓
      Expense ──→ Invoice (optional)
```

---

## Important Numbers & Formats

- **Invoice Number Format:** `PREFIX-YEAR-SEQNUM` (e.g., `RE-2025-0001`)
- **Prefixes by Type:**
  - RE = Invoice (Rechnung)
  - AN = Quote (Angebot)
  - GS = Credit Note (Gutschrift)
  - ST = Cancellation (Stornierung)
- **VAT Default:** 19%
- **Pagination Max:** 500 items per request
- **Supported Payment Methods:** 7 (cash, bank_transfer, credit_card, debit_card, paypal, sepa, other)

---

## File Locations

| Component | Path |
|-----------|------|
| Invoice Models | `backend/app/modules/backoffice/invoices/models.py` |
| Invoice API | `backend/app/modules/backoffice/invoices/routes.py` |
| Invoice CRUD | `backend/app/modules/backoffice/invoices/crud.py` |
| Payments CRUD | `backend/app/modules/backoffice/invoices/payments_crud.py` |
| PDF Generator | `backend/app/modules/backoffice/invoices/pdf_generator.py` |
| Finance Models | `backend/app/modules/backoffice/finance/models.py` |
| Finance API | `backend/app/modules/backoffice/finance/router.py` |
| Finance CRUD | `backend/app/modules/backoffice/finance/crud.py` |
| Schemas | `backend/app/modules/backoffice/{invoices,finance}/schemas.py` |
| Migrations | `backend/alembic/versions/*` (3 migration files) |

---

## Invoice Object Properties (Computed)

```python
invoice.paid_amount          # Sum of all payments
invoice.outstanding_amount   # Total - paid_amount
invoice.is_paid             # Boolean: outstanding_amount == 0
invoice.is_overdue          # Boolean: today > due_date and not paid
invoice.payment_rate        # Percentage paid (0-100)
invoice.days_until_due      # Remaining days (-N if overdue)
```

---

## Line Item Calculations

```
subtotal               = quantity × unit_price
discount_amount        = subtotal × (discount_percent / 100)
subtotal_after_discount = subtotal - discount_amount
tax_amount             = subtotal_after_discount × (tax_rate / 100)
line_total             = subtotal_after_discount + tax_amount
```

---

## Invoice Status Flow

```
DRAFT → SENT → { PAID | PARTIAL | OVERDUE } | CANCELLED
```

Status is **auto-updated** when:
- Payment created: may become PAID or PARTIAL
- Payment updated: status recalculated
- Payment deleted: status recalculated

---

## Company Details (Hardcoded in PDF)

- **Name:** K.I.T. Solutions
- **Owner:** Joshua Phu Kuhrau
- **Address:** Dietzstr. 1, 56073 Koblenz, Germany
- **Email:** info@kit-it-koblenz.de
- **Phone:** Tel. 0162 / 2654262
- **Website:** https://kit-it-koblenz.de
- **IBAN:** DE94100110012706471170
- **BIC:** NTSBDEB1XX

---

## Recent Changes (from git commits)

1. **2025-10-24**: Initial invoices & payments module with PDF generation
2. **2025-11-19**: Added document_type field (multi-document support)
3. **2025-12-16**: Enhanced with finance module & expense tracking
4. **2025-12-19**: Nextcloud storage integration for documents

---

## Testing

**Test File:** `backend/tests/test_invoice.py`

Manual integration test against live API. Tests:
- Invoice creation with line items
- PDF generation & download
- Payment flow
- Status updates

Run with: `python tests/test_invoice.py`

---

## Next Priorities

1. **UI Module** - Create Vue.3/Vite components for invoice/finance management
2. **Payment Gateway** - Stripe/PayPal integration with webhooks
3. **Advanced Reports** - P&L, tax, cash flow, profitability analysis
4. **Accounting** - Chart of accounts, journal entries, ledger views
5. **Financial Analytics** - Dashboards, trend analysis, forecasting

