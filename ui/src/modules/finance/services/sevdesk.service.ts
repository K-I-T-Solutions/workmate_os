/**
 * SevDesk Integration Service
 */
import { apiClient } from '@/services/api/client';
import type {
  SevDeskConfig,
  SevDeskConfigRequest,
  SevDeskConfigResponse,
  SevDeskConnectionTestResponse,
  SevDeskSyncInvoiceRequest,
  SevDeskSyncInvoiceResponse,
  SevDeskSyncPaymentsRequest,
  SevDeskSyncPaymentsResponse,
  SevDeskSyncBankAccountRequest,
  SevDeskSyncBankAccountResponse,
  SevDeskSyncTransactionsRequest,
  SevDeskSyncTransactionsResponse,
  SevDeskSyncHistoryListResponse,
} from '../types/sevdesk';

const API_BASE = '/api/backoffice/finance/sevdesk';

export const sevdeskApi = {
  async getConfig(): Promise<SevDeskConfig | null> {
    try {
      const { data } = await apiClient.get(`${API_BASE}/config`);
      return data;
    } catch (e: any) {
      if (e.response?.status === 404) return null;
      throw e;
    }
  },

  async saveConfig(data: SevDeskConfigRequest): Promise<SevDeskConfigResponse> {
    const response = await apiClient.post(`${API_BASE}/config`, data);
    return response.data;
  },

  async deleteConfig(): Promise<void> {
    await apiClient.delete(`${API_BASE}/config`);
  },

  async testConnection(): Promise<SevDeskConnectionTestResponse> {
    const { data } = await apiClient.get(`${API_BASE}/test`);
    return data;
  },

  async syncInvoice(invoiceId: string): Promise<SevDeskSyncInvoiceResponse> {
    const { data } = await apiClient.post(`${API_BASE}/sync/invoice`, {
      invoice_id: invoiceId,
    } as SevDeskSyncInvoiceRequest);
    return data;
  },

  async syncPayments(
    request: SevDeskSyncPaymentsRequest = { sync_all: true }
  ): Promise<SevDeskSyncPaymentsResponse> {
    const { data } = await apiClient.post(`${API_BASE}/sync/payments`, request);
    return data;
  },

  async syncInvoicePayments(invoiceId: string): Promise<SevDeskSyncPaymentsResponse> {
    return this.syncPayments({ invoice_id: invoiceId, sync_all: false });
  },

  async syncBankAccount(bankAccountId: string): Promise<SevDeskSyncBankAccountResponse> {
    const { data } = await apiClient.post(`${API_BASE}/sync/bank-account`, {
      bank_account_id: bankAccountId,
    } as SevDeskSyncBankAccountRequest);
    return data;
  },

  async syncTransactions(
    request: SevDeskSyncTransactionsRequest = {}
  ): Promise<SevDeskSyncTransactionsResponse> {
    const { data } = await apiClient.post(`${API_BASE}/sync/transactions`, request);
    return data;
  },

  async getSyncHistory(params?: {
    sync_type?: string;
    direction?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<SevDeskSyncHistoryListResponse> {
    const { data } = await apiClient.get(`${API_BASE}/sync/history`, { params });
    return data;
  },
};
