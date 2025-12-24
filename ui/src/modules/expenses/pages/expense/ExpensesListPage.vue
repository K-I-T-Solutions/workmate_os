<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useExpenses } from '../../composables/useExpenses';
import { ExpenseCategoryLabels, ExpenseCategory, type ExpenseFilters } from '../../types';
import {
  Receipt,
  Edit2,
  Trash2,
  Filter,
  X,
  Search,
  Calendar,
  Tag,
  Euro,
  ChevronLeft,
  Plus,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  editExpense: [id: string];
  openDashboard: [];
  createExpense: [];
}>();

// Composables
const { expenses, isLoading, loadExpenses, deleteExpense } = useExpenses();

// Filter State
const showFilters = ref(false);
const filters = ref<ExpenseFilters>({
  title: '',
  category: undefined,
  from_date: '',
  to_date: '',
});

// Lifecycle
onMounted(() => {
  applyFilters();
});

// Actions
async function applyFilters() {
  const activeFilters: ExpenseFilters = {};

  if (filters.value.title) activeFilters.title = filters.value.title;
  if (filters.value.category) activeFilters.category = filters.value.category;
  if (filters.value.from_date) activeFilters.from_date = filters.value.from_date;
  if (filters.value.to_date) activeFilters.to_date = filters.value.to_date;

  await loadExpenses(activeFilters);
}

function clearFilters() {
  filters.value = {
    title: '',
    category: undefined,
    from_date: '',
    to_date: '',
  };
  applyFilters();
}

async function handleDelete(id: string, title: string) {
  if (confirm(`Ausgabe "${title}" wirklich löschen?`)) {
    const success = await deleteExpense(id);
    if (success) {
      // Refresh list after deletion
      applyFilters();
    }
  }
}

// Computed
const hasActiveFilters = computed(() => {
  return !!(
    filters.value.title ||
    filters.value.category ||
    filters.value.from_date ||
    filters.value.to_date
  );
});

const filteredExpenses = computed(() => {
  return expenses.value;
});

const totalAmount = computed(() => {
  return filteredExpenses.value.reduce((sum, e) => sum + e.amount, 0);
});

// Helpers
function getCategoryColor(category: ExpenseCategory): string {
  const colors = {
    [ExpenseCategory.TRAVEL]: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    [ExpenseCategory.MATERIAL]:
      'bg-purple-500/20 border-purple-400/30 text-purple-200',
    [ExpenseCategory.SOFTWARE]:
      'bg-cyan-500/20 border-cyan-400/30 text-cyan-200',
    [ExpenseCategory.HARDWARE]:
      'bg-green-500/20 border-green-400/30 text-green-200',
    [ExpenseCategory.CONSULTING]:
      'bg-orange-500/20 border-orange-400/30 text-orange-200',
    [ExpenseCategory.MARKETING]:
      'bg-pink-500/20 border-pink-400/30 text-pink-200',
    [ExpenseCategory.OFFICE]:
      'bg-yellow-500/20 border-yellow-400/30 text-yellow-200',
    [ExpenseCategory.TRAINING]:
      'bg-indigo-500/20 border-indigo-400/30 text-indigo-200',
    [ExpenseCategory.OTHER]: 'bg-white/5 border-white/10 text-white/60',
  };
  return colors[category];
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}

function formatDate(dateString: string): string {
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(dateString));
}
</script>

