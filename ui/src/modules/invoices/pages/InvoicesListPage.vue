<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useInvoices } from '../composables/useInvoices';
import type { InvoiceStatus, InvoiceFilterParams } from '../types';
import {
  Search,
  Filter,
  Download,
  Eye,
  ChevronLeft,
  ChevronRight,
  FileText,
  Calendar,
  Plus
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openInvoice: [id: string];
  openCreate: [];
  back: [];
}>();

// Composables
const {
  invoices,
  total,
  page,
  pages,
  limit,
  loading,
  error,
  isEmpty,
  loadInvoices,
  downloadPdf,
} = useInvoices();

// ─── FILTER STATE ─────────────────────────────────────────
const searchQuery = ref('');
const selectedStatus = ref<InvoiceStatus | ''>('');
const dateFrom = ref('');
const dateTo = ref('');
const currentPage = ref(1);

// ─── LIFECYCLE ────────────────────────────────────────────
onMounted(() => {
  applyFilters();
});

// ─── COMPUTED ─────────────────────────────────────────────
const hasFilters = computed(() => {
  return !!(selectedStatus.value || dateFrom.value || dateTo.value);
});

// ─── ACTIONS ──────────────────────────────────────────────
async function applyFilters() {
  const filters: InvoiceFilterParams = {
    skip: (currentPage.value - 1) * limit.value,
    limit: limit.value,
  };

  if (selectedStatus.value) {
    filters.status = selectedStatus.value;
  }

  if (dateFrom.value) {
    filters.date_from = dateFrom.value;
  }

  if (dateTo.value) {
    filters.date_to = dateTo.value;
  }

  await loadInvoices(filters);
}

function clearFilters() {
  selectedStatus.value = '';
  dateFrom.value = '';
  dateTo.value = '';
  currentPage.value = 1;
  applyFilters();
}

function goToPage(pageNum: number) {
  if (pageNum >= 1 && pageNum <= pages.value) {
    currentPage.value = pageNum;
    applyFilters();
  }
}

function handleDownloadPdf(invoiceId: string, invoiceNumber: string) {
  downloadPdf(invoiceId, invoiceNumber);
}

// ─── HELPERS ──────────────────────────────────────────────
function getStatusBadgeClass(status: InvoiceStatus): string {
  const classes = {
    draft: 'bg-white/5 border-white/10 text-white/80',
    sent: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    paid: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    partial: 'bg-yellow-500/20 border-yellow-400/30 text-yellow-200',
    overdue: 'bg-red-500/20 border-red-400/30 text-red-200',
    cancelled: 'bg-white/5 border-white/10 text-white/60',
  };
  return classes[status] || classes.draft;
}

function getStatusLabel(status: InvoiceStatus): string {
  const labels = {
    draft: 'Entwurf',
    sent: 'Versendet',
    paid: 'Bezahlt',
    partial: 'Teilbezahlt',
    overdue: 'Überfällig',
    cancelled: 'Storniert',
  };
  return labels[status] || status;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}

function formatDate(dateString: string | null): string {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('de-DE');
}
</script>

