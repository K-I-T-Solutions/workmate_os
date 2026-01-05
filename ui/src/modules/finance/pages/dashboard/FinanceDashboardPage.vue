<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useFinance } from '../../composables/useFinance';
import { useSevDesk } from '../../composables';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Receipt,
  Wallet,
  PieChart,
  ArrowUpCircle,
  ArrowDownCircle,
  RefreshCw,
} from 'lucide-vue-next';

// Composable
const { overview, isLoading, loadOverview } = useFinance();
const {
  isConfigured: isSevDeskConfigured,
  syncing: sevdeskSyncing,
  syncPayments,
  lastSyncTime,
  fetchConfig,
} = useSevDesk();

// SevDesk Sync State
const syncSuccess = ref<string | null>(null);
const syncError = ref<string | null>(null);

// Lifecycle
onMounted(async () => {
  loadOverview();
  // Load SevDesk config to check if it's configured
  try {
    await fetchConfig();
  } catch (e) {
    // Ignore errors, just means not configured
    console.log('SevDesk not configured');
  }
});

// Computed
const profitColor = computed(() => {
  if (!overview.value) return 'text-white';
  return overview.value.profit >= 0 ? 'text-emerald-400' : 'text-red-400';
});

const profitIcon = computed(() => {
  if (!overview.value) return TrendingUp;
  return overview.value.profit >= 0 ? TrendingUp : TrendingDown;
});

// Helpers
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

// Invoice Status Labels
const invoiceStatusLabels: Record<string, string> = {
  draft: 'Entwurf',
  sent: 'Versendet',
  paid: 'Bezahlt',
  overdue: 'Überfällig',
  cancelled: 'Storniert',
};

// Expense Category Labels
const expenseCategoryLabels: Record<string, string> = {
  travel: 'Reisekosten',
  material: 'Material',
  software: 'Software',
  hardware: 'Hardware',
  consulting: 'Beratung',
  marketing: 'Marketing',
  office: 'Büro',
  training: 'Schulung',
  other: 'Sonstiges',
};

// Get status badge color
function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'bg-white/5 border-white/10 text-white/60',
    sent: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    paid: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    overdue: 'bg-red-500/20 border-red-400/30 text-red-200',
    cancelled: 'bg-white/5 border-white/10 text-white/60',
  };
  return colors[status] || colors.draft;
}

// Get category bar color
function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    travel: 'bg-blue-500',
    material: 'bg-purple-500',
    software: 'bg-cyan-500',
    hardware: 'bg-green-500',
    consulting: 'bg-orange-500',
    marketing: 'bg-pink-500',
    office: 'bg-yellow-500',
    training: 'bg-indigo-500',
    other: 'bg-gray-500',
  };
  return colors[category] || colors.other;
}

// SevDesk Payment Sync
async function handleSyncPayments() {
  syncSuccess.value = null;
  syncError.value = null;

  try {
    const result = await syncPayments();
    if (result.success) {
      syncSuccess.value = `Erfolgreich: ${result.payments_created} Zahlung(en) erstellt, ${result.invoices_status_updated} Rechnung(en) aktualisiert`;
      // Auto-hide after 5 seconds
      setTimeout(() => {
        syncSuccess.value = null;
      }, 5000);
      // Reload overview to show updated data
      loadOverview();
    } else {
      syncError.value = 'Synchronisation fehlgeschlagen';
    }
  } catch (e: any) {
    syncError.value = e.message || 'Fehler beim Synchronisieren der Zahlungen';
  }
}

function formatDateTime(dateString?: string) {
  if (!dateString) return 'Nie';
  return new Date(dateString).toLocaleString('de-DE');
}
</script>

