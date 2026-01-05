/**
 * Banking Service
 *
 * API-Client für Bank-Konten, Transaktionen und CSV-Import
 */
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

/**
 * Authenticated fetch wrapper with credentials
 */
async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  console.log('🏦 [Banking API] Request:', {
    url,
    method: options.method || 'GET',
    credentials: 'include',
    hasBody: !!options.body,
  });

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Send cookies for authentication
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  console.log('🏦 [Banking API] Response:', {
    url,
    status: response.status,
    statusText: response.statusText,
    ok: response.ok,
    contentType: response.headers.get('content-type'),
  });

  // Log response body if it's not JSON (this is the problem!)
  const contentType = response.headers.get('content-type');
  if (contentType && !contentType.includes('application/json')) {
    const text = await response.text();
    console.error('⚠️ [Banking API] Expected JSON but got HTML:', {
      url,
      contentType,
      bodyPreview: text.substring(0, 500), // First 500 chars
    });
    throw new Error(`API returned HTML instead of JSON. Check proxy/CORS configuration.`);
  }

  if (!response.ok) {
    const text = await response.text();
    console.error('❌ [Banking API] Error Response:', {
      url,
      status: response.status,
      body: text,
    });
  }

  return response;
}

/**
 * Bank Accounts API
 */
export const bankAccountsApi = {
  /**
   * Alle Bank-Konten abrufen
   */
  async getAll(): Promise<BankAccount[]> {
    console.log('🏦 [bankAccountsApi.getAll] Starting...');
    const response = await authFetch(`${API_BASE}/bank-accounts`);

    if (!response.ok) {
      console.error('❌ [bankAccountsApi.getAll] Response not OK');
      throw new Error('Failed to fetch bank accounts');
    }

    const data = await response.json();
    console.log('🏦 [bankAccountsApi.getAll] Parsed JSON:', data);

    const accounts = data.items || data;
    console.log('🏦 [bankAccountsApi.getAll] Returning accounts:', accounts);

    return accounts;
  },

  /**
   * Ein Bank-Konto per ID abrufen
   */
  async getById(id: string): Promise<BankAccount> {
    const response = await authFetch(`${API_BASE}/bank-accounts/${id}`);
    if (!response.ok) throw new Error('Failed to fetch bank account');
    return response.json();
  },

  /**
   * Neues Bank-Konto erstellen
   */
  async create(data: BankAccountCreate): Promise<BankAccount> {
    const response = await authFetch(`${API_BASE}/bank-accounts`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create bank account');
    return response.json();
  },

  /**
   * Bank-Konto aktualisieren
   */
  async update(id: string, data: Partial<BankAccountCreate>): Promise<BankAccount> {
    const response = await authFetch(`${API_BASE}/bank-accounts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update bank account');
    return response.json();
  },

  /**
   * Bank-Konto löschen
   */
  async delete(id: string): Promise<void> {
    const response = await authFetch(`${API_BASE}/bank-accounts/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete bank account');
  },

  /**
   * Bank-Konten Statistiken
   */
  async getStats(): Promise<BankAccountsStats> {
    const response = await authFetch(`${API_BASE}/bank-accounts/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },
};

/**
 * Bank Transactions API
 */
export const bankTransactionsApi = {
  /**
   * Transaktionen für ein Konto abrufen
   */
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
    const query = new URLSearchParams();
    if (params?.date_from) query.set('date_from', params.date_from);
    if (params?.date_to) query.set('date_to', params.date_to);
    if (params?.transaction_type) query.set('transaction_type', params.transaction_type);
    if (params?.reconciliation_status) query.set('reconciliation_status', params.reconciliation_status);
    if (params?.skip) query.set('skip', params.skip.toString());
    if (params?.limit) query.set('limit', params.limit.toString());

    const response = await authFetch(
      `${API_BASE}/bank-transactions/account/${accountId}?${query.toString()}`
    );
    if (!response.ok) throw new Error('Failed to fetch transactions');
    const data = await response.json();
    return data.items || data;
  },

  /**
   * Alle Transaktionen abrufen
   */
  async getAll(params?: {
    date_from?: string;
    date_to?: string;
    skip?: number;
    limit?: number;
  }): Promise<BankTransaction[]> {
    const query = new URLSearchParams();
    if (params?.date_from) query.set('date_from', params.date_from);
    if (params?.date_to) query.set('date_to', params.date_to);
    if (params?.skip) query.set('skip', params.skip.toString());
    if (params?.limit) query.set('limit', params.limit.toString());

    const response = await authFetch(`${API_BASE}/bank-transactions?${query.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch transactions');
    const data = await response.json();
    return data.items || data;
  },

  /**
   * Transaktion per ID abrufen
   */
  async getById(id: string): Promise<BankTransaction> {
    const response = await authFetch(`${API_BASE}/bank-transactions/${id}`);
    if (!response.ok) throw new Error('Failed to fetch transaction');
    return response.json();
  },

  /**
   * Neue Transaktion erstellen
   */
  async create(data: BankTransactionCreate): Promise<BankTransaction> {
    const response = await authFetch(`${API_BASE}/bank-transactions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create transaction');
    return response.json();
  },

  /**
   * Transaktion löschen
   */
  async delete(id: string): Promise<void> {
    const response = await authFetch(`${API_BASE}/bank-transactions/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete transaction');
  },

  /**
   * Transaktionen-Statistiken
   */
  async getStats(accountId?: string): Promise<TransactionStats> {
    const url = accountId
      ? `${API_BASE}/bank-transactions/stats?account_id=${accountId}`
      : `${API_BASE}/bank-transactions/stats`;
    const response = await authFetch(url);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },

  /**
   * CSV-Import
   */
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

    const query = new URLSearchParams();
    query.set('account_id', accountId);
    if (options?.delimiter) query.set('delimiter', options.delimiter);
    if (options?.skip_duplicates !== undefined)
      query.set('skip_duplicates', options.skip_duplicates.toString());
    if (options?.auto_reconcile !== undefined)
      query.set('auto_reconcile', options.auto_reconcile.toString());

    // Special handling for FormData - don't set Content-Type (browser will set multipart/form-data)
    const response = await fetch(
      `${API_BASE}/bank-transactions/import-csv?${query.toString()}`,
      {
        method: 'POST',
        credentials: 'include',
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'CSV import failed');
    }

    return response.json();
  },
};

/**
 * PSD2 API
 */
export const psd2Api = {
  /**
   * PSD2 Consent Flow starten
   */
  async initiateConsent(data: PSD2ConsentRequest): Promise<PSD2ConsentResponse> {
    const response = await fetch(`${API_BASE}/psd2/consent/initiate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to initiate consent');
    return response.json();
  },

  /**
   * PSD2 Consent Callback (Authorization Code Exchange)
   */
  async exchangeCode(data: PSD2TokenRequest): Promise<PSD2TokenResponse> {
    const response = await fetch(`${API_BASE}/psd2/consent/callback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to exchange authorization code');
    return response.json();
  },

  /**
   * PSD2 Konten synchronisieren
   */
  async syncAccounts(data: {
    client_id: string;
    access_token: string;
    create_missing?: boolean;
  }): Promise<any> {
    const query = new URLSearchParams();
    if (data.create_missing !== undefined)
      query.set('create_missing', data.create_missing.toString());

    const response = await fetch(`${API_BASE}/psd2/accounts/sync?${query.toString()}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: data.client_id,
        access_token: data.access_token,
      }),
    });
    if (!response.ok) throw new Error('Failed to sync accounts');
    return response.json();
  },

  /**
   * PSD2 Transaktionen synchronisieren
   */
  async syncTransactions(data: {
    client_id: string;
    access_token: string;
    account_id: string;
    psd2_account_id: string;
    date_from?: string;
    date_to?: string;
    skip_duplicates?: boolean;
    auto_reconcile?: boolean;
  }): Promise<any> {
    const response = await fetch(`${API_BASE}/psd2/transactions/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to sync transactions');
    return response.json();
  },
};
