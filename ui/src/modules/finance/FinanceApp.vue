<script setup lang="ts">
import { ref } from 'vue';
import FinanceDashboardPage from './pages/dashboard/FinanceDashboardPage.vue';
import AuditLogsPage from './pages/AuditLogsPage.vue';
import BankAccountsPage from './pages/banking/BankAccountsPage.vue';
import BankTransactionsPage from './pages/banking/BankTransactionsPage.vue';

const props = defineProps<{
  initialView?: string;
}>();

const currentView = ref(props.initialView || 'dashboard');

const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'bank-accounts', label: 'Bank-Konten', icon: '🏦' },
  { id: 'transactions', label: 'Transaktionen', icon: '💳' },
  { id: 'audit', label: 'Audit Trail', icon: '📋' },
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
      <BankAccountsPage v-if="currentView === 'bank-accounts'" />
      <BankTransactionsPage v-if="currentView === 'transactions'" />
      <AuditLogsPage v-if="currentView === 'audit'" />
    </div>
  </div>
</template>
