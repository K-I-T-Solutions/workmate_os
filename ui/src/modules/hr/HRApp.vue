<script setup lang="ts">
import { ref } from 'vue';
import HRDashboardPage from './pages/HRDashboardPage.vue';
import LeaveManagementPage from './pages/LeaveManagementPage.vue';
import LeaveApprovalsPage from './pages/LeaveApprovalsPage.vue';
import EmployeeListPage from './pages/EmployeeListPage.vue';

// Props for deep-linking from other apps (if needed in future)
const props = defineProps<{
  initialView?: string;
}>();

// Current view state
const currentView = ref(props.initialView || 'dashboard');

// Navigation tabs
const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'leave', label: 'Urlaubsverwaltung', icon: '🌴' },
  { id: 'approvals', label: 'Genehmigungen', icon: '✅' },
  { id: 'employees', label: 'Mitarbeiter', icon: '👥' },
];
</script>

<template>
  <div class="hr-app h-full flex flex-col">
    <!-- Navigation Tabs -->
    <div class="border-b border-white/10 bg-white/5">
      <div class="flex gap-2 p-4">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentView = tab.id"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            currentView === tab.id
              ? 'bg-blue-500/20 text-blue-300 font-semibold'
              : 'text-white/60 hover:bg-white/10 hover:text-white'
          ]"
        >
          <span class="mr-2">{{ tab.icon }}</span>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-4">
      <HRDashboardPage v-if="currentView === 'dashboard'" />
      <LeaveManagementPage v-if="currentView === 'leave'" />
      <LeaveApprovalsPage v-if="currentView === 'approvals'" />
      <EmployeeListPage v-if="currentView === 'employees'" />
    </div>
  </div>
</template>

<style scoped>
.hr-app {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}
</style>
