/**
 * Invoice Types
 * Entsprechen den Backend-Schemas aus backend/app/modules/backoffice/invoices/schemas.py
 */

export type InvoiceStatus =
  | 'draft'      // Entwurf
  | 'sent'       // Versendet
  | 'paid'       // Bezahlt
  | 'partial'    // Teilbezahlt
  | 'overdue'    // Überfällig
  | 'cancelled'; // Storniert

export type DocumentType =
  | 'invoice'              // Rechnung
  | 'quote'                // Angebot
  | 'credit_note'          // Gutschrift
  | 'order_confirmation';  // Auftragsbestätigung

export interface InvoiceLineItem {
  id?: string;
  position: number;
  description: string;
  quantity: number;
  unit: string;
  unit_price: number;
  tax_rate: number;
  discount_percent: number;
  // Berechnete Felder (vom Backend)
  subtotal?: number;
  discount_amount?: number;
  subtotal_after_discount?: number;
  tax_amount?: number;
  total?: number;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  project_id?: string | null;
  status: InvoiceStatus;
  document_type: DocumentType;
  issued_date?: string | null;
  due_date?: string | null;
  total: number;
  subtotal: number;
  tax_amount: number;
  notes?: string | null;
  terms?: string | null;
  pdf_path?: string | null;
  created_at: string;
  updated_at: string;

  // Relationen
  line_items: InvoiceLineItem[];
  payments?: Payment[];

  // Berechnete Felder (vom Backend)
  paid_amount: number;
  outstanding_amount: number;
  is_paid: boolean;
  is_overdue: boolean;
  payment_rate: number;
  days_until_due?: number | null;

  // Optional: Populated Relations
  customer?: any; // TODO: Type aus CRM-Modul importieren
  project?: any;  // TODO: Type aus Project-Modul importieren
}

export interface Payment {
  id: string;
  invoice_id: string;
  amount: number;
  payment_date: string;
  method: PaymentMethod;
  reference?: string | null;
  note?: string | null;
  created_at: string;
  updated_at: string;
}

export type PaymentMethod =
  | 'cash'           // Bargeld
  | 'bank_transfer'  // Überweisung
  | 'credit_card'    // Kreditkarte
  | 'debit_card'     // EC-Karte
  | 'paypal'         // PayPal
  | 'sepa'           // SEPA-Lastschrift
  | 'other';         // Sonstige

// ============================================
// Request/Response Types für API
// ============================================

export interface InvoiceCreateRequest {
  customer_id: string;
  project_id?: string | null;
  document_type?: DocumentType;
  issued_date?: string | null;
  due_date?: string | null;
  notes?: string | null;
  terms?: string | null;
  line_items: Omit<InvoiceLineItem, 'id' | 'subtotal' | 'discount_amount' | 'subtotal_after_discount' | 'tax_amount' | 'total'>[];
  generate_pdf?: boolean;
}

export interface InvoiceUpdateRequest {
  status?: InvoiceStatus;
  notes?: string | null;
  terms?: string | null;
}

export interface InvoiceListResponse {
  items: Invoice[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

export interface InvoiceStatistics {
  total_count: number;
  total_revenue: number;
  outstanding_amount: number;
  overdue_count: number;
  draft_count: number;
  sent_count: number;
  paid_count: number;
  cancelled_count: number;
}

export interface InvoiceFilterParams {
  skip?: number;
  limit?: number;
  status?: InvoiceStatus;
  customer_id?: string;
  project_id?: string;
  date_from?: string;
  date_to?: string;
}

export interface PaymentCreateRequest {
  amount: number;
  payment_date: string;
  method: PaymentMethod;
  reference?: string | null;
  note?: string | null;
}

export interface PaymentUpdateRequest {
  amount?: number;
  payment_date?: string;
  method?: PaymentMethod;
  reference?: string | null;
  note?: string | null;
}

export interface BulkStatusUpdateRequest {
  invoice_ids: string[];
  new_status: InvoiceStatus;
}

export interface BulkStatusUpdateResponse {
  success_count: number;
  failed_count: number;
  failed_ids: string[];
}
