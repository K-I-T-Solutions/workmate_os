<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useProjects } from '../../composables/useProjects';
import type { ProjectFilters } from '../../composables/useProjects';
import {
  ChevronLeft,
  Plus,
  Filter,
  Briefcase,
  Calendar,
  Euro,
  Trash2,
  Eye,
  X,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openProject: [id: string];
  openDashboard: [];
}>();

// Composables
const {
  projects,
  loading,
  error,
  isEmpty,
  loadProjects,
  deleteProject,
} = useProjects();

// ─── FILTER STATE ─────────────────────────────────────────
const searchQuery = ref('');
const selectedStatus = ref<string>('');

// ─── LIFECYCLE ────────────────────────────────────────────
onMounted(() => {
  applyFilters();
});

// ─── COMPUTED ─────────────────────────────────────────────
const hasFilters = computed(() => {
  return !!(selectedStatus.value || searchQuery.value);
});

// ─── ACTIONS ──────────────────────────────────────────────
async function applyFilters() {
  const filters: ProjectFilters = {};

  if (selectedStatus.value) {
    filters.status = selectedStatus.value;
  }

  if (searchQuery.value) {
    filters.search = searchQuery.value;
  }

  await loadProjects(filters);
}

function clearFilters() {
  selectedStatus.value = '';
  searchQuery.value = '';
  applyFilters();
}

// Delete confirmation
const deleteConfirmId = ref<string | null>(null);

function showDeleteConfirm(projectId: string) {
  deleteConfirmId.value = projectId;
}

async function confirmDelete() {
  if (deleteConfirmId.value) {
    const success = await deleteProject(deleteConfirmId.value);
    if (success) {
      deleteConfirmId.value = null;
      applyFilters();
    }
  }
}

// ─── HELPERS ──────────────────────────────────────────────
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
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('openDashboard')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white">Projekte</h1>
          <p class="text-sm text-white/60 mt-1">{{ projects.length }} Projekte</p>
        </div>
      </div>
      <button @click="$emit('openProject', 'create')" class="kit-btn-primary">
        <Plus :size="18" />
        Neues Projekt
      </button>
    </div>

    <!-- Filters -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Status Filter -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Filter :size="14" />
            Status
          </label>
          <select
            v-model="selectedStatus"
            @change="applyFilters"
            class="kit-input"
          >
            <option value="">Alle Status</option>
            <option value="planning">Planung</option>
            <option value="active">Aktiv</option>
            <option value="on_hold">Pausiert</option>
            <option value="completed">Abgeschlossen</option>
            <option value="cancelled">Abgebrochen</option>
          </select>
        </div>

        <!-- Search -->
        <div class="sm:col-span-2">
          <label class="kit-label">Suche</label>
          <input
            v-model="searchQuery"
            @input="applyFilters"
            type="text"
            placeholder="Titel, Beschreibung oder Projektnummer..."
            class="kit-input"
          />
        </div>
      </div>

      <!-- Clear Filters -->
      <button
        v-if="hasFilters"
        @click="clearFilters"
        class="kit-btn-ghost mt-3 text-sm"
      >
        <X :size="16" />
        Filter zurücksetzen
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Projekte...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1">
      <div class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <p class="text-red-200">{{ error }}</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <Briefcase :size="64" class="mx-auto text-white/20 mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Keine Projekte gefunden</h3>
        <p class="text-white/60 mb-6">
          {{ hasFilters ? 'Keine Projekte entsprechen den Filterkriterien' : 'Erstellen Sie Ihr erstes Projekt' }}
        </p>
        <button v-if="!hasFilters" @click="$emit('openProject', 'create')" class="kit-btn-primary">
          <Plus :size="18" />
          Erstes Projekt erstellen
        </button>
      </div>
    </div>

    <!-- Project List -->
    <div v-else class="flex-1 overflow-auto">
      <div class="space-y-3">
        <div
          v-for="project in projects"
          :key="project.id"
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="emit('openProject', project.id)"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Project Info -->
            <div class="flex-1 min-w-0">
              <!-- Title + Badges --><div class="flex items-center gap-3 mb-3">
                <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
                  <Briefcase :size="18" class="text-emerald-200" />
                </div>
                <span class="font-semibold text-lg text-white truncate">
                  {{ project.title }}
                </span>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium border',
                    getStatusBadge(project.status),
                  ]"
                >
                  {{ getStatusLabel(project.status) }}
                </span>
                <span
                  v-if="project.priority"
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium border',
                    getPriorityBadge(project.priority),
                  ]"
                >
                  {{ getPriorityLabel(project.priority) }}
                </span>
              </div>

              <!-- Description -->
              <p v-if="project.description" class="text-sm text-white/70 mb-3 line-clamp-2">
                {{ project.description }}
              </p>

              <!-- Info Grid -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                <div v-if="project.project_number">
                  <div class="text-white/50 text-xs">Projektnummer</div>
                  <div class="font-medium text-white font-mono text-xs">
                    {{ project.project_number }}
                  </div>
                </div>

                <div v-if="project.start_date || project.end_date">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Calendar :size="12" />
                    Zeitraum
                  </div>
                  <div class="font-medium text-white">
                    {{ formatDate(project.start_date) }} - {{ formatDate(project.end_date) }}
                  </div>
                </div>

                <div v-if="project.budget">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Euro :size="12" />
                    Budget
                  </div>
                  <div class="font-medium text-white">
                    {{ formatCurrency(project.budget) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Actions -->
            <div class="flex items-start gap-2">
              <button
                @click.stop="emit('openProject', project.id)"
                class="p-2 hover:bg-blue-500/20 rounded-lg transition"
                title="Details anzeigen"
              >
                <Eye :size="18" class="text-blue-200" />
              </button>
              <button
                @click.stop="showDeleteConfirm(project.id)"
                class="p-2 hover:bg-red-500/20 rounded-lg transition"
                title="Projekt löschen"
              >
                <Trash2 :size="18" class="text-red-200" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteConfirmId"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="deleteConfirmId = null"
    >
      <div
        class="rounded-lg border border-white/10 bg-stone-900 p-6 max-w-md"
        @click.stop
      >
        <h3 class="text-xl font-bold text-white mb-2">Projekt löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie dieses Projekt wirklich löschen? Diese Aktion kann nicht
          rückgängig gemacht werden.
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="deleteConfirmId = null" class="kit-btn-ghost">
            Abbrechen
          </button>
          <button @click="confirmDelete" class="kit-btn-danger">
            <Trash2 :size="18" />
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
