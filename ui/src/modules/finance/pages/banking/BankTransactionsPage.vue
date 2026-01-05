<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useBanking } from '../../composables/useBanking';
import type { BankTransaction } from '../../types/banking';

const {
  accounts,
  transactions,
  loading,
  error,
  fetchAccounts,
  fetchAllTransactions,
  fetchTransactionsByAccount,
  deleteTransaction,
  importCsv,
} = useBanking();

// Filter state
const selectedAccountId = ref<string>('all');
const selectedType = ref<string>('all');
const selectedStatus = ref<string>('all');
const searchQuery = ref('');

// CSV Import state
const showImportModal = ref(false);
const importFile = ref<File | null>(null);
const importAccountId = ref('');
const importDelimiter = ref(';');
const importSkipDuplicates = ref(true);
const importAutoReconcile = ref(true);
const importResult = ref<any>(null);

// Load data on mount
onMounted(async () => {
  await fetchAccounts();
  await fetchAllTransactions();
});

// Filtered transactions
const filteredTransactions = computed(() => {
  let result = transactions.value;

  // Filter by account
  if (selectedAccountId.value !== 'all') {
    result = result.filter((t) => t.account_id === selectedAccountId.value);
  }

  // Filter by type
  if (selectedType.value !== 'all') {
    result = result.filter((t) => t.transaction_type === selectedType.value);
  }

  // Filter by status
  if (selectedStatus.value !== 'all') {
    result = result.filter((t) => t.reconciliation_status === selectedStatus.value);
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (t) =>
        t.counterparty_name?.toLowerCase().includes(query) ||
        t.purpose?.toLowerCase().includes(query) ||
        t.reference?.toLowerCase().includes(query)
    );
  }

  return result;
});

// Transaction stats
const stats = computed(() => {
  const filtered = filteredTransactions.value;
  return {
    total: filtered.length,
    income: filtered.filter((t) => t.transaction_type === 'income').reduce((sum, t) => sum + t.amount, 0),
    expense: filtered.filter((t) => t.transaction_type === 'expense').reduce((sum, t) => sum + Math.abs(t.amount), 0),
    reconciled: filtered.filter((t) => t.reconciliation_status === 'reconciled').length,
    unreconciled: filtered.filter((t) => t.reconciliation_status === 'unreconciled').length,
  };
});

// Format currency
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
}

// Format date
function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('de-DE');
}

// Get account name by ID
function getAccountName(accountId: string): string {
  const account = accounts.value.find((a) => a.id === accountId);
  return account?.account_name || '-';
}

// Delete transaction
async function handleDeleteTransaction(transaction: BankTransaction) {
  if (confirm(`Transaktion wirklich löschen?`)) {
    try {
      await deleteTransaction(transaction.id);
    } catch (e) {
      console.error('Failed to delete transaction:', e);
    }
  }
}

// CSV Import handlers
function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    importFile.value = target.files[0];
  }
}

async function handleImport() {
  if (!importFile.value || !importAccountId.value) {
    alert('Bitte wähle eine Datei und ein Konto aus');
    return;
  }

  try {
    const result = await importCsv(importFile.value, importAccountId.value, {
      delimiter: importDelimiter.value,
      skip_duplicates: importSkipDuplicates.value,
      auto_reconcile: importAutoReconcile.value,
    });

    importResult.value = result;

    // Reload transactions
    if (result.success) {
      await fetchAllTransactions();
    }
  } catch (e: any) {
    importResult.value = {
      success: false,
      message: e.message,
    };
  }
}

function closeImportModal() {
  showImportModal.value = false;
  importFile.value = null;
  importAccountId.value = '';
  importResult.value = null;
}
</script>

