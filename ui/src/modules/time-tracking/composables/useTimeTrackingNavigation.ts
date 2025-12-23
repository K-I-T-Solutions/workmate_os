/**
 * useTimeTrackingNavigation Composable
 * Verwaltet die Navigation innerhalb des Time Tracking Moduls
 */

import { ref } from 'vue';

export type TimeTrackingView =
  | 'dashboard'
  | 'entries'
  | 'entry-detail'
  | 'entry-create'
  | 'entry-edit';

export function useTimeTrackingNavigation() {
  // ─── STATE ────────────────────────────────────────────────
  const view = ref<TimeTrackingView>('dashboard');
  const activeEntryId = ref<string | null>(null);

  // ─── NAVIGATION METHODS ───────────────────────────────────

  function goDashboard() {
    view.value = 'dashboard';
    activeEntryId.value = null;
  }

  function goEntries() {
    view.value = 'entries';
    activeEntryId.value = null;
  }

  function goEntryDetail(entryId: string) {
    view.value = 'entry-detail';
    activeEntryId.value = entryId;
  }

  function goCreateEntry() {
    view.value = 'entry-create';
    activeEntryId.value = null;
  }

  function goEditEntry(entryId: string) {
    view.value = 'entry-edit';
    activeEntryId.value = entryId;
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    view,
    activeEntryId,

    // Actions
    goDashboard,
    goEntries,
    goEntryDetail,
    goCreateEntry,
    goEditEntry,
  };
}
