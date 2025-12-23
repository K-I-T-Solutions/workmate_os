/**
 * useCustomers Composable
 * Verwaltet das Laden und Verarbeiten von Kunden
 */

import { ref, computed } from 'vue';
import { crmService } from '../services/crm.service';
import type { Customer } from '../types/customer';

export interface CustomerFilters {
  status?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export function useCustomers() {
  // ─── STATE ────────────────────────────────────────────────
  const customers = ref<Customer[]>([]);
  const currentCustomer = ref<Customer | null>(null);
  const total = ref(0);
  const page = ref(1);
  const pages = ref(1);
  const limit = ref(20);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ─── COMPUTED ─────────────────────────────────────────────
  const hasCustomers = computed(() => customers.value.length > 0);
  const isEmpty = computed(() => !loading.value && customers.value.length === 0);

  // ─── ACTIONS ──────────────────────────────────────────────

  /**
   * Kunden laden mit Filtern
   */
  async function loadCustomers(filters?: CustomerFilters) {
    loading.value = true;
    error.value = null;

    try {
      // API-Call mit Filtern
      const response = await crmService.getCustomers();

      // Client-seitige Filterung bis Backend-Pagination implementiert ist
      let filtered = response;

      if (filters?.status) {
        filtered = filtered.filter((c) => c.status === filters.status);
      }

      if (filters?.search) {
        const search = filters.search.toLowerCase();
        filtered = filtered.filter((c) =>
          c.name.toLowerCase().includes(search) ||
          c.email?.toLowerCase().includes(search) ||
          c.customer_number?.toLowerCase().includes(search)
        );
      }

      // Pagination berechnen
      const totalCount = filtered.length;
      const currentLimit = filters?.limit || limit.value;
      const currentSkip = filters?.skip || 0;
      const currentPage = Math.floor(currentSkip / currentLimit) + 1;
      const totalPages = Math.ceil(totalCount / currentLimit);

      // Pagination anwenden
      const start = currentSkip;
      const end = start + currentLimit;
      customers.value = filtered.slice(start, end);

      // Meta-Daten setzen
      total.value = totalCount;
      page.value = currentPage;
      pages.value = totalPages;
      limit.value = currentLimit;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Kunden';
      console.error('Error loading customers:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Einzelnen Kunden laden
   */
  async function loadCustomer(id: string) {
    loading.value = true;
    error.value = null;

    try {
      currentCustomer.value = await crmService.getCustomer(id);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden des Kunden';
      console.error('Error loading customer:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Neuen Kunden erstellen
   */
  async function createCustomer(data: Partial<Customer>): Promise<Customer | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await crmService.createCustomer(data);
      const customer = response.data;

      // Zur Liste hinzufügen wenn bereits geladen
      if (customers.value.length > 0) {
        customers.value.unshift(customer);
        total.value += 1;
      }

      return customer;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Erstellen des Kunden';
      console.error('Error creating customer:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Kunden aktualisieren
   */
  async function updateCustomer(id: string, data: Partial<Customer>): Promise<Customer | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await crmService.updateCustomer(id, data);
      const updated = response.data;

      // In der Liste aktualisieren
      const index = customers.value.findIndex((c) => c.id === id);
      if (index !== -1) {
        customers.value[index] = updated;
      }

      // Current customer aktualisieren
      if (currentCustomer.value?.id === id) {
        currentCustomer.value = updated;
      }

      return updated;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren des Kunden';
      console.error('Error updating customer:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Kunden löschen
   */
  async function deleteCustomer(id: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await crmService.deleteCustomer(id);

      // Aus der Liste entfernen
      customers.value = customers.value.filter((c) => c.id !== id);
      total.value -= 1;

      // Current customer zurücksetzen
      if (currentCustomer.value?.id === id) {
        currentCustomer.value = null;
      }

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Löschen des Kunden';
      console.error('Error deleting customer:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Kunden suchen (für Autocomplete)
   */
  async function searchCustomers(query: string): Promise<Customer[]> {
    try {
      const response = await crmService.searchCustomers(query);
      return response.data;
    } catch (e: any) {
      console.error('Error searching customers:', e);
      return [];
    }
  }

  /**
   * Fehler zurücksetzen
   */
  function clearError() {
    error.value = null;
  }

  /**
   * State zurücksetzen
   */
  function reset() {
    customers.value = [];
    currentCustomer.value = null;
    total.value = 0;
    page.value = 1;
    pages.value = 1;
    loading.value = false;
    error.value = null;
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    customers,
    currentCustomer,
    total,
    page,
    pages,
    limit,
    loading,
    error,

    // Computed
    hasCustomers,
    isEmpty,

    // Actions
    loadCustomers,
    loadCustomer,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    searchCustomers,
    clearError,
    reset,
  };
}
