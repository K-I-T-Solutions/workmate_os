/**
 * useTimeTrackingStats Composable
 * Lädt und verwaltet Zeiterfassungs-Statistiken
 */

import { ref } from 'vue';
import { timeTrackingService } from '../services/timeTracking.service';
import type { TimeTrackingStats } from '../types/timeEntry';

export function useTimeTrackingStats() {
  const stats = ref<TimeTrackingStats | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchStats(employeeId?: string) {
    loading.value = true;
    error.value = null;

    try {
      stats.value = await timeTrackingService.getStats(employeeId);
    } catch (e: any) {
      error.value = e.message ?? 'Stats konnten nicht geladen werden';
      console.error('Error fetching time tracking stats:', e);
    } finally {
      loading.value = false;
    }
  }

  return { stats, loading, error, fetchStats };
}
