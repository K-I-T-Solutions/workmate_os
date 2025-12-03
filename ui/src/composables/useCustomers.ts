import { ref } from 'vue';
import { apiClient } from '@/services/api/client';
import type { Customer } from '@/types/api';

export function useCustomers() {
  const customers = ref<Customer[]>([]);
  const customer = ref<Customer | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Liste laden
  const fetchCustomers = async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    search?: string;
  }) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/api/backoffice/crm/customers', { params });
      customers.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Kunden';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Einzelnen Kunden laden
  const fetchCustomer = async (customerId: string) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get(`/api/backoffice/crm/customers/${customerId}`);
      customer.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden des Kunden';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Kunden erstellen
  const createCustomer = async (data: {
    name: string;
    email?: string;
    phone?: string;
    type?: string;
    street?: string;
    zip_code?: string;
    city?: string;
    country?: string;
    tax_id?: string;
    website?: string;
    notes?: string;
    status?: string;
  }) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.post('/api/backoffice/crm/customers', data);
      customers.value.push(response.data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Erstellen des Kunden';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Kunden aktualisieren
  const updateCustomer = async (customerId: string, data: Partial<Customer>) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.put(`/api/backoffice/crm/customers/${customerId}`, data);
      const index = customers.value.findIndex(c => c.id === customerId);
      if (index !== -1) {
        customers.value[index] = response.data;
      }
      customer.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Aktualisieren des Kunden';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Kunden löschen
  const deleteCustomer = async (customerId: string) => {
    loading.value = true;
    error.value = null;
    try {
      await apiClient.delete(`/api/backoffice/crm/customers/${customerId}`);
      customers.value = customers.value.filter(c => c.id !== customerId);
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Löschen des Kunden';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    customers,
    customer,
    loading,
    error,
    fetchCustomers,
    fetchCustomer,
    createCustomer,
    updateCustomer,
    deleteCustomer,
  };
}
