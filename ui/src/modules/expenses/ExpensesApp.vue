<script setup lang="ts">
import { onMounted } from 'vue';
import ExpensesDashboardPage from './pages/dashboard/ExpensesDashboardPage.vue';
import ExpensesListPage from './pages/expense/ExpensesListPage.vue';
import ExpenseFormPage from './pages/expense/ExpenseFormPage.vue';
import { useExpensesNavigation } from './composables/useExpensesNavigation';

// Props for deep-linking from other apps
const props = defineProps<{
  initialView?: string;
  initialExpenseId?: string;
}>();

const { view, activeExpenseId, goDashboard, goList, goCreate, goEdit } =
  useExpensesNavigation();

// Handle deep-linking on mount
onMounted(() => {
  if (props.initialView && props.initialExpenseId) {
    switch (props.initialView) {
      case 'edit':
        goEdit(props.initialExpenseId);
        break;
      default:
        break;
    }
  } else if (props.initialView === 'create') {
    goCreate();
  } else if (props.initialView === 'list') {
    goList();
  }
});

// Event Handlers
function handleSaved() {
  // After saving, go back to list
  goList();
}

function handleFormClose() {
  // Close form, go back to list
  goList();
}
</script>

<template>
  <div class="expenses-app h-full">
    <!-- Dashboard -->
    <ExpensesDashboardPage
      v-if="view === 'dashboard'"
      @openExpenses="goList"
      @createExpense="goCreate"
    />

    <!-- List -->
    <ExpensesListPage v-else-if="view === 'list'" @editExpense="goEdit" />

    <!-- Create Form -->
    <ExpenseFormPage
      v-else-if="view === 'create'"
      @close="handleFormClose"
      @saved="handleSaved"
    />

    <!-- Edit Form -->
    <ExpenseFormPage
      v-else-if="view === 'edit'"
      :expense-id="activeExpenseId"
      @close="handleFormClose"
      @saved="handleSaved"
    />
  </div>
</template>
