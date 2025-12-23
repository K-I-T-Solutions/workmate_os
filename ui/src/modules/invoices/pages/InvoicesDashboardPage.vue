<script setup lang="ts">
import { onMounted } from 'vue';
import { useInvoiceStats } from '../composables/useInvoiceStats';
import {
  FileText,
  Euro,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  ArrowRight,
  Plus
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openList: [];
  openCreate: [];
}>();

// Composables
const { stats, loading, error, loadStats } = useInvoiceStats();

// Lifecycle
onMounted(() => {
  loadStats();
});

// Helper: Format currency
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white">Rechnungen</h1>
      <div class="flex gap-2">
        <button
          @click="emit('openList')"
          class="kit-btn-ghost"
        >
          <FileText :size="18" />
          Alle Rechnungen
        </button>
        <button
          @click="emit('openCreate')"
          class="kit-btn-primary"
        >
          <Plus :size="18" />
          Neue Rechnung
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Statistiken...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1">
      <div class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <div class="flex items-start gap-3">
          <AlertCircle :size="20" class="text-red-200 mt-0.5" />
          <div>
            <h3 class="font-medium text-red-100">Fehler beim Laden</h3>
            <p class="text-sm text-red-200/80 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="stats" class="flex-1 overflow-auto space-y-4">
      <!-- KPI Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Total Count -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <FileText :size="20" class="text-blue-200" />
            </div>
            <TrendingUp :size="16" class="text-emerald-400" />
          </div>
          <div class="text-2xl font-bold text-white">{{ stats.total_count }}</div>
          <div class="text-sm text-white/60 mt-1">Rechnungen gesamt</div>
        </div>

        <!-- Total Revenue -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <Euro :size="20" class="text-emerald-200" />
            </div>
            <CheckCircle :size="16" class="text-emerald-400" />
          </div>
          <div class="text-2xl font-bold text-white">
            {{ formatCurrency(stats.total_revenue) }}
          </div>
          <div class="text-sm text-white/60 mt-1">Gesamtumsatz</div>
        </div>

        <!-- Outstanding Amount -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-orange-500/20 rounded-lg border border-orange-400/30">
              <Clock :size="20" class="text-orange-200" />
            </div>
            <span class="text-xs font-medium text-orange-200 bg-orange-500/20 px-2 py-1 rounded border border-orange-400/30">
              Offen
            </span>
          </div>
          <div class="text-2xl font-bold text-white">
            {{ formatCurrency(stats.outstanding_amount) }}
          </div>
          <div class="text-sm text-white/60 mt-1">Offene Forderungen</div>
        </div>

        <!-- Overdue Count -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-red-500/20 rounded-lg border border-red-400/30">
              <AlertCircle :size="20" class="text-red-200" />
            </div>
            <span class="text-xs font-medium text-red-200 bg-red-500/20 px-2 py-1 rounded border border-red-400/30">
              Überfällig
            </span>
          </div>
          <div class="text-2xl font-bold text-white">{{ stats.overdue_count }}</div>
          <div class="text-sm text-white/60 mt-1">Überfällige Rechnungen</div>
        </div>
      </div>

      <!-- Status Breakdown -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 class="text-lg font-semibold text-white mb-4">Status-Übersicht</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <!-- Draft -->
          <div class="text-center p-4 rounded-lg border border-white/10 bg-white/5">
            <div class="text-2xl font-bold text-white/80">{{ stats.draft_count }}</div>
            <div class="text-sm text-white/50 mt-1">Entwürfe</div>
          </div>

          <!-- Sent -->
          <div class="text-center p-4 rounded-lg border border-blue-400/30 bg-blue-500/20">
            <div class="text-2xl font-bold text-blue-200">{{ stats.sent_count }}</div>
            <div class="text-sm text-blue-300/80 mt-1">Versendet</div>
          </div>

          <!-- Paid -->
          <div class="text-center p-4 rounded-lg border border-emerald-400/30 bg-emerald-500/20">
            <div class="text-2xl font-bold text-emerald-200">{{ stats.paid_count }}</div>
            <div class="text-sm text-emerald-300/80 mt-1">Bezahlt</div>
          </div>

          <!-- Overdue -->
          <div class="text-center p-4 rounded-lg border border-red-400/30 bg-red-500/20">
            <div class="text-2xl font-bold text-red-200">{{ stats.overdue_count }}</div>
            <div class="text-sm text-red-300/80 mt-1">Überfällig</div>
          </div>

          <!-- Cancelled -->
          <div class="text-center p-4 rounded-lg border border-white/10 bg-white/5">
            <div class="text-2xl font-bold text-white/80">{{ stats.cancelled_count }}</div>
            <div class="text-sm text-white/50 mt-1">Storniert</div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 class="text-lg font-semibold text-white mb-4">Schnellzugriff</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            @click="emit('openList')"
            class="p-4 text-left rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition group"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-white">Alle Rechnungen</div>
                <div class="text-sm text-white/60 mt-1">Liste anzeigen</div>
              </div>
              <ArrowRight :size="20" class="text-white/40 group-hover:text-white/80 transition" />
            </div>
          </button>

          <button
            @click="emit('openCreate')"
            class="p-4 text-left rounded-lg border border-blue-400/30 bg-blue-500/20 hover:bg-blue-500/30 transition group"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-blue-100">Neue Rechnung</div>
                <div class="text-sm text-blue-200/80 mt-1">Rechnung erstellen</div>
              </div>
              <ArrowRight :size="20" class="text-blue-300/60 group-hover:text-blue-200 transition" />
            </div>
          </button>

          <button
            @click="loadStats"
            class="p-4 text-left rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition group"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-white">Aktualisieren</div>
                <div class="text-sm text-white/60 mt-1">Daten neu laden</div>
              </div>
              <ArrowRight :size="20" class="text-white/40 group-hover:text-white/80 transition" />
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
