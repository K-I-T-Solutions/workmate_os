<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useBanking } from '../../composables/useBanking';
import type { BankAccount, BankAccountCreate } from '../../types/banking';

const {
  accounts,
  loading,
  error,
  totalBalance,
  fetchAccounts,
  createAccount,
  deleteAccount,
} = useBanking();

// Modal state
const showCreateModal = ref(false);
const newAccount = ref<BankAccountCreate>({
  account_name: '',
  bank_name: '',
  iban: '',
  currency: 'EUR',
  account_type: 'checking',
  connection_type: 'manual',
});

// Load accounts on mount
onMounted(async () => {
  await fetchAccounts();
});

// Create account
async function handleCreateAccount() {
  try {
    await createAccount(newAccount.value);
    showCreateModal.value = false;
    // Reset form
    newAccount.value = {
      account_name: '',
      bank_name: '',
      iban: '',
      currency: 'EUR',
      account_type: 'checking',
      connection_type: 'manual',
    };
  } catch (e) {
    console.error('Failed to create account:', e);
  }
}

// Delete account
async function handleDeleteAccount(account: BankAccount) {
  if (confirm(`Konto "${account.account_name}" wirklich löschen?`)) {
    try {
      await deleteAccount(account.id);
    } catch (e) {
      console.error('Failed to delete account:', e);
    }
  }
}

// Format currency
function formatCurrency(amount: number | undefined): string {
  if (amount === undefined) return '-';
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
}

// Account type labels
const accountTypeLabels: Record<string, string> = {
  checking: 'Girokonto',
  savings: 'Sparkonto',
  credit_card: 'Kreditkarte',
  other: 'Sonstiges',
};

// Connection type labels
const connectionTypeLabels: Record<string, string> = {
  manual: 'Manuell',
  csv_import: 'CSV-Import',
  fints: 'FinTS',
  psd2_api: 'PSD2 API',
};
</script>

<template>
  <div class="bank-accounts-page">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-white mb-1">Bank-Konten</h1>
        <p class="text-white/60 text-sm">
          Verwalte deine Bankverbindungen und synchronisiere Transaktionen
        </p>
      </div>
      <button
        @click="showCreateModal = true"
        class="kit-btn-primary"
      >
        <span>+</span>
        <span>Konto hinzufügen</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Anzahl Konten</div>
        <div class="text-2xl font-bold text-white">{{ accounts.length }}</div>
      </div>
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Gesamtsaldo</div>
        <div class="text-2xl font-bold text-white">{{ formatCurrency(totalBalance) }}</div>
      </div>
      <div class="bg-white/5 rounded-lg p-4 border border-white/10">
        <div class="text-white/60 text-sm mb-1">Letzte Synchronisation</div>
        <div class="text-sm text-white">Noch nie</div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-4">
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="loading && accounts.length === 0" class="text-center py-12 text-white/60">
      Lade Konten...
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!loading && accounts.length === 0"
      class="text-center py-12 bg-white/5 rounded-lg border border-white/10"
    >
      <div class="text-white/60 mb-4">
        <div class="text-4xl mb-2">🏦</div>
        <div class="text-lg">Noch keine Bank-Konten vorhanden</div>
        <div class="text-sm mt-2">
          Füge dein erstes Konto hinzu, um Transaktionen zu verwalten
        </div>
      </div>
      <button
        @click="showCreateModal = true"
        class="kit-btn-primary"
      >
        Konto hinzufügen
      </button>
    </div>

    <!-- Accounts Table -->
    <div v-else class="bg-white/5 rounded-lg border border-white/10 overflow-hidden">
      <table class="w-full">
        <thead class="bg-white/5 border-b border-white/10">
          <tr>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Konto</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Bank</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">IBAN</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Typ</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Saldo</th>
            <th class="px-4 py-3 text-left text-white/80 font-semibold text-sm">Verbindung</th>
            <th class="px-4 py-3 text-right text-white/80 font-semibold text-sm">Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="account in accounts"
            :key="account.id"
            class="border-b border-white/5 hover:bg-white/5 transition-colors"
          >
            <td class="px-4 py-3 text-white">{{ account.account_name }}</td>
            <td class="px-4 py-3 text-white/80">{{ account.bank_name }}</td>
            <td class="px-4 py-3 text-white/60 font-mono text-sm">
              {{ account.iban || '-' }}
            </td>
            <td class="px-4 py-3 text-white/60 text-sm">
              {{ accountTypeLabels[account.account_type] || account.account_type }}
            </td>
            <td class="px-4 py-3 text-white font-semibold">
              {{ formatCurrency(typeof account.balance === 'string' ? parseFloat(account.balance) : (account.balance || account.current_balance)) }}
            </td>
            <td class="px-4 py-3">
              <span
                :class="[
                  'px-2 py-1 rounded text-xs',
                  account.connection_type === 'psd2_api'
                    ? 'bg-green-500/20 text-green-300'
                    : account.connection_type === 'csv_import'
                    ? 'bg-blue-500/20 text-blue-300'
                    : 'bg-white/10 text-white/60',
                ]"
              >
                {{ connectionTypeLabels[account.connection_type] || account.connection_type }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button
                @click="handleDeleteAccount(account)"
                class="kit-btn-danger"
              >
                Löschen
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Account Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-[#1a1a1a] rounded-lg p-6 w-full max-w-md border border-white/10">
        <h2 class="text-xl font-bold text-white mb-4">Neues Konto hinzufügen</h2>

        <form @submit.prevent="handleCreateAccount" class="space-y-4">
          <div>
            <label class="kit-label">
              Kontoname <span class="text-red-400">*</span>
            </label>
            <input
              v-model="newAccount.account_name"
              type="text"
              required
              class="kit-input"
              placeholder="z.B. ING Geschäftskonto"
            />
          </div>

          <div>
            <label class="kit-label">
              Bank <span class="text-red-400">*</span>
            </label>
            <input
              v-model="newAccount.bank_name"
              type="text"
              required
              class="kit-input"
              placeholder="z.B. ING"
            />
          </div>

          <div>
            <label class="kit-label">IBAN</label>
            <input
              v-model="newAccount.iban"
              type="text"
              class="kit-input font-mono"
              placeholder="DE89 3704 0044 0532 0130 00"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="kit-label">Kontotyp</label>
              <select
                v-model="newAccount.account_type"
                class="kit-input"
              >
                <option value="checking">Girokonto</option>
                <option value="savings">Sparkonto</option>
                <option value="credit_card">Kreditkarte</option>
                <option value="other">Sonstiges</option>
              </select>
            </div>

            <div>
              <label class="kit-label">Währung</label>
              <select
                v-model="newAccount.currency"
                class="kit-input"
              >
                <option value="EUR">EUR</option>
                <option value="USD">USD</option>
                <option value="GBP">GBP</option>
              </select>
            </div>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="showCreateModal = false"
              class="flex-1 kit-btn-ghost"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="flex-1 kit-btn-primary"
            >
              Erstellen
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