<template>
  <div class="h-full flex flex-col gap-3 sm:gap-4 p-3 sm:p-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
      <h1 class="text-2xl font-bold text-white">Finanzen Dashboard</h1>
    </div>

    <!-- SevDesk Sync Messages -->
    <div v-if="syncSuccess" class="p-4 rounded-lg bg-green-500/20 text-green-300 border border-green-500/30">
      {{ syncSuccess }}
    </div>
    <div v-if="syncError" class="p-4 rounded-lg bg-red-500/20 text-red-300 border border-red-500/30">
      {{ syncError }}
    </div>

    <!-- SevDesk Sync Card -->
    <div v-if="isSevDeskConfigured" class="rounded-lg border border-blue-500/30 bg-blue-500/10 p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
            <RefreshCw :size="20" class="text-blue-200" />
          </div>
          <div>
            <h3 class="text-sm font-semibold text-white">SevDesk Zahlungssync</h3>
            <p class="text-xs text-white/60 mt-0.5">
              Letzte Synchronisation: {{ formatDateTime(lastSyncTime) }}
            </p>
          </div>
        </div>
        <button
          @click="handleSyncPayments"
          :disabled="sevdeskSyncing"
          class="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <RefreshCw :size="16" :class="{ 'animate-spin': sevdeskSyncing }" />
          {{ sevdeskSyncing ? 'Synchronisiere...' : 'Zahlungen synchronisieren' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="overview" class="flex-1 overflow-y-auto space-y-4">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <!-- Total Revenue -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-white/60">Gesamtumsatz</span>
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <DollarSign :size="18" class="text-emerald-200" />
            </div>
          </div>
          <div class="text-2xl font-bold text-white">
            {{ formatCurrency(overview.total_revenue) }}
          </div>
          <div class="text-xs text-white/40 mt-1">
            Aus {{ overview.invoice_count }} Rechnungen
          </div>
        </div>

        <!-- Total Expenses -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-white/60">Gesamtausgaben</span>
            <div class="p-2 bg-red-500/20 rounded-lg border border-red-400/30">
              <Receipt :size="18" class="text-red-200" />
            </div>
          </div>
          <div class="text-2xl font-bold text-white">
            {{ formatCurrency(overview.total_expenses) }}
          </div>
          <div class="text-xs text-white/40 mt-1">
            Betriebsausgaben
          </div>
        </div>

        <!-- Profit -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-white/60">Gewinn</span>
            <div :class="[
              'p-2 rounded-lg border',
              overview.profit >= 0
                ? 'bg-emerald-500/20 border-emerald-400/30'
                : 'bg-red-500/20 border-red-400/30'
            ]">
              <component :is="profitIcon" :size="18" :class="profitColor" />
            </div>
          </div>
          <div class="text-2xl font-bold" :class="profitColor">
            {{ formatCurrency(overview.profit) }}
          </div>
          <div class="text-xs text-white/40 mt-1">
            Umsatz - Ausgaben
          </div>
        </div>

        <!-- Profit Margin -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-white/60">Gewinnmarge</span>
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <PieChart :size="18" class="text-blue-200" />
            </div>
          </div>
          <div class="text-2xl font-bold text-white">
            {{ formatPercent(overview.profit_margin) }}
          </div>
          <div class="text-xs text-white/40 mt-1">
            Rentabilität
          </div>
        </div>
      </div>

      <!-- Outstanding & Overdue -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        <!-- Outstanding Revenue -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-yellow-500/20 rounded-lg border border-yellow-400/30">
              <ArrowUpCircle :size="18" class="text-yellow-200" />
            </div>
            <div>
              <div class="text-sm font-semibold text-white">Offene Forderungen</div>
              <div class="text-xs text-white/40">Noch nicht bezahlt</div>
            </div>
          </div>
          <div class="text-xl font-bold text-yellow-200">
            {{ formatCurrency(overview.outstanding_revenue) }}
          </div>
        </div>

        <!-- Overdue Revenue -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-red-500/20 rounded-lg border border-red-400/30">
              <ArrowDownCircle :size="18" class="text-red-200" />
            </div>
            <div>
              <div class="text-sm font-semibold text-white">Überfällige Forderungen</div>
              <div class="text-xs text-white/40">Zahlungsverzug</div>
            </div>
          </div>
          <div class="text-xl font-bold text-red-200">
            {{ formatCurrency(overview.overdue_revenue) }}
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
        <!-- Invoices by Status -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-sm font-semibold text-white mb-4">Rechnungen nach Status</h3>
          <div class="space-y-3">
            <div
              v-for="(count, status) in overview.invoices_by_status"
              :key="status"
              class="flex items-center justify-between"
            >
              <div class="flex items-center gap-2 flex-1">
                <span
                  :class="['px-2 py-0.5 rounded text-xs font-medium border', getStatusColor(status)]"
                >
                  {{ invoiceStatusLabels[status] || status }}
                </span>
              </div>
              <div class="text-sm font-semibold text-white">
                {{ count }}
              </div>
            </div>
          </div>
        </div>

        <!-- Expenses by Category -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-sm font-semibold text-white mb-4">Ausgaben nach Kategorie</h3>
          <div class="space-y-3">
            <div
              v-for="(amount, category) in overview.expenses_by_category"
              :key="category"
              class="space-y-1"
            >
              <div class="flex items-center justify-between text-xs">
                <span class="text-white/80">
                  {{ expenseCategoryLabels[category] || category }}
                </span>
                <span class="text-white font-medium">
                  {{ formatCurrency(Number(amount)) }}
                </span>
              </div>
              <div class="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                <div
                  :class="getCategoryColor(category)"
                  class="h-full rounded-full transition-all"
                  :style="{
                    width: `${(Number(amount) / overview.total_expenses) * 100}%`
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <Wallet :size="64" class="text-white/20 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-white mb-2">Keine Finanzdaten</h3>
        <p class="text-white/60">
          Erstelle Rechnungen und erfasse Ausgaben, um deine Finanzen zu verwalten
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Mobile Optimizations */
@media (max-width: 640px) {
  .p-4 {
    padding: 0.75rem;
  }

  .text-2xl {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .flex-col.gap-3 {
    gap: 0.5rem;
  }
}
</style>
