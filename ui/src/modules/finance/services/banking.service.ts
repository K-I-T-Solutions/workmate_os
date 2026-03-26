/**
 * Banking Service
 */
import { apiClient } from '@/services/api/client';
import type {
  BankAccount,
  BankAccountCreate,
  BankTransaction,
  BankTransactionCreate,
  CsvImportResponse,
  PSD2ConsentRequest,
  PSD2ConsentResponse,
  PSD2TokenRequest,
  PSD2TokenResponse,
  BankAccountsStats,
  TransactionStats,
} from '../types/banking';

const API_BASE = '/api/backoffice/finance';

export const bankAccountsApi = {
  async getAll(): Promise<BankAccount[]> {
    const { data } = await apiClient.get(`${API_BASE}/bank-accounts`);
    return data.items || data;
  },

  async getById(id: string): Promise<BankAccount> {
    const { data } = await apiClient.get(`${API_BASE}/bank-accounts/${id}`);
    return data;
  },

  async create(payload: BankAccountCreate): Promise<BankAccount> {
    const { data } = await apiClient.post(`${API_BASE}/bank-accounts`, payload);
    return data;
  },

  async update(id: string, payload: Partial<BankAccountCreate>): Promise<BankAccount> {
    const { data } = await apiClient.put(`${API_BASE}/bank-accounts/${id}`, payload);
    return data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`${API_BASE}/bank-accounts/${id}`);
  },

  async getStats(): Promise<BankAccountsStats> {
    const { data } = await apiClient.get(`${API_BASE}/bank-accounts/stats`);
    return data;
  },
};

export const bankTransactionsApi = {
  async getByAccount(
    accountId: string,
    params?: {
      date_from?: string;
      date_to?: string;
      transaction_type?: string;
      reconciliation_status?: string;
      skip?: number;
      limit?: number;
    }
  ): Promise<BankTransaction[]> {
    const { data } = await apiClient.get(
      `${API_BASE}/bank-transactions/account/${accountId}`,
      { params }
    );
    return data.items || data;
  },

  async getAll(params?: {
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }): Promise<BankTransaction[]> {
    const { data } = await apiClient.get(`${API_BASE}/bank-transactions`, { params });
    return data.items || data;
  },

  async getById(id: string): Promise<BankTransaction> {
    const { data } = await apiClient.get(`${API_BASE}/bank-transactions/${id}`);
    return data;
  },

  async create(payload: BankTransactionCreate): Promise<BankTransaction> {
    const { data } = await apiClient.post(`${API_BASE}/bank-transactions`, payload);
    return data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`${API_BASE}/bank-transactions/${id}`);
  },

  async getStats(accountId?: string): Promise<TransactionStats> {
    const { data } = await apiClient.get(`${API_BASE}/bank-transactions/stats`, {
      params: accountId ? { account_id: accountId } : undefined,
    });
    return data;
  },

  async importCsv(
    file: File,
    accountId: string,
    options?: {
      delimiter?: string;
      skip_duplicates?: boolean;
      auto_reconcile?: boolean;
    }
  ): Promise<CsvImportResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await apiClient.post(
      `${API_BASE}/bank-transactions/import-csv`,
      formData,
      {
        params: { account_id: accountId, ...options },
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return data;
  },
};

export const psd2Api = {
  async initiateConsent(payload: PSD2ConsentRequest): Promise<PSD2ConsentResponse> {
    const { data } = await apiClient.post(`${API_BASE}/psd2/consent/initiate`, payload);
    return data;
  },

  async exchangeCode(payload: PSD2TokenRequest): Promise<PSD2TokenResponse> {
    const { data } = await apiClient.post(`${API_BASE}/psd2/consent/callback`, payload);
    return data;
  },

  async syncAccounts(payload: {
    client_id: string;
    access_token: string;
    create_missing?: boolean;
  }): Promise<any> {
    const { create_missing, ...body } = payload;
    const { data } = await apiClient.post(`${API_BASE}/psd2/accounts/sync`, body, {
      params: create_missing !== undefined ? { create_missing } : undefined,
    });
    return data;
  },

  async syncTransactions(payload: {
    client_id: string;
    access_token: string;
    account_id: string;
    psd2_account_id: string;
    date_from?: string;
    date_to?: string;
    skip_duplicates?: boolean;
    auto_reconcile?: boolean;
  }): Promise<any> {
    const { data } = await apiClient.post(`${API_BASE}/psd2/transactions/sync`, payload);
    return data;
  },
};
