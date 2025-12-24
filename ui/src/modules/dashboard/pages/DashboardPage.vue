<template>
  <div class="w-full h-full p-6 space-y-8 text-white">

    <!-- Header (Spacer) -->
    <div class="h-8"></div>

    <!-- Widgets Grid -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div v-for="i in 3" :key="i" class="p-5 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
        <div class="animate-pulse space-y-3">
          <div class="h-4 bg-white/10 rounded w-3/4"></div>
          <div class="h-8 bg-white/10 rounded w-1/2"></div>
        </div>
      </div>
    </div>

    <div v-else>
      <!-- Main KPI Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- Customers Card -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <Users :size="16" class="text-blue-200" />
            </div>
            <span class="text-sm font-medium text-white/80">Kunden</span>
          </div>
          <div class="text-3xl font-bold text-white mb-1">{{ stats.customers_total }}</div>
          <div class="flex gap-2 text-xs">
            <span class="text-emerald-300">{{ stats.customers_active }} aktiv</span>
            <span class="text-white/40">•</span>
            <span class="text-blue-300">{{ stats.leads }} leads</span>
          </div>
        </div>

        <!-- Invoices Card -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-2 bg-orange-500/20 rounded-lg border border-orange-400/30">
              <Receipt :size="16" class="text-orange-200" />
            </div>
            <span class="text-sm font-medium text-white/80">Rechnungen</span>
          </div>
          <div class="text-3xl font-bold text-white mb-1">{{ stats.invoices_total }}</div>
          <div class="flex gap-2 text-xs">
            <span class="text-emerald-300">{{ stats.invoices_paid }} bezahlt</span>
            <span class="text-white/40">•</span>
            <span class="text-yellow-300">{{ stats.invoices_sent }} offen</span>
          </div>
        </div>

        <!-- Revenue Card -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <TrendingUp :size="16" class="text-emerald-200" />
            </div>
            <span class="text-sm font-medium text-white/80">Umsatz</span>
          </div>
          <div class="text-2xl font-bold text-emerald-200 mb-1">{{ formatCurrency(stats.total_revenue) }}</div>
          <div class="text-xs text-white/60">Gesamtumsatz</div>
        </div>

        <!-- Profit Card -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
          <div class="flex items-center gap-2 mb-2">
            <div :class="[
              'p-2 rounded-lg border',
              stats.profit >= 0
                ? 'bg-emerald-500/20 border-emerald-400/30'
                : 'bg-red-500/20 border-red-400/30'
            ]">
              <Wallet :size="16" :class="stats.profit >= 0 ? 'text-emerald-200' : 'text-red-200'" />
            </div>
            <span class="text-sm font-medium text-white/80">Gewinn</span>
          </div>
          <div :class="[
            'text-2xl font-bold mb-1',
            stats.profit >= 0 ? 'text-emerald-200' : 'text-red-200'
          ]">
            {{ formatCurrency(stats.profit) }}
          </div>
          <div class="text-xs text-white/60">{{ formatPercent(stats.profit_margin) }} Marge</div>
        </div>
      </div>

      <!-- Secondary Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <!-- Financial Details Widget -->
        <div class="p-5 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
          <h3 class="text-sm font-semibold text-white mb-4">Finanzen</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 rounded-lg bg-white/5">
              <div class="flex items-center gap-2">
                <Euro :size="14" class="text-yellow-300" />
                <span class="text-sm text-white/80">Offen</span>
              </div>
              <span class="text-sm font-semibold text-yellow-200">{{ formatCurrency(stats.outstanding_amount) }}</span>
            </div>
            <div class="flex items-center justify-between p-3 rounded-lg bg-white/5">
              <div class="flex items-center gap-2">
                <Receipt :size="14" class="text-red-300" />
                <span class="text-sm text-white/80">Überfällig</span>
              </div>
              <span class="text-sm font-semibold text-red-200">{{ stats.invoices_overdue }}</span>
            </div>
            <div class="flex items-center justify-between p-3 rounded-lg bg-white/5">
              <div class="flex items-center gap-2">
                <FileText :size="14" class="text-purple-300" />
                <span class="text-sm text-white/80">Ausgaben</span>
              </div>
              <span class="text-sm font-semibold text-white">{{ formatCurrency(stats.total_expenses) }}</span>
            </div>
          </div>
        </div>

      <!-- Recent Activities Widget -->
      <div class="p-5 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
        <div class="mb-3"></div>
        <div v-if="recentActivities.length > 0" class="space-y-3">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="flex items-start gap-3 p-2 rounded-lg bg-white/5"
          >
            <div class="p-1.5 bg-blue-500/20 rounded border border-blue-400/30 flex-shrink-0">
              <component :is="getActivityIcon(activity.type)" :size="14" class="text-blue-200" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs text-white/80 truncate">{{ activity.description }}</p>
              <p class="text-xs text-white/40 mt-0.5">{{ formatRelativeTime(activity.occurred_at) }}</p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-4 text-white/40 text-sm">
          Keine Aktivitäten
        </div>
      </div>

      <!-- Module Shortcuts -->
      <div class="p-5 rounded-xl bg-white/5 border border-white/10 shadow-soft backdrop-blur-sm">
        <div class="mb-3"></div>
        <div class="space-y-2">
          <button
            v-for="shortcut in shortcuts"
            :key="shortcut.id"
            @click="openApp(shortcut.id)"
            class="w-full flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-blue-400/30 transition cursor-pointer text-left"
          >
            <component :is="shortcut.icon" :size="20" :class="shortcut.color" />
            <span class="text-white font-medium">{{ shortcut.label }}</span>
          </button>
        </div>
      </div>
      </div>
      <!-- End Secondary Stats Grid -->

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw } from 'vue';
import { Users, Briefcase, Receipt, Wallet, TrendingUp, Euro, FileText, Phone, Mail } from 'lucide-vue-next';
import { useAppManager } from '@/layouts/app-manager/useAppManager';
import { apiClient } from '@/services/api/client';

