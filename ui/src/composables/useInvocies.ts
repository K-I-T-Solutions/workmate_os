import { ref } from 'vue';
import { apiClient } from '@/services/api/client';
import type { Invoice } from '@/types/api';

export function useInvoices() {
  const invoices = ref<Invoice[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchInvoices = async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/api/backoffice/invoices/', { params });
      invoices.value = response.data.items;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Rechnungen';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getStatistics = async (customerId?: string) => {
    try {
      const response = await apiClient.get('/api/backoffice/invoices/statistics', {
        params: customerId ? { customer_id: customerId } : undefined,
      });
      return response.data;
    } catch (err: any) {
      throw err;
    }
  };

  return {
    invoices,
    loading,
    error,
    fetchInvoices,
    getStatistics,
  };
}
