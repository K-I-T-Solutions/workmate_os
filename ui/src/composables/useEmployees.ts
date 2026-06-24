import { ref } from 'vue';
import { apiClient } from '@/services/api/client';
import type { Employee } from '@/types/api';

export function useEmployees() {
  const employees = ref<Employee[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchEmployees = async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/api/employees', { params });
      employees.value = response.data.employees;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Mitarbeiter';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    employees,
    loading,
    error,
    fetchEmployees,
  };
}
