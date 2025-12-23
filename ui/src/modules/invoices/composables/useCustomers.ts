/**
 * useCustomers Composable
 * Lädt Kunden-Daten für Dropdowns
 */

import { ref } from 'vue';
import { apiClient } from '@/services/api/client';

interface Customer {
  id: string;
  name: string;
  email?: string;
  company?: string;
}

export function useCustomers() {
  const customers = ref<Customer[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadCustomers() {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.get<Customer[]>('/api/backoffice/crm/customers');
      customers.value = response.data;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Kunden';
      console.error('Error loading customers:', e);
    } finally {
      loading.value = false;
    }
  }

  return {
    customers,
    loading,
    error,
    loadCustomers,
  };
}
