/**
 * useTimeTracking Composable
 * Verwaltet Zeiterfassung, Timer und Time Entries
 */

import { ref, computed, onMounted, onUnmounted } from 'vue';
import { timeTrackingService } from '../services/timeTracking.service';
import type { TimeEntry, TimeEntryCreateRequest, TimeEntryUpdateRequest, RunningTimer } from '../types/timeEntry';

export interface TimeEntryFilters {
  projectId?: string;
  employeeId?: string;
  startDate?: string;
  endDate?: string;
}

export function useTimeTracking() {
  // ─── STATE ────────────────────────────────────────────────
  const entries = ref<TimeEntry[]>([]);
  const currentEntry = ref<TimeEntry | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Timer state
  const runningTimer = ref<RunningTimer | null>(null);
  const timerInterval = ref<number | null>(null);

  // ─── COMPUTED ─────────────────────────────────────────────
  const hasEntries = computed(() => entries.value.length > 0);
  const isEmpty = computed(() => !loading.value && entries.value.length === 0);
  const isTimerRunning = computed(() => runningTimer.value !== null);

  const formattedElapsedTime = computed(() => {
    if (!runningTimer.value) return '00:00:00';

    const seconds = runningTimer.value.elapsed_seconds;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  });

  // ─── TIMER MANAGEMENT ─────────────────────────────────────

  /**
   * Timer starten
   */
  async function startTimer(projectId: string | null = null, employeeId: string = 'current-user-id'): Promise<boolean> {
    if (isTimerRunning.value) {
      error.value = 'Timer läuft bereits';
      return false;
    }

    loading.value = true;
    error.value = null;

    try {
      // Time Entry in Backend erstellen
      const entry = await timeTrackingService.createTimeEntry({
        employee_id: employeeId,
        project_id: projectId,
        start_time: new Date().toISOString(),
        note: null,
      });

      // Running timer state setzen
      runningTimer.value = {
        id: entry.id,
        project_id: projectId,
        start_time: entry.start_time,
        elapsed_seconds: 0,
      };

      // Interval starten (jede Sekunde)
      timerInterval.value = window.setInterval(() => {
        if (runningTimer.value) {
          runningTimer.value.elapsed_seconds++;
        }
      }, 1000);

      // Zu Entries hinzufügen
      entries.value.unshift(entry);

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Starten des Timers';
      console.error('Error starting timer:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Timer stoppen
   */
  async function stopTimer(note: string | null = null): Promise<boolean> {
    if (!runningTimer.value) {
      error.value = 'Kein Timer läuft';
      return false;
    }

    loading.value = true;
    error.value = null;

    try {
      const timerId = runningTimer.value.id;

      // Interval stoppen
      if (timerInterval.value) {
        clearInterval(timerInterval.value);
        timerInterval.value = null;
      }

      // Time Entry in Backend aktualisieren (end_time setzen)
      const updated = await timeTrackingService.updateTimeEntry(timerId, {
        end_time: new Date().toISOString(),
        note,
      });

      // Running timer state zurücksetzen
      runningTimer.value = null;

      // In der Liste aktualisieren
      const index = entries.value.findIndex((e) => e.id === timerId);
      if (index !== -1) {
        entries.value[index] = updated;
      }

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Stoppen des Timers';
      console.error('Error stopping timer:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Laufenden Timer abbrechen (Entry löschen)
   */
  async function cancelTimer(): Promise<boolean> {
    if (!runningTimer.value) {
      return false;
    }

    const timerId = runningTimer.value.id;

    // Interval stoppen
    if (timerInterval.value) {
      clearInterval(timerInterval.value);
      timerInterval.value = null;
    }

    // Entry löschen
    const success = await deleteEntry(timerId);

    if (success) {
      runningTimer.value = null;
    }

    return success;
  }

  // ─── CRUD ACTIONS ─────────────────────────────────────────

  /**
   * Time Entries laden
   */
  async function loadEntries(filters?: TimeEntryFilters) {
    loading.value = true;
    error.value = null;

    try {
      const response = await timeTrackingService.getTimeEntries();

      // Client-seitige Filterung
      let filtered = response;

      if (filters?.projectId) {
        filtered = filtered.filter((e) => e.project_id === filters.projectId);
      }

      if (filters?.employeeId) {
        filtered = filtered.filter((e) => e.employee_id === filters.employeeId);
      }

      // Date filtering
      if (filters?.startDate || filters?.endDate) {
        filtered = filtered.filter((e) => {
          const entryDate = new Date(e.start_time).toISOString().split('T')[0];
          if (filters.startDate && entryDate < filters.startDate) return false;
          if (filters.endDate && entryDate > filters.endDate) return false;
          return true;
        });
      }

      entries.value = filtered;

      // Check for running timer
      checkForRunningTimer();
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Einträge';
      console.error('Error loading entries:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Einzelnen Entry laden
   */
  async function loadEntry(id: string) {
    loading.value = true;
    error.value = null;

    try {
      currentEntry.value = await timeTrackingService.getTimeEntry(id);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden des Eintrags';
      console.error('Error loading entry:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Entry erstellen (manuell)
   */
  async function createEntry(data: TimeEntryCreateRequest): Promise<TimeEntry | null> {
    loading.value = true;
    error.value = null;

    try {
      const entry = await timeTrackingService.createTimeEntry(data);

      // Zur Liste hinzufügen
      if (entries.value.length > 0) {
        entries.value.unshift(entry);
      }

      return entry;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Erstellen des Eintrags';
      console.error('Error creating entry:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Entry aktualisieren
   */
  async function updateEntry(id: string, data: TimeEntryUpdateRequest): Promise<TimeEntry | null> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await timeTrackingService.updateTimeEntry(id, data);

      // In der Liste aktualisieren
      const index = entries.value.findIndex((e) => e.id === id);
      if (index !== -1) {
        entries.value[index] = updated;
      }

      // Current entry aktualisieren
      if (currentEntry.value?.id === id) {
        currentEntry.value = updated;
      }

      return updated;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren des Eintrags';
      console.error('Error updating entry:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Entry löschen
   */
  async function deleteEntry(id: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await timeTrackingService.deleteTimeEntry(id);

      // Aus der Liste entfernen
      entries.value = entries.value.filter((e) => e.id !== id);

      // Current entry zurücksetzen
      if (currentEntry.value?.id === id) {
        currentEntry.value = null;
      }

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Löschen des Eintrags';
      console.error('Error deleting entry:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  // ─── HELPER FUNCTIONS ─────────────────────────────────────

  /**
   * Prüfe ob ein Timer läuft (nach Reload)
   */
  function checkForRunningTimer() {
    const running = entries.value.find((e) => e.end_time === null);

    if (running) {
      const startTime = new Date(running.start_time);
      const now = new Date();
      const elapsedSeconds = Math.floor((now.getTime() - startTime.getTime()) / 1000);

      runningTimer.value = {
        id: running.id,
        project_id: running.project_id,
        start_time: running.start_time,
        elapsed_seconds: elapsedSeconds,
      };

      // Interval starten
      timerInterval.value = window.setInterval(() => {
        if (runningTimer.value) {
          runningTimer.value.elapsed_seconds++;
        }
      }, 1000);
    }
  }

  /**
   * Fehler zurücksetzen
   */
  function clearError() {
    error.value = null;
  }

  /**
   * State zurücksetzen
   */
  function reset() {
    entries.value = [];
    currentEntry.value = null;
    loading.value = false;
    error.value = null;

    // Timer stoppen
    if (timerInterval.value) {
      clearInterval(timerInterval.value);
      timerInterval.value = null;
    }
    runningTimer.value = null;
  }

  // ─── LIFECYCLE ────────────────────────────────────────────

  // Cleanup on unmount
  onUnmounted(() => {
    if (timerInterval.value) {
      clearInterval(timerInterval.value);
    }
  });

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    entries,
    currentEntry,
    loading,
    error,

    // Timer State
    runningTimer,
    isTimerRunning,
    formattedElapsedTime,

    // Computed
    hasEntries,
    isEmpty,

    // Timer Actions
    startTimer,
    stopTimer,
    cancelTimer,

    // CRUD Actions
    loadEntries,
    loadEntry,
    createEntry,
    updateEntry,
    deleteEntry,

    // Utils
    clearError,
    reset,
  };
}
