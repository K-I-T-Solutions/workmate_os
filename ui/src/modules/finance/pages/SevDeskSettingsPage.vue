<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useSevDesk } from '../composables';
import type { SevDeskConfigRequest } from '../types/sevdesk';

const {
  config,
  loading,
  error,
  isConfigured,
  autoSyncEnabled,
  lastSyncTime,
  syncHistory,
  fetchConfig,
  saveConfig,
  deleteConfig,
  testConnection,
  fetchSyncHistory,
} = useSevDesk();

// Form state
const showConfigForm = ref(false);
const apiToken = ref('');
const formAutoSync = ref(true);
const formSyncInvoices = ref(true);
const formSyncBankAccounts = ref(false);
const formSyncTransactions = ref(false);

// Connection test state
const testResult = ref<any>(null);
const testLoading = ref(false);

// Toast messages
const successMessage = ref<string | null>(null);
const errorMessage = ref<string | null>(null);

onMounted(async () => {
  await fetchConfig();
  if (config.value) {
    formAutoSync.value = config.value.auto_sync_enabled;
    formSyncInvoices.value = config.value.sync_invoices;
    formSyncBankAccounts.value = config.value.sync_bank_accounts;
    formSyncTransactions.value = config.value.sync_transactions;
  }
  // Load sync history
  if (isConfigured.value) {
    await fetchSyncHistory({ limit: 20 });
  }
});

function clearMessages() {
  successMessage.value = null;
  errorMessage.value = null;
}

async function handleSaveConfig() {
  clearMessages();
  try {
    const configData: SevDeskConfigRequest = {
      api_token: apiToken.value,
      auto_sync_enabled: formAutoSync.value,
      sync_invoices: formSyncInvoices.value,
      sync_bank_accounts: formSyncBankAccounts.value,
      sync_transactions: formSyncTransactions.value,
    };

    const response = await saveConfig(configData);
    successMessage.value = response.message || 'SevDesk Konfiguration gespeichert';
    showConfigForm.value = false;
    apiToken.value = ''; // Clear token input
  } catch (e: any) {
    errorMessage.value = e.message || 'Fehler beim Speichern der Konfiguration';
  }
}

async function handleDeleteConfig() {
  if (!confirm('Möchten Sie die SevDesk-Konfiguration wirklich löschen?')) {
    return;
  }

  clearMessages();
  try {
    await deleteConfig();
    successMessage.value = 'SevDesk Konfiguration gelöscht';
    showConfigForm.value = false;
  } catch (e: any) {
    errorMessage.value = e.message || 'Fehler beim Löschen der Konfiguration';
  }
}

async function handleTestConnection() {
  clearMessages();
  testResult.value = null;
  testLoading.value = true;

  try {
    const result = await testConnection();
    testResult.value = result;
    if (result.success) {
      successMessage.value = result.message || 'Verbindung erfolgreich';
    } else {
      errorMessage.value = result.message || 'Verbindung fehlgeschlagen';
    }
  } catch (e: any) {
    errorMessage.value = e.message || 'Verbindungstest fehlgeschlagen';
  } finally {
    testLoading.value = false;
  }
}

function formatDateTime(dateString?: string) {
  if (!dateString) return 'Nie';
  return new Date(dateString).toLocaleString('de-DE');
}

function getSyncTypeLabel(syncType: string): string {
  const labels: Record<string, string> = {
    invoice: 'Rechnung',
    payment: 'Zahlung',
    bank_account: 'Bankkonto',
    transaction: 'Transaktion',
  };
  return labels[syncType] || syncType;
}

function getSyncDirectionLabel(direction: string): string {
  const labels: Record<string, string> = {
    push_to_sevdesk: 'Push → SevDesk',
    pull_from_sevdesk: 'Pull ← SevDesk',
  };
  return labels[direction] || direction;
}

function getStatusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    success: 'bg-green-500/20 border-green-500/30 text-green-300',
    failed: 'bg-red-500/20 border-red-500/30 text-red-300',
    partial: 'bg-yellow-500/20 border-yellow-500/30 text-yellow-300',
  };
  return classes[status] || classes.success;
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    success: 'Erfolgreich',
    failed: 'Fehlgeschlagen',
    partial: 'Teilweise',
  };
  return labels[status] || status;
}
</script>

