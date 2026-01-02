/**
 * Invoice Service
 * API-Calls für das Invoices-Modul
 * Basiert auf backend/app/modules/backoffice/invoices/routes.py
 */

import { apiClient } from '@/services/api/client';
import type {
  Invoice,
  InvoiceCreateRequest,
  InvoiceUpdateRequest,
  InvoiceListResponse,
  InvoiceStatistics,
  InvoiceFilterParams,
  Payment,
  PaymentCreateRequest,
  PaymentUpdateRequest,
  BulkStatusUpdateRequest,
  BulkStatusUpdateResponse,
} from '../types';

const BASE_PATH = '/api/backoffice/invoices';

/**
 * Invoice Service
 */
export const invoicesService = {
  // ============================================
  // Liste & Statistiken
  // ============================================

  /**
   * Rechnungen mit Filtern und Pagination abrufen
   * GET /api/backoffice/invoices/
   */
  async list(params?: InvoiceFilterParams): Promise<InvoiceListResponse> {
    const response = await apiClient.get<InvoiceListResponse>(BASE_PATH, {
      params,
    });
    return response.data;
  },

  /**
   * Rechnungsstatistiken abrufen
   * GET /api/backoffice/invoices/statistics
   */
  async getStatistics(): Promise<InvoiceStatistics> {
    const response = await apiClient.get<InvoiceStatistics>(`${BASE_PATH}/statistics`);
    return response.data;
  },

  // ============================================
  // Einzelne Rechnung
  // ============================================

  /**
   * Rechnung nach ID abrufen
   * GET /api/backoffice/invoices/{id}
   */
  async getById(id: string): Promise<Invoice> {
    const response = await apiClient.get<Invoice>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  /**
   * Rechnung nach Rechnungsnummer abrufen
   * GET /api/backoffice/invoices/by-number/{invoice_number}
   */
  async getByNumber(invoiceNumber: string): Promise<Invoice> {
    const response = await apiClient.get<Invoice>(`${BASE_PATH}/by-number/${invoiceNumber}`);
    return response.data;
  },

  /**
   * Neue Rechnung erstellen
   * POST /api/backoffice/invoices/
   */
  async create(data: InvoiceCreateRequest): Promise<Invoice> {
    const response = await apiClient.post<Invoice>(BASE_PATH, data);
    return response.data;
  },

  /**
   * Rechnung aktualisieren
   * PATCH /api/backoffice/invoices/{id}
   */
  async update(id: string, data: InvoiceUpdateRequest): Promise<Invoice> {
    const response = await apiClient.patch<Invoice>(`${BASE_PATH}/${id}`, data);
    return response.data;
  },

  /**
   * Nur Rechnungsstatus aktualisieren
   * PATCH /api/backoffice/invoices/{id}/status
   */
  async updateStatus(id: string, status: string): Promise<Invoice> {
    const response = await apiClient.patch<Invoice>(`${BASE_PATH}/${id}/status`, {
      status,
    });
    return response.data;
  },

  /**
   * Rechnungssummen neu berechnen
   * POST /api/backoffice/invoices/{id}/recalculate
   */
  async recalculate(id: string): Promise<Invoice> {
    const response = await apiClient.post<Invoice>(`${BASE_PATH}/${id}/recalculate`);
    return response.data;
  },

  /**
   * Rechnung löschen
   * DELETE /api/backoffice/invoices/{id}
   */
  async delete(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  // ============================================
  // PDF-Operationen
  // ============================================

  /**
   * Rechnungs-PDF herunterladen
   * GET /api/backoffice/invoices/{id}/pdf
   * @returns Blob URL zum Öffnen/Herunterladen
   */
  async downloadPdf(id: string): Promise<Blob> {
    const response = await apiClient.get(`${BASE_PATH}/${id}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * PDF neu generieren
   * POST /api/backoffice/invoices/{id}/regenerate-pdf
   */
  async regeneratePdf(id: string): Promise<Invoice> {
    const response = await apiClient.post<Invoice>(`${BASE_PATH}/${id}/regenerate-pdf`);
    return response.data;
  },

  // ============================================
  // Bulk-Operationen
  // ============================================

  /**
   * Status für mehrere Rechnungen gleichzeitig aktualisieren
   * POST /api/backoffice/invoices/bulk/status-update
   */
  async bulkUpdateStatus(data: BulkStatusUpdateRequest): Promise<BulkStatusUpdateResponse> {
    const response = await apiClient.post<BulkStatusUpdateResponse>(
      `${BASE_PATH}/bulk/status-update`,
      data
    );
    return response.data;
  },

  // ============================================
  // Zahlungen
  // ============================================

  /**
   * Zahlung für Rechnung erstellen
   * POST /api/backoffice/invoices/{invoice_id}/payments
   */
  async createPayment(invoiceId: string, data: PaymentCreateRequest): Promise<Payment> {
    const response = await apiClient.post<Payment>(`${BASE_PATH}/${invoiceId}/payments`, data);
    return response.data;
  },

  /**
   * Alle Zahlungen für eine Rechnung abrufen
   * GET /api/backoffice/invoices/{invoice_id}/payments
   */
  async listPayments(invoiceId: string): Promise<Payment[]> {
    const response = await apiClient.get<Payment[]>(`${BASE_PATH}/${invoiceId}/payments`);
    return response.data;
  },

  /**
   * Einzelne Zahlung abrufen
   * GET /api/backoffice/invoices/payments/{payment_id}
   */
  async getPayment(paymentId: string): Promise<Payment> {
    const response = await apiClient.get<Payment>(`${BASE_PATH}/payments/${paymentId}`);
    return response.data;
  },

  /**
   * Zahlung aktualisieren
   * PATCH /api/backoffice/invoices/payments/{payment_id}
   */
  async updatePayment(paymentId: string, data: PaymentUpdateRequest): Promise<Payment> {
    const response = await apiClient.patch<Payment>(`${BASE_PATH}/payments/${paymentId}`, data);
    return response.data;
  },

  /**
   * Zahlung löschen
   * DELETE /api/backoffice/invoices/payments/{payment_id}
   */
  async deletePayment(paymentId: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(
      `${BASE_PATH}/payments/${paymentId}`
    );
    return response.data;
  },

  // ============================================
  // Hilfsfunktionen
  // ============================================

  /**
   * PDF-Blob in neuem Tab öffnen
   */
  openPdfInNewTab(blob: Blob, filename: string = 'rechnung.pdf'): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.target = '_blank';
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  },

  /**
   * PDF-Download auslösen
   */
  triggerPdfDownload(blob: Blob, filename: string = 'rechnung.pdf'): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  // ============================================
  // Audit Logs (GoBD Compliance)
  // ============================================

  /**
   * Audit Logs mit Filtern abrufen
   * GET /api/backoffice/invoices/audit-logs
   */
  async getAuditLogs(params?: {
    entity_type?: string
    entity_id?: string
    action?: string
    skip?: number
    limit?: number
  }): Promise<{
    items: any[]
    total: number
    skip: number
    limit: number
  }> {
    const response = await apiClient.get(`${BASE_PATH}/audit-logs`, {
      params,
    });
    return response.data;
  },
};

export default invoicesService;
