<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useProjects } from '../../composables/useProjects';
import { useAppManager } from '@/layouts/app-manager/useAppManager';
import {
  Briefcase,
  CheckCircle,
  Clock,
  Pause,
  Plus,
  ArrowRight,
  TrendingUp,
  Euro,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openProjects: [];
  createProject: [];
}>();

// Composables
const { projects, loading, loadProjects } = useProjects();
const { openWindow } = useAppManager();

// Lifecycle
onMounted(() => {
  loadProjects();
});

// Computed Stats
const stats = computed(() => {
  const all = projects.value;

  return {
    total: all.length,
    active: all.filter(p => p.status === 'active').length,
    planning: all.filter(p => p.status === 'planning').length,
    onHold: all.filter(p => p.status === 'on_hold').length,
    completed: all.filter(p => p.status === 'completed').length,
    totalBudget: all.reduce((sum, p) => sum + (p.budget || 0), 0),
  };
});

// Recent Projects (last 5)
const recentProjects = computed(() => {
  return [...projects.value]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 5);
});

// Helpers
function getStatusBadge(status: string) {
  const badges = {
    planning: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    active: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    on_hold: 'bg-yellow-500/20 border-yellow-400/30 text-yellow-200',
    completed: 'bg-white/5 border-white/10 text-white/60',
    cancelled: 'bg-red-500/20 border-red-400/30 text-red-200',
  };
  return badges[status as keyof typeof badges] || badges.active;
}

function getStatusLabel(status: string): string {
  const labels = {
    planning: 'Planung',
    active: 'Aktiv',
    on_hold: 'Pausiert',
    completed: 'Abgeschlossen',
    cancelled: 'Abgebrochen',
  };
  return labels[status as keyof typeof labels] || 'Aktiv';
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('de-DE');
}

function openTimeTracking() {
  openWindow('time-tracking');
}
</script>

