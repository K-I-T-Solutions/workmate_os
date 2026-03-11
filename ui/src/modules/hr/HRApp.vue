<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import HRDashboardPage from './pages/HRDashboardPage.vue';
import LeaveManagementPage from './pages/LeaveManagementPage.vue';
import LeaveApprovalsPage from './pages/LeaveApprovalsPage.vue';
import EmployeeListPage from './pages/EmployeeListPage.vue';
import MyLeavePage from './pages/MyLeavePage.vue';
import EmployeeDetailPage from './pages/EmployeeDetailPage.vue';
import LeaveDetailPage from './pages/LeaveDetailPage.vue';

const route = useRoute();
const router = useRouter();

const currentView = computed(() => (route.meta.view as string) || 'my-leave');
const currentEmployeeId = computed(() => route.params.id as string | undefined);
const currentRequestId = computed(() => route.params.id as string | undefined);

const tabs = [
  { id: 'my-leave',   label: 'Mein Urlaub',        icon: '🏖️', path: '/app/hr/my-leave' },
  { id: 'dashboard',  label: 'Dashboard',            icon: '📊', path: '/app/hr/dashboard' },
  { id: 'leave',      label: 'Urlaubsverwaltung',    icon: '🌴', path: '/app/hr/leave/requests' },
  { id: 'approvals',  label: 'Genehmigungen',        icon: '✅', path: '/app/hr/leave/approvals' },
  { id: 'employees',  label: 'Mitarbeiter',           icon: '👥', path: '/app/hr/employees' },
];

function navigateTo(path: string) {
  router.push(path);
}
</script>

<template>
  <div class="hr-app h-full flex flex-col">
    <!-- Navigation Tabs -->
    <div class="border-b border-white/10 bg-white/5">
      <div class="flex gap-2 p-4 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="navigateTo(tab.path)"
          :class="[
            'px-4 py-2 rounded-lg transition-colors whitespace-nowrap flex-shrink-0',
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
      <MyLeavePage v-if="currentView === 'my-leave'" />
      <HRDashboardPage v-if="currentView === 'dashboard'" />
      <LeaveManagementPage v-if="currentView === 'leave'" />
      <LeaveApprovalsPage v-if="currentView === 'approvals'" />
      <EmployeeListPage v-if="currentView === 'employees'" />
      <EmployeeDetailPage v-if="currentView === 'employee-detail' && currentEmployeeId" :employee-id="currentEmployeeId" />
      <LeaveDetailPage v-if="currentView === 'leave-detail' && currentRequestId" :request-id="currentRequestId" />
    </div>
  </div>
</template>

<style scoped>
.hr-app {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}
</style>
