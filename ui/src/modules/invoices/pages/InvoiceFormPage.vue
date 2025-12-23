<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useInvoices } from '../composables/useInvoices';
import { CustomerSelect, ProjectSelect } from '../components';
import type { InvoiceCreateRequest, InvoiceLineItem } from '../types';
import {
  ChevronLeft,
  Save,
  Plus,
  Trash2,
  Calculator
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  invoiceId?: string; // Optional: wenn gesetzt = Edit-Mode
}>();

// Emits
const emit = defineEmits<{
  back: [];
  saved: [id: string];
}>();

// Composables
const { currentInvoice, loading, createInvoice, updateInvoice, loadInvoice } = useInvoices();

// State
const formData = ref({
  customer_id: '',
  project_id: '',
  document_type: 'invoice' as const,
  issued_date: new Date().toISOString().split('T')[0],
  due_date: '',
  notes: '',
  terms: 'Zahlbar innerhalb von 14 Tagen ohne Abzug.',
  generate_pdf: true,
});

const lineItems = ref<Omit<InvoiceLineItem, 'id' | 'subtotal' | 'discount_amount' | 'subtotal_after_discount' | 'tax_amount' | 'total'>[]>([
  {
    position: 1,
    description: '',
    quantity: 1,
    unit: 'Stück',
    unit_price: 0,
    tax_rate: 19,
    discount_percent: 0,
  },
]);

const saving = ref(false);
const errors = ref<Record<string, string>>({});

// Computed
const isEditMode = computed(() => !!props.invoiceId);

const calculatedItems = computed(() => {
  return lineItems.value.map((item) => {
    const subtotal = item.quantity * item.unit_price;
    const discount_amount = subtotal * (item.discount_percent / 100);
    const subtotal_after_discount = subtotal - discount_amount;
    const tax_amount = subtotal_after_discount * (item.tax_rate / 100);
    const total = subtotal_after_discount + tax_amount;

    return {
      ...item,
      subtotal,
      discount_amount,
      subtotal_after_discount,
      tax_amount,
      total,
    };
  });
});

const invoiceTotal = computed(() => {
  return calculatedItems.value.reduce((sum, item) => sum + (item.total || 0), 0);
});

const invoiceSubtotal = computed(() => {
  return calculatedItems.value.reduce((sum, item) => sum + (item.subtotal_after_discount || 0), 0);
});

const invoiceTaxAmount = computed(() => {
  return calculatedItems.value.reduce((sum, item) => sum + (item.tax_amount || 0), 0);
});

// Lifecycle
onMounted(async () => {
  if (props.invoiceId) {
    await loadInvoice(props.invoiceId);

    // Populate form with currentInvoice data
    if (currentInvoice.value) {
      formData.value = {
        customer_id: currentInvoice.value.customer_id || '',
        project_id: currentInvoice.value.project_id || '',
        document_type: currentInvoice.value.document_type || 'invoice',
        issued_date: currentInvoice.value.issued_date || '',
        due_date: currentInvoice.value.due_date || '',
        notes: currentInvoice.value.notes || '',
        terms: currentInvoice.value.terms || '',
        generate_pdf: true,
      };

      // Populate line items
      if (currentInvoice.value.line_items && currentInvoice.value.line_items.length > 0) {
        lineItems.value = currentInvoice.value.line_items.map((item) => ({
          position: item.position,
          description: item.description,
          quantity: item.quantity,
          unit: item.unit,
          unit_price: item.unit_price,
          tax_rate: item.tax_rate,
          discount_percent: item.discount_percent,
        }));
      }
    }
  } else {
    // Set default due date (14 days from now) only for new invoices
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 14);
    formData.value.due_date = dueDate.toISOString().split('T')[0];
  }
});

// Actions
function addLineItem() {
  lineItems.value.push({
    position: lineItems.value.length + 1,
    description: '',
    quantity: 1,
    unit: 'Stück',
    unit_price: 0,
    tax_rate: 19,
    discount_percent: 0,
  });
}

