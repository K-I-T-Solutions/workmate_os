<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useInvoices } from '../composables/useInvoices';
import type { InvoiceStatus } from '../types';
import {
  ChevronLeft,
  Download,
  ExternalLink,
  Edit,
  Trash2,
  Plus,
  Calendar,
  User,
  Building2,
  CreditCard,
  CheckCircle,
  AlertCircle,
  Clock,
  FileText
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  invoiceId: string;
}>();

// Emits
const emit = defineEmits<{
  back: [];
  edit: [id: string];
}>();

// Composables
const {
  currentInvoice,
  loading,
  error,
  loadInvoice,
  updateInvoiceStatus,
  deleteInvoice,
  downloadPdf,
  openPdf,
} = useInvoices();

// State
const showDeleteConfirm = ref(false);
const statusLoading = ref(false);

// Lifecycle
onMounted(() => {
  loadInvoice(props.invoiceId);
});

// Computed
const invoice = computed(() => currentInvoice.value);

// Actions
async function handleStatusChange(newStatus: InvoiceStatus) {
  if (!invoice.value) return;

  statusLoading.value = true;
  await updateInvoiceStatus(invoice.value.id, newStatus);
  statusLoading.value = false;
}

async function handleDelete() {
  if (!invoice.value) return;

  const success = await deleteInvoice(invoice.value.id);
  if (success) {
    emit('back');
  }
}

function handleDownloadPdf() {
  if (!invoice.value) return;
  downloadPdf(invoice.value.id, invoice.value.invoice_number);
}

function handleOpenPdf() {
  if (!invoice.value) return;
  openPdf(invoice.value.id, invoice.value.invoice_number);
}

