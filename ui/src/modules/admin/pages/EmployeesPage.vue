<template>
  <div class="employees-page">
    <!-- Header with Actions -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Mitarbeiter</h2>
        <span class="count-badge">{{ total }} Mitarbeiter</span>
      </div>
      <div class="header-right">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Suchen..."
          class="search-input"
        />
        <button @click="showCreateDialog = true" class="btn-primary">
          <Plus :size="18" />
          Neuer Mitarbeiter
        </button>
      </div>
    </div>

    <!-- Employees Table -->
    <div class="table-container">
      <table v-if="!loading && employees.length > 0" class="data-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Email</th>
            <th>Abteilung</th>
            <th>Rolle</th>
            <th>Status</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="emp in employees" :key="emp.id">
            <td><code>{{ emp.employee_code }}</code></td>
            <td>{{ emp.first_name }} {{ emp.last_name }}</td>
            <td>{{ emp.email }}</td>
            <td>{{ emp.department?.name || '-' }}</td>
            <td>{{ emp.role?.name || '-' }}</td>
            <td>
              <span :class="['status-badge', emp.status]">
                {{ emp.status }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button @click="editEmployee(emp)" class="btn-icon" title="Bearbeiten">
                  <Pencil :size="16" />
                </button>
                <button @click="deleteEmployee(emp)" class="btn-icon btn-danger" title="Löschen">
                  <Trash2 :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        Lade Mitarbeiter...
      </div>

      <!-- Empty State -->
      <div v-if="!loading && employees.length === 0" class="empty-state">
        <Users :size="48" />
        <p>Keine Mitarbeiter gefunden</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination">
      <button
        @click="page--"
        :disabled="page === 1"
        class="btn-secondary"
      >
        Zurück
      </button>
      <span class="page-info">Seite {{ page }} von {{ totalPages }}</span>
      <button
        @click="page++"
        :disabled="page >= totalPages"
        class="btn-secondary"
      >
        Weiter
      </button>
    </div>

    <!-- Create/Edit Dialog (Placeholder) -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <h3>Neuer Mitarbeiter</h3>
        <p>Formular kommt noch...</p>
        <button @click="showCreateDialog = false" class="btn-secondary">Schließen</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Plus, Pencil, Trash2, Users } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

// State
const employees = ref<any[]>([]);
const loading = ref(false);
const total = ref(0);
const page = ref(1);
const pageSize = ref(20);
const searchQuery = ref('');
const showCreateDialog = ref(false);

// Computed
const totalPages = computed(() => Math.ceil(total.value / pageSize.value));

// Fetch employees
async function fetchEmployees() {
  loading.value = true;
  try {
    const skip = (page.value - 1) * pageSize.value;
    const params: any = { skip, limit: pageSize.value };

    if (searchQuery.value) {
      params.search = searchQuery.value;
    }

    const response = await apiClient.get('/api/employees', { params });
    employees.value = response.data.employees;
    total.value = response.data.total;
  } catch (error) {
    console.error('Failed to fetch employees:', error);
  } finally {
    loading.value = false;
  }
}

// Actions
function editEmployee(emp: any) {
  alert(`Edit ${emp.first_name} ${emp.last_name} - TODO`);
}

async function deleteEmployee(emp: any) {
  if (!confirm(`Mitarbeiter ${emp.first_name} ${emp.last_name} wirklich löschen?`)) {
    return;
  }

  try {
    await apiClient.delete(`/api/employees/${emp.id}`);
    await fetchEmployees();
  } catch (error) {
    console.error('Failed to delete employee:', error);
    alert('Fehler beim Löschen');
  }
}

// Watch for changes
watch([page, searchQuery], () => {
  fetchEmployees();
});

// Initial fetch
fetchEmployees();
</script>

<style scoped>
.employees-page {
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

.header-right {
  display: flex;
  gap: 0.75rem;
}

.search-input {
  padding: 0.5rem 1rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  min-width: 250px;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
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

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* Table */
.table-container {
  flex: 1;
  overflow: auto;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  position: sticky;
  top: 0;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border-light);
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.data-table tr:hover {
  background: var(--color-bg-hover);
}

.data-table code {
  padding: 0.125rem 0.5rem;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

/* States */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--color-text-secondary);
}

.empty-state svg {
  margin-bottom: 1rem;
  opacity: 0.3;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.page-info {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
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
  .data-table {
    min-width: 800px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-left, .header-right {
    width: 100%;
  }

  .header-right {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
    min-width: auto;
  }

  .data-table th,
  .data-table td {
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
  }

  .data-table th {
    font-size: 0.6875rem;
  }

  .pagination {
    flex-wrap: wrap;
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

  .search-input {
    font-size: 0.8125rem;
    padding: 0.4rem 0.75rem;
  }

  .btn-primary, .btn-secondary {
    padding: 0.4rem 0.875rem;
    font-size: 0.8125rem;
  }

  .dialog {
    padding: 1.5rem;
  }
}
</style>