<template>
  <div class="expenses-list h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-white/10">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button @click="emit('openDashboard')" class="kit-btn-ghost">
            <ChevronLeft :size="18" />
          </button>
          <div>
            <h2 class="text-xl font-semibold text-white">Alle Ausgaben</h2>
            <p class="text-sm text-white/60 mt-1">
              {{ filteredExpenses.length }} Ausgaben ·
              {{ formatCurrency(totalAmount) }} gesamt
            </p>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="showFilters = !showFilters"
            :class="[
              'px-4 py-2 rounded-lg border font-medium transition-colors flex items-center gap-2',
              hasActiveFilters
                ? 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200'
                : 'bg-white/5 border-white/10 text-white/80 hover:bg-white/10',
            ]"
          >
            <Filter :size="18" />
            Filter
            <span
              v-if="hasActiveFilters"
              class="ml-1 px-1.5 py-0.5 bg-emerald-400/30 rounded text-xs"
            >
              Aktiv
            </span>
          </button>
          <button @click="emit('createExpense')" class="kit-btn-primary">
            <Plus :size="18" />
            Neue Ausgabe
          </button>
        </div>
      </div>

      <!-- Filters Panel -->
      <div
        v-if="showFilters"
        class="mt-4 p-4 bg-white/5 rounded-lg border border-white/10 space-y-3"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <!-- Title Search -->
          <div>
            <label class="kit-label">Bezeichnung</label>
            <div class="relative">
              <Search
                :size="16"
                class="absolute left-3 top-1/2 -translate-y-1/2 text-white/40"
              />
              <input
                v-model="filters.title"
                type="text"
                placeholder="Suchen..."
                class="kit-input pl-9"
                @keyup.enter="applyFilters"
              />
            </div>
          </div>

          <!-- Category -->
          <div>
            <label class="kit-label">Kategorie</label>
            <div class="relative">
              <Tag
                :size="16"
                class="absolute left-3 top-1/2 -translate-y-1/2 text-white/40"
              />
              <select
                v-model="filters.category"
                class="kit-input pl-9"
              >
                <option :value="undefined">Alle</option>
                <option
                  v-for="(label, cat) in ExpenseCategoryLabels"
                  :key="cat"
                  :value="cat"
                >
                  {{ label }}
                </option>
              </select>
            </div>
          </div>

          <!-- From Date -->
          <div>
            <label class="kit-label">Von Datum</label>
            <div class="relative">
              <Calendar
                :size="16"
                class="absolute left-3 top-1/2 -translate-y-1/2 text-white/40"
              />
              <input
                v-model="filters.from_date"
                type="date"
                class="kit-input pl-9"
              />
            </div>
          </div>

          <!-- To Date -->
          <div>
            <label class="kit-label">Bis Datum</label>
            <div class="relative">
              <Calendar
                :size="16"
                class="absolute left-3 top-1/2 -translate-y-1/2 text-white/40"
              />
              <input
                v-model="filters.to_date"
                type="date"
                class="kit-input pl-9"
              />
            </div>
          </div>
        </div>

        <!-- Filter Actions -->
        <div class="flex gap-2 justify-end">
          <button
            @click="clearFilters"
            class="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/80 text-sm transition-colors"
          >
            Zurücksetzen
          </button>
          <button
            @click="applyFilters"
            class="px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/30 rounded-lg text-emerald-200 text-sm transition-colors"
          >
            Anwenden
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="filteredExpenses.length === 0"
      class="flex-1 flex flex-col items-center justify-center p-6"
    >
      <Receipt :size="64" class="text-white/20 mb-4" />
      <h3 class="text-lg font-semibold text-white mb-2">Keine Ausgaben gefunden</h3>
      <p class="text-white/60 mb-4">
        {{ hasActiveFilters ? 'Versuche andere Filter' : 'Erstelle deine erste Ausgabe' }}
      </p>
      <button
        v-if="hasActiveFilters"
        @click="clearFilters"
        class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white transition-colors"
      >
        Filter zurücksetzen
      </button>
    </div>

    <!-- Expenses Table -->
    <div v-else class="flex-1 overflow-auto p-6">
      <div class="space-y-2">
        <div
          v-for="expense in filteredExpenses"
          :key="expense.id"
          class="p-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl hover:bg-white/10 transition-colors"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-2">
                <h3 class="font-semibold text-white truncate">{{ expense.title }}</h3>
                <span
                  :class="getCategoryColor(expense.category)"
                  class="px-2 py-0.5 rounded text-xs font-medium border whitespace-nowrap"
                >
                  {{ ExpenseCategoryLabels[expense.category] }}
                </span>
                <span
                  v-if="expense.is_billable"
                  class="px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/20 border-emerald-400/30 text-emerald-200 border whitespace-nowrap"
                >
                  Abrechenbar
                </span>
                <span
                  v-if="expense.is_invoiced"
                  class="px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 border-yellow-400/30 text-yellow-200 border whitespace-nowrap"
                >
                  Abgerechnet
                </span>
              </div>
              <p class="text-sm text-white/60 line-clamp-2 mb-2">
                {{ expense.description }}
              </p>
              <div class="flex items-center gap-3 text-xs text-white/40">
                <span class="flex items-center gap-1">
                  <Calendar :size="12" />
                  {{ formatDate(expense.created_at) }}
                </span>
              </div>
            </div>

            <!-- Right: Amount & Actions -->
            <div class="flex items-center gap-4">
              <div class="text-right">
                <div class="flex items-center gap-1 text-xl font-bold text-white">
                  <Euro :size="18" />
                  {{ formatCurrency(expense.amount) }}
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-2">
                <button
                  @click="emit('editExpense', expense.id)"
                  class="p-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 rounded-lg text-blue-200 transition-colors"
                  title="Bearbeiten"
                >
                  <Edit2 :size="16" />
                </button>
                <button
                  @click="handleDelete(expense.id, expense.title)"
                  class="p-2 bg-red-500/20 hover:bg-red-500/30 border border-red-400/30 rounded-lg text-red-200 transition-colors"
                  title="Löschen"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
