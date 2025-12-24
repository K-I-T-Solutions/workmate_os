/**
 * Expenses Internal Navigation
 */
import { ref } from 'vue';

type ExpenseView = 'dashboard' | 'list' | 'create' | 'edit';

const view = ref<ExpenseView>('dashboard');
const activeExpenseId = ref<string | null>(null);

export function useExpensesNavigation() {
  function goDashboard() {
    view.value = 'dashboard';
    activeExpenseId.value = null;
  }

  function goList() {
    view.value = 'list';
    activeExpenseId.value = null;
  }

  function goCreate() {
    view.value = 'create';
    activeExpenseId.value = null;
  }

  function goEdit(expenseId: string) {
    view.value = 'edit';
    activeExpenseId.value = expenseId;
  }

  return {
    view,
    activeExpenseId,
    goDashboard,
    goList,
    goCreate,
    goEdit,
  };
}
