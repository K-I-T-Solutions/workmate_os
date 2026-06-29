export type InvoiceStatus = "draft" | "sent" | "paid" | "partial" | "overdue" | "cancelled"
export type DocumentType = "invoice" | "quote" | "credit_note" | "order_confirmation"
export type PaymentMethod = "cash" | "bank_transfer" | "credit_card" | "debit_card" | "paypal" | "sepa" | "other"

export interface InvoiceLineItem {
  id: string
  position: number
  description: string
  quantity: string
  unit: string
  unit_price: string
  tax_rate: string
  discount_percent: string
  subtotal: string
  discount_amount: string
  subtotal_after_discount: string
  tax_amount: string
  total: string
}

export interface InvoiceLineItemInput {
  position: number
  description: string
  quantity: string
  unit: string
  unit_price: string
  tax_rate: string
  discount_percent: string
}

export interface CustomerBrief {
  id: string
  name: string
  email: string | null
  city: string | null
}

export interface Invoice {
  id: string
  invoice_number: string
  customer_id: string
  customer: CustomerBrief
  project_id: string | null
  issued_date: string | null
  due_date: string | null
  status: InvoiceStatus
  document_type: DocumentType
  notes: string | null
  terms: string | null
  total: string
  subtotal: string
  tax_amount: string
  pdf_path: string | null
  line_items: InvoiceLineItem[]
  reminders: InvoiceReminder[]
  created_at: string
  updated_at: string
}

export interface InvoiceListResponse {
  items: Invoice[]
  total: number
  skip: number
  limit: number
}

export interface Payment {
  id: string
  invoice_id: string
  amount: string
  payment_date: string | null
  method: PaymentMethod
  reference: string | null
  note: string | null
  created_at: string
  updated_at: string
}

export interface InvoiceReminder {
  id: string
  invoice_id: string
  level: 1 | 2 | 3
  fee: string
  due_date: string | null
  sent_at: string | null
  pdf_path: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CreateInvoicePayload {
  customer_id: string
  document_type: DocumentType
  issued_date?: string | null
  due_date?: string | null
  notes?: string | null
  terms?: string | null
  line_items: InvoiceLineItemInput[]
}

export interface UpdateInvoicePayload {
  customer_id?: string
  document_type?: DocumentType
  issued_date?: string | null
  due_date?: string | null
  notes?: string | null
  terms?: string | null
  line_items?: InvoiceLineItemInput[]
}
