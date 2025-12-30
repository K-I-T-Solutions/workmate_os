<template>
  <div class="departments-page">
    <!-- Header with Actions -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Abteilungen</h2>
        <span class="count-badge">{{ departments.length }} Abteilungen</span>
      </div>
      <button @click="showCreateDialog = true" class="btn-primary">
        <Plus :size="18" />
        Neue Abteilung
      </button>
    </div>

    <!-- Departments Grid -->
    <div class="departments-grid">
      <div v-for="dept in departments" :key="dept.id" class="department-card">
        <div class="card-header">
          <div class="dept-info">
            <Building2 :size="20" />
            <div>
              <h3 class="dept-name">{{ dept.name }}</h3>
              <code v-if="dept.code" class="dept-code">{{ dept.code }}</code>
            </div>
          </div>
          <div class="card-actions">
            <button @click="editDepartment(dept)" class="btn-icon" title="Bearbeiten">
              <Pencil :size="16" />
            </button>
            <button @click="deleteDepartment(dept)" class="btn-icon btn-danger" title="Löschen">
              <Trash2 :size="16" />
            </button>
          </div>
        </div>

        <p v-if="dept.description" class="dept-description">
          {{ dept.description }}
        </p>

        <div v-if="dept.manager" class="dept-manager">
          <Users :size="14" />
          <span>Leiter: {{ dept.manager.first_name }} {{ dept.manager.last_name }}</span>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && departments.length === 0" class="empty-state">
        <Building2 :size="48" />
        <p>Keine Abteilungen vorhanden</p>
        <button @click="showCreateDialog = true" class="btn-primary">
          <Plus :size="18" />
          Erste Abteilung erstellen
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      Lade Abteilungen...
    </div>

    <!-- Create/Edit Dialog (Placeholder) -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <h3>Neue Abteilung</h3>
        <p>Formular kommt noch...</p>
        <button @click="showCreateDialog = false" class="btn-secondary">Schließen</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus, Pencil, Trash2, Building2, Users } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

// State
const departments = ref<any[]>([]);
const loading = ref(false);
const showCreateDialog = ref(false);

// Fetch departments
async function fetchDepartments() {
  loading.value = true;
  try {
    const response = await apiClient.get('/api/departments');
    departments.value = response.data;
  } catch (error) {
    console.error('Failed to fetch departments:', error);
  } finally {
    loading.value = false;
  }
}

// Actions
function editDepartment(dept: any) {
  alert(`Edit ${dept.name} - TODO`);
}

async function deleteDepartment(dept: any) {
  if (!confirm(`Abteilung "${dept.name}" wirklich löschen?`)) {
    return;
  }

  try {
    await apiClient.delete(`/api/departments/${dept.id}`);
    await fetchDepartments();
  } catch (error) {
    console.error('Failed to delete department:', error);
    alert('Fehler beim Löschen');
  }
}

// Initial fetch
onMounted(() => {
  fetchDepartments();
});
</script>

<style scoped>
.departments-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.count-badge {
  padding: 0.25rem 0.75rem;
  background: var(--color-bg-tertiary);
  border-radius: 12px;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

/* Buttons */
.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
}

.btn-secondary:hover {
  background: var(--color-bg-hover);
}

.btn-icon {
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.btn-icon.btn-danger:hover {
  background: #fee;
  color: #c00;
}

/* Grid */
.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
  overflow: auto;
}

.department-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.department-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.dept-info {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.dept-info svg {
  color: var(--color-primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.dept-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 0.25rem 0;
}

.dept-code {
  padding: 0.125rem 0.5rem;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.card-actions {
  display: flex;
  gap: 0.25rem;
}

.dept-description {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 0 1rem 0;
}

.dept-manager {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border-light);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.dept-manager svg {
  color: var(--color-text-tertiary);
}

/* States */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--color-text-secondary);
  text-align: center;
}

.empty-state svg {
  margin-bottom: 1rem;
  opacity: 0.3;
}

.empty-state p {
  margin-bottom: 1rem;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: var(--color-bg-primary);
  padding: 2rem;
  border-radius: 8px;
  min-width: 400px;
  max-width: 600px;
}

.dialog h3 {
  margin-top: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .departments-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-left {
    width: 100%;
  }

  .departments-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .department-card {
    padding: 1rem;
  }

  .dept-name {
    font-size: 0.9375rem;
  }

  .dept-description {
    font-size: 0.8125rem;
  }

  .dialog {
    min-width: auto;
    max-width: 90vw;
    margin: 1rem;
  }
}

@media (max-width: 480px) {
  .count-badge {
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
  }

  .btn-primary {
    padding: 0.4rem 0.875rem;
    font-size: 0.8125rem;
  }

  .department-card {
    padding: 0.875rem;
  }

  .card-header {
    margin-bottom: 0.75rem;
  }

  .dialog {
    padding: 1.5rem;
  }
}
</style>
