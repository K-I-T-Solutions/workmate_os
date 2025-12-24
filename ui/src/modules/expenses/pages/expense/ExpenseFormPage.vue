<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useExpenses } from '../../composables/useExpenses';
import {
  ExpenseCategoryLabels,
  ExpenseCategory,
  type ExpenseCreate,
  type ExpenseUpdate,
} from '../../types';
import { Save, X, Receipt } from 'lucide-vue-next';

// Props
const props = defineProps<{
  expenseId?: string | null;
}>();

// Emits
const emit = defineEmits<{
  close: [];
  saved: [];
}>();

// Composables
const { currentExpense, isLoading, loadExpense, createExpense, updateExpense, clearCurrentExpense } =
  useExpenses();

// Form State
const form = ref<ExpenseCreate>({
  title: '',
  category: ExpenseCategory.OTHER,
  amount: 0,
  description: '',
  receipt_path: null,
  note: null,
  is_billable: true,
  project_id: null,
  invoice_id: null,
});

// Validation
const errors = ref<Record<string, string>>({});

// Computed
const isEditMode = computed(() => !!props.expenseId);
const isFormValid = computed(() => {
  return (
    form.value.title.trim().length > 0 &&
    form.value.amount > 0 &&
    form.value.description.trim().length > 0
  );
});

// Lifecycle
onMounted(async () => {
  if (isEditMode.value && props.expenseId) {
    await loadExpense(props.expenseId);
    if (currentExpense.value) {
      populateForm(currentExpense.value);
    }
  }
});

// Watch for expense ID changes
watch(
  () => props.expenseId,
  async (newId) => {
    if (newId) {
      await loadExpense(newId);
      if (currentExpense.value) {
        populateForm(currentExpense.value);
      }
    } else {
      resetForm();
    }
  }
);

// Actions
function populateForm(expense: any) {
  form.value = {
    title: expense.title,
    category: expense.category,
    amount: expense.amount,
    description: expense.description,
    receipt_path: expense.receipt_path,
    note: expense.note,
    is_billable: expense.is_billable,
    project_id: expense.project_id,
    invoice_id: expense.invoice_id,
  };
}

function resetForm() {
  form.value = {
    title: '',
    category: ExpenseCategory.OTHER,
    amount: 0,
    description: '',
    receipt_path: null,
    note: null,
    is_billable: true,
    project_id: null,
    invoice_id: null,
  };
  errors.value = {};
  clearCurrentExpense();
}

function validateForm(): boolean {
  errors.value = {};

  if (!form.value.title.trim()) {
    errors.value.title = 'Bezeichnung ist erforderlich';
  }

  if (form.value.amount <= 0) {
    errors.value.amount = 'Betrag muss größer als 0 sein';
  }

  if (!form.value.description.trim()) {
    errors.value.description = 'Beschreibung ist erforderlich';
  }

  return Object.keys(errors.value).length === 0;
}

async function handleSave() {
  if (!validateForm()) return;

  let success = false;

  if (isEditMode.value && props.expenseId) {
    // Update existing
    const updateData: ExpenseUpdate = {
      title: form.value.title,
      category: form.value.category,
      amount: form.value.amount,
      description: form.value.description,
      receipt_path: form.value.receipt_path,
      note: form.value.note,
      is_billable: form.value.is_billable,
      project_id: form.value.project_id,
      invoice_id: form.value.invoice_id,
    };
    success = await updateExpense(props.expenseId, updateData);
  } else {
    // Create new
    success = await createExpense(form.value);
  }

  if (success) {
    emit('saved');
    resetForm();
  }
}

function handleClose() {
  resetForm();
  emit('close');
}
</script>

