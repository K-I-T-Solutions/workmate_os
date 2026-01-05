<template>
  <div class="audit-log-page">
    <!-- Header with Filters -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Audit-Log</h2>
        <span class="count-badge">{{ total }} Einträge</span>
      </div>
      <button @click="refreshLogs" class="btn-secondary" :disabled="loading">
        <RefreshCw :size="18" :class="{ spin: loading }" />
        Aktualisieren
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Benutzer</label>
        <select v-model="filters.user_id">
          <option value="">Alle Benutzer</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.first_name }} {{ user.last_name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Aktion</label>
        <select v-model="filters.action">
          <option value="">Alle Aktionen</option>
          <option value="create">Erstellt</option>
          <option value="update">Geändert</option>
          <option value="delete">Gelöscht</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Ressource</label>
        <select v-model="filters.resource_type">
          <option value="">Alle Ressourcen</option>
          <option value="employee">Mitarbeiter</option>
          <option value="department">Abteilung</option>
          <option value="role">Rolle</option>
          <option value="customer">Kunde</option>
          <option value="invoice">Rechnung</option>
          <option value="project">Projekt</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Von Datum</label>
        <input v-model="filters.date_from" type="date" />
      </div>

      <div class="filter-group">
        <label>Bis Datum</label>
        <input v-model="filters.date_to" type="date" />
      </div>

      <button @click="clearFilters" class="btn-secondary">
        <X :size="18" />
        Filter zurücksetzen
      </button>
    </div>

    <!-- Audit Log Table -->
    <div class="table-container">
      <table v-if="!loading && logs.length > 0" class="audit-table">
        <thead>
          <tr>
            <th>Zeitstempel</th>
            <th>Benutzer</th>
            <th>Aktion</th>
            <th>Ressource</th>
            <th>Details</th>
            <th>IP-Adresse</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" @click="showDetails(log)" class="clickable">
            <td>
              <div class="timestamp">
                <Calendar :size="14" />
                {{ formatDateTime(log.timestamp) }}
              </div>
            </td>
            <td>
              <div class="user-cell">
                <User :size="14" />
                {{ log.user_name }}
              </div>
            </td>
            <td>
              <span :class="['action-badge', log.action]">
                <component :is="getActionIcon(log.action)" :size="14" />
                {{ getActionLabel(log.action) }}
              </span>
            </td>
            <td>
              <div class="resource-cell">
                <code>{{ log.resource_type }}</code>
                <span v-if="log.resource_name" class="resource-name">{{ log.resource_name }}</span>
              </div>
            </td>
            <td>
              <span class="details-preview">{{ log.details || '-' }}</span>
            </td>
            <td>
              <code class="ip-address">{{ log.ip_address || '-' }}</code>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <RefreshCw :size="32" class="spin" />
        <p>Lade Audit-Logs...</p>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && logs.length === 0" class="empty-state">
        <FileText :size="48" />
        <p>Keine Audit-Logs gefunden</p>
        <p class="empty-hint">Versuche die Filter anzupassen</p>
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

    <!-- Details Dialog -->
    <div v-if="selectedLog" class="dialog-overlay" @click.self="selectedLog = null">
      <div class="dialog">
        <div class="dialog-header">
          <h3>Audit-Log Details</h3>
          <button @click="selectedLog = null" class="btn-icon">
            <X :size="20" />
          </button>
        </div>
        <div class="dialog-body">
          <div class="detail-row">
            <span class="detail-label">Zeitstempel:</span>
            <span class="detail-value">{{ formatDateTime(selectedLog.timestamp) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Benutzer:</span>
            <span class="detail-value">{{ selectedLog.user_name }} ({{ selectedLog.user_email }})</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Aktion:</span>
            <span class="detail-value">{{ getActionLabel(selectedLog.action) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Ressource:</span>
            <span class="detail-value">{{ selectedLog.resource_type }} - {{ selectedLog.resource_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">IP-Adresse:</span>
            <span class="detail-value">{{ selectedLog.ip_address }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Details:</span>
            <pre class="detail-json">{{ JSON.stringify(selectedLog.changes, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { RefreshCw, X, Calendar, User, FileText, Plus, Pencil, Trash2, LogIn, LogOut } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

// State
const logs = ref<any[]>([]);
const users = ref<any[]>([]);
const loading = ref(false);
const total = ref(0);
const page = ref(1);
const pageSize = ref(50);
const selectedLog = ref<any>(null);

const filters = ref({
  user_id: '',
  action: '',
  resource_type: '',
  date_from: '',
  date_to: '',
});

// Computed
const totalPages = computed(() => Math.ceil(total.value / pageSize.value));

// Fetch audit logs
async function fetchLogs() {
  loading.value = true;
  try {
    const skip = (page.value - 1) * pageSize.value;
    const response = await apiClient.get('/api/audit-logs', {
      params: { ...filters.value, skip, limit: pageSize.value }
    });
    logs.value = response.data.items || [];
    total.value = response.data.total || 0;
  } catch (error) {
    console.error('Failed to fetch audit logs:', error);
    logs.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

// Fetch users for filter
async function fetchUsers() {
  try {
    const response = await apiClient.get('/api/employees', { params: { limit: 1000 } });
    users.value = response.data.employees || [];
  } catch (error) {
    console.error('Failed to fetch users:', error);
  }
}


// Helpers
function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

function getActionLabel(action: string): string {
  const labels: Record<string, string> = {
    create: 'Erstellt',
    update: 'Geändert',
    delete: 'Gelöscht',
    login: 'Login',
    logout: 'Logout',
  };
  return labels[action] || action;
}

function getActionIcon(action: string) {
  const icons: Record<string, any> = {
    create: Plus,
    update: Pencil,
    delete: Trash2,
    login: LogIn,
    logout: LogOut,
  };
  return icons[action] || FileText;
}

function showDetails(log: any) {
  selectedLog.value = log;
}

function refreshLogs() {
  fetchLogs();
}

function clearFilters() {
  filters.value = {
    user_id: '',
    action: '',
    resource_type: '',
    date_from: '',
    date_to: '',
  };
}

// Watch for changes
watch([page, filters], () => {
  fetchLogs();
}, { deep: true });

// Initial fetch
onMounted(() => {
  fetchUsers();
  fetchLogs();
});
</script>

<style scoped>
.audit-log-page {
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
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover:not(:disabled) {
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Filters */
.filters-bar {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 150px;
}

.filter-group label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem 0.75rem;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Table */
.table-container {
  flex: 1;
  overflow: auto;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
}

.audit-table th {
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

.audit-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.audit-table tr.clickable {
  cursor: pointer;
}

.audit-table tr.clickable:hover {
  background: var(--color-bg-hover);
}

.timestamp, .user-cell, .resource-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.timestamp svg, .user-cell svg {
  color: var(--color-text-tertiary);
}

.resource-cell {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}

.resource-name {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.action-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.action-badge.create {
  background: #d4edda;
  color: #155724;
}

.action-badge.update {
  background: #d1ecf1;
  color: #0c5460;
}

.action-badge.delete {
  background: #f8d7da;
  color: #721c24;
}

.action-badge.login {
  background: #d6d8db;
  color: #383d41;
}

.action-badge.logout {
  background: #d6d8db;
  color: #383d41;
}

code {
  padding: 0.125rem 0.5rem;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
}

.ip-address {
  color: var(--color-text-secondary);
}

.details-preview {
  display: block;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
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

.empty-hint {
  font-size: 0.875rem;
  margin-top: 0.5rem;
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
  border-radius: 8px;
  min-width: 500px;
  max-width: 700px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border-light);
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.dialog-body {
  padding: 1.5rem;
  overflow: auto;
}

.detail-row {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-border-light);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 120px;
}

.detail-value {
  color: var(--color-text-primary);
}

.detail-json {
  background: var(--color-bg-tertiary);
  padding: 1rem;
  border-radius: 6px;
  font-size: 0.75rem;
  overflow: auto;
  max-height: 300px;
}

/* Responsive */
@media (max-width: 1024px) {
  .audit-table {
    min-width: 900px;
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

  .btn-secondary {
    width: 100%;
    justify-content: center;
  }

  .filters-bar {
    padding: 0.875rem;
    gap: 0.75rem;
  }

  .filter-group {
    min-width: 100%;
    flex: 1 1 100%;
  }

  .filter-group label {
    font-size: 0.6875rem;
  }

  .filter-group select,
  .filter-group input {
    padding: 0.4rem 0.625rem;
    font-size: 0.8125rem;
  }

  .audit-table {
    min-width: 800px;
  }

  .audit-table th,
  .audit-table td {
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
  }

  .audit-table th {
    font-size: 0.6875rem;
  }

  .action-badge {
    font-size: 0.6875rem;
    padding: 0.2rem 0.625rem;
  }

  .details-preview {
    max-width: 200px;
    font-size: 0.75rem;
  }

  .pagination {
    flex-wrap: wrap;
  }

  .dialog {
    min-width: auto;
    max-width: 90vw;
    margin: 1rem;
  }

  .dialog-header {
    padding: 1rem;
  }

  .dialog-header h3 {
    font-size: 1rem;
  }

  .dialog-body {
    padding: 1rem;
  }

  .detail-row {
    flex-direction: column;
    gap: 0.375rem;
    padding: 0.625rem 0;
  }

  .detail-label {
    min-width: auto;
    font-size: 0.8125rem;
  }

  .detail-value {
    font-size: 0.8125rem;
  }

  .detail-json {
    font-size: 0.6875rem;
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .count-badge {
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
  }

  .page-title {
    font-size: 1.125rem;
  }

  .btn-secondary {
    padding: 0.4rem 0.875rem;
    font-size: 0.8125rem;
  }

  .filters-bar {
    padding: 0.75rem;
  }

  .filter-group select,
  .filter-group input {
    font-size: 0.75rem;
  }

  .action-badge {
    font-size: 0.625rem;
    padding: 0.2rem 0.5rem;
    gap: 0.25rem;
  }

  .action-badge svg {
    display: none;
  }

  .details-preview {
    max-width: 150px;
  }

  code {
    font-size: 0.6875rem;
    padding: 0.1rem 0.375rem;
  }

  .dialog {
    margin: 0.5rem;
  }

  .dialog-header {
    padding: 0.875rem;
  }

  .dialog-body {
    padding: 0.875rem;
  }

  .detail-json {
    max-height: 200px;
  }
}
</style>