// Helpers
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
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div v-if="invoice">
          <h1 class="text-2xl font-bold text-white flex items-center gap-3">
            {{ invoice.invoice_number }}
            <span :class="['px-2 py-1 rounded text-sm font-medium border', getStatusBadgeClass(invoice.status)]">
              {{ getStatusLabel(invoice.status) }}
            </span>
          </h1>
          <p class="text-sm text-white/60 mt-1">
            Erstellt am {{ formatDate(invoice.created_at) }}
          </p>
        </div>
      </div>

      <div v-if="invoice" class="flex gap-2">
        <button @click="handleDownloadPdf" class="kit-btn-ghost" title="PDF herunterladen">
          <Download :size="18" />
        </button>
        <button @click="handleOpenPdf" class="kit-btn-ghost" title="PDF öffnen">
          <ExternalLink :size="18" />
        </button>
        <button @click="emit('edit', invoice.id)" class="kit-btn-secondary">
          <Edit :size="18" />
          Bearbeiten
        </button>
        <button @click="showDeleteConfirm = true" class="kit-btn-danger">
          <Trash2 :size="18" />
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Rechnung...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1">
      <div class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <p class="text-red-200">{{ error }}</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="invoice" class="flex-1 overflow-auto space-y-4">
      <!-- Main Info Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Customer Info -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <Building2 :size="16" />
            <h3 class="text-sm font-medium">Kunde</h3>
          </div>
          <div class="text-white font-medium">{{ invoice.customer?.name || 'Unbekannt' }}</div>
          <div class="text-sm text-white/60 mt-1">{{ invoice.customer?.email || '-' }}</div>
        </div>

        <!-- Dates -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <Calendar :size="16" />
            <h3 class="text-sm font-medium">Datum</h3>
          </div>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-white/60">Rechnungsdatum:</span>
              <span class="text-white">{{ formatDate(invoice.issued_date) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-white/60">Fällig am:</span>
              <span class="text-white">{{ formatDate(invoice.due_date) }}</span>
            </div>
            <div v-if="invoice.days_until_due !== null" class="flex justify-between">
              <span class="text-white/60">Verbleibend:</span>
              <span :class="invoice.days_until_due < 0 ? 'text-red-200' : 'text-white'">
                {{ invoice.days_until_due }} Tage
              </span>
            </div>
          </div>
        </div>

        <!-- Amounts -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <CreditCard :size="16" />
            <h3 class="text-sm font-medium">Beträge</h3>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-white/60 text-sm">Zwischensumme:</span>
              <span class="text-white">{{ formatCurrency(invoice.subtotal) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-white/60 text-sm">MwSt.:</span>
              <span class="text-white">{{ formatCurrency(invoice.tax_amount) }}</span>
            </div>
            <div class="flex justify-between pt-2 border-t border-white/10">
              <span class="text-white font-medium">Gesamt:</span>
              <span class="text-white font-bold text-lg">{{ formatCurrency(invoice.total) }}</span>
            </div>
            <div v-if="invoice.outstanding_amount > 0" class="flex justify-between text-orange-200">
              <span class="text-sm">Offen:</span>
              <span class="font-medium">{{ formatCurrency(invoice.outstanding_amount) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Line Items -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Positionen</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b border-white/10">
              <tr class="text-left text-white/60">
                <th class="pb-2">#</th>
                <th class="pb-2">Beschreibung</th>
                <th class="pb-2 text-right">Menge</th>
                <th class="pb-2">Einheit</th>
                <th class="pb-2 text-right">Einzelpreis</th>
                <th class="pb-2 text-right">Rabatt</th>
                <th class="pb-2 text-right">MwSt.</th>
                <th class="pb-2 text-right">Gesamt</th>
              </tr>
            </thead>
            <tbody class="text-white">
              <tr
                v-for="item in invoice.line_items"
                :key="item.id"
                class="border-b border-white/5"
              >
                <td class="py-3">{{ item.position }}</td>
                <td class="py-3">{{ item.description }}</td>
                <td class="py-3 text-right">{{ item.quantity }}</td>
                <td class="py-3">{{ item.unit }}</td>
                <td class="py-3 text-right">{{ formatCurrency(item.unit_price) }}</td>
                <td class="py-3 text-right">{{ item.discount_percent }}%</td>
                <td class="py-3 text-right">{{ item.tax_rate }}%</td>
                <td class="py-3 text-right font-medium">{{ formatCurrency(item.total || 0) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Payments -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">Zahlungen</h3>
          <button class="kit-btn-primary text-sm">
            <Plus :size="16" />
            Zahlung erfassen
          </button>
        </div>

        <div v-if="invoice.payments && invoice.payments.length > 0" class="space-y-2">
          <div
            v-for="payment in invoice.payments"
            :key="payment.id"
            class="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5"
          >
            <div>
              <div class="text-white font-medium">{{ formatCurrency(payment.amount) }}</div>
              <div class="text-xs text-white/60">
                {{ formatDate(payment.payment_date) }} · {{ payment.method }}
                <span v-if="payment.reference"> · {{ payment.reference }}</span>
              </div>
            </div>
            <CheckCircle :size="18" class="text-emerald-400" />
          </div>
        </div>
        <div v-else class="text-center py-8 text-white/40">
          Keine Zahlungen erfasst
        </div>
      </div>

      <!-- Notes & Terms -->
      <div v-if="invoice.notes || invoice.terms" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div v-if="invoice.notes" class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-sm font-medium text-white/60 mb-2">Notizen</h3>
          <p class="text-white text-sm whitespace-pre-wrap">{{ invoice.notes }}</p>
        </div>
        <div v-if="invoice.terms" class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-sm font-medium text-white/60 mb-2">Zahlungsbedingungen</h3>
          <p class="text-white text-sm whitespace-pre-wrap">{{ invoice.terms }}</p>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="showDeleteConfirm = false"
    >
      <div
        class="rounded-lg border border-white/10 bg-stone-900 p-6 max-w-md"
        @click.stop
      >
        <h3 class="text-xl font-bold text-white mb-2">Rechnung löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie die Rechnung {{ invoice?.invoice_number }} wirklich löschen?
          Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="showDeleteConfirm = false" class="kit-btn-ghost">
            Abbrechen
          </button>
          <button @click="handleDelete" class="kit-btn-danger">
            <Trash2 :size="18" />
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
