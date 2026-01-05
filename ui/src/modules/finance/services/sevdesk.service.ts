/**
 * SevDesk Integration Service
 *
 * API-Client für SevDesk Buchhaltungs-Integration
 */
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
const TOKEN_KEY = 'auth_token';

/**
 * Check if token looks like a valid JWT
 */
function isValidJWT(token: string): boolean {
  // JWT has 3 parts separated by dots
  const parts = token.split('.');
  return parts.length === 3;
}

/**
 * Authenticated fetch wrapper with JWT token
 */
async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  // Get token from localStorage
  const token = localStorage.getItem(TOKEN_KEY);

  console.log('💼 [SevDesk API] Request:', {
    url,
    method: options.method || 'GET',
    hasToken: !!token,
    tokenLength: token?.length || 0,
    isValidJWT: token ? isValidJWT(token) : false,
    tokenPreview: token ? token.substring(0, 50) + '...' : 'none',
    hasBody: !!options.body,
  });

  // Build headers with Authorization token
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token && isValidJWT(token)) {
    headers['Authorization'] = `Bearer ${token}`;
  } else if (token && !isValidJWT(token)) {
    console.error('⚠️ [SevDesk API] Token in localStorage is not a valid JWT! This might be the SevDesk API token instead of auth token.');
    console.error('⚠️ [SevDesk API] Please re-login to get a valid JWT token.');
  } else {
    console.warn('⚠️ [SevDesk API] No auth token found in localStorage!');
  }

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Send cookies if any
    headers,
  });

  console.log('💼 [SevDesk API] Response:', {
    url,
    status: response.status,
    statusText: response.statusText,
    ok: response.ok,
    contentType: response.headers.get('content-type'),
  });

  return response;
}

/**
 * SevDesk API
 */
