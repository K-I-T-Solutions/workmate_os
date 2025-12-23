<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useTimeTracking } from '../../composables/useTimeTracking';
import { useAppManager } from '@/layouts/app-manager/useAppManager';
import { apiClient } from '@/services/api/client';
import {
  ChevronLeft,
  Clock,
  Calendar,
  FileText,
  DollarSign,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
  User,
  Briefcase,
} from 'lucide-vue-next';

// Props & Emits
const props = defineProps<{
  entryId: string;
}>();

const emit = defineEmits<{
  back: [];
  edit: [id: string];
}>();

// Composables
const { currentEntry, loading, error, loadEntry, deleteEntry } = useTimeTracking();
const { openWindow } = useAppManager();

// State
const showDeleteModal = ref(false);
const employee = ref<any>(null);
const loadingEmployee = ref(false);

// Data Loading
async function loadEmployeeData() {
  if (!currentEntry.value?.employee_id) return;

  loadingEmployee.value = true;
  try {
    const response = await apiClient.get(`/api/employees/${currentEntry.value.employee_id}`);
    employee.value = response.data;
  } catch (error) {
    console.error('Error loading employee data:', error);
  } finally {
    loadingEmployee.value = false;
  }
}

// Lifecycle
onMounted(async () => {
  await loadEntry(props.entryId);
  await loadEmployeeData();
});

// Computed
const formattedDuration = computed(() => {
  if (!currentEntry.value) return '-';
  const minutes = currentEntry.value.duration_minutes;
  if (!minutes) return 'Läuft...';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
});

const formattedHours = computed(() => {
  if (!currentEntry.value?.duration_minutes) return '-';
  return (currentEntry.value.duration_minutes / 60).toFixed(2);
});

const totalAmount = computed(() => {
  if (!currentEntry.value?.hourly_rate || !currentEntry.value.duration_minutes) return null;
  const hours = currentEntry.value.duration_minutes / 60;
  return (hours * currentEntry.value.hourly_rate).toFixed(2);
});

const statusBadge = computed(() => {
  if (!currentEntry.value) return '';
  return currentEntry.value.end_time === null
    ? 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200'
    : 'bg-white/5 border-white/10 text-white/60';
});

const statusLabel = computed(() => {
  if (!currentEntry.value) return '';
  return currentEntry.value.end_time === null ? 'Läuft' : 'Beendet';
});

const taskTypeBadge = computed(() => {
  if (!currentEntry.value?.task_type) return '';
  const badges: Record<string, string> = {
    development: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    meeting: 'bg-purple-500/20 border-purple-400/30 text-purple-200',
    support: 'bg-orange-500/20 border-orange-400/30 text-orange-200',
    documentation: 'bg-yellow-500/20 border-yellow-400/30 text-yellow-200',
    testing: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    planning: 'bg-indigo-500/20 border-indigo-400/30 text-indigo-200',
    other: 'bg-white/5 border-white/10 text-white/60',
  };
  return badges[currentEntry.value.task_type] || badges.other;
});

const taskTypeLabel = computed(() => {
  if (!currentEntry.value?.task_type) return 'Nicht festgelegt';
  const labels: Record<string, string> = {
    development: 'Entwicklung',
    meeting: 'Meeting',
    support: 'Support',
    documentation: 'Dokumentation',
    testing: 'Testing',
    planning: 'Planung',
    other: 'Sonstiges',
  };
  return labels[currentEntry.value.task_type] || 'Sonstiges';
});

// Actions
async function handleDelete() {
  const success = await deleteEntry(props.entryId);
  if (success) {
    emit('back');
  }
}

// Cross-App Navigation
function openProject() {
  if (!currentEntry.value?.project_id) return;
  openWindow('projects', {
    initialView: 'project-detail',
    initialProjectId: currentEntry.value.project_id,
  });
}

