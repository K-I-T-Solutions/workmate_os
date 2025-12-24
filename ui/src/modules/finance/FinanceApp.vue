<script setup lang="ts">
import FinanceDashboardPage from './pages/dashboard/FinanceDashboardPage.vue';

// Props for deep-linking from other apps (if needed in future)
const props = defineProps<{
  initialView?: string;
}>();
</script>

<template>
  <div class="finance-app h-full">
    <!-- For now, just show the dashboard -->
    <!-- In the future, we could add views for detailed reports, etc. -->
    <FinanceDashboardPage />
  </div>
</template>