<template>
  <div class="h-full flex flex-col gap-3 sm:gap-4 p-3 sm:p-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
      <h1 class="text-2xl font-bold text-white">Projekte Dashboard</h1>
      <div class="flex gap-2 w-full sm:w-auto">
        <button @click="emit('openProjects')" class="kit-btn-ghost">
          <Briefcase :size="18" />
          Alle Projekte
        </button>
        <button @click="emit('createProject')" class="kit-btn-primary">
          <Plus :size="18" />
          Neues Projekt
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
      <div v-for="i in 4" :key="i" class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="animate-pulse space-y-3">
          <div class="h-4 bg-white/10 rounded w-3/4"></div>
          <div class="h-8 bg-white/10 rounded w-1/2"></div>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
      <!-- Total Projects -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
        <div class="flex items-center gap-3 mb-2">
          <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
            <Briefcase :size="18" class="text-blue-200" />
          </div>
          <span class="text-sm text-white/60">Projekte gesamt</span>
        </div>
        <div class="text-2xl font-bold text-white">{{ stats.total }}</div>
      </div>

      <!-- Active Projects -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
        <div class="flex items-center gap-3 mb-2">
          <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
            <TrendingUp :size="18" class="text-emerald-200" />
          </div>
          <span class="text-sm text-white/60">Aktive Projekte</span>
        </div>
        <div class="text-2xl font-bold text-white">{{ stats.active }}</div>
      </div>

      <!-- Planning Projects -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
        <div class="flex items-center gap-3 mb-2">
          <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
            <Clock :size="18" class="text-blue-200" />
          </div>
          <span class="text-sm text-white/60">In Planung</span>
        </div>
        <div class="text-2xl font-bold text-white">{{ stats.planning }}</div>
      </div>

      <!-- Total Budget -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition">
        <div class="flex items-center gap-3 mb-2">
          <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
            <Euro :size="18" class="text-emerald-200" />
          </div>
          <span class="text-sm text-white/60">Gesamt-Budget</span>
        </div>
        <div class="text-2xl font-bold text-white">{{ formatCurrency(stats.totalBudget) }}</div>
      </div>
    </div>

    <!-- Status Overview -->
    <div class="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 sm:gap-3">
      <!-- Active -->
      <div class="rounded-lg border border-emerald-400/30 bg-emerald-500/10 p-3 text-center">
        <div class="text-2xl font-bold text-emerald-200">{{ stats.active }}</div>
        <div class="text-xs text-emerald-300 mt-1">Aktiv</div>
      </div>

      <!-- Planning -->
      <div class="rounded-lg border border-blue-400/30 bg-blue-500/10 p-3 text-center">
        <div class="text-2xl font-bold text-blue-200">{{ stats.planning }}</div>
        <div class="text-xs text-blue-300 mt-1">Planung</div>
      </div>

      <!-- On Hold -->
      <div class="rounded-lg border border-yellow-400/30 bg-yellow-500/10 p-3 text-center">
        <div class="text-2xl font-bold text-yellow-200">{{ stats.onHold }}</div>
        <div class="text-xs text-yellow-300 mt-1">Pausiert</div>
      </div>

      <!-- Completed -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
        <div class="text-2xl font-bold text-white/80">{{ stats.completed }}</div>
        <div class="text-xs text-white/60 mt-1">Abgeschlossen</div>
      </div>

      <!-- Total -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
        <div class="text-2xl font-bold text-white/80">{{ stats.total }}</div>
        <div class="text-xs text-white/60 mt-1">Gesamt</div>
      </div>
    </div>

    <!-- Recent Projects -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-white">Letzte Projekte</h3>
        <button @click="emit('openProjects')" class="text-sm text-blue-300 hover:text-blue-200 flex items-center gap-1">
          Alle anzeigen
          <ArrowRight :size="14" />
        </button>
      </div>

      <div v-if="recentProjects.length > 0" class="space-y-2">
        <div
          v-for="project in recentProjects"
          :key="project.id"
          class="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition cursor-pointer"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-medium text-white truncate">{{ project.title }}</span>
              <span
                :class="[
                  'px-2 py-0.5 rounded text-xs font-medium border',
                  getStatusBadge(project.status),
                ]"
              >
                {{ getStatusLabel(project.status) }}
              </span>
            </div>
            <div class="text-xs text-white/50">
              Aktualisiert: {{ formatDate(project.updated_at) }}
            </div>
          </div>
          <div v-if="project.budget" class="text-sm text-white/70">
            {{ formatCurrency(project.budget) }}
          </div>
        </div>
      </div>

      <div v-else class="text-center py-8 text-white/40">
        <Briefcase :size="32" class="mx-auto mb-2 opacity-50" />
        <p class="text-sm">Noch keine Projekte erstellt</p>
        <button @click="emit('createProject')" class="kit-btn-primary mt-4">
          <Plus :size="18" />
          Erstes Projekt erstellen
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <button @click="emit('openProjects')" class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition text-left">
        <Briefcase :size="20" class="text-blue-300 mb-2" />
        <div class="font-semibold text-white">Alle Projekte</div>
        <div class="text-xs text-white/60 mt-1">Projekt-Übersicht anzeigen</div>
      </button>

      <button @click="emit('createProject')" class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition text-left">
        <Plus :size="20" class="text-emerald-300 mb-2" />
        <div class="font-semibold text-white">Neues Projekt</div>
        <div class="text-xs text-white/60 mt-1">Projekt erstellen</div>
      </button>

      <button @click="openTimeTracking" class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition text-left">
        <Clock :size="20" class="text-purple-300 mb-2" />
        <div class="font-semibold text-white">Zeiterfassung</div>
        <div class="text-xs text-white/60 mt-1">Zeiten verwalten</div>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Mobile Optimizations */
@media (max-width: 640px) {
  .p-4 {
    padding: 0.75rem;
  }

  .p-3 {
    padding: 0.625rem;
  }

  .text-2xl {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .flex-col.gap-3 {
    gap: 0.5rem;
  }
}
</style>
