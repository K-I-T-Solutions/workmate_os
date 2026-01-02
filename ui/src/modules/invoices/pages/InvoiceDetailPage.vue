<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useInvoices } from '../composables/useInvoices';
import type { InvoiceStatus, Payment, PaymentMethod, PaymentCreateRequest, PaymentUpdateRequest } from '../types';
import { apiClient } from '@/services/api/client';
import { useAppManager } from '@/layouts/app-manager/useAppManager';
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
  FileText,
  X
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
const { openWindow } = useAppManager();

// State
const showDeleteConfirm = ref(false);
const statusLoading = ref(false);
const showPaymentModal = ref(false);
const editingPayment = ref<Payment | null>(null);
const paymentLoading = ref(false);
const paymentError = ref<string | null>(null);

// Payment Form State
const paymentForm = ref<PaymentCreateRequest>({
  amount: 0,
  payment_date: new Date().toISOString().split('T')[0],
  method: 'bank_transfer',
  reference: null,
  note: null,
});

// Payment Methods
const paymentMethods: { value: PaymentMethod; label: string }[] = [
  { value: 'bank_transfer', label: 'Überweisung' },
  { value: 'cash', label: 'Bargeld' },
  { value: 'credit_card', label: 'Kreditkarte' },
  { value: 'debit_card', label: 'EC-Karte' },
  { value: 'paypal', label: 'PayPal' },
  { value: 'sepa', label: 'SEPA-Lastschrift' },
  { value: 'other', label: 'Sonstige' },
];

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

// Cross-App Navigation
function handleCustomerClick() {
  if (!invoice.value?.customer_id) return;
  openWindow('crm', {
    initialView: 'customer-detail',
    initialCustomerId: invoice.value.customer_id,
  });
}