<template>
  <div class="sevdesk-settings-page">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-white mb-2">SevDesk Integration</h1>
      <p class="text-white/60">
        Konfigurieren Sie die Verbindung zu SevDesk für automatische Rechnungs- und
        Zahlungssynchronisation
      </p>
    </div>

    <!-- Toast Messages -->
    <div v-if="successMessage" class="mb-4 p-4 rounded-lg bg-green-500/20 text-green-300 border border-green-500/30">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="mb-4 p-4 rounded-lg bg-red-500/20 text-red-300 border border-red-500/30">
      {{ errorMessage }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-white/60">Lade Konfiguration...</div>
    </div>

    <!-- Configuration Status -->
    <div v-else-if="!showConfigForm" class="space-y-6">
      <!-- Status Card -->
      <div class="p-6 rounded-lg border" :class="isConfigured ? 'bg-green-500/10 border-green-500/30' : 'bg-white/5 border-white/10'">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div v-if="isConfigured" class="text-3xl">✅</div>
            <div v-else class="text-3xl">⚙️</div>
            <div>
              <h2 class="text-xl font-semibold text-white">
                {{ isConfigured ? 'Konfiguriert' : 'Nicht konfiguriert' }}
              </h2>
              <p class="text-white/60 text-sm">
                {{ isConfigured ? 'SevDesk ist verbunden und aktiv' : 'Bitte API-Token eingeben' }}
              </p>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              v-if="isConfigured"
              @click="handleTestConnection"
              :disabled="testLoading"
              class="px-4 py-2 rounded-lg bg-blue-500/20 text-blue-300 hover:bg-blue-500/30 disabled:opacity-50 transition-colors"
            >
              {{ testLoading ? 'Teste...' : 'Verbindung testen' }}
            </button>
            <button
              @click="showConfigForm = true"
              class="px-4 py-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
            >
              {{ isConfigured ? 'Bearbeiten' : 'Konfigurieren' }}
            </button>
          </div>
        </div>

        <!-- Config Details -->
        <div v-if="config" class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
          <div>
            <div class="text-white/60 text-sm mb-1">Auto-Sync</div>
            <div class="text-white font-semibold">{{ autoSyncEnabled ? 'Aktiviert' : 'Deaktiviert' }}</div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Rechnungen</div>
            <div class="text-white font-semibold">{{ config.sync_invoices ? '✓' : '—' }}</div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Bankkonten</div>
            <div class="text-white font-semibold">{{ config.sync_bank_accounts ? '✓' : '—' }}</div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Transaktionen</div>
            <div class="text-white font-semibold">{{ config.sync_transactions ? '✓' : '—' }}</div>
          </div>
        </div>

        <!-- Last Sync -->
        <div v-if="lastSyncTime" class="mt-4 text-white/60 text-sm">
          Letzte Synchronisation: {{ formatDateTime(lastSyncTime) }}
        </div>
      </div>

      <!-- Connection Test Result -->
      <div v-if="testResult" class="p-6 rounded-lg bg-white/5 border border-white/10">
        <h3 class="text-lg font-semibold text-white mb-4">Verbindungstest Ergebnis</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div class="text-white/60 text-sm mb-1">Check Accounts</div>
            <div class="text-white font-semibold text-2xl">{{ testResult.check_accounts }}</div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Rechnungen</div>
            <div class="text-white font-semibold text-2xl">{{ testResult.invoices }}</div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Kontakte</div>
            <div class="text-white font-semibold text-2xl">{{ testResult.contacts }}</div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Transaktionen</div>
            <div class="text-white font-semibold text-2xl">{{ testResult.transactions }}</div>
          </div>
        </div>
      </div>

      <!-- Sync History -->
      <div v-if="isConfigured && syncHistory.length > 0" class="p-6 rounded-lg bg-white/5 border border-white/10">
        <h3 class="text-lg font-semibold text-white mb-4">Synchronisations-Historie</h3>
        <div class="space-y-3">
          <div
            v-for="sync in syncHistory"
            :key="sync.id"
            class="p-4 rounded-lg bg-white/5 border border-white/10"
          >
            <div class="flex items-start justify-between mb-2">
              <div class="flex items-center gap-3">
                <span :class="['px-2 py-1 rounded text-xs font-medium border', getStatusBadgeClass(sync.status)]">
                  {{ getStatusLabel(sync.status) }}
                </span>
                <span class="text-white/80 font-medium">
                  {{ getSyncTypeLabel(sync.sync_type) }}
                </span>
                <span class="text-white/60 text-sm">
                  {{ getSyncDirectionLabel(sync.direction) }}
                </span>
              </div>
              <div class="text-white/60 text-sm">
                {{ formatDateTime(sync.started_at) }}
              </div>
            </div>

            <div class="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div class="text-white/60 mb-1">Verarbeitet</div>
                <div class="text-white font-semibold">{{ sync.records_processed }}</div>
              </div>
              <div>
                <div class="text-white/60 mb-1">Erfolgreich</div>
                <div class="text-green-300 font-semibold">{{ sync.records_success }}</div>
              </div>
              <div>
                <div class="text-white/60 mb-1">Fehlgeschlagen</div>
                <div class="text-red-300 font-semibold">{{ sync.records_failed }}</div>
              </div>
            </div>

            <div v-if="sync.error_message" class="mt-3 p-2 rounded bg-red-500/10 border border-red-500/30">
              <div class="text-red-300 text-xs">{{ sync.error_message }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuration Form -->
    <div v-else class="space-y-6">
      <div class="p-6 rounded-lg bg-white/5 border border-white/10">
        <h2 class="text-xl font-semibold text-white mb-6">
          {{ isConfigured ? 'Konfiguration bearbeiten' : 'Neue Konfiguration' }}
        </h2>

        <form @submit.prevent="handleSaveConfig" class="space-y-6">
          <!-- API Token -->
          <div>
            <label class="block text-white/80 mb-2 font-medium">
              API Token
              <span class="text-red-400">*</span>
            </label>
            <input
              v-model="apiToken"
              type="password"
              :placeholder="isConfigured ? '••••••••••••' : 'SevDesk API Token eingeben'"
              required
              class="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-400/50"
            />
            <p class="text-white/50 text-sm mt-1">
              Ihren API-Token finden Sie in SevDesk unter Einstellungen → Benutzer → API-Token
            </p>
          </div>

          <!-- Auto-Sync Toggle -->
          <div class="flex items-center gap-3">
            <input
              v-model="formAutoSync"
              type="checkbox"
              id="autoSync"
              class="w-4 h-4 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-2 focus:ring-blue-400/50"
            />
            <label for="autoSync" class="text-white/80 cursor-pointer">
              Automatische Synchronisation aktivieren
            </label>
          </div>

          <!-- Sync Options -->
          <div class="space-y-3">
            <h3 class="text-white/80 font-medium">Synchronisations-Optionen</h3>

            <div class="flex items-center gap-3">
              <input
                v-model="formSyncInvoices"
                type="checkbox"
                id="syncInvoices"
                class="w-4 h-4 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-2 focus:ring-blue-400/50"
              />
              <label for="syncInvoices" class="text-white/60 cursor-pointer">
                Rechnungen zu SevDesk pushen
              </label>
            </div>

            <div class="flex items-center gap-3">
              <input
                v-model="formSyncBankAccounts"
                type="checkbox"
                id="syncBankAccounts"
                class="w-4 h-4 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-2 focus:ring-blue-400/50"
              />
              <label for="syncBankAccounts" class="text-white/60 cursor-pointer">
                Bankkonten mappen
              </label>
            </div>

            <div class="flex items-center gap-3">
              <input
                v-model="formSyncTransactions"
                type="checkbox"
                id="syncTransactions"
                class="w-4 h-4 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-2 focus:ring-blue-400/50"
              />
              <label for="syncTransactions" class="text-white/60 cursor-pointer">
                Transaktionen von SevDesk pullen
              </label>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex gap-3 pt-4 border-t border-white/10">
            <button
              type="submit"
              :disabled="loading || !apiToken"
              class="flex-1 px-6 py-3 rounded-lg bg-blue-500 text-white font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ loading ? 'Speichert...' : 'Speichern' }}
            </button>
            <button
              type="button"
              @click="showConfigForm = false; apiToken = ''"
              class="px-6 py-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
            >
              Abbrechen
            </button>
            <button
              v-if="isConfigured"
              type="button"
              @click="handleDeleteConfig"
              class="px-6 py-3 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition-colors"
            >
              Löschen
            </button>
          </div>
        </form>
      </div>

      <!-- Info Box -->
      <div class="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
        <div class="flex items-start gap-3">
          <div class="text-2xl">ℹ️</div>
          <div>
            <h4 class="text-blue-300 font-semibold mb-1">Hinweis zur Sicherheit</h4>
            <p class="text-blue-200/80 text-sm">
              Ihr API-Token wird verschlüsselt in der Datenbank gespeichert und niemals im Klartext angezeigt.
              Die Verbindung zu SevDesk erfolgt über HTTPS.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sevdesk-settings-page {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
