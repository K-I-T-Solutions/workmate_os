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
        <button v-if="canWrite" @click="showCreateDialog = true" class="kit-btn-primary">
          <Plus :size="18" />
          Neuer Mitarbeiter
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Abteilung</label>
        <select v-model="filters.department_id">
          <option value="">Alle Abteilungen</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">
            {{ dept.name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Rolle</label>
        <select v-model="filters.role_id">
          <option value="">Alle Rollen</option>
          <option v-for="role in roles" :key="role.id" :value="role.id">
            {{ role.name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.status">
          <option value="">Alle Status</option>
          <option value="active">Aktiv</option>
          <option value="inactive">Inaktiv</option>
          <option value="on_leave">Im Urlaub</option>
        </select>
      </div>

      <button
        v-if="hasActiveFilters"
        @click="clearFilters"
        class="btn-secondary btn-small"
      >
        <X :size="16" />
        Filter zurücksetzen
      </button>
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
                <CircleDot :size="10" />
                {{ getStatusLabel(emp.status) }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button
                  v-if="canEdit"
                  @click="editEmployee(emp)"
                  class="btn-icon"
                  title="Bearbeiten"
                >
                  <Pencil :size="16" />
                </button>
                <button
                  v-if="canWrite && emp.id !== currentUserId"
                  @click="toggleStatus(emp)"
                  :class="['btn-icon', emp.status === 'active' ? 'btn-warning' : 'btn-success']"
                  :title="emp.status === 'active' ? 'Deaktivieren' : 'Aktivieren'"
                >
                  <Power :size="16" />
                </button>
                <button
                  v-if="canWrite"
                  @click="showPasswordReset(emp)"
                  class="btn-icon"
                  title="Passwort zurücksetzen"
                >
                  <Key :size="16" />
                </button>
                <button
                  v-if="canDelete && emp.id !== currentUserId"
                  @click="deleteEmployee(emp)"
                  class="btn-icon btn-danger"
                  title="Löschen"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Loading State -->
      <table v-if="loading" class="data-table skeleton-table">
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
          <tr v-for="i in 8" :key="i">
            <td><div class="skeleton-box skeleton-code"></div></td>
            <td><div class="skeleton-box skeleton-name"></div></td>
            <td><div class="skeleton-box skeleton-email"></div></td>
            <td><div class="skeleton-box skeleton-dept"></div></td>
            <td><div class="skeleton-box skeleton-role"></div></td>
            <td><div class="skeleton-box skeleton-status"></div></td>
            <td>
              <div class="action-buttons">
                <div class="skeleton-box skeleton-btn"></div>
                <div class="skeleton-box skeleton-btn"></div>
                <div class="skeleton-box skeleton-btn"></div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="!loading && employees.length === 0" class="empty-state">
        <Users :size="48" />
        <p>Keine Mitarbeiter gefunden</p>
        <button v-if="canWrite" @click="showCreateDialog = true" class="kit-btn-primary">
          <Plus :size="18" />
          Ersten Mitarbeiter anlegen
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination">
      <button @click="page--" :disabled="page === 1" class="btn-secondary">
        Zurück
      </button>
      <span class="page-info">Seite {{ page }} von {{ totalPages }}</span>
      <button @click="page++" :disabled="page >= totalPages" class="btn-secondary">
        Weiter
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <EmployeeFormModal
      v-if="showCreateDialog || editingEmployee"
      :employee="editingEmployee"
      :departments="departments"
      :roles="roles"
      :employees="employees"
      @close="closeEmployeeModal"
      @save="handleSaveEmployee"
    />

    <!-- Password Reset Modal -->
    <PasswordResetModal
      v-if="resettingPasswordFor"
      :employee="resettingPasswordFor"
      @close="resettingPasswordFor = null"
      @reset="handlePasswordReset"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { Plus, Pencil, Trash2, Users, X, Power, Key, CircleDot } from 'lucide-vue-next';
import { useEmployees } from '@/composables/useEmployees';
import { usePermissions } from '@/composables/usePermissions';
import { useAuth } from '@/composables/useAuth';
import EmployeeFormModal from '../components/EmployeeFormModal.vue';
import PasswordResetModal from '../components/PasswordResetModal.vue';

// Composables
const {
  employees,
  departments,
  roles,
  loading,
  total,
  fetchEmployees,
  fetchDepartments,
  fetchRoles,
  createEmployee,
  updateEmployee,
  deleteEmployee: deleteEmployeeAPI,
  resetPassword,
  updateStatus,
} = useEmployees();

const { hasPermission } = usePermissions();
const { user } = useAuth();

// State
const page = ref(1);
const pageSize = ref(20);
const searchQuery = ref('');
const showCreateDialog = ref(false);
const editingEmployee = ref<any>(null);
const resettingPasswordFor = ref<any>(null);

const filters = ref({
  department_id: '',
  role_id: '',
  status: '',
});

// Computed
const totalPages = computed(() => Math.ceil(total.value / pageSize.value));

const hasActiveFilters = computed(() => {
  return filters.value.department_id || filters.value.role_id || filters.value.status;
});

const currentUserId = computed(() => user.value?.id);

// Permissions
const canEdit = computed(() => hasPermission('admin.employees.write') || hasPermission('admin.*'));
const canWrite = computed(() => hasPermission('admin.employees.write') || hasPermission('admin.*'));
const canDelete = computed(() => hasPermission('admin.employees.delete') || hasPermission('admin.*'));

// Helpers
function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    active: 'Aktiv',
    inactive: 'Inaktiv',
    on_leave: 'Im Urlaub',
  };
  return labels[status] || status;
}

// Actions
function editEmployee(emp: any) {
  editingEmployee.value = emp;
}

function showPasswordReset(emp: any) {
  resettingPasswordFor.value = emp;
}

function closeEmployeeModal() {
  showCreateDialog.value = false;
  editingEmployee.value = null;
}

async function handleSaveEmployee(data: any) {
  try {
    if (editingEmployee.value) {
      await updateEmployee(editingEmployee.value.id, data);
    } else {
      await createEmployee(data);
    }
    closeEmployeeModal();
    await loadData();
    alert('Mitarbeiter erfolgreich gespeichert');
  } catch (error: any) {
    console.error('Failed to save employee:', error);
    alert(error.response?.data?.detail || 'Fehler beim Speichern');
  }
}

async function handlePasswordReset(data: { newPassword: string; sendNotification: boolean }) {
  if (!resettingPasswordFor.value) return;

  try {
    await resetPassword(
      resettingPasswordFor.value.id,
      data.newPassword,
      data.sendNotification
    );
    resettingPasswordFor.value = null;
    alert('Passwort erfolgreich zurückgesetzt');
  } catch (error: any) {
    console.error('Failed to reset password:', error);
    alert(error.response?.data?.detail || 'Fehler beim Zurücksetzen des Passworts');
  }
}

async function toggleStatus(emp: any) {
  const newStatus = emp.status === 'active' ? 'inactive' : 'active';
  const action = newStatus === 'active' ? 'aktivieren' : 'deaktivieren';

  if (!confirm(`Mitarbeiter ${emp.first_name} ${emp.last_name} wirklich ${action}?`)) {
    return;
  }

  try {
    await updateStatus(emp.id, newStatus);
    await loadData();
    alert(`Mitarbeiter erfolgreich ${action === 'aktivieren' ? 'aktiviert' : 'deaktiviert'}`);
  } catch (error: any) {
    console.error('Failed to update status:', error);
    alert(error.response?.data?.detail || 'Fehler beim Ändern des Status');
  }
}

async function deleteEmployee(emp: any) {
  if (!confirm(`Mitarbeiter ${emp.first_name} ${emp.last_name} wirklich löschen?`)) {
    return;
  }

  try {
    await deleteEmployeeAPI(emp.id);
    await loadData();
    alert('Mitarbeiter erfolgreich gelöscht');
  } catch (error: any) {
    console.error('Failed to delete employee:', error);
    alert(error.response?.data?.detail || 'Fehler beim Löschen');
  }
}

function clearFilters() {
  filters.value = {
    department_id: '',
    role_id: '',
    status: '',
  };
}

async function loadData() {
  await fetchEmployees({
    skip: (page.value - 1) * pageSize.value,
    limit: pageSize.value,
    search: searchQuery.value,
    ...filters.value,
  });
}

// Watch for changes
watch([page, searchQuery, filters], () => {
  loadData();
}, { deep: true });

// Initial fetch
onMounted(async () => {
  await Promise.all([
    loadData(),
    fetchDepartments(),
    fetchRoles(),
  ]);
});
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

/* Filters */
.filters-bar {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 180px;
}

.filter-group label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.filter-group select {
  padding: 0.5rem;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  cursor: pointer;
}

.filter-group select:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Buttons */
.btn-primary,
.btn-secondary {
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

.btn-small {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.btn-icon.btn-danger:hover {
  background: #fee2e2;
  color: #dc2626;
}

.btn-icon.btn-warning:hover {
  background: #fef3c7;
  color: #d97706;
}

.btn-icon.btn-success:hover {
  background: #d1fae5;
  color: #059669;
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
  z-index: 10;
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
  font-family: 'Courier New', monospace;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.on_leave {
  background: #fff3cd;
  color: #856404;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

/* States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem 2rem;
  color: var(--color-text-secondary);
}

.empty-state svg {
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

  .header-left,
  .header-right {
    width: 100%;
  }

  .header-right {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
    min-width: auto;
  }

  .filters-bar {
    flex-direction: column;
  }

  .filter-group {
    min-width: auto;
  }
}

/* Skeleton Loading */
.skeleton-table {
  pointer-events: none;
}

.skeleton-box {
  height: 16px;
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 0%,
    var(--color-bg-hover) 50%,
    var(--color-bg-tertiary) 100%
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton-code {
  width: 80px;
}

.skeleton-name {
  width: 140px;
}

.skeleton-email {
  width: 180px;
}

.skeleton-dept {
  width: 100px;
}

.skeleton-role {
  width: 90px;
}

.skeleton-status {
  width: 70px;
  height: 24px;
  border-radius: 12px;
}

.skeleton-btn {
  width: 28px;
  height: 28px;
  border-radius: 4px;
}

.skeleton-table .action-buttons {
  gap: 0.5rem;
}
</style>
