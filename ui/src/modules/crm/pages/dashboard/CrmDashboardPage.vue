<script setup lang="ts">
import { onMounted } from 'vue';
import { useCrmStats } from '../../composables/useCrmStats';
import { useCrmActivity } from '../../composables/useCrmActivity';
import {
  Users,
  TrendingUp,
  Euro,
  Briefcase,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Plus,
  Phone,
  Mail,
  MapPin,
  MonitorPlay,
  FileText,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openCustomers: [];
  createCustomer: [];
  createContact: [];
}>();

// Composables
const { stats, loading: statsLoading, error: statsError, fetchStats } = useCrmStats();
const { activities, loading: activitiesLoading, fetchLatestActivities } = useCrmActivity();

// Lifecycle
onMounted(() => {
  fetchStats();
  fetchLatestActivities(10);
});

// Helper: Format currency
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}

// Helper: Format relative time
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

// Helper: Get activity icon
function getActivityIcon(type: string) {
  const icons: Record<string, any> = {
    call: Phone,
    email: Mail,
    onsite: MapPin,
    remote: MonitorPlay,
    note: FileText,
  };
  return icons[type] || FileText;
}

// Helper: Get activity label
function getActivityLabel(type: string): string {
  const labels: Record<string, string> = {
    call: 'Anruf',
    email: 'E-Mail',
    onsite: 'Vor-Ort-Besuch',
    remote: 'Remote-Meeting',
    note: 'Notiz',
  };
  return labels[type] || type;
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white">CRM Dashboard</h1>
      <div class="flex gap-2">
        <button @click="emit('openCustomers')" class="kit-btn-ghost">
          <Users :size="18" />
          Alle Kunden
        </button>
        <button @click="emit('createCustomer')" class="kit-btn-primary">
          <Plus :size="18" />
          Neuer Kunde
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="statsLoading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Statistiken...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="statsError" class="flex-1">
      <div class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <div class="flex items-start gap-3">
          <AlertCircle :size="20" class="text-red-200 mt-0.5" />
          <div>
            <h3 class="font-medium text-red-100">Fehler beim Laden</h3>
            <p class="text-sm text-red-200/80 mt-1">{{ statsError }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="stats" class="flex-1 overflow-auto space-y-4">
      <!-- KPI Cards Grid (4 Spalten) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Total Customers -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <Users :size="20" class="text-blue-200" />
            </div>
            <TrendingUp :size="16" class="text-emerald-400" />
          </div>
          <div class="text-2xl font-bold text-white">{{ stats.total_customers }}</div>
          <div class="text-sm text-white/60 mt-1">Kunden gesamt</div>
        </div>

        <!-- Active Customers -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <CheckCircle :size="20" class="text-emerald-200" />
            </div>
            <span class="text-xs font-medium text-emerald-200 bg-emerald-500/20 px-2 py-1 rounded border border-emerald-400/30">
              Aktiv
            </span>
          </div>
          <div class="text-2xl font-bold text-white">{{ stats.active_customers }}</div>
          <div class="text-sm text-white/60 mt-1">Aktive Kunden</div>
        </div>

        <!-- Leads -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-orange-500/20 rounded-lg border border-orange-400/30">
              <Users :size="20" class="text-orange-200" />
            </div>
            <span class="text-xs font-medium text-orange-200 bg-orange-500/20 px-2 py-1 rounded border border-orange-400/30">
              Lead
            </span>
          </div>
          <div class="text-2xl font-bold text-white">{{ stats.leads }}</div>
          <div class="text-sm text-white/60 mt-1">Interessenten</div>
        </div>

        <!-- Total Revenue -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
          <div class="flex items-center justify-between mb-3">
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <Euro :size="20" class="text-blue-200" />
            </div>
          </div>
          <div class="text-2xl font-bold text-white">
            {{ formatCurrency(stats.total_revenue) }}
          </div>
          <div class="text-sm text-white/60 mt-1">Gesamtumsatz</div>
        </div>
      </div>

      <!-- Status-Übersicht (5 Spalten) -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 class="text-lg font-semibold text-white mb-4">Status-Übersicht</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <!-- Aktive -->
          <div class="text-center p-4 rounded-lg border border-emerald-400/30 bg-emerald-500/20">
            <div class="text-2xl font-bold text-emerald-200">{{ stats.active_customers }}</div>
            <div class="text-sm text-emerald-300/80 mt-1">Aktive</div>
          </div>

          <!-- Leads -->
          <div class="text-center p-4 rounded-lg border border-blue-400/30 bg-blue-500/20">
            <div class="text-2xl font-bold text-blue-200">{{ stats.leads }}</div>
            <div class="text-sm text-blue-300/80 mt-1">Leads</div>
          </div>

          <!-- Inaktive -->
          <div class="text-center p-4 rounded-lg border border-white/10 bg-white/5">
            <div class="text-2xl font-bold text-white/80">
              {{ stats.total_customers - stats.active_customers - stats.leads - stats.blocked_customers }}
            </div>
            <div class="text-sm text-white/50 mt-1">Inaktive</div>
          </div>

          <!-- Blockiert -->
          <div class="text-center p-4 rounded-lg border border-red-400/30 bg-red-500/20">
            <div class="text-2xl font-bold text-red-200">{{ stats.blocked_customers }}</div>
            <div class="text-sm text-red-300/80 mt-1">Blockiert</div>
          </div>

          <!-- Projekte -->
          <div class="text-center p-4 rounded-lg border border-orange-400/30 bg-orange-500/20">
            <div class="text-2xl font-bold text-orange-200">{{ stats.active_projects }}</div>
            <div class="text-sm text-orange-300/80 mt-1">Projekte</div>
          </div>
        </div>
      </div>

      <!-- Letzte Aktivitäten -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 class="text-lg font-semibold text-white mb-4">Letzte Aktivitäten</h2>

        <!-- Loading -->
        <div v-if="activitiesLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
          <p class="text-white/60 text-sm mt-2">Lade Aktivitäten...</p>
        </div>

        <!-- Activities List -->
        <div v-else-if="activities && activities.length > 0" class="space-y-3">
          <div
            v-for="activity in activities"
            :key="activity.id"
            class="flex items-start gap-3 p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition"
          >
            <!-- Icon -->
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30 flex-shrink-0">
              <component :is="getActivityIcon(activity.type)" :size="16" class="text-blue-200" />
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <span class="text-xs font-medium text-blue-200 bg-blue-500/20 px-2 py-0.5 rounded border border-blue-400/30">
                    {{ getActivityLabel(activity.type) }}
                  </span>
                  <p class="text-white mt-1">{{ activity.description }}</p>
                </div>
                <span class="text-xs text-white/40 whitespace-nowrap">
                  {{ formatRelativeTime(activity.occurred_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 text-white/40">
          <FileText :size="40" class="mx-auto mb-2 opacity-50" />
          <p>Keine Aktivitäten vorhanden</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Alle Kunden -->
        <button
          @click="emit('openCustomers')"
          class="p-4 text-left rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition group"
        >
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-white">Alle Kunden</div>
              <div class="text-sm text-white/60 mt-1">Liste anzeigen</div>
            </div>
            <ArrowRight :size="20" class="text-white/40 group-hover:text-white/80 transition" />
          </div>
        </button>

        <!-- Neuer Kunde -->
        <button
          @click="emit('createCustomer')"
          class="p-4 text-left rounded-lg border border-blue-400/30 bg-blue-500/20 hover:bg-blue-500/30 transition group"
        >
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-blue-200">Neuer Kunde</div>
              <div class="text-sm text-blue-300/80 mt-1">Kunde anlegen</div>
            </div>
            <Plus :size="20" class="text-blue-200/60 group-hover:text-blue-200 transition" />
          </div>
        </button>

        <!-- Umsatzübersicht -->
        <button
          class="p-4 text-left rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition group"
        >
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-white">Umsatzübersicht</div>
              <div class="text-sm text-white/60 mt-1">Offener Umsatz: {{ formatCurrency(stats.outstanding_revenue) }}</div>
            </div>
            <Euro :size="20" class="text-white/40 group-hover:text-white/80 transition" />
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Zusätzliche Styles falls benötigt */
</style>
