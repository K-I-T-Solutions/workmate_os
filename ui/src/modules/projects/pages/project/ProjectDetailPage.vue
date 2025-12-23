<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useProjects } from '../../composables/useProjects';
import { useAppManager } from '@/layouts/app-manager/useAppManager';
import {
  ChevronLeft,
  Edit,
  Trash2,
  Briefcase,
  Calendar,
  Euro,
  Clock,
  TrendingUp,
  AlertCircle,
  Users,
  Receipt,
  Plus,
  ExternalLink,
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  projectId: string;
}>();

// Emits
const emit = defineEmits<{
  back: [];
  edit: [projectId: string];
}>();

// Composables
const { currentProject, loading, loadProject, deleteProject } = useProjects();
const { openWindow } = useAppManager();

// State
const showDeleteConfirm = ref(false);

// Lifecycle
onMounted(() => {
  loadProject(props.projectId);
});

// Computed
const project = computed(() => currentProject.value);

// Actions
async function handleDelete() {
  if (!project.value) return;

  const success = await deleteProject(project.value.id);
  if (success) {
    emit('back');
  }
}

// Cross-App Navigation
function openCustomer() {
  if (!project.value) return;
  openWindow('crm', {
    initialView: 'customer-detail',
    initialCustomerId: project.value.customer_id,
  });
}

function openTimeTracking() {
  if (!project.value) return;
  openWindow('time-tracking', {
    initialView: 'entries',
    filterByProject: project.value.id,
  });
}

function openInvoices() {
  if (!project.value) return;
  openWindow('invoices', {
    initialView: 'list',
    filterByProject: project.value.id,
  });
}

function createInvoice() {
  if (!project.value) return;
  openWindow('invoices', {
    initialView: 'create',
    prefilledProjectId: project.value.id,
    prefilledCustomerId: project.value.customer_id,
  });
}

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

function getPriorityBadge(priority: string | null) {
  if (!priority) return 'bg-white/5 border-white/10 text-white/60';

  const badges = {
    low: 'bg-white/5 border-white/10 text-white/60',
    medium: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    high: 'bg-orange-500/20 border-orange-400/30 text-orange-200',
    urgent: 'bg-red-500/20 border-red-400/30 text-red-200',
  };
  return badges[priority as keyof typeof badges] || badges.medium;
}

function getPriorityLabel(priority: string | null): string {
  if (!priority) return 'Normal';

  const labels = {
    low: 'Niedrig',
    medium: 'Mittel',
    high: 'Hoch',
    urgent: 'Dringend',
  };
  return labels[priority as keyof typeof labels] || 'Mittel';
}

function formatDate(dateString: string | null): string {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('de-DE');
}

function formatCurrency(value: number | null): string {
  if (value === null) return '-';
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4 overflow-y-auto">
    <!-- Loading State -->
    <div v-if="loading && !project" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Projekt...</p>
      </div>
    </div>

    <!-- Project Content -->
    <template v-else-if="project">
      <!-- Header -->
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-3 flex-1">
          <button @click="emit('back')" class="kit-btn-ghost mt-1">
            <ChevronLeft :size="18" />
          </button>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-white flex items-center gap-3">
              {{ project.title }}
              <span
                :class="[
                  'px-2 py-1 rounded text-sm font-medium border',
                  getStatusBadge(project.status),
                ]"
              >
                {{ getStatusLabel(project.status) }}
              </span>
              <span
                v-if="project.priority"
                :class="[
                  'px-2 py-1 rounded text-sm font-medium border',
                  getPriorityBadge(project.priority),
                ]"
              >
                {{ getPriorityLabel(project.priority) }}
              </span>
            </h1>
            <p v-if="project.project_number" class="text-sm text-white/60 mt-1 font-mono">
              {{ project.project_number }}
            </p>
          </div>
        </div>

        <div class="flex gap-2">
          <button @click="emit('edit', project.id)" class="kit-btn-secondary">
            <Edit :size="18" />
            Bearbeiten
          </button>
          <button @click="showDeleteConfirm = true" class="kit-btn-danger">
            <Trash2 :size="18" />
          </button>
        </div>
      </div>

      <!-- Description -->
      <div v-if="project.description" class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-sm font-semibold text-white/60 mb-2">Beschreibung</h3>
        <p class="text-white/80">{{ project.description }}</p>
      </div>

      <!-- Info Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Zeitraum Card -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <Calendar :size="18" class="text-blue-200" />
            </div>
            <h3 class="font-semibold text-white">Zeitraum</h3>
          </div>
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-white/50">Start:</span>
              <span class="text-white ml-2">{{ formatDate(project.start_date) }}</span>
            </div>
            <div>
              <span class="text-white/50">Ende:</span>
              <span class="text-white ml-2">{{ formatDate(project.end_date) }}</span>
            </div>
            <div v-if="project.deadline">
              <span class="text-white/50">Deadline:</span>
              <span class="text-white ml-2">{{ formatDate(project.deadline) }}</span>
            </div>
          </div>
        </div>

        <!-- Budget Card -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <Euro :size="18" class="text-emerald-200" />
            </div>
            <h3 class="font-semibold text-white">Finanzen</h3>
          </div>
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-white/50">Budget:</span>
              <span class="text-white ml-2">{{ formatCurrency(project.budget) }}</span>
            </div>
            <div>
              <span class="text-white/50">Stundensatz:</span>
              <span class="text-white ml-2">{{ formatCurrency(project.hourly_rate) }}</span>
            </div>
          </div>
        </div>

        <!-- Stats Card -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-orange-500/20 rounded-lg border border-orange-400/30">
              <TrendingUp :size="18" class="text-orange-200" />
            </div>
            <h3 class="font-semibold text-white">Statistik</h3>
          </div>
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-white/50">Erstellt:</span>
              <span class="text-white ml-2">{{ formatDate(project.created_at) }}</span>
            </div>
            <div>
              <span class="text-white/50">Aktualisiert:</span>
              <span class="text-white ml-2">{{ formatDate(project.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Related Data Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="font-semibold text-white mb-4">Verknüpfte Daten</h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <!-- Customer Link -->
          <button
            @click="openCustomer"
            class="flex items-center gap-3 p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition text-left"
          >
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <Users :size="16" class="text-blue-200" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs text-white/50">Kunde</div>
              <div class="text-sm font-medium text-white truncate">Zu Kunde</div>
            </div>
            <ExternalLink :size="14" class="text-white/40" />
          </button>

          <!-- Time Tracking Link -->
          <button
            @click="openTimeTracking"
            class="flex items-center gap-3 p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition text-left"
          >
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <Clock :size="16" class="text-emerald-200" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs text-white/50">Zeiterfassung</div>
              <div class="text-sm font-medium text-white truncate">Zeiteinträge</div>
            </div>
            <ExternalLink :size="14" class="text-white/40" />
          </button>

          <!-- Invoices Link -->
          <button
            @click="openInvoices"
            class="flex items-center gap-3 p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition text-left"
          >
            <div class="p-2 bg-purple-500/20 rounded-lg border border-purple-400/30">
              <Receipt :size="16" class="text-purple-200" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs text-white/50">Rechnungen</div>
              <div class="text-sm font-medium text-white truncate">Rechnungen</div>
            </div>
            <ExternalLink :size="14" class="text-white/40" />
          </button>
        </div>
      </div>
    </template>

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
        <h3 class="text-xl font-bold text-white mb-2">Projekt löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie dieses Projekt wirklich löschen? Alle zugehörigen Daten
          (Zeiterfassungen, etc.) werden ebenfalls gelöscht.
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