function removeLineItem(index: number) {
  if (lineItems.value.length > 1) {
    lineItems.value.splice(index, 1);
    // Re-number positions
    lineItems.value.forEach((item, idx) => {
      item.position = idx + 1;
    });
  }
}

function validate(): boolean {
  errors.value = {};

  if (!formData.value.customer_id) {
    errors.value.customer_id = 'Kunde ist erforderlich';
  }

  if (!formData.value.issued_date) {
    errors.value.issued_date = 'Rechnungsdatum ist erforderlich';
  }

  if (lineItems.value.length === 0) {
    errors.value.line_items = 'Mindestens eine Position ist erforderlich';
  }

  lineItems.value.forEach((item, idx) => {
    if (!item.description) {
      errors.value[`line_item_${idx}_description`] = 'Beschreibung ist erforderlich';
    }
    if (item.quantity <= 0) {
      errors.value[`line_item_${idx}_quantity`] = 'Menge muss größer als 0 sein';
    }
  });

  return Object.keys(errors.value).length === 0;
}

async function handleSubmit() {
  if (!validate()) {
    return;
  }

  saving.value = true;

  try {
    const payload: InvoiceCreateRequest = {
      customer_id: formData.value.customer_id,
      project_id: formData.value.project_id || null,
      document_type: formData.value.document_type,
      issued_date: formData.value.issued_date || null,
      due_date: formData.value.due_date || null,
      notes: formData.value.notes || null,
      terms: formData.value.terms || null,
      line_items: lineItems.value,
      generate_pdf: formData.value.generate_pdf,
    };

    let invoice;

    if (isEditMode.value && props.invoiceId) {
      // Update existing invoice
      invoice = await updateInvoice(props.invoiceId, payload);
    } else {
      // Create new invoice
      invoice = await createInvoice(payload);
    }

    if (invoice) {
      emit('saved', invoice.id);
    }
  } finally {
    saving.value = false;
  }
}

