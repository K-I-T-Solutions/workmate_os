// src/modules/backoffice/crm/composables/useActivity.ts
import { ref } from "vue";
import type {
  CrmActivity,
  CreateCrmActivity,
} from "../types/activity";
import { crmService } from "../services/crm.service";

export function useCrmActivity() {
  const activities = ref<CrmActivity[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchLatestActivities(limit: number) {
    loading.value = true;
    error.value = null;

    try {
      const data = await crmService.getLastestActivities(limit);
      activities.value = data;
    } catch (e: any) {
      error.value =
        e.message ?? "Aktivitäten konnten nicht geladen werden";
    } finally {
      loading.value = false;
    }
  }
  async function fetchCustomerActivities(customerId:string) {
     loading.value =true;
     error.value = null;

     try{
      const data = await crmService.getCustomerActivities(customerId);
      activities.value = data;
     } catch (e: any){
      error.value = e.message ?? "Aktivitäten für den Kunden kann nicht geladen werden"
     }finally{
      loading.value = false;
     }
  }

  async function createActivity(payload: CreateCrmActivity) {
    loading.value = true;
    error.value = null;

    try {
      const created = await crmService.createActivity(payload);
      // append-only → neueste oben
      activities.value.unshift(created);
      return created;
    } catch (e: any) {
      error.value =
        e.message ?? "Aktivität konnte nicht erstellt werden";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    activities,
    loading,
    error,
    fetchLatestActivities,
    createActivity,
    fetchCustomerActivities,
  };
}