export const sevdeskApi = {
  // ============================================================================
  // CONFIG
  // ============================================================================

  /**
   * SevDesk Konfiguration abrufen
   */
  async getConfig(): Promise<SevDeskConfig | null> {
    console.log('💼 [sevdeskApi.getConfig] Starting...');
    const response = await authFetch(`${API_BASE}/config`);

    if (response.status === 404) {
      console.log('💼 [sevdeskApi.getConfig] No config found (404)');
      return null;
    }

    if (!response.ok) {
      console.error('❌ [sevdeskApi.getConfig] Response not OK');
      throw new Error('Failed to fetch SevDesk config');
    }

    const data = await response.json();
    console.log('💼 [sevdeskApi.getConfig] Parsed JSON:', data);
    return data;
  },

  /**
   * SevDesk Konfiguration speichern/aktualisieren
   */
  async saveConfig(data: SevDeskConfigRequest): Promise<SevDeskConfigResponse> {
    console.log('💼 [sevdeskApi.saveConfig] Saving config...', data);

    try {
      const response = await authFetch(`${API_BASE}/config`, {
        method: 'POST',
        body: JSON.stringify(data),
      });

      console.log('💼 [sevdeskApi.saveConfig] Response received, status:', response.status);
      console.log('💼 [sevdeskApi.saveConfig] Content-Type:', response.headers.get('content-type'));

      // Clone response so we can read it multiple times if needed
      const responseClone = response.clone();

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        // Not JSON, try to read as text
        const text = await response.text();
        console.error('💼 [sevdeskApi.saveConfig] Non-JSON response:', text.substring(0, 500));
        throw new Error(`Server returned non-JSON response: ${text.substring(0, 200)}`);
      }

      // Read the response body as JSON
      let responseData;
      try {
        responseData = await response.json();
        console.log('💼 [sevdeskApi.saveConfig] Response data:', responseData);
      } catch (parseError) {
        // Use the cloned response to read as text
        const text = await responseClone.text();
        console.error('💼 [sevdeskApi.saveConfig] JSON parse error:', parseError);
        console.error('💼 [sevdeskApi.saveConfig] Response text:', text);
        throw new Error(`Failed to parse JSON response: ${text.substring(0, 200)}`);
      }

      if (!response.ok) {
        const errorMessage = responseData.detail || responseData.message || 'Failed to save SevDesk config';
        console.error('💼 [sevdeskApi.saveConfig] Error:', errorMessage);
        throw new Error(errorMessage);
      }

      return responseData;
    } catch (e: any) {
      console.error('💼 [sevdeskApi.saveConfig] Exception:', e);
      throw e;
    }
  },

  /**
   * SevDesk Konfiguration deaktivieren
   */
  async deleteConfig(): Promise<void> {
    console.log('💼 [sevdeskApi.deleteConfig] Deleting config...');
    const response = await authFetch(`${API_BASE}/config`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete SevDesk config');
    }
  },

  // ============================================================================
  // TEST CONNECTION
  // ============================================================================

  /**
   * SevDesk Verbindung testen
   */
  async testConnection(): Promise<SevDeskConnectionTestResponse> {
    console.log('💼 [sevdeskApi.testConnection] Testing connection...');
    const response = await authFetch(`${API_BASE}/test`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to test SevDesk connection');
    }

    return response.json();
  },

  // ============================================================================
  // INVOICE SYNC
  // ============================================================================

  /**
   * Rechnung zu SevDesk pushen
   */
  async syncInvoice(invoiceId: string): Promise<SevDeskSyncInvoiceResponse> {
    console.log('💼 [sevdeskApi.syncInvoice] Syncing invoice:', invoiceId);
    const requestData: SevDeskSyncInvoiceRequest = {
      invoice_id: invoiceId,
    };

    const response = await authFetch(`${API_BASE}/sync/invoice`, {
      method: 'POST',
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to sync invoice to SevDesk');
    }

    return response.json();
  },

  // ============================================================================
  // PAYMENT SYNC
  // ============================================================================

  /**
   * Zahlungen von SevDesk pullen
   */
  async syncPayments(
    request: SevDeskSyncPaymentsRequest = { sync_all: true }
  ): Promise<SevDeskSyncPaymentsResponse> {
    console.log('💼 [sevdeskApi.syncPayments] Syncing payments:', request);
    const response = await authFetch(`${API_BASE}/sync/payments`, {
      method: 'POST',
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to sync payments from SevDesk');
    }

    return response.json();
  },

  /**
   * Zahlungen für eine spezifische Rechnung pullen
   */
  async syncInvoicePayments(invoiceId: string): Promise<SevDeskSyncPaymentsResponse> {
    console.log('💼 [sevdeskApi.syncInvoicePayments] Syncing payments for invoice:', invoiceId);
    return this.syncPayments({
      invoice_id: invoiceId,
      sync_all: false,
    });
  },

  // ============================================================================
  // BANK ACCOUNT SYNC
  // ============================================================================

  /**
   * Bankkonto zu SevDesk mappen
   */
  async syncBankAccount(bankAccountId: string): Promise<SevDeskSyncBankAccountResponse> {
    console.log('💼 [sevdeskApi.syncBankAccount] Syncing bank account:', bankAccountId);
    const requestData: SevDeskSyncBankAccountRequest = {
      bank_account_id: bankAccountId,
    };

    const response = await authFetch(`${API_BASE}/sync/bank-account`, {
      method: 'POST',
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to sync bank account to SevDesk');
    }

    return response.json();
  },

  // ============================================================================
  // TRANSACTION SYNC
  // ============================================================================

  /**
   * Transaktionen von SevDesk pullen
   */
  async syncTransactions(
    request: SevDeskSyncTransactionsRequest = {}
  ): Promise<SevDeskSyncTransactionsResponse> {
    console.log('💼 [sevdeskApi.syncTransactions] Syncing transactions:', request);
    const response = await authFetch(`${API_BASE}/sync/transactions`, {
      method: 'POST',
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to sync transactions from SevDesk');
    }

    return response.json();
  },

  // ============================================================================
  // SYNC HISTORY
  // ============================================================================

  /**
   * Sync-Historie abrufen
   */
  async getSyncHistory(params?: {
    sync_type?: string;
    direction?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<SevDeskSyncHistoryListResponse> {
    console.log('💼 [sevdeskApi.getSyncHistory] Fetching sync history...');
    const query = new URLSearchParams();
    if (params?.sync_type) query.set('sync_type', params.sync_type);
    if (params?.direction) query.set('direction', params.direction);
    if (params?.status) query.set('status', params.status);
    if (params?.skip) query.set('skip', params.skip.toString());
    if (params?.limit) query.set('limit', params.limit.toString());

    const url = query.toString()
      ? `${API_BASE}/sync/history?${query.toString()}`
      : `${API_BASE}/sync/history`;

    const response = await authFetch(url);

    if (!response.ok) {
      throw new Error('Failed to fetch sync history');
    }

    return response.json();
  },
};
