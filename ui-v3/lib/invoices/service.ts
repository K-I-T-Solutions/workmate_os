import { apiClient } from "@/lib/api/client"
import type {
  Invoice, InvoiceListResponse, InvoiceStatus, Payment, InvoiceReminder,
  CreateInvoicePayload, UpdateInvoicePayload,
} from "./types"

export const invoiceService = {
  async list(params?: {
    status?: string
    customer_id?: string
    date_from?: string
    date_to?: string
    skip?: number
    limit?: number
  }): Promise<InvoiceListResponse> {
    const { data } = await apiClient.get("/api/backoffice/invoices", { params })
    return data
  },

  async get(id: string): Promise<Invoice> {
    const { data } = await apiClient.get(`/api/backoffice/invoices/${id}`)
    return data
  },

  async create(payload: CreateInvoicePayload): Promise<Invoice> {
    const { data } = await apiClient.post("/api/backoffice/invoices", payload)
    return data
  },

  async update(id: string, payload: UpdateInvoicePayload): Promise<Invoice> {
    const { data } = await apiClient.patch(`/api/backoffice/invoices/${id}`, payload)
    return data
  },

  async updateStatus(id: string, status: InvoiceStatus): Promise<Invoice> {
    const { data } = await apiClient.patch(`/api/backoffice/invoices/${id}/status`, { status })
    return data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/invoices/${id}`)
  },

  async downloadPdf(id: string, filename?: string): Promise<void> {
    const { data } = await apiClient.get(`/api/backoffice/invoices/${id}/pdf`, {
      responseType: "blob",
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement("a")
    a.href = url
    a.target = "_blank"
    a.download = filename ?? `rechnung-${id}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  },

  async getPayments(id: string): Promise<Payment[]> {
    const { data } = await apiClient.get(`/api/backoffice/invoices/${id}/payments`)
    return data
  },

  async addPayment(id: string, payload: {
    amount: string
    payment_date?: string
    method?: string
    reference?: string
    note?: string
  }): Promise<Payment> {
    const { data } = await apiClient.post(`/api/backoffice/invoices/${id}/payments`, payload)
    return data
  },

  async deletePayment(paymentId: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/invoices/payments/${paymentId}`)
  },

  async sendEmail(id: string, payload: { to_email: string; cc_email?: string; message?: string }): Promise<void> {
    await apiClient.post(`/api/backoffice/invoices/${id}/send`, payload)
  },

  async getReminders(invoiceId: string): Promise<InvoiceReminder[]> {
    const { data } = await apiClient.get(`/api/backoffice/invoices/${invoiceId}/reminders`)
    return Array.isArray(data) ? data : []
  },

  async createReminder(invoiceId: string, payload: { level: number; fee?: string; due_date?: string; notes?: string }): Promise<InvoiceReminder> {
    const { data } = await apiClient.post(`/api/backoffice/invoices/${invoiceId}/reminders`, payload)
    return data
  },

  async markReminderSent(reminderId: string): Promise<InvoiceReminder> {
    const { data } = await apiClient.post(`/api/backoffice/invoices/reminders/${reminderId}/mark-sent`)
    return data
  },

  async deleteReminder(reminderId: string): Promise<void> {
    await apiClient.delete(`/api/backoffice/invoices/reminders/${reminderId}`)
  },

  async exportDatevCsv(params?: { status?: string; date_from?: string; date_to?: string }): Promise<void> {
    const res = await invoiceService.list({ ...params, limit: 1000 })
    const rows = res.items

    const fmtNum = (v: string) => parseFloat(v).toFixed(2).replace(".", ",")
    const fmtDate = (d: string | null) =>
      d ? new Date(d).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }) : ""
    const escape = (s: string) => `"${s.replace(/"/g, '""')}"`

    const header = [
      "Belegnummer", "Belegtyp", "Belegdatum", "Fälligkeitsdatum",
      "Kunde", "Status", "Netto", "MwSt", "Brutto", "Notizen",
    ].join(";")

    const lines = rows.map(inv => [
      escape(inv.invoice_number),
      escape(inv.document_type === "invoice" ? "Rechnung" : inv.document_type === "credit_note" ? "Gutschrift" : inv.document_type === "quote" ? "Angebot" : "Auftragsbestätigung"),
      fmtDate(inv.issued_date),
      fmtDate(inv.due_date),
      escape(inv.customer.name),
      escape(inv.status),
      fmtNum(inv.subtotal),
      fmtNum(inv.tax_amount),
      fmtNum(inv.total),
      escape(inv.notes ?? ""),
    ].join(";"))

    const bom = "﻿"
    const csv = bom + [header, ...lines].join("\r\n")
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `datev-export-${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  },
}
