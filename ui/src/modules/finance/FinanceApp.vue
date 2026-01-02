<script setup lang="ts">
import { ref } from 'vue';
import FinanceDashboardPage from './pages/dashboard/FinanceDashboardPage.vue';
import AuditLogsPage from './pages/AuditLogsPage.vue';

// Props for deep-linking from other apps (if needed in future)
const props = defineProps<{
  initialView?: string;
}>();

// Current view state
const currentView = ref(props.initialView || 'dashboard');

// Navigation tabs
const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'audit', label: 'Audit Trail', icon: '📋' }
];
</script>

<template>
  <div class="finance-app h-full flex flex-col">
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
      <FinanceDashboardPage v-if="currentView === 'dashboard'" />
      <AuditLogsPage v-if="currentView === 'audit'" />
    </div>
  </div>
</template>
