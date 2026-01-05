<template>
  <div class="roles-page">
    <!-- Header with Actions -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Rollen & Berechtigungen</h2>
        <span class="count-badge">{{ roles.length }} Rollen</span>
      </div>
      <button @click="showCreateDialog = true" class="btn-primary">
        <Plus :size="18" />
        Neue Rolle
      </button>
    </div>

    <!-- Roles Grid -->
    <div class="roles-grid">
      <div v-for="role in roles" :key="role.id" class="role-card">
        <div class="card-header">
          <div class="role-info">
            <Shield :size="20" :class="['role-icon', getRoleColorClass(role.name)]" />
            <div>
              <h3 class="role-name">{{ role.name }}</h3>
              <p v-if="role.description" class="role-description">
                {{ role.description }}
              </p>
            </div>
          </div>
          <div class="card-actions">
            <button @click="editRole(role)" class="btn-icon" title="Bearbeiten">
              <Pencil :size="16" />
            </button>
            <button
              v-if="!isSystemRole(role.name)"
              @click="deleteRole(role)"
              class="btn-icon btn-danger"
              title="Löschen"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>

        <!-- Permissions -->
        <div class="permissions-section">
          <div class="section-title">
            <Key :size="14" />
            <span>Berechtigungen</span>
          </div>

          <div v-if="role.permissions_json && role.permissions_json.length > 0" class="permissions-list">
            <span v-for="(perm, idx) in role.permissions_json" :key="idx" class="permission-badge">
              {{ perm }}
            </span>
          </div>
          <div v-else class="no-permissions">
            Keine Berechtigungen zugewiesen
          </div>
        </div>

        <!-- Zitadel ID -->
        <div v-if="role.keycloak_id" class="zitadel-id">
          <span class="id-label">Zitadel Role ID:</span>
          <code class="id-value">{{ role.keycloak_id }}</code>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && roles.length === 0" class="empty-state">
        <Shield :size="48" />
        <p>Keine Rollen vorhanden</p>
        <button @click="showCreateDialog = true" class="btn-primary">
          <Plus :size="18" />
          Erste Rolle erstellen
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      Lade Rollen...
    </div>

    <!-- Create/Edit Dialog (Placeholder) -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <h3>Neue Rolle</h3>
        <p>Formular kommt noch...</p>
        <button @click="showCreateDialog = false" class="btn-secondary">Schließen</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus, Pencil, Trash2, Shield, Key } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

// State
const roles = ref<any[]>([]);
const loading = ref(false);
const showCreateDialog = ref(false);

// System roles that cannot be deleted
const systemRoles = ['Admin', 'CEO', 'Manager', 'Employee'];

// Fetch roles
async function fetchRoles() {
  loading.value = true;
  try {
    const response = await apiClient.get('/api/roles');
    roles.value = response.data;
  } catch (error) {
    console.error('Failed to fetch roles:', error);
  } finally {
    loading.value = false;
  }
}

// Helpers
function isSystemRole(roleName: string): boolean {
  return systemRoles.includes(roleName);
}

function getRoleColorClass(roleName: string): string {
  const colorMap: Record<string, string> = {
    'Admin': 'role-admin',
    'CEO': 'role-ceo',
    'Manager': 'role-manager',
    'Employee': 'role-employee',
  };
  return colorMap[roleName] || 'role-custom';
}

// Actions
function editRole(role: any) {
  alert(`Edit ${role.name} - TODO`);
}

async function deleteRole(role: any) {
  if (isSystemRole(role.name)) {
    alert('Systemrollen können nicht gelöscht werden!');
    return;
  }

  if (!confirm(`Rolle "${role.name}" wirklich löschen?`)) {
    return;
  }

  try {
    await apiClient.delete(`/api/roles/${role.id}`);
    await fetchRoles();
  } catch (error) {
    console.error('Failed to delete role:', error);
    alert('Fehler beim Löschen');
  }
}

// Initial fetch
onMounted(() => {
  fetchRoles();
});
</script>

<style scoped>
.roles-page {
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
.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1rem;
  overflow: auto;
}

.role-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.role-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.role-info {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  flex: 1;
}

.role-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.role-icon.role-admin { color: #dc3545; }
.role-icon.role-ceo { color: #6f42c1; }
.role-icon.role-manager { color: #007bff; }
.role-icon.role-employee { color: #28a745; }
.role-icon.role-custom { color: var(--color-primary); }

.role-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 0.25rem 0;
}

.role-description {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.5;
}

.card-actions {
  display: flex;
  gap: 0.25rem;
}

/* Permissions Section */
.permissions-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border-light);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  margin-bottom: 0.75rem;
}

.section-title svg {
  color: var(--color-text-tertiary);
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.permission-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  color: var(--color-text-primary);
}

.no-permissions {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
  font-style: italic;
}

/* Zitadel ID */
.zitadel-id {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border-light);
  font-size: 0.75rem;
}

.id-label {
  color: var(--color-text-secondary);
  margin-right: 0.5rem;
}

.id-value {
  padding: 0.125rem 0.5rem;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
  color: var(--color-primary);
  font-family: 'Courier New', monospace;
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
  .roles-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
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

  .roles-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .role-card {
    padding: 1rem;
  }

  .role-name {
    font-size: 1rem;
  }

  .permissions-list {
    gap: 0.375rem;
  }

  .permission-badge {
    font-size: 0.6875rem;
    padding: 0.2rem 0.625rem;
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

  .role-card {
    padding: 0.875rem;
  }

  .role-name {
    font-size: 0.9375rem;
  }

  .dialog {
    padding: 1.5rem;
  }
}
</style>
