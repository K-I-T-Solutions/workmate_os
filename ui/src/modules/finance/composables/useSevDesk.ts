/**
 * SevDesk Composable
 *
 * State-Management und Business-Logic für SevDesk Integration
 */
import { ref, computed } from 'vue';
import { sevdeskApi } from '../services/sevdesk.service';
import type {
  SevDeskConfig,
  SevDeskConfigRequest,
  SevDeskConnectionTestResponse,
  SevDeskSyncInvoiceResponse,
  SevDeskSyncPaymentsResponse,
  SevDeskSyncBankAccountResponse,
  SevDeskSyncTransactionsResponse,
  SevDeskSyncHistory,
} from '../types/sevdesk';

export function useSevDesk() {
  // State
  const config = ref<SevDeskConfig | null>(null);
  const syncHistory = ref<SevDeskSyncHistory[]>([]);
  const loading = ref(false);
  const syncing = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const isConfigured = computed(() => {
    return config.value !== null && config.value.configured && config.value.is_active;
  });

  const autoSyncEnabled = computed(() => {
    return config.value?.auto_sync_enabled || false;
  });

  const lastSyncTime = computed(() => {
    return config.value?.last_sync_at || null;
  });

  const recentSyncHistory = computed(() => {
    return syncHistory.value.slice(0, 10); // Last 10 syncs
  });

  // Config Actions
  async function fetchConfig() {
    loading.value = true;
    error.value = null;
    try {
      config.value = await sevdeskApi.getConfig();
      return config.value;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to fetch SevDesk config:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function saveConfig(data: SevDeskConfigRequest) {
    loading.value = true;
    error.value = null;
    try {
      const response = await sevdeskApi.saveConfig(data);
      if (response.success) {
        // Refresh config after save
        await fetchConfig();
      }
      return response;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to save SevDesk config:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function deleteConfig() {
    loading.value = true;
    error.value = null;
    try {
      await sevdeskApi.deleteConfig();
      config.value = null;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to delete SevDesk config:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  // Connection Test
  async function testConnection(): Promise<SevDeskConnectionTestResponse> {
    loading.value = true;
    error.value = null;
    try {
      const result = await sevdeskApi.testConnection();
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to test SevDesk connection:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  // Invoice Sync
  async function syncInvoice(invoiceId: string): Promise<SevDeskSyncInvoiceResponse> {
    syncing.value = true;
    error.value = null;
    try {
      const result = await sevdeskApi.syncInvoice(invoiceId);
      // Refresh sync history after successful sync
      if (result.success) {
        await fetchSyncHistory({ sync_type: 'invoice', limit: 10 });
      }
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to sync invoice to SevDesk:', e);
      throw e;
    } finally {
      syncing.value = false;
    }
  }

  // Payment Sync
  async function syncPayments(invoiceId?: string): Promise<SevDeskSyncPaymentsResponse> {
    syncing.value = true;
    error.value = null;
    try {
      const result = invoiceId
        ? await sevdeskApi.syncInvoicePayments(invoiceId)
        : await sevdeskApi.syncPayments({ sync_all: true });

      // Refresh sync history after successful sync
      if (result.success) {
        await fetchSyncHistory({ sync_type: 'payment', limit: 10 });
        await fetchConfig(); // Update last_sync_at
      }
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to sync payments from SevDesk:', e);
      throw e;
    } finally {
      syncing.value = false;
    }
  }

  // Bank Account Sync
  async function syncBankAccount(bankAccountId: string): Promise<SevDeskSyncBankAccountResponse> {
    syncing.value = true;
    error.value = null;
    try {
      const result = await sevdeskApi.syncBankAccount(bankAccountId);
      // Refresh sync history after successful sync
      if (result.success) {
        await fetchSyncHistory({ sync_type: 'bank_account', limit: 10 });
      }
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to sync bank account to SevDesk:', e);
      throw e;
    } finally {
      syncing.value = false;
    }
  }

  // Transaction Sync
  async function syncTransactions(
    checkAccountId?: string,
    limit?: number
  ): Promise<SevDeskSyncTransactionsResponse> {
    syncing.value = true;
    error.value = null;
    try {
      const result = await sevdeskApi.syncTransactions({
        check_account_id: checkAccountId,
        limit: limit,
      });
      // Refresh sync history after successful sync
      if (result.success) {
        await fetchSyncHistory({ sync_type: 'transaction', limit: 10 });
        await fetchConfig(); // Update last_sync_at
      }
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to sync transactions from SevDesk:', e);
      throw e;
    } finally {
      syncing.value = false;
    }
  }

  // Sync History
  async function fetchSyncHistory(params?: {
    sync_type?: string;
    direction?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }) {
    loading.value = true;
    error.value = null;
    try {
      const result = await sevdeskApi.getSyncHistory(params);
      syncHistory.value = result.items || [];
      return result;
    } catch (e: any) {
      error.value = e.message;
      console.error('Failed to fetch sync history:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  // Helper: Check if config exists and is valid
  async function checkConfiguration(): Promise<boolean> {
    try {
      await fetchConfig();
      return isConfigured.value;
    } catch (e) {
      return false;
    }
  }

  return {
    // State
    config,
    syncHistory,
    loading,
    syncing,
    error,

    // Computed
    isConfigured,
    autoSyncEnabled,
    lastSyncTime,
    recentSyncHistory,

    // Actions
    fetchConfig,
    saveConfig,
    deleteConfig,
    testConnection,
    syncInvoice,
    syncPayments,
    syncBankAccount,
    syncTransactions,
    fetchSyncHistory,
    checkConfiguration,
  };
}
