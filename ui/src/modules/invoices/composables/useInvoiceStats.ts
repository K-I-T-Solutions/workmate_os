/**
 * useInvoiceStats Composable
 * Lädt und verwaltet Rechnungsstatistiken
 */

import { ref } from 'vue';
import { invoicesService } from '../services/invoices.service';
import type { InvoiceStatistics } from '../types';

export function useInvoiceStats() {
  // ─── STATE ────────────────────────────────────────────────
  const stats = ref<InvoiceStatistics | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ─── ACTIONS ──────────────────────────────────────────────

  /**
   * Statistiken laden
   */
  async function loadStats() {
    loading.value = true;
    error.value = null;

    try {
      stats.value = await invoicesService.getStatistics();
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Statistiken';
      console.error('Error loading invoice stats:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Statistiken neu laden
   */
  async function refresh() {
    await loadStats();
  }

  /**
   * State zurücksetzen
   */
  function reset() {
    stats.value = null;
    loading.value = false;
    error.value = null;
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    stats,
    loading,
    error,

    // Actions
    loadStats,
    refresh,
    reset,
  };
}
