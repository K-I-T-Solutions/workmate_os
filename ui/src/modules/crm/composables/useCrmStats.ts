// src/modules/backoffice/crm/composables/useCrmStats.ts
import { ref } from "vue";
import { crmService } from "../services/crm.service";
import type { CrmStats } from "../types/stats";

export function useCrmStats() {
  const stats = ref<CrmStats | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchStats() {
    loading.value = true;
    error.value = null;

    try {
      const data = await crmService.getCrmStats(); // ✅ anderer Name
      stats.value = data;                          // ✅ korrekt
    } catch (e: any) {
      error.value = e.message ?? "CRM Stats konnten nicht geladen werden";
    } finally {
      loading.value = false;
    }
  }

  return {
    stats,
    loading,
    error,
    fetchStats,
  };
}
