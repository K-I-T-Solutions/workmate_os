/**
 * Expenses State Management & API Integration
 */
import { ref, computed } from 'vue';
import type {
  ExpenseRead,
  ExpenseCreate,
  ExpenseUpdate,
  ExpenseKpiResponse,
  ExpenseFilters,
} from '../types';
import {
  createExpense as apiCreateExpense,
  listExpenses as apiListExpenses,
  getExpense as apiGetExpense,
  updateExpense as apiUpdateExpense,
  deleteExpense as apiDeleteExpense,
  getExpenseKpis as apiGetExpenseKpis,
} from '../services/expenses.service';

const expenses = ref<ExpenseRead[]>([]);
const currentExpense = ref<ExpenseRead | null>(null);
const kpis = ref<ExpenseKpiResponse | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const filters = ref<ExpenseFilters>({});

export function useExpenses() {
  /**
   * Load expenses list with optional filters
   */
  async function loadExpenses(newFilters?: ExpenseFilters) {
    isLoading.value = true;
    error.value = null;
    try {
      if (newFilters) {
        filters.value = newFilters;
      }
      const response = await apiListExpenses(filters.value);
      expenses.value = response.items;
    } catch (err: any) {
      error.value = err.message || 'Failed to load expenses';
      console.error('Error loading expenses:', err);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load a single expense by ID
   */
  async function loadExpense(id: string) {
    isLoading.value = true;
    error.value = null;
    try {
      currentExpense.value = await apiGetExpense(id);
    } catch (err: any) {
      error.value = err.message || 'Failed to load expense';
      console.error('Error loading expense:', err);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Create a new expense
   */
  async function createExpense(data: ExpenseCreate): Promise<boolean> {
    isLoading.value = true;
    error.value = null;
    try {
      const newExpense = await apiCreateExpense(data);
      expenses.value.unshift(newExpense);
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to create expense';
      console.error('Error creating expense:', err);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update an existing expense
   */
  async function updateExpense(id: string, data: ExpenseUpdate): Promise<boolean> {
    isLoading.value = true;
    error.value = null;
    try {
      const updated = await apiUpdateExpense(id, data);
      const index = expenses.value.findIndex((e) => e.id === id);
      if (index !== -1) {
        expenses.value[index] = updated;
      }
      if (currentExpense.value?.id === id) {
        currentExpense.value = updated;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to update expense';
      console.error('Error updating expense:', err);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete an expense
   */
  async function deleteExpense(id: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;
    try {
      await apiDeleteExpense(id);
      expenses.value = expenses.value.filter((e) => e.id !== id);
      if (currentExpense.value?.id === id) {
        currentExpense.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to delete expense';
      console.error('Error deleting expense:', err);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load expense KPIs
   */
  async function loadKpis(kpiFilters?: Omit<ExpenseFilters, 'limit' | 'offset'>) {
    isLoading.value = true;
    error.value = null;
    try {
      kpis.value = await apiGetExpenseKpis(kpiFilters);
    } catch (err: any) {
      error.value = err.message || 'Failed to load KPIs';
      console.error('Error loading KPIs:', err);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Clear current expense
   */
  function clearCurrentExpense() {
    currentExpense.value = null;
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null;
  }

  // Computed
  const totalExpenses = computed(() => expenses.value.length);
  const hasExpenses = computed(() => expenses.value.length > 0);

  return {
    // State
    expenses,
    currentExpense,
    kpis,
    isLoading,
    error,
    filters,

    // Actions
    loadExpenses,
    loadExpense,
    createExpense,
    updateExpense,
    deleteExpense,
    loadKpis,
    clearCurrentExpense,
    clearError,

    // Computed
    totalExpenses,
    hasExpenses,
  };
}
