<template>
  <div class="roles-page">
    <!-- Header with Actions -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Rollen & Berechtigungen</h2>
        <span class="count-badge">{{ roles.length }} Rollen</span>
      </div>
      <button @click="openCreate" class="kit-btn-primary">
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
            <button @click="openEdit(role)" class="btn-icon" title="Bearbeiten">
              <Pencil :size="16" />
            </button>
            <button
              v-if="!isSystemRole(role.name)"
              @click="handleDelete(role)"
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

        <!-- Keycloak ID -->
        <div v-if="role.keycloak_id" class="keycloak-id">
          <span class="id-label">Keycloak Role ID:</span>
          <code class="id-value">{{ role.keycloak_id }}</code>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && roles.length === 0" class="empty-state">
        <Shield :size="48" />
        <p>Keine Rollen vorhanden</p>
        <button @click="openCreate" class="kit-btn-primary">
          <Plus :size="18" />
          Erste Rolle erstellen
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      Lade Rollen...
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="kit-card p-6 text-center">
      <p class="text-red-400 text-sm">{{ error }}</p>
      <button class="kit-btn-secondary mt-3 text-xs" @click="fetchRoles()">Erneut versuchen</button>
    </div>

    <!-- Create / Edit Modal -->
    <div
      v-if="showModal"
      class="modal-overlay"
      @click.self="closeModal"
      @keydown.escape="closeModal"
      tabindex="-1"
    >
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ editingRole ? 'Rolle bearbeiten' : 'Neue Rolle erstellen' }}</h3>
          <button class="btn-icon" @click="closeModal" title="Schließen">
            <X :size="18" />
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-form">
          <!-- Name -->
          <div class="field">
            <label class="kit-label" for="role-name">Name <span class="required">*</span></label>
            <input
              id="role-name"
              v-model="form.name"
              type="text"
              class="kit-input"
              :class="{ 'input-error': formErrors.name }"
              placeholder="z. B. Projektleiter"
              required
            />
            <p v-if="formErrors.name" class="field-error">{{ formErrors.name }}</p>
          </div>

          <!-- Description -->
          <div class="field">
            <label class="kit-label" for="role-desc">Beschreibung</label>
            <textarea
              id="role-desc"
              v-model="form.description"
              class="kit-input"
              rows="3"
              placeholder="Kurze Beschreibung der Rolle..."
            ></textarea>
          </div>

          <!-- Permissions -->
          <div class="field">
            <label class="kit-label" for="role-perms">
              Berechtigungen
              <span class="field-hint">— kommagetrennt, z.&thinsp;B. <code>invoices.view, projects.*</code></span>
            </label>
            <textarea
              id="role-perms"
              v-model="permissionsRaw"
              class="kit-input font-mono"
              rows="4"
              placeholder="invoices.view, projects.write, admin.*"
            ></textarea>
            <!-- Live preview -->
            <div v-if="parsedPermissions.length > 0" class="perm-preview">
              <span
                v-for="(p, i) in parsedPermissions"
                :key="i"
                class="permission-badge"
              >{{ p }}</span>
            </div>
          </div>

          <!-- Form error -->
          <p v-if="submitError" class="submit-error">{{ submitError }}</p>

          <div class="modal-actions">
            <button type="button" class="kit-btn-secondary" @click="closeModal">
              Abbrechen
            </button>
            <button type="submit" class="kit-btn-primary" :disabled="saving">
              <span v-if="saving">Speichere...</span>
              <span v-else>{{ editingRole ? 'Speichern' : 'Erstellen' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Plus, Pencil, Trash2, Shield, Key, X } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';
import { useToast } from '@/composables/useToast';

const toast = useToast();

// ─── Types ───────────────────────────────────────────────────────────────────

interface Role {
  id: string;
  name: string;
  description?: string | null;
  permissions_json?: string[];
  keycloak_id?: string | null;
}

interface RoleForm {
  name: string;
  description: string;
}

// ─── State ───────────────────────────────────────────────────────────────────

const roles      = ref<Role[]>([]);
const loading    = ref(false);
const error      = ref<string | null>(null);
const showModal  = ref(false);
const saving     = ref(false);
const editingRole = ref<Role | null>(null);

const form = ref<RoleForm>({ name: '', description: '' });
const permissionsRaw = ref('');
const formErrors  = ref<Partial<Record<keyof RoleForm, string>>>({});
const submitError = ref<string | null>(null);

// System roles that cannot be deleted
const systemRoles = ['Admin', 'CEO', 'Manager', 'Employee'];

// ─── Computed ────────────────────────────────────────────────────────────────

const parsedPermissions = computed<string[]>(() => {
  return permissionsRaw.value
    .split(',')
    .map(p => p.trim())
    .filter(p => p.length > 0);
});

// ─── Data Loading ────────────────────────────────────────────────────────────

async function fetchRoles() {
  loading.value = true;
  error.value   = null;
  try {
    const response = await apiClient.get('/api/roles');
    roles.value = response.data;
  } catch {
    error.value = 'Daten konnten nicht geladen werden.';
  } finally {
    loading.value = false;
  }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function isSystemRole(roleName: string): boolean {
  return systemRoles.includes(roleName);
}

function getRoleColorClass(roleName: string): string {
  const colorMap: Record<string, string> = {
    Admin:    'role-admin',
    CEO:      'role-ceo',
    Manager:  'role-manager',
    Employee: 'role-employee',
  };
  return colorMap[roleName] || 'role-custom';
}

// ─── Modal ───────────────────────────────────────────────────────────────────

function openCreate() {
  editingRole.value  = null;
  form.value         = { name: '', description: '' };
  permissionsRaw.value = '';
  formErrors.value   = {};
  submitError.value  = null;
  showModal.value    = true;
}

function openEdit(role: Role) {
  editingRole.value  = role;
  form.value         = { name: role.name, description: role.description ?? '' };
  permissionsRaw.value = (role.permissions_json ?? []).join(', ');
  formErrors.value   = {};
  submitError.value  = null;
  showModal.value    = true;
}

function closeModal() {
  showModal.value = false;
}

function validate(): boolean {
  formErrors.value = {};
  if (!form.value.name.trim()) {
    formErrors.value.name = 'Name ist erforderlich.';
    return false;
  }
  return true;
}

// ─── CRUD ────────────────────────────────────────────────────────────────────

async function handleSubmit() {
  if (!validate()) return;

  saving.value       = true;
  submitError.value  = null;

  const payload = {
    name:             form.value.name.trim(),
    description:      form.value.description.trim() || null,
    permissions_json: parsedPermissions.value,
  };

  try {
    if (editingRole.value) {
      await apiClient.put(`/api/roles/${editingRole.value.id}`, payload);
      toast.success('Rolle gespeichert');
    } else {
      await apiClient.post('/api/roles', payload);
      toast.success('Rolle erstellt');
    }
    closeModal();
    await fetchRoles();
  } catch (err: unknown) {
    const axiosErr = err as { response?: { data?: { detail?: string } } };
    submitError.value = axiosErr.response?.data?.detail ?? 'Fehler beim Speichern';
  } finally {
    saving.value = false;
  }
}

async function handleDelete(role: Role) {
  if (isSystemRole(role.name)) {
    toast.warning('Systemrollen können nicht gelöscht werden!');
    return;
  }

  if (!confirm(`Rolle „${role.name}" wirklich löschen?`)) {
    return;
  }

  try {
    await apiClient.delete(`/api/roles/${role.id}`);
    toast.success('Rolle gelöscht');
    await fetchRoles();
  } catch (err: unknown) {
    const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
    if (axiosErr.response?.status === 405 || axiosErr.response?.status === 404) {
      toast.error('Löschen ist für diese Ressource nicht verfügbar.');
    } else {
      toast.error(axiosErr.response?.data?.detail ?? 'Fehler beim Löschen');
    }
  }
}

// ─── Lifecycle ───────────────────────────────────────────────────────────────

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

/* Icon Buttons */
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
  background: rgb(239 68 68 / 0.15);
  color: #fca5a5;
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

.role-icon.role-admin    { color: #ef4444; }
.role-icon.role-ceo      { color: #a855f7; }
.role-icon.role-manager  { color: #3b82f6; }
.role-icon.role-employee { color: #22c55e; }
.role-icon.role-custom   { color: var(--kit-orange, #FF6B35); }

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
  background: rgb(6 182 212 / 0.1);
  border: 1px solid rgb(6 182 212 / 0.25);
  border-radius: 12px;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  color: #67e8f9;
}

.no-permissions {
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
  font-style: italic;
}

/* Keycloak ID */
.keycloak-id {
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
  font-family: 'JetBrains Mono', 'Courier New', monospace;
}

/* States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--color-text-secondary);
  text-align: center;
  gap: 1rem;
}

.empty-state svg {
  opacity: 0.3;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border-light);
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-form {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.field-hint {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  font-weight: 400;
  text-transform: none;
}

.kit-input.input-error {
  border-color: #ef4444;
}

.field-error {
  font-size: 0.75rem;
  color: #fca5a5;
  margin: 0;
}

.submit-error {
  font-size: 0.8125rem;
  color: #fca5a5;
  margin: 0;
  padding: 0.75rem 1rem;
  background: rgb(239 68 68 / 0.1);
  border: 1px solid rgb(239 68 68 / 0.25);
  border-radius: 6px;
}

.required {
  color: #fca5a5;
}

.font-mono {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.8125rem;
}

.perm-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-top: 0.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border-light);
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

  .modal {
    max-width: 100%;
    border-radius: 8px;
  }
}

@media (max-width: 480px) {
  .count-badge {
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
  }

  .role-card {
    padding: 0.875rem;
  }

  .role-name {
    font-size: 0.9375rem;
  }

  .modal-form {
    padding: 1rem;
  }
}
</style>
