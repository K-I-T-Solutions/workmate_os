<template>
  <div class="admin-app">
    <!-- Header -->
    <div class="admin-header">
      <h1 class="admin-title">System Administration</h1>
      <p class="admin-subtitle">Verwaltung von Mitarbeitern, Abteilungen und Rollen</p>
    </div>

    <!-- Tabs -->
    <div class="admin-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
      >
        <component :is="tab.icon" :size="18" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- Tab Content -->
    <div class="admin-content">
      <EmployeesPage v-if="activeTab === 'employees'" />
      <DepartmentsPage v-if="activeTab === 'departments'" />
      <RolesPage v-if="activeTab === 'roles'" />
      <SystemSettingsPage v-if="activeTab === 'settings'" />
      <AuditLogPage v-if="activeTab === 'audit'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Users, Building2, Shield, Settings, FileText } from 'lucide-vue-next';
import EmployeesPage from './pages/EmployeesPage.vue';
import DepartmentsPage from './pages/DepartmentsPage.vue';
import RolesPage from './pages/RolesPage.vue';
import SystemSettingsPage from './pages/SystemSettingsPage.vue';
import AuditLogPage from './pages/AuditLogPage.vue';

const activeTab = ref('employees');

const tabs = [
  { id: 'employees', label: 'Mitarbeiter', icon: Users },
  { id: 'departments', label: 'Abteilungen', icon: Building2 },
  { id: 'roles', label: 'Rollen & Berechtigungen', icon: Shield },
  { id: 'settings', label: 'System-Einstellungen', icon: Settings },
  { id: 'audit', label: 'Audit-Log', icon: FileText },
];
</script>

<style scoped>
.admin-app {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg-primary);
}

/* Header */
.admin-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-secondary);
}

.admin-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 0.25rem 0;
}

.admin-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Tabs */
.admin-tabs {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 2rem 0 2rem;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-light);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-button:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-hover);
}

.tab-button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

/* Content */
.admin-content {
  flex: 1;
  overflow: auto;
  padding: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-header {
    padding: 1rem;
  }

  .admin-title {
    font-size: 1.25rem;
  }

  .admin-subtitle {
    font-size: 0.8125rem;
  }

  .admin-tabs {
    padding: 0.75rem 1rem 0 1rem;
    gap: 0.25rem;
  }

  .tab-button {
    padding: 0.625rem 0.875rem;
    font-size: 0.8125rem;
  }

  .tab-button span {
    display: none;
  }

  .admin-content {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .admin-header {
    padding: 0.75rem;
  }

  .admin-title {
    font-size: 1.125rem;
  }

  .admin-content {
    padding: 0.75rem;
  }
}
</style>
