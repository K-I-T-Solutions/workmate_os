/**
 * Banking Composable
 *
 * State-Management und Business-Logic für Banking-Module
 */
import { ref, computed } from 'vue';
import type { Ref } from 'vue';
import { bankAccountsApi, bankTransactionsApi, psd2Api } from '../services/banking.service';
import type {
  BankAccount,
  BankAccountCreate,
  BankTransaction,
  CsvImportResponse,
} from '../types/banking';

export function useBanking() {
  // State
  const accounts = ref<BankAccount[]>([]);
  const transactions = ref<BankTransaction[]>([]);
  const selectedAccount = ref<BankAccount | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const totalBalance = computed(() => {
    return accounts.value.reduce((sum, acc) => {
      const balance = acc.balance || acc.current_balance || 0;
      const balanceNum = typeof balance === 'string' ? parseFloat(balance) : balance;
      return sum + (isNaN(balanceNum) ? 0 : balanceNum);
    }, 0);
  });

  const accountsByType = computed(() => {
    return accounts.value.reduce((acc, account) => {
      const type = account.account_type;
      if (!acc[type]) acc[type] = [];
      acc[type].push(account);
      return acc;
    }, {} as Record<string, BankAccount[]>);
  });

  // Bank Accounts Actions
  async function fetchAccounts() {
    loading.value = true;
    error.value = null;
    try {
      accounts.value = await bankAccountsApi.getAll();
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchAccountById(id: string) {
    loading.value = true;
    error.value = null;
    try {
      selectedAccount.value = await bankAccountsApi.getById(id);
      return selectedAccount.value;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function createAccount(data: BankAccountCreate) {
    loading.value = true;
    error.value = null;
    try {
      const account = await bankAccountsApi.create(data);
      accounts.value.push(account);
      return account;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function updateAccount(id: string, data: Partial<BankAccountCreate>) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await bankAccountsApi.update(id, data);
      const index = accounts.value.findIndex((a) => a.id === id);
      if (index !== -1) {
        accounts.value[index] = updated;
      }
      if (selectedAccount.value?.id === id) {
        selectedAccount.value = updated;
      }
      return updated;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function deleteAccount(id: string) {
    loading.value = true;
    error.value = null;
    try {
      await bankAccountsApi.delete(id);
      accounts.value = accounts.value.filter((a) => a.id !== id);
      if (selectedAccount.value?.id === id) {
        selectedAccount.value = null;
      }
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  // Bank Transactions Actions
  async function fetchTransactionsByAccount(accountId: string, params?: any) {
    loading.value = true;
    error.value = null;
    try {
      transactions.value = await bankTransactionsApi.getByAccount(accountId, params);
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchAllTransactions(params?: any) {
    loading.value = true;
    error.value = null;
    try {
      transactions.value = await bankTransactionsApi.getAll(params);
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTransaction(id: string) {
    loading.value = true;
    error.value = null;
    try {
      await bankTransactionsApi.delete(id);
      transactions.value = transactions.value.filter((t) => t.id !== id);
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  // CSV Import
  async function importCsv(
    file: File,
    accountId: string,
    options?: any
  ): Promise<CsvImportResponse> {
    loading.value = true;
    error.value = null;
    try {
      const result = await bankTransactionsApi.importCsv(file, accountId, options);
      // Refresh transactions after import
      if (result.success && result.imported && result.imported > 0) {
        await fetchTransactionsByAccount(accountId);
      }
      return result;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  // PSD2 Integration
  async function initiatePSD2Consent(clientId: string, redirectUri: string) {
    loading.value = true;
    error.value = null;
    try {
      const result = await psd2Api.initiateConsent({
        client_id: clientId,
        redirect_uri: redirectUri,
      });
      return result;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function exchangePSD2Code(
    clientId: string,
    authorizationCode: string,
    redirectUri: string
  ) {
    loading.value = true;
    error.value = null;
    try {
      const result = await psd2Api.exchangeCode({
        client_id: clientId,
        authorization_code: authorizationCode,
        redirect_uri: redirectUri,
      });
      return result;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function syncPSD2Accounts(clientId: string, accessToken: string) {
    loading.value = true;
    error.value = null;
    try {
      const result = await psd2Api.syncAccounts({
        client_id: clientId,
        access_token: accessToken,
        create_missing: true,
      });
      // Refresh accounts after sync
      await fetchAccounts();
      return result;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    // State
    accounts,
    transactions,
    selectedAccount,
    loading,
    error,

    // Computed
    totalBalance,
    accountsByType,

    // Actions
    fetchAccounts,
    fetchAccountById,
    createAccount,
    updateAccount,
    deleteAccount,
    fetchTransactionsByAccount,
    fetchAllTransactions,
    deleteTransaction,
    importCsv,
    initiatePSD2Consent,
    exchangePSD2Code,
    syncPSD2Accounts,
  };
}