function handleProjectClick() {
  if (!invoice.value?.project_id) return;
  openWindow('projects', {
    initialView: 'project-detail',
    initialProjectId: invoice.value.project_id,
  });
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

// Payment Functions
function openPaymentModal() {
  if (!invoice.value) return;

  editingPayment.value = null;
  paymentForm.value = {
    amount: invoice.value.outstanding_amount > 0 ? invoice.value.outstanding_amount : invoice.value.total,
    payment_date: new Date().toISOString().split('T')[0],
    method: 'bank_transfer',
    reference: null,
    note: null,
  };
  paymentError.value = null;
  showPaymentModal.value = true;
}

function openEditPaymentModal(payment: Payment) {
  editingPayment.value = payment;
  paymentForm.value = {
    amount: payment.amount,
    payment_date: payment.payment_date.split('T')[0],
    method: payment.method,
    reference: payment.reference,
    note: payment.note,
  };
  paymentError.value = null;
  showPaymentModal.value = true;
}

function closePaymentModal() {
  showPaymentModal.value = false;
  editingPayment.value = null;
  paymentError.value = null;
}

async function handleSavePayment() {
  if (!invoice.value) return;

  // Validation
  if (paymentForm.value.amount <= 0) {
    paymentError.value = 'Betrag muss größer als 0 sein';
    return;
  }

  if (paymentForm.value.amount > invoice.value.outstanding_amount && !editingPayment.value) {
    paymentError.value = `Betrag kann nicht größer als offener Betrag (${formatCurrency(invoice.value.outstanding_amount)}) sein`;
    return;
  }

  paymentLoading.value = true;
  paymentError.value = null;

  try {
    if (editingPayment.value) {
      // Update existing payment
      await apiClient.patch(
        `/api/backoffice/invoices/payments/${editingPayment.value.id}`,
        paymentForm.value
      );
    } else {
      // Create new payment
      await apiClient.post(
        `/api/backoffice/invoices/${invoice.value.id}/payments`,
        paymentForm.value
      );
    }

    // Reload invoice to get updated data
    await loadInvoice(props.invoiceId);
    closePaymentModal();
  } catch (err: any) {
    paymentError.value = err.response?.data?.detail || 'Fehler beim Speichern der Zahlung';
  } finally {
    paymentLoading.value = false;
  }
}

async function handleDeletePayment(paymentId: string) {
  if (!confirm('Möchten Sie diese Zahlung wirklich löschen?')) return;

  paymentLoading.value = true;

  try {
    await apiClient.delete(`/api/backoffice/invoices/payments/${paymentId}`);
    await loadInvoice(props.invoiceId);
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Fehler beim Löschen der Zahlung');
  } finally {
    paymentLoading.value = false;
  }
}

function getPaymentMethodLabel(method: PaymentMethod): string {
  const found = paymentMethods.find(m => m.value === method);
  return found?.label || method;
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
        <div
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="handleCustomerClick"
        >
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <Building2 :size="16" />
            <h3 class="text-sm font-medium">Kunde</h3>
          </div>
          <div class="text-white font-medium">{{ invoice.customer?.name || 'Unbekannt' }}</div>
          <div class="text-sm text-white/60 mt-1">{{ invoice.customer?.email || '-' }}</div>
          <div class="flex items-center gap-1 text-xs text-blue-300 mt-2">
            <ExternalLink :size="12" />
            Zum Kunden
          </div>
        </div>

        <!-- Project Info (if available) -->
        <div
          v-if="invoice.project_id"
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="handleProjectClick"
        >
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <FileText :size="16" />
            <h3 class="text-sm font-medium">Projekt</h3>
          </div>
          <div class="text-white font-medium">Projekt</div>
          <div class="text-sm text-white/60 mt-1">{{ invoice.project_id }}</div>
          <div class="flex items-center gap-1 text-xs text-blue-300 mt-2">
            <ExternalLink :size="12" />
            Zum Projekt
          </div>
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
        <div class="space-y-3">
          <div
            v-for="item in invoice.line_items"
            :key="item.id"
            class="rounded-lg border border-white/5 bg-white/5 p-4 hover:bg-white/10 transition"
          >
            <!-- Position Header -->
            <div class="flex items-start justify-between gap-4 mb-3">
              <div class="flex items-start gap-3 flex-1 min-w-0">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 border border-blue-400/30 flex items-center justify-center">
                  <span class="text-blue-200 text-sm font-bold">{{ item.position }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-white font-medium text-sm leading-relaxed">{{ item.description }}</p>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <div class="text-white font-bold text-lg">{{ formatCurrency(item.total || 0) }}</div>
                <div class="text-white/40 text-xs">Gesamt</div>
              </div>
            </div>

            <!-- Position Details -->
            <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm pt-3 border-t border-white/5">
              <div>
                <span class="text-white/40">Menge:</span>
                <span class="text-white ml-2 font-medium">{{ item.quantity }} {{ item.unit }}</span>
              </div>
              <div>
                <span class="text-white/40">Einzelpreis:</span>
                <span class="text-white ml-2">{{ formatCurrency(item.unit_price) }}</span>
              </div>
              <div v-if="item.discount_percent > 0">
                <span class="text-white/40">Rabatt:</span>
                <span class="text-orange-300 ml-2 font-medium">{{ item.discount_percent }}%</span>
              </div>
              <div>
                <span class="text-white/40">MwSt.:</span>
                <span class="text-white ml-2">{{ item.tax_rate }}%</span>
              </div>
              <div v-if="item.discount_percent > 0">
                <span class="text-white/40">Zwischensumme:</span>
                <span class="text-white ml-2">{{ formatCurrency(item.subtotal_after_discount || 0) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Payments -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">Zahlungen</h3>
          <button @click="openPaymentModal" class="kit-btn-primary text-sm">
            <Plus :size="16" />
            Zahlung erfassen
          </button>
        </div>

        <div v-if="invoice.payments && invoice.payments.length > 0" class="space-y-2">
          <div
            v-for="payment in invoice.payments"
            :key="payment.id"
            class="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition group"
          >
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <CheckCircle :size="18" class="text-emerald-400 flex-shrink-0" />
                <div>
                  <div class="text-white font-medium">{{ formatCurrency(payment.amount) }}</div>
                  <div class="text-xs text-white/60">
                    {{ formatDate(payment.payment_date) }} · {{ getPaymentMethodLabel(payment.method) }}
                    <span v-if="payment.reference"> · Ref: {{ payment.reference }}</span>
                  </div>
                  <div v-if="payment.note" class="text-xs text-white/40 mt-1">{{ payment.note }}</div>
                </div>
              </div>
            </div>
            <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition">
              <button
                @click="openEditPaymentModal(payment)"
                class="p-1.5 rounded hover:bg-white/10 text-blue-300"
                title="Bearbeiten"
              >
                <Edit :size="14" />
              </button>
              <button
                @click="handleDeletePayment(payment.id)"
                class="p-1.5 rounded hover:bg-white/10 text-red-300"
                title="Löschen"
              >
                <Trash2 :size="14" />
              </button>
            </div>
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

    <!-- Payment Modal -->
    <div
      v-if="showPaymentModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click="closePaymentModal"
    >
      <div
        class="rounded-lg border border-white/10 bg-stone-900 p-6 max-w-lg w-full"
        @click.stop
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-white">
            {{ editingPayment ? 'Zahlung bearbeiten' : 'Zahlung erfassen' }}
          </h3>
          <button @click="closePaymentModal" class="text-white/60 hover:text-white">
            <X :size="20" />
          </button>
        </div>

        <!-- Error Message -->
        <div
          v-if="paymentError"
          class="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-400/30 text-red-200 text-sm"
        >
          {{ paymentError }}
        </div>

        <!-- Form -->
        <div class="space-y-4">
          <!-- Amount -->
          <div>
            <label class="kit-label">Betrag *</label>
            <input
              v-model.number="paymentForm.amount"
              type="number"
              step="0.01"
              class="kit-input"
              placeholder="0.00"
              required
            />
            <p v-if="invoice" class="text-xs text-white/40 mt-1">
              Offener Betrag: {{ formatCurrency(invoice.outstanding_amount) }}
            </p>
          </div>

          <!-- Payment Date -->
          <div>
            <label class="kit-label">Zahlungsdatum *</label>
            <input
              v-model="paymentForm.payment_date"
              type="date"
              class="kit-input"
              required
            />
          </div>

          <!-- Payment Method -->
          <div>
            <label class="kit-label">Zahlungsmethode *</label>
            <select v-model="paymentForm.method" class="kit-input">
              <option v-for="method in paymentMethods" :key="method.value" :value="method.value">
                {{ method.label }}
              </option>
            </select>
          </div>

          <!-- Reference -->
          <div>
            <label class="kit-label">Referenz</label>
            <input
              v-model="paymentForm.reference"
              type="text"
              class="kit-input"
              placeholder="z.B. Transaktions-ID, Belegnummer"
            />
          </div>

          <!-- Note -->
          <div>
            <label class="kit-label">Notiz</label>
            <textarea
              v-model="paymentForm.note"
              class="kit-input"
              rows="3"
              placeholder="Optionale Notiz zur Zahlung"
            ></textarea>
          </div>
        </div>

        <!-- Modal Actions -->
        <div class="flex gap-3 justify-end mt-6">
          <button @click="closePaymentModal" class="kit-btn-ghost" :disabled="paymentLoading">
            Abbrechen
          </button>
          <button @click="handleSavePayment" class="kit-btn-primary" :disabled="paymentLoading">
            <span v-if="paymentLoading">Speichere...</span>
            <span v-else>{{ editingPayment ? 'Aktualisieren' : 'Zahlung erfassen' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