// Helpers
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
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <h1 class="text-2xl font-bold text-white">
          {{ isEditMode ? 'Rechnung bearbeiten' : 'Neue Rechnung' }}
        </h1>
      </div>

      <div class="flex gap-2">
        <button @click="emit('back')" class="kit-btn-ghost">
          Abbrechen
        </button>
        <button
          @click="handleSubmit"
          :disabled="saving"
          class="kit-btn-primary"
        >
          <Save :size="18" />
          {{ saving ? 'Speichere...' : 'Speichern' }}
        </button>
      </div>
    </div>

    <!-- Form -->
    <div class="flex-1 overflow-auto space-y-4">
      <!-- Basic Info -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Allgemeine Informationen</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Customer -->
          <CustomerSelect
            v-model="formData.customer_id"
            :error="errors.customer_id"
          />

          <!-- Project -->
          <ProjectSelect
            v-model="formData.project_id"
          />

          <!-- Document Type -->
          <div>
            <label class="kit-label">Dokumenttyp</label>
            <select v-model="formData.document_type" class="kit-input">
              <option value="invoice">Rechnung</option>
              <option value="quote">Angebot</option>
              <option value="credit_note">Gutschrift</option>
              <option value="order_confirmation">Auftragsbestätigung</option>
            </select>
          </div>

          <!-- Issued Date -->
          <div>
            <label class="kit-label">
              Rechnungsdatum <span class="text-red-400">*</span>
            </label>
            <input
              v-model="formData.issued_date"
              type="date"
              class="kit-input"
              :class="{ 'border-red-400': errors.issued_date }"
            />
          </div>

          <!-- Due Date -->
          <div>
            <label class="kit-label">Fälligkeitsdatum</label>
            <input
              v-model="formData.due_date"
              type="date"
              class="kit-input"
            />
          </div>

          <!-- Generate PDF -->
          <div class="flex items-center gap-2 pt-6">
            <input
              v-model="formData.generate_pdf"
              type="checkbox"
              id="generate_pdf"
              class="rounded"
            />
            <label for="generate_pdf" class="text-sm text-white cursor-pointer">
              PDF automatisch generieren
            </label>
          </div>
        </div>
      </div>

      <!-- Line Items -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">
            Positionen
            <span v-if="errors.line_items" class="text-sm text-red-300 ml-2">
              {{ errors.line_items }}
            </span>
          </h3>
          <button @click="addLineItem" class="kit-btn-primary text-sm">
            <Plus :size="16" />
            Position hinzufügen
          </button>
        </div>

        <div class="space-y-3">
          <div
            v-for="(item, index) in lineItems"
            :key="index"
            class="rounded-lg border border-white/5 bg-white/5 p-4"
          >
            <div class="flex items-start justify-between mb-3">
              <span class="text-white/60 text-sm font-medium">Position {{ item.position }}</span>
              <button
                v-if="lineItems.length > 1"
                @click="removeLineItem(index)"
                class="p-1 hover:bg-red-500/20 rounded transition"
              >
                <Trash2 :size="16" class="text-red-300" />
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-6 gap-3">
              <!-- Description -->
              <div class="md:col-span-3">
                <label class="kit-label">Beschreibung *</label>
                <input
                  v-model="item.description"
                  type="text"
                  placeholder="z.B. Webdesign, IT-Support..."
                  class="kit-input"
                  :class="{ 'border-red-400': errors[`line_item_${index}_description`] }"
                />
              </div>

              <!-- Quantity -->
              <div>
                <label class="kit-label">Menge</label>
                <input
                  v-model.number="item.quantity"
                  type="number"
                  step="0.01"
                  min="0"
                  class="kit-input"
                  :class="{ 'border-red-400': errors[`line_item_${index}_quantity`] }"
                />
              </div>

              <!-- Unit -->
              <div>
                <label class="kit-label">Einheit</label>
                <select v-model="item.unit" class="kit-input">
                  <option>Stück</option>
                  <option>Stunden</option>
                  <option>Tage</option>
                  <option>m²</option>
                  <option>kg</option>
                  <option>Pauschal</option>
                </select>
              </div>

              <!-- Unit Price -->
              <div>
                <label class="kit-label">Einzelpreis (€)</label>
                <input
                  v-model.number="item.unit_price"
                  type="number"
                  step="0.01"
                  min="0"
                  class="kit-input"
                />
              </div>

              <!-- Tax Rate -->
              <div>
                <label class="kit-label">MwSt. (%)</label>
                <select v-model.number="item.tax_rate" class="kit-input">
                  <option :value="0">0%</option>
                  <option :value="7">7%</option>
                  <option :value="19">19%</option>
                </select>
              </div>

              <!-- Discount -->
              <div>
                <label class="kit-label">Rabatt (%)</label>
                <input
                  v-model.number="item.discount_percent"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  class="kit-input"
                />
              </div>

              <!-- Calculated Total -->
              <div class="md:col-span-4"></div>
              <div class="text-right">
                <label class="kit-label">Gesamt</label>
                <div class="text-white font-bold">
                  {{ formatCurrency(calculatedItems[index]?.total || 0) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Totals -->
        <div class="mt-6 pt-4 border-t border-white/10">
          <div class="flex justify-end">
            <div class="w-64 space-y-2">
              <div class="flex justify-between text-white/60">
                <span>Zwischensumme:</span>
                <span>{{ formatCurrency(invoiceSubtotal) }}</span>
              </div>
              <div class="flex justify-between text-white/60">
                <span>MwSt.:</span>
                <span>{{ formatCurrency(invoiceTaxAmount) }}</span>
              </div>
              <div class="flex justify-between text-white font-bold text-lg pt-2 border-t border-white/10">
                <span>Gesamt:</span>
                <span>{{ formatCurrency(invoiceTotal) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Notes & Terms -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Notes -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <label class="kit-label">Notizen (Optional)</label>
          <textarea
            v-model="formData.notes"
            rows="4"
            placeholder="Interne Notizen..."
            class="kit-input resize-none"
          ></textarea>
        </div>

        <!-- Terms -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <label class="kit-label">Zahlungsbedingungen</label>
          <textarea
            v-model="formData.terms"
            rows="4"
            placeholder="z.B. Zahlbar innerhalb von 14 Tagen..."
            class="kit-input resize-none"
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
