<template>
  <div class="departments-page">
    <!-- Header with Actions -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Abteilungen</h2>
        <span class="count-badge">{{ departments.length }} Abteilungen</span>
      </div>
      <button @click="openCreate" class="kit-btn-primary">
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
            <button @click="openEdit(dept)" class="btn-icon" title="Bearbeiten">
              <Pencil :size="16" />
            </button>
            <button @click="handleDelete(dept)" class="btn-icon btn-danger" title="Löschen">
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
        <button @click="openCreate" class="kit-btn-primary">
          <Plus :size="18" />
          Erste Abteilung erstellen
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      Lade Abteilungen...
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="kit-card p-6 text-center">
      <p class="text-red-400 text-sm">{{ error }}</p>
      <button class="kit-btn-secondary mt-3 text-xs" @click="fetchDepartments()">Erneut versuchen</button>
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
          <h3 class="modal-title">{{ editingDept ? 'Abteilung bearbeiten' : 'Neue Abteilung erstellen' }}</h3>
          <button class="btn-icon" @click="closeModal" title="Schließen">
            <X :size="18" />
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-form">
          <!-- Name -->
          <div class="field">
            <label class="kit-label" for="dept-name">Name <span class="required">*</span></label>
            <input
              id="dept-name"
              v-model="form.name"
              type="text"
              class="kit-input"
              :class="{ 'input-error': formErrors.name }"
              placeholder="z. B. Entwicklung"
              required
            />
            <p v-if="formErrors.name" class="field-error">{{ formErrors.name }}</p>
          </div>

          <!-- Code -->
          <div class="field">
            <label class="kit-label" for="dept-code">Kürzel <span class="required">*</span></label>
            <input
              id="dept-code"
              v-model="form.code"
              type="text"
              class="kit-input font-mono"
              :class="{ 'input-error': formErrors.code }"
              placeholder="z. B. DEV"
              required
            />
            <p v-if="formErrors.code" class="field-error">{{ formErrors.code }}</p>
          </div>

          <!-- Description -->
          <div class="field">
            <label class="kit-label" for="dept-desc">Beschreibung</label>
            <textarea
              id="dept-desc"
              v-model="form.description"
              class="kit-input"
              rows="3"
              placeholder="Kurze Beschreibung der Abteilung..."
            ></textarea>
          </div>

          <!-- Manager (only on edit, since DepartmentCreate has no manager_id) -->
          <div class="field">
            <label class="kit-label" for="dept-manager">
              Abteilungsleiter
              <span v-if="!editingDept" class="field-hint">— nach dem Anlegen auswählbar</span>
            </label>
            <select
              id="dept-manager"
              v-model="form.manager_id"
              class="kit-input"
              :disabled="!editingDept"
            >
              <option value="">Kein Leiter zugewiesen</option>
              <option
                v-for="emp in employees"
                :key="emp.id"
                :value="emp.id"
              >
                {{ emp.first_name }} {{ emp.last_name }} ({{ emp.employee_code }})
              </option>
            </select>
          </div>

          <!-- Form error -->
          <p v-if="submitError" class="submit-error">{{ submitError }}</p>

          <div class="modal-actions">
            <button type="button" class="kit-btn-secondary" @click="closeModal">
              Abbrechen
            </button>
            <button type="submit" class="kit-btn-primary" :disabled="saving">
              <span v-if="saving">Speichere...</span>
              <span v-else>{{ editingDept ? 'Speichern' : 'Erstellen' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus, Pencil, Trash2, Building2, Users, X } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';
import { useToast } from '@/composables/useToast';

const toast = useToast();

// ─── Types ───────────────────────────────────────────────────────────────────

interface ManagerStub {
  first_name: string;
  last_name: string;
}

interface Department {
  id: string;
  name: string;
  code?: string | null;
  description?: string | null;
  manager_id?: string | null;
  manager?: ManagerStub | null;
}

interface Employee {
  id: string;
  first_name: string;
  last_name: string;
  employee_code: string;
}

interface DeptForm {
  name: string;
  code: string;
  description: string;
  manager_id: string;
}

// ─── State ───────────────────────────────────────────────────────────────────

const departments = ref<Department[]>([]);
const employees   = ref<Employee[]>([]);
const loading     = ref(false);
const error       = ref<string | null>(null);
const showModal   = ref(false);
const saving      = ref(false);
const editingDept = ref<Department | null>(null);

const form        = ref<DeptForm>({ name: '', code: '', description: '', manager_id: '' });
const formErrors  = ref<Partial<Record<keyof DeptForm, string>>>({});
const submitError = ref<string | null>(null);

// ─── Data Loading ─────────────────────────────────────────────────────────────

async function fetchDepartments() {
  loading.value = true;
  error.value   = null;
  try {
    const response = await apiClient.get('/api/departments');
    departments.value = response.data;
  } catch {
    error.value = 'Daten konnten nicht geladen werden.';
  } finally {
    loading.value = false;
  }
}

async function fetchEmployees() {
  try {
    const response = await apiClient.get('/api/employees', {
      params: { limit: 500, status: 'active' },
    });
    // API returns { employees: [...], total: n }
    employees.value = response.data.employees ?? response.data;
  } catch {
    // Non-critical — manager dropdown simply stays empty
  }
}

// ─── Modal ───────────────────────────────────────────────────────────────────

function openCreate() {
  editingDept.value = null;
  form.value        = { name: '', code: '', description: '', manager_id: '' };
  formErrors.value  = {};
  submitError.value = null;
  showModal.value   = true;
}

function openEdit(dept: Department) {
  editingDept.value = dept;
  form.value        = {
    name:        dept.name,
    code:        dept.code ?? '',
    description: dept.description ?? '',
    manager_id:  dept.manager_id ?? '',
  };
  formErrors.value  = {};
  submitError.value = null;
  showModal.value   = true;
}

function closeModal() {
  showModal.value = false;
}

function validate(): boolean {
  formErrors.value = {};
  let ok = true;

  if (!form.value.name.trim()) {
    formErrors.value.name = 'Name ist erforderlich.';
    ok = false;
  }
  if (!form.value.code.trim()) {
    formErrors.value.code = 'Kürzel ist erforderlich.';
    ok = false;
  }
  return ok;
}

// ─── CRUD ────────────────────────────────────────────────────────────────────

async function handleSubmit() {
  if (!validate()) return;

  saving.value      = true;
  submitError.value = null;

  try {
    if (editingDept.value) {
      // PUT — DepartmentUpdate (all optional, includes manager_id)
      const payload = {
        name:        form.value.name.trim(),
        code:        form.value.code.trim() || null,
        description: form.value.description.trim() || null,
        manager_id:  form.value.manager_id || null,
      };
      await apiClient.put(`/api/departments/${editingDept.value.id}`, payload);
      toast.success('Abteilung gespeichert');
    } else {
      // POST — DepartmentCreate (no manager_id field)
      const payload = {
        name:        form.value.name.trim(),
        code:        form.value.code.trim() || null,
        description: form.value.description.trim() || null,
      };
      await apiClient.post('/api/departments', payload);
      toast.success('Abteilung erstellt');
    }
    closeModal();
    await fetchDepartments();
  } catch (err: unknown) {
    const axiosErr = err as { response?: { data?: { detail?: string } } };
    submitError.value = axiosErr.response?.data?.detail ?? 'Fehler beim Speichern';
  } finally {
    saving.value = false;
  }
}

async function handleDelete(dept: Department) {
  if (!confirm(`Abteilung „${dept.name}" wirklich löschen?`)) {
    return;
  }

  try {
    await apiClient.delete(`/api/departments/${dept.id}`);
    toast.success('Abteilung gelöscht');
    await fetchDepartments();
  } catch (err: unknown) {
    const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
    if (axiosErr.response?.status === 405 || axiosErr.response?.status === 404) {
      toast.error('Löschen ist für diese Ressource nicht verfügbar.');
    } else {
      toast.error(axiosErr.response?.data?.detail ?? 'Fehler beim Löschen');
    }
  }
}

// ─── Lifecycle ────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([fetchDepartments(), fetchEmployees()]);
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
  font-family: 'JetBrains Mono', 'Courier New', monospace;
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
  max-width: 520px;
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

.kit-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

  .department-card {
    padding: 0.875rem;
  }

  .card-header {
    margin-bottom: 0.75rem;
  }

  .modal-form {
    padding: 1rem;
  }
}
</style>
