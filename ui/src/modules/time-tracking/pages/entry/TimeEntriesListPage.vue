<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useTimeTracking } from '../../composables/useTimeTracking';
import type { TimeEntryFilters } from '../../composables/useTimeTracking';
import {
  ChevronLeft,
  Plus,
  Clock,
  Trash2,
  Eye,
  Calendar,
  X,
  Filter,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openEntry: [id: string];
  openDashboard: [];
}>();

// Composables
const {
  entries,
  loading,
  error,
  isEmpty,
  loadEntries,
  deleteEntry,
} = useTimeTracking();

// ─── FILTER STATE ─────────────────────────────────────────
const startDate = ref('');
const endDate = ref('');

// ─── LIFECYCLE ────────────────────────────────────────────
onMounted(() => {
  applyFilters();
});

// ─── COMPUTED ─────────────────────────────────────────────
const hasFilters = computed(() => {
  return !!(startDate.value || endDate.value);
});

const totalMinutes = computed(() => {
  return entries.value.reduce((sum, e) => sum + (e.duration_minutes || 0), 0);
});

const totalHours = computed(() => {
  return (totalMinutes.value / 60).toFixed(2);
});

// ─── ACTIONS ──────────────────────────────────────────────
async function applyFilters() {
  const filters: TimeEntryFilters = {};

  if (startDate.value) {
    filters.startDate = startDate.value;
  }

  if (endDate.value) {
    filters.endDate = endDate.value;
  }

  await loadEntries(filters);
}

function clearFilters() {
  startDate.value = '';
  endDate.value = '';
  applyFilters();
}

// Delete confirmation
const deleteConfirmId = ref<string | null>(null);

function showDeleteConfirm(entryId: string) {
  deleteConfirmId.value = entryId;
}

async function confirmDelete() {
  if (deleteConfirmId.value) {
    const success = await deleteEntry(deleteConfirmId.value);
    if (success) {
      deleteConfirmId.value = null;
      applyFilters();
    }
  }
}

// ─── HELPERS ──────────────────────────────────────────────
function formatDuration(minutes: number | null): string {
  if (!minutes) return 'läuft...';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}

function formatTime(dateString: string | null): string {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('de-DE');
}

function getStatusBadge(entry: any) {
  return entry.end_time === null
    ? 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200'
    : 'bg-white/5 border-white/10 text-white/60';
}

function getStatusLabel(entry: any): string {
  return entry.end_time === null ? 'Läuft' : 'Beendet';
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
          <h1 class="text-2xl font-bold text-white">Zeiteinträge</h1>
          <p class="text-sm text-white/60 mt-1">{{ entries.length }} Einträge • {{ totalHours }}h gesamt</p>
        </div>
      </div>
      <button @click="$emit('openEntry', 'create')" class="kit-btn-primary">
        <Plus :size="18" />
        Manueller Eintrag
      </button>
    </div>

    <!-- Filters -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Start Date -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Calendar :size="14" />
            Von Datum
          </label>
          <input
            v-model="startDate"
            @change="applyFilters"
            type="date"
            class="kit-input"
          />
        </div>

        <!-- End Date -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Calendar :size="14" />
            Bis Datum
          </label>
          <input
            v-model="endDate"
            @change="applyFilters"
            type="date"
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
        <p class="mt-4 text-white/60">Lade Einträge...</p>
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
        <Clock :size="64" class="mx-auto text-white/20 mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Keine Einträge gefunden</h3>
        <p class="text-white/60 mb-6">
          {{ hasFilters ? 'Keine Einträge im gewählten Zeitraum' : 'Starte deinen ersten Timer' }}
        </p>
        <button v-if="!hasFilters" @click="emit('openDashboard')" class="kit-btn-primary">
          <Clock :size="18" />
          Zum Dashboard
        </button>
      </div>
    </div>

    <!-- Entries List -->
    <div v-else class="flex-1 overflow-auto">
      <div class="space-y-3">
        <div
          v-for="entry in entries"
          :key="entry.id"
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="emit('openEntry', entry.id)"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Entry Info -->
            <div class="flex-1 min-w-0">
              <!-- Date + Status Badge -->
              <div class="flex items-center gap-3 mb-2">
                <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
                  <Clock :size="18" class="text-blue-200" />
                </div>
                <span class="font-semibold text-white">
                  {{ formatDate(entry.start_time) }}
                </span>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium border',
                    getStatusBadge(entry),
                  ]"
                >
                  {{ getStatusLabel(entry) }}
                </span>
              </div>

              <!-- Note -->
              <p v-if="entry.note" class="text-sm text-white/70 mb-3">
                {{ entry.note }}
              </p>
              <p v-else class="text-sm text-white/40 mb-3 italic">
                Kein Kommentar
              </p>

              <!-- Time Info -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                <div>
                  <div class="text-white/50 text-xs">Zeitraum</div>
                  <div class="font-medium text-white">
                    {{ formatTime(entry.start_time) }} - {{ formatTime(entry.end_time) }}
                  </div>
                </div>

                <div>
                  <div class="text-white/50 text-xs">Dauer</div>
                  <div class="font-medium text-white">
                    {{ formatDuration(entry.duration_minutes) }}
                  </div>
                </div>

                <div v-if="entry.billable">
                  <div class="text-white/50 text-xs">Abrechenbar</div>
                  <div class="font-medium text-emerald-200">Ja</div>
                </div>
              </div>
            </div>

            <!-- Right: Actions -->
            <div class="flex items-start gap-2">
              <button
                @click.stop="emit('openEntry', entry.id)"
                class="p-2 hover:bg-blue-500/20 rounded-lg transition"
                title="Details anzeigen"
              >
                <Eye :size="18" class="text-blue-200" />
              </button>
              <button
                @click.stop="showDeleteConfirm(entry.id)"
                class="p-2 hover:bg-red-500/20 rounded-lg transition"
                title="Eintrag löschen"
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
        <h3 class="text-xl font-bold text-white mb-2">Eintrag löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie diesen Zeiteintrag wirklich löschen? Diese Aktion kann nicht
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
