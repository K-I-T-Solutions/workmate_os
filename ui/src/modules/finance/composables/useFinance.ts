import { ref } from 'vue';
import type { FinanceOverview, FinanceFilters } from '../types';
import { getFinanceOverview } from '../services/finance.service';

const overview = ref<FinanceOverview | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

export function useFinance() {
  async function loadOverview(filters?: FinanceFilters): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      overview.value = await getFinanceOverview(filters);
      return true;
    } catch (err: any) {
      console.error('Error loading finance overview:', err);
      error.value = err.response?.data?.detail || 'Fehler beim Laden der Finanzdaten';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  function clearOverview() {
    overview.value = null;
    error.value = null;
  }

  return {
    // State
    overview,
    isLoading,
    error,

    // Actions
    loadOverview,
    clearOverview,
  };
}