<template>
  <div class="bank-transactions-page">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-white mb-1">Transaktionen</h1>
        <p class="text-white/60 text-sm">
          Übersicht aller Bank-Transaktionen und CSV-Import
        </p>
      </div>
      <button
        @click="showImportModal = true"
        class="kit-btn-primary"
      >
        <span>📁</span>
        <span>CSV importieren</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Anzahl</div>
        <div class="text-2xl font-bold text-white">{{ stats.total }}</div>
      </div>
      <div class="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
        <div class="text-green-300 text-sm mb-1">Einnahmen</div>
        <div class="text-2xl font-bold text-green-300">{{ formatCurrency(stats.income) }}</div>
      </div>
      <div class="bg-red-500/10 rounded-lg p-4 border border-red-500/20">
        <div class="text-red-300 text-sm mb-1">Ausgaben</div>
        <div class="text-2xl font-bold text-red-300">{{ formatCurrency(stats.expense) }}</div>
      </div>
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Zugeordnet</div>
        <div class="text-2xl font-bold text-white">{{ stats.reconciled }}</div>
      </div>
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Offen</div>
        <div class="text-2xl font-bold text-white">{{ stats.unreconciled }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white/5 rounded-lg p-4 border border-white/10 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Account Filter -->
        <div>
          <label class="kit-label">Konto</label>
          <select
            v-model="selectedAccountId"
            class="kit-input"
          >
            <option value="all">Alle Konten</option>
            <option v-for="account in accounts" :key="account.id" :value="account.id">
              {{ account.account_name }}
            </option>
          </select>
        </div>

        <!-- Type Filter -->
        <div>
          <label class="kit-label">Typ</label>
          <select
            v-model="selectedType"
            class="kit-input"
          >
            <option value="all">Alle Typen</option>
            <option value="income">Einnahmen</option>
            <option value="expense">Ausgaben</option>
            <option value="transfer">Überweisungen</option>
          </select>
        </div>

        <!-- Status Filter -->
        <div>
          <label class="kit-label">Status</label>
          <select
            v-model="selectedStatus"
            class="kit-input"
          >
            <option value="all">Alle Status</option>
            <option value="reconciled">Zugeordnet</option>
            <option value="unreconciled">Offen</option>
            <option value="partial">Teilweise</option>
          </select>
        </div>

        <!-- Search -->
        <div>
          <label class="kit-label">Suche</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Empfänger, Zweck, Referenz..."
            class="kit-input"
          />
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-4">
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="loading && transactions.length === 0" class="text-center py-12 text-white/60">
      Lade Transaktionen...
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!loading && filteredTransactions.length === 0"
      class="text-center py-12 bg-white/5 rounded-lg border border-white/10"
    >
      <div class="text-white/60 mb-4">
        <div class="text-4xl mb-2">💳</div>
        <div class="text-lg">Keine Transaktionen gefunden</div>
        <div class="text-sm mt-2">
          Importiere Transaktionen via CSV oder synchronisiere sie über PSD2
        </div>
      </div>
      <button
        @click="showImportModal = true"
        class="kit-btn-primary"
      >
        CSV importieren
      </button>
    </div>

    <!-- Transactions Table -->
    <div v-else class="bg-white/5 rounded-lg border border-white/10 overflow-hidden">
      <table class="w-full">
        <thead class="bg-white/5 border-b border-white/10">
          <tr>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Datum</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Konto</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Empfänger/Auftraggeber</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Verwendungszweck</th>
            <th class="px-4 py-3 text-right text-white/80 font-semibold text-sm">Betrag</th>
            <th class="px-4 py-3 text-center text-white/80 font-semibold text-sm">Status</th>
            <th class="px-4 py-3 text-right text-white/80 font-semibold text-sm">Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="transaction in filteredTransactions"
            :key="transaction.id"
            class="border-b border-white/5 hover:bg-white/5 transition-colors"
          >
            <td class="px-4 py-3 text-white/80 text-sm">
              {{ formatDate(transaction.transaction_date) }}
            </td>
            <td class="px-4 py-3 text-white/60 text-sm">
              {{ getAccountName(transaction.account_id) }}
            </td>
            <td class="px-4 py-3 text-white">
              {{ transaction.counterparty_name || '-' }}
            </td>
            <td class="px-4 py-3 text-white/60 text-sm max-w-xs truncate">
              {{ transaction.purpose || '-' }}
            </td>
            <td class="px-4 py-3 text-right font-semibold">
              <span
                :class="transaction.transaction_type === 'income' ? 'text-green-300' : 'text-red-300'"
              >
                {{ transaction.transaction_type === 'income' ? '+' : '-' }}{{ formatCurrency(Math.abs(transaction.amount)) }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <span
                :class="[
                  'px-2 py-1 rounded text-xs',
                  transaction.reconciliation_status === 'reconciled'
                    ? 'bg-green-500/20 text-green-300'
                    : transaction.reconciliation_status === 'partial'
                    ? 'bg-yellow-500/20 text-yellow-300'
                    : 'bg-white/10 text-white/60',
                ]"
              >
                {{
                  transaction.reconciliation_status === 'reconciled'
                    ? 'Zugeordnet'
                    : transaction.reconciliation_status === 'partial'
                    ? 'Teilweise'
                    : 'Offen'
                }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button
                @click="handleDeleteTransaction(transaction)"
                class="kit-btn-danger"
              >
                Löschen
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- CSV Import Modal -->
    <div
      v-if="showImportModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closeImportModal"
    >
      <div class="bg-[#1a1a1a] rounded-lg p-6 w-full max-w-md border border-white/10">
        <h2 class="text-xl font-bold text-white mb-4">CSV-Import</h2>

        <!-- Import Result -->
        <div v-if="importResult" class="mb-4">
          <div
            v-if="importResult.success"
            class="bg-green-500/20 border border-green-500 text-green-300 px-4 py-3 rounded-lg"
          >
            <div class="font-semibold mb-1">Import erfolgreich!</div>
            <div class="text-sm">
              {{ importResult.imported }} Transaktionen importiert<br />
              {{ importResult.skipped }} übersprungen<br />
              {{ importResult.reconciled }} automatisch zugeordnet
            </div>
          </div>
          <div
            v-else
            class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg"
          >
            <div class="font-semibold mb-1">Import fehlgeschlagen</div>
            <div class="text-sm">{{ importResult.message }}</div>
          </div>
          <button
            @click="closeImportModal"
            class="w-full mt-3 kit-btn-primary"
          >
            Schließen
          </button>
        </div>

        <!-- Import Form -->
        <form v-else @submit.prevent="handleImport" class="space-y-4">
          <div>
            <label class="kit-label">
              Konto <span class="text-red-400">*</span>
            </label>
            <select
              v-model="importAccountId"
              required
              class="kit-input"
            >
              <option value="">-- Konto wählen --</option>
              <option v-for="account in accounts" :key="account.id" :value="account.id">
                {{ account.account_name }} ({{ account.bank_name }})
              </option>
            </select>
          </div>

          <div>
            <label class="kit-label">
              CSV-Datei <span class="text-red-400">*</span>
            </label>
            <input
              type="file"
              accept=".csv"
              required
              @change="handleFileChange"
              class="kit-input"
            />
            <p class="text-white/40 text-xs mt-1">
              Unterstützt: ING Lexware, N26, Sparkasse, Volksbank, etc.
            </p>
          </div>

          <div>
            <label class="kit-label">Trennzeichen</label>
            <select
              v-model="importDelimiter"
              class="kit-input"
            >
              <option value=";">Semikolon (;) - ING Lexware</option>
              <option value=",">Komma (,)</option>
              <option value="\t">Tab</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="flex items-center gap-2 text-white/80 text-sm">
              <input
                v-model="importSkipDuplicates"
                type="checkbox"
                class="rounded"
              />
              <span>Duplikate überspringen</span>
            </label>
            <label class="flex items-center gap-2 text-white/80 text-sm">
              <input
                v-model="importAutoReconcile"
                type="checkbox"
                class="rounded"
              />
              <span>Automatische Zuordnung zu Rechnungen</span>
            </label>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="closeImportModal"
              class="flex-1 kit-btn-ghost"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 kit-btn-primary disabled:opacity-50"
            >
              {{ loading ? 'Importiere...' : 'Importieren' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