const { openWindow } = useAppManager();

const shortcuts = [
  { id: 'crm', label: 'Kunden', icon: markRaw(Users), color: 'text-blue-300' },
  { id: 'invoices', label: 'Rechnungen', icon: markRaw(Receipt), color: 'text-orange-300' },
  { id: 'projects', label: 'Projekte', icon: markRaw(Briefcase), color: 'text-purple-300' },
  { id: 'finance', label: 'Finanzen', icon: markRaw(Wallet), color: 'text-emerald-300' },
];

// State
const loading = ref(true);
const stats = ref({
  // Customer stats
  customers_total: 0,
  customers_active: 0,
  leads: 0,

  // Invoice stats
  invoices_total: 0,
  invoices_paid: 0,
  invoices_sent: 0,
  invoices_overdue: 0,

  // Financial stats
  total_revenue: 0,
  outstanding_amount: 0,
  overdue_amount: 0,
  total_expenses: 0,
  profit: 0,
  profit_margin: 0,
});
const recentActivities = ref<any[]>([]);

// Load data
onMounted(async () => {
  await Promise.all([
    loadCrmStats(),
    loadInvoiceStats(),
    loadFinanceStats(),
    loadRecentActivities(),
  ]);
  loading.value = false;
});

async function loadCrmStats() {
  try {
    const response = await apiClient.get('/api/backoffice/crm/stats');
    // Fixed: Backend returns total_customers, active_customers (not customers_total, customers_active)
    stats.value.customers_total = response.data.total_customers || 0;
    stats.value.customers_active = response.data.active_customers || 0;
    stats.value.leads = response.data.leads || 0;
  } catch (error) {
    console.error('Error loading CRM stats:', error);
  }
}

async function loadInvoiceStats() {
  try {
    const response = await apiClient.get('/api/backoffice/invoices/statistics');
    stats.value.invoices_total = response.data.total_count || 0;
    stats.value.invoices_paid = response.data.paid_count || 0;
    stats.value.invoices_sent = response.data.sent_count || 0;
    stats.value.invoices_overdue = response.data.overdue_count || 0;
    stats.value.total_revenue = response.data.total_revenue || 0;
    stats.value.outstanding_amount = response.data.outstanding_amount || 0;
  } catch (error) {
    console.error('Error loading invoice stats:', error);
  }
}

async function loadFinanceStats() {
  try {
    const response = await apiClient.get('/api/backoffice/finance/kpis/expenses');
    stats.value.total_expenses = Number(response.data.total) || 0;

    // Calculate profit and margin
    stats.value.profit = stats.value.total_revenue - stats.value.total_expenses;
    stats.value.profit_margin = stats.value.total_revenue > 0
      ? (stats.value.profit / stats.value.total_revenue) * 100
      : 0;
  } catch (error) {
    console.error('Error loading finance stats:', error);
  }
}

async function loadRecentActivities() {
  try {
    const response = await apiClient.get('/api/backoffice/crm/activities/latest', {
      params: { limit: 5 }
    });
    recentActivities.value = response.data || [];
  } catch (error) {
    console.error('Error loading activities:', error);
  }
}

function openApp(appId: string) {
  openWindow(appId);
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Gerade eben';
  if (diffMins < 60) return `vor ${diffMins} Min`;
  if (diffHours < 24) return `vor ${diffHours} Std`;
  if (diffDays < 7) return `vor ${diffDays} Tagen`;

  return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function getActivityIcon(type: string) {
  const icons: Record<string, any> = {
    call: Phone,
    email: Mail,
    note: FileText,
  };
  return icons[type] || FileText;
}
</script>