<template>
  <div class="h-full flex flex-col gap-3 sm:gap-4 p-3 sm:p-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
      <div class="flex items-center gap-3">
        <button
          @click="emit('back')"
          class="kit-btn-ghost"
        >
          <ChevronLeft :size="18" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white">Rechnungen</h1>
          <p class="text-sm text-white/60 mt-1">{{ total }} Rechnungen insgesamt</p>
        </div>
      </div>
      <button
        @click="emit('openCreate')"
        class="kit-btn-primary"
      >
        <Plus :size="18" />
        Neue Rechnung
      </button>
    </div>

    <!-- Filters -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Status Filter -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Filter :size="14" />
            Status
          </label>
          <select
            v-model="selectedStatus"
            @change="applyFilters"
            class="kit-input"
          >
            <option value="">Alle Status</option>
            <option value="draft">Entwurf</option>
            <option value="sent">Versendet</option>
            <option value="paid">Bezahlt</option>
            <option value="partial">Teilbezahlt</option>
            <option value="overdue">Überfällig</option>
            <option value="cancelled">Storniert</option>
          </select>
        </div>

        <!-- Date From -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Calendar :size="14" />
            Von Datum
          </label>
          <input
            v-model="dateFrom"
            @change="applyFilters"
            type="date"
            class="kit-input"
          />
        </div>

        <!-- Date To -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Calendar :size="14" />
            Bis Datum
          </label>
          <input
            v-model="dateTo"
            @change="applyFilters"
            type="date"
            class="kit-input"
          />
        </div>
      </div>

      <!-- Clear Filters Button -->
      <button
        v-if="hasFilters"
        @click="clearFilters"
        class="kit-btn-ghost mt-3"
      >
        Filter zurücksetzen
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
          <p class="mt-4 text-white/60">Lade Rechnungen...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <p class="text-red-200">{{ error }}</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="isEmpty" class="text-center py-12">
        <FileText :size="48" class="mx-auto text-white/20 mb-4" />
        <h3 class="text-lg font-medium text-white">Keine Rechnungen gefunden</h3>
        <p class="text-white/60 mt-2">
          {{ hasFilters ? 'Versuchen Sie andere Filter' : 'Erstellen Sie Ihre erste Rechnung' }}
        </p>
        <button
          v-if="!hasFilters"
          @click="emit('openCreate')"
          class="kit-btn-primary mt-4"
        >
          <Plus :size="18" />
          Neue Rechnung
        </button>
      </div>

      <!-- Invoice List -->
      <div v-else class="space-y-3">
        <div
          v-for="invoice in invoices"
          :key="invoice.id"
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="emit('openInvoice', invoice.id)"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Invoice Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-3">
                <span class="font-mono font-semibold text-lg text-white">
                  {{ invoice.invoice_number }}
                </span>
                <span
                  :class="['px-2 py-1 rounded text-xs font-medium border', getStatusBadgeClass(invoice.status)]"
                >
                  {{ getStatusLabel(invoice.status) }}
                </span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                <div>
                  <div class="text-white/50 text-xs">Kunde</div>
                  <div class="font-medium text-white truncate">
                    {{ invoice.customer?.name || 'Unbekannt' }}
                  </div>
                </div>
                <div>
                  <div class="text-white/50 text-xs">Rechnungsdatum</div>
                  <div class="font-medium text-white">
                    {{ formatDate(invoice.issued_date) }}
                  </div>
                </div>
                <div>
                  <div class="text-white/50 text-xs">Fällig am</div>
                  <div class="font-medium text-white">
                    {{ formatDate(invoice.due_date) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Amount & Actions -->
            <div class="flex items-start gap-4">
              <div class="text-right">
                <div class="text-xs text-white/50 mb-1">Gesamtbetrag</div>
                <div class="text-xl font-bold text-white whitespace-nowrap">
                  {{ formatCurrency(invoice.total) }}
                </div>
                <div v-if="invoice.outstanding_amount > 0" class="text-xs text-orange-200 mt-1">
                  Offen: {{ formatCurrency(invoice.outstanding_amount) }}
                </div>
              </div>

              <div class="flex gap-2">
                <button
                  @click.stop="handleDownloadPdf(invoice.id, invoice.invoice_number)"
                  class="p-2 hover:bg-white/10 rounded-lg transition"
                  title="PDF herunterladen"
                >
                  <Download :size="18" class="text-white/60 hover:text-white" />
                </button>
                <button
                  @click.stop="emit('openInvoice', invoice.id)"
                  class="p-2 hover:bg-blue-500/20 rounded-lg transition"
                  title="Details anzeigen"
                >
                  <Eye :size="18" class="text-blue-200" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && !isEmpty" class="flex items-center justify-between text-sm text-white/60">
      <div>
        Seite {{ page }} von {{ pages }} ({{ total }} Rechnungen)
      </div>
      <div class="flex gap-2">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          :class="[
            'px-3 py-2 rounded-lg transition flex items-center gap-1',
            currentPage === 1
              ? 'opacity-30 cursor-not-allowed text-white/40'
              : 'kit-btn-ghost'
          ]"
        >
          <ChevronLeft :size="16" />
          Zurück
        </button>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === pages"
          :class="[
            'px-3 py-2 rounded-lg transition flex items-center gap-1',
            currentPage === pages
              ? 'opacity-30 cursor-not-allowed text-white/40'
              : 'kit-btn-ghost'
          ]"
        >
          Weiter
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