<template>
  <div class="expense-form h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-white/10">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-emerald-500/20 rounded-lg">
            <Receipt :size="20" class="text-emerald-400" />
          </div>
          <div>
            <h2 class="text-xl font-semibold text-white">
              {{ isEditMode ? 'Ausgabe bearbeiten' : 'Neue Ausgabe' }}
            </h2>
            <p class="text-sm text-white/60 mt-1">
              {{ isEditMode ? 'Aktualisiere die Ausgabendetails' : 'Erstelle eine neue Ausgabe' }}
            </p>
          </div>
        </div>
        <button
          @click="handleClose"
          class="p-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/80 transition-colors"
          title="Schließen"
        >
          <X :size="20" />
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && isEditMode" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
    </div>

    <!-- Form -->
    <div v-else class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl mx-auto space-y-6">
        <!-- Title -->
        <div>
          <label class="kit-label">
            Bezeichnung <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.title"
            type="text"
            placeholder="z.B. Bahnticket nach Berlin"
            class="kit-input"
            :class="{ 'border-red-400/50': errors.title }"
          />
          <p v-if="errors.title" class="mt-1 text-sm text-red-400">{{ errors.title }}</p>
        </div>

        <!-- Category & Amount -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Category -->
          <div>
            <label class="kit-label">
              Kategorie <span class="text-red-400">*</span>
            </label>
            <select
              v-model="form.category"
              class="kit-input"
            >
              <option v-for="(label, cat) in ExpenseCategoryLabels" :key="cat" :value="cat">
                {{ label }}
              </option>
            </select>
          </div>

          <!-- Amount -->
          <div>
            <label class="kit-label">
              Betrag (EUR) <span class="text-red-400">*</span>
            </label>
            <input
              v-model.number="form.amount"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="kit-input"
              :class="{ 'border-red-400/50': errors.amount }"
            />
            <p v-if="errors.amount" class="mt-1 text-sm text-red-400">{{ errors.amount }}</p>
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="kit-label">
            Beschreibung <span class="text-red-400">*</span>
          </label>
          <textarea
            v-model="form.description"
            rows="4"
            placeholder="Detaillierte Beschreibung der Ausgabe..."
            class="kit-input resize-none"
            :class="{ 'border-red-400/50': errors.description }"
          />
          <p v-if="errors.description" class="mt-1 text-sm text-red-400">
            {{ errors.description }}
          </p>
        </div>

        <!-- Receipt Path (optional) -->
        <div>
          <label class="kit-label">
            Beleg-Pfad (optional)
          </label>
          <input
            v-model="form.receipt_path"
            type="text"
            placeholder="/pfad/zum/beleg.pdf"
            class="kit-input"
          />
          <p class="mt-1 text-xs text-white/40">
            Pfad oder URL zu Beleg/Quittung (z.B. Nextcloud-Link)
          </p>
        </div>

        <!-- Note (optional) -->
        <div>
          <label class="kit-label">
            Notizen (optional)
          </label>
          <textarea
            v-model="form.note"
            rows="3"
            placeholder="Zusätzliche Notizen..."
            class="kit-input resize-none"
          />
        </div>

        <!-- Is Billable Checkbox -->
        <div class="flex items-center gap-3">
          <input
            v-model="form.is_billable"
            type="checkbox"
            id="is_billable"
            class="w-5 h-5 bg-white/5 border-white/10 rounded text-emerald-500 focus:ring-2 focus:ring-emerald-500/50"
          />
          <label for="is_billable" class="text-sm text-white/80 cursor-pointer">
            Abrechenbar (kann an Kunden weiterberechnet werden)
          </label>
        </div>
      </div>
    </div>

    <!-- Footer Actions -->
    <div class="p-6 border-t border-white/10 bg-white/5">
      <div class="flex justify-end gap-3">
        <button
          @click="handleClose"
          class="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white transition-colors"
          :disabled="isLoading"
        >
          Abbrechen
        </button>
        <button
          @click="handleSave"
          :disabled="!isFormValid || isLoading"
          class="px-6 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/30 rounded-lg text-emerald-200 font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save :size="18" />
          {{ isLoading ? 'Speichere...' : isEditMode ? 'Aktualisieren' : 'Erstellen' }}
        </button>
      </div>
    </div>
  </div>
</template>
