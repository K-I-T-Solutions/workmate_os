<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useTimeTracking } from '../../composables/useTimeTracking';
import {
  Clock,
  Play,
  Square,
  Plus,
  TrendingUp,
  Calendar,
  ArrowRight,
  X,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openEntries: [];
  createEntry: [];
}>();

// Composables
const {
  entries,
  loading,
  loadEntries,
  runningTimer,
  isTimerRunning,
  formattedElapsedTime,
  startTimer,
  stopTimer,
  cancelTimer,
} = useTimeTracking();

// State
const showStopModal = ref(false);
const stopNote = ref('');

// Lifecycle
onMounted(() => {
  loadEntries();
});

// Computed
const todayEntries = computed(() => {
  const today = new Date().toISOString().split('T')[0];
  return entries.value.filter((e) => {
    const entryDate = new Date(e.start_time).toISOString().split('T')[0];
    return entryDate === today;
  });
});

const todayTotalMinutes = computed(() => {
  return todayEntries.value.reduce((sum, e) => {
    return sum + (e.duration_minutes || 0);
  }, 0);
});

const todayTotalHours = computed(() => {
  return (todayTotalMinutes.value / 60).toFixed(2);
});

const recentEntries = computed(() => {
  return [...entries.value]
    .filter(e => e.end_time !== null)
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
    .slice(0, 5);
});

// Actions
async function handleStartTimer() {
  await startTimer();
}

function handleStopClick() {
  showStopModal.value = true;
}

async function confirmStop() {
  const success = await stopTimer(stopNote.value || null);
  if (success) {
    showStopModal.value = false;
    stopNote.value = '';
    await loadEntries();
  }
}

async function handleCancelTimer() {
  if (confirm('Timer wirklich abbrechen? Der Eintrag wird gelöscht.')) {
    await cancelTimer();
    await loadEntries();
  }
}

// Helpers
function formatDuration(minutes: number | null): string {
  if (!minutes) return '-';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}

function formatTime(dateString: string): string {
  return new Date(dateString).toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('de-DE');
}
</script>

<template>
  <div class="h-full flex flex-col gap-3 sm:gap-4 p-3 sm:p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white">Zeiterfassung</h1>
      <div class="flex gap-2">
        <button @click="emit('openEntries')" class="kit-btn-ghost">
          <Calendar :size="18" />
          Alle Einträge
        </button>
        <button @click="emit('createEntry')" class="kit-btn-secondary">
          <Plus :size="18" />
          Manueller Eintrag
        </button>
      </div>
    </div>

    <!-- Timer Card -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-8">
      <div class="text-center">
        <!-- Timer Display -->
        <div class="mb-6">
          <div class="flex items-center justify-center gap-3 mb-2">
            <Clock :size="32" class="text-blue-300" />
            <h2 class="text-sm font-semibold text-white/60 uppercase tracking-wide">Aktiver Timer</h2>
          </div>
          <div class="text-6xl font-bold text-white font-mono mb-2">
            {{ formattedElapsedTime }}
          </div>
          <p v-if="isTimerRunning" class="text-sm text-white/60">
            Gestartet um {{ formatTime(runningTimer!.start_time) }}
          </p>
        </div>

        <!-- Timer Controls -->
        <div class="flex justify-center gap-3">
          <button
            v-if="!isTimerRunning"
            @click="handleStartTimer"
            class="kit-btn-primary px-8 py-4 text-lg"
            :disabled="loading"
          >
            <Play :size="24" />
            Timer starten
          </button>

          <template v-else>
            <button
              @click="handleStopClick"
              class="px-8 py-4 text-lg rounded-lg bg-emerald-500/20 border-2 border-emerald-400/30 text-emerald-200 hover:bg-emerald-500/30 transition font-semibold flex items-center gap-2"
            >
              <Square :size="24" />
              Timer stoppen
            </button>
            <button
              @click="handleCancelTimer"
              class="px-4 py-4 text-lg rounded-lg bg-red-500/20 border-2 border-red-400/30 text-red-200 hover:bg-red-500/30 transition"
              title="Timer abbrechen"
            >
              <X :size="24" />
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- Today Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-2">
          <Clock :size="16" class="text-blue-300" />
          <span class="text-sm text-white/60">Heute erfasst</span>
        </div>
        <div class="text-2xl font-bold text-white">{{ todayTotalHours }}h</div>
      </div>

      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-2">
          <TrendingUp :size="16" class="text-emerald-300" />
          <span class="text-sm text-white/60">Einträge heute</span>
        </div>
        <div class="text-2xl font-bold text-white">{{ todayEntries.length }}</div>
      </div>

      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-2">
          <Calendar :size="16" class="text-orange-300" />
          <span class="text-sm text-white/60">Gesamt-Einträge</span>
        </div>
        <div class="text-2xl font-bold text-white">{{ entries.length }}</div>
      </div>
    </div>

    <!-- Recent Entries -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4 flex-1 overflow-hidden flex flex-col">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-white">Letzte Einträge</h3>
        <button @click="emit('openEntries')" class="text-sm text-blue-300 hover:text-blue-200 flex items-center gap-1">
          Alle anzeigen
          <ArrowRight :size="14" />
        </button>
      </div>

      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
      </div>

      <div v-else-if="recentEntries.length > 0" class="space-y-2 overflow-y-auto">
        <div
          v-for="entry in recentEntries"
          :key="entry.id"
          class="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition"
        >
          <div class="flex-1 min-w-0">
            <div class="text-sm text-white/80 truncate">
              {{ entry.note || 'Kein Kommentar' }}
            </div>
            <div class="text-xs text-white/50 mt-1">
              {{ formatDate(entry.start_time) }} • {{ formatTime(entry.start_time) }} - {{ formatTime(entry.end_time!) }}
            </div>
          </div>
          <div class="text-sm font-medium text-white ml-4">
            {{ formatDuration(entry.duration_minutes) }}
          </div>
        </div>
      </div>

      <div v-else class="flex-1 flex items-center justify-center text-center py-8 text-white/40">
        <div>
          <Clock :size="32" class="mx-auto mb-2 opacity-50" />
          <p class="text-sm">Noch keine Zeiteinträge</p>
          <button @click="handleStartTimer" class="kit-btn-primary mt-4">
            <Play :size="18" />
            Ersten Timer starten
          </button>
        </div>
      </div>
    </div>

    <!-- Stop Modal -->
    <div
      v-if="showStopModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="showStopModal = false"
    >
      <div
        class="rounded-lg border border-white/10 bg-stone-900 p-6 max-w-md w-full"
        @click.stop
      >
        <h3 class="text-xl font-bold text-white mb-4">Timer stoppen</h3>
        <div class="mb-4">
          <label class="kit-label">Notiz (optional)</label>
          <textarea
            v-model="stopNote"
            rows="3"
            class="kit-input"
            placeholder="Woran hast du gearbeitet?"
            autofocus
          ></textarea>
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="showStopModal = false" class="kit-btn-ghost">
            Abbrechen
          </button>
          <button @click="confirmStop" class="kit-btn-primary">
            <Square :size="18" />
            Timer stoppen
          </button>
        </div>
      </div>
    </div>
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
  .flex-col.gap-3 {
    gap: 0.5rem;
  }
}
</style>