function formatTime(dateString: string | null): string {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('de-DE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Eintrag...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error || !currentEntry" class="flex-1">
      <div class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <p class="text-red-200">{{ error || 'Eintrag nicht gefunden' }}</p>
      </div>
      <button @click="emit('back')" class="kit-btn-ghost mt-4">
        <ChevronLeft :size="18" />
        Zurück
      </button>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-3 flex-1">
          <button @click="emit('back')" class="kit-btn-ghost mt-1">
            <ChevronLeft :size="18" />
          </button>
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h1 class="text-2xl font-bold text-white">Zeiteintrag</h1>
              <span :class="['px-3 py-1 rounded-full text-sm font-medium border', statusBadge]">
                {{ statusLabel }}
              </span>
            </div>
            <p class="text-white/60">{{ formatDate(currentEntry.start_time) }}</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            v-if="currentEntry.end_time !== null"
            @click="emit('edit', currentEntry.id)"
            class="kit-btn-secondary"
          >
            <Edit :size="18" />
            Bearbeiten
          </button>
          <button @click="showDeleteModal = true" class="kit-btn-danger">
            <Trash2 :size="18" />
            Löschen
          </button>
        </div>
      </div>

      <!-- Main Info Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Zeitraum -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <Clock :size="18" class="text-blue-200" />
            </div>
            <h3 class="font-semibold text-white">Zeitraum</h3>
          </div>
          <div class="space-y-2">
            <div>
              <div class="text-xs text-white/50">Start</div>
              <div class="text-white font-medium">{{ formatTime(currentEntry.start_time) }}</div>
            </div>
            <div>
              <div class="text-xs text-white/50">Ende</div>
              <div class="text-white font-medium">{{ formatTime(currentEntry.end_time) }}</div>
            </div>
            <div class="pt-2 border-t border-white/10">
              <div class="text-xs text-white/50">Dauer</div>
              <div class="text-lg font-bold text-white">{{ formattedDuration }}</div>
              <div class="text-xs text-white/40">{{ formattedHours }} Stunden</div>
            </div>
          </div>
        </div>

        <!-- Details -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-purple-500/20 rounded-lg border border-purple-400/30">
              <FileText :size="18" class="text-purple-200" />
            </div>
            <h3 class="font-semibold text-white">Details</h3>
          </div>
          <div class="space-y-2">
            <div>
              <div class="text-xs text-white/50">Aufgabentyp</div>
              <span :class="['px-2 py-1 rounded text-xs font-medium border inline-block', taskTypeBadge]">
                {{ taskTypeLabel }}
              </span>
            </div>
            <div>
              <div class="text-xs text-white/50">Abrechenbar</div>
              <div class="flex items-center gap-1">
                <CheckCircle v-if="currentEntry.billable" :size="16" class="text-emerald-300" />
                <XCircle v-else :size="16" class="text-white/40" />
                <span :class="currentEntry.billable ? 'text-emerald-200' : 'text-white/60'">
                  {{ currentEntry.billable ? 'Ja' : 'Nein' }}
                </span>
              </div>
            </div>
            <div v-if="currentEntry.project_id">
              <div class="text-xs text-white/50">Projekt</div>
              <button
                @click="openProject"
                class="flex items-center gap-1 text-white/80 hover:text-blue-300 transition"
              >
                <Briefcase :size="14" />
                <span class="underline">Zum Projekt</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Finanzen -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <DollarSign :size="18" class="text-emerald-200" />
            </div>
            <h3 class="font-semibold text-white">Finanzen</h3>
          </div>
          <div class="space-y-2">
            <div>
              <div class="text-xs text-white/50">Stundensatz</div>
              <div class="text-white font-medium">
                {{ currentEntry.hourly_rate ? `${currentEntry.hourly_rate.toFixed(2)} €` : '-' }}
              </div>
            </div>
            <div v-if="totalAmount" class="pt-2 border-t border-white/10">
              <div class="text-xs text-white/50">Gesamtbetrag</div>
              <div class="text-lg font-bold text-emerald-200">{{ totalAmount }} €</div>
            </div>
            <div class="pt-2 border-t border-white/10">
              <div class="text-xs text-white/50">Status</div>
              <div class="flex flex-col gap-1">
                <div class="flex items-center gap-1">
                  <CheckCircle v-if="currentEntry.is_approved" :size="14" class="text-emerald-300" />
                  <XCircle v-else :size="14" class="text-white/40" />
                  <span :class="currentEntry.is_approved ? 'text-emerald-200' : 'text-white/60'" class="text-xs">
                    {{ currentEntry.is_approved ? 'Genehmigt' : 'Nicht genehmigt' }}
                  </span>
                </div>
                <div class="flex items-center gap-1">
                  <CheckCircle v-if="currentEntry.is_invoiced" :size="14" class="text-blue-300" />
                  <XCircle v-else :size="14" class="text-white/40" />
                  <span :class="currentEntry.is_invoiced ? 'text-blue-200' : 'text-white/60'" class="text-xs">
                    {{ currentEntry.is_invoiced ? 'Abgerechnet' : 'Nicht abgerechnet' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Notiz Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-3">
          <FileText :size="18" class="text-white/60" />
          <h3 class="font-semibold text-white">Notiz</h3>
        </div>
        <p v-if="currentEntry.note" class="text-white/80 whitespace-pre-wrap">
          {{ currentEntry.note }}
        </p>
        <p v-else class="text-white/40 italic">Keine Notiz hinterlegt</p>
      </div>

      <!-- Meta Information -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-3">
          <Calendar :size="18" class="text-white/60" />
          <h3 class="font-semibold text-white">Meta-Informationen</h3>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
          <div>
            <div class="text-xs text-white/50">Mitarbeiter</div>
            <div class="text-white/80 flex items-center gap-1">
              <User :size="14" />
              <span v-if="loadingEmployee">Lade...</span>
              <span v-else-if="employee">
                {{ employee.first_name }} {{ employee.last_name }} ({{ employee.employee_code }})
              </span>
              <span v-else class="text-white/40">Nicht verfügbar</span>
            </div>
          </div>
          <div>
            <div class="text-xs text-white/50">Erstellt am</div>
            <div class="text-white/80">{{ formatDateTime(currentEntry.created_at) }}</div>
          </div>
          <div>
            <div class="text-xs text-white/50">Aktualisiert am</div>
            <div class="text-white/80">{{ formatDateTime(currentEntry.updated_at) }}</div>
          </div>
        </div>
      </div>
    </template>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="showDeleteModal = false"
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
          <button @click="showDeleteModal = false" class="kit-btn-ghost">
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
