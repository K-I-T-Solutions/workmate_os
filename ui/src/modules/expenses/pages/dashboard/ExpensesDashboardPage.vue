<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useExpenses } from '../../composables/useExpenses';
import { ExpenseCategoryLabels, ExpenseCategory } from '../../types';
import {
  Receipt,
  TrendingUp,
  Euro,
  Plus,
  ArrowRight,
  Wallet,
  PieChart,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openExpenses: [];
  createExpense: [];
}>();

// Composables
const { expenses, kpis, isLoading, loadExpenses, loadKpis } = useExpenses();

// Lifecycle
onMounted(async () => {
  await Promise.all([loadExpenses(), loadKpis()]);
});

// Computed Stats
const stats = computed(() => {
  const all = expenses.value;

  return {
    total: all.length,
    billable: all.filter((e) => e.is_billable).length,
    invoiced: all.filter((e) => e.is_invoiced).length,
    totalAmount: kpis.value?.total || 0,
  };
});

// Recent Expenses (last 5)
const recentExpenses = computed(() => {
  return [...expenses.value]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    .slice(0, 5);
});

// Category breakdown for chart display
const categoryBreakdown = computed(() => {
  if (!kpis.value?.by_category) return [];

  return Object.entries(kpis.value.by_category)
    .map(([category, amount]) => ({
      category: category as ExpenseCategory,
      label: ExpenseCategoryLabels[category as ExpenseCategory],
      amount,
      percentage:
        kpis.value && kpis.value.total > 0
          ? (amount / kpis.value.total) * 100
          : 0,
    }))
    .filter((item) => item.amount > 0)
    .sort((a, b) => b.amount - a.amount);
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
  <div class="expenses-dashboard h-full overflow-y-auto p-3 sm:p-6 space-y-4 sm:space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
      <div>
        <h1 class="text-2xl font-semibold text-white">Ausgaben Dashboard</h1>
        <p class="text-sm text-white/60 mt-1">
          Übersicht über alle Ausgaben und Kosten
        </p>
      </div>
      <button
        @click="emit('createExpense')"
        class="px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/30 rounded-lg text-emerald-200 font-medium transition-colors flex items-center gap-2"
      >
        <Plus :size="18" />
        Neue Ausgabe
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
    </div>

    <template v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <!-- Total Expenses -->
        <div
          class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4"
        >
          <div class="flex items-center justify-between">
            <div class="p-2 bg-emerald-500/20 rounded-lg">
              <Receipt :size="20" class="text-emerald-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-white mt-3">{{ stats.total }}</p>
          <p class="text-sm text-white/60 mt-1">Gesamt Ausgaben</p>
        </div>

        <!-- Total Amount -->
        <div
          class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4"
        >
          <div class="flex items-center justify-between">
            <div class="p-2 bg-blue-500/20 rounded-lg">
              <Euro :size="20" class="text-blue-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-white mt-3">
            {{ formatCurrency(stats.totalAmount) }}
          </p>
          <p class="text-sm text-white/60 mt-1">Gesamtbetrag</p>
        </div>

        <!-- Billable -->
        <div
          class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4"
        >
          <div class="flex items-center justify-between">
            <div class="p-2 bg-purple-500/20 rounded-lg">
              <TrendingUp :size="20" class="text-purple-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-white mt-3">{{ stats.billable }}</p>
          <p class="text-sm text-white/60 mt-1">Abrechenbar</p>
        </div>

        <!-- Invoiced -->
        <div
          class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4"
        >
          <div class="flex items-center justify-between">
            <div class="p-2 bg-yellow-500/20 rounded-lg">
              <Wallet :size="20" class="text-yellow-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-white mt-3">{{ stats.invoiced }}</p>
          <p class="text-sm text-white/60 mt-1">Abgerechnet</p>
        </div>
      </div>

      <!-- Category Breakdown -->
      <div
        v-if="categoryBreakdown.length > 0"
        class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6"
      >
        <div class="flex items-center gap-2 mb-4">
          <PieChart :size="20" class="text-white/60" />
          <h2 class="text-lg font-semibold text-white">Ausgaben nach Kategorie</h2>
        </div>

        <div class="space-y-3">
          <div
            v-for="item in categoryBreakdown"
            :key="item.category"
            class="flex items-center gap-3"
          >
            <span
              :class="getCategoryColor(item.category)"
              class="px-2 py-1 rounded text-xs font-medium border min-w-[100px] text-center"
            >
              {{ item.label }}
            </span>
            <div class="flex-1">
              <div class="flex items-center justify-between text-sm mb-1">
                <span class="text-white/80">{{ formatCurrency(item.amount) }}</span>
                <span class="text-white/60">{{ item.percentage.toFixed(1) }}%</span>
              </div>
              <div class="w-full bg-white/5 rounded-full h-2">
                <div
                  class="bg-emerald-500/50 h-2 rounded-full transition-all"
                  :style="{ width: `${item.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Expenses -->
      <div class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-white">Neueste Ausgaben</h2>
          <button
            @click="emit('openExpenses')"
            class="text-sm text-emerald-400 hover:text-emerald-300 transition-colors flex items-center gap-1"
          >
            Alle anzeigen
            <ArrowRight :size="16" />
          </button>
        </div>

        <div v-if="recentExpenses.length === 0" class="text-center py-8">
          <Receipt :size="48" class="mx-auto text-white/20 mb-3" />
          <p class="text-white/60">Noch keine Ausgaben vorhanden</p>
          <button
            @click="emit('createExpense')"
            class="mt-3 text-sm text-emerald-400 hover:text-emerald-300"
          >
            Erste Ausgabe erstellen
          </button>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="expense in recentExpenses"
            :key="expense.id"
            class="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <p class="font-medium text-white">{{ expense.title }}</p>
                <span
                  :class="getCategoryColor(expense.category)"
                  class="px-2 py-0.5 rounded text-xs font-medium border"
                >
                  {{ ExpenseCategoryLabels[expense.category] }}
                </span>
              </div>
              <p class="text-sm text-white/60 mt-1 line-clamp-1">
                {{ expense.description }}
              </p>
              <p class="text-xs text-white/40 mt-1">
                {{ formatDate(expense.created_at) }}
              </p>
            </div>
            <div class="text-right ml-4">
              <p class="text-lg font-semibold text-white">
                {{ formatCurrency(expense.amount) }}
              </p>
              <p v-if="expense.is_billable" class="text-xs text-emerald-400">
                Abrechenbar
              </p>
              <p v-if="expense.is_invoiced" class="text-xs text-yellow-400">
                Abgerechnet
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
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
  .space-y-4 {
    gap: 0.5rem;
  }
}
</style>
