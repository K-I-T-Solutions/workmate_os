<template>
  <div class="dialog-overlay" @click.self="$emit('close')">
    <div class="dialog-large">
      <div class="dialog-header">
        <h3>{{ isEditMode ? 'Mitarbeiter bearbeiten' : 'Neuer Mitarbeiter' }}</h3>
        <button @click="$emit('close')" class="btn-icon">
          <X :size="20" />
        </button>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['tab', { active: activeTab === tab.id }]"
        >
          {{ tab.label }}
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="dialog-content">
        <!-- Tab: Persönlich -->
        <div v-show="activeTab === 'personal'" class="tab-content">
          <div class="form-row">
            <div class="form-field">
              <label>Mitarbeiter-Code *</label>
              <input v-model="formData.employee_code" type="text" placeholder="KIT-0001" required :disabled="isEditMode" />
              <p class="field-hint">Eindeutige Kennung, z.B. KIT-0001</p>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Vorname</label>
              <input v-model="formData.first_name" type="text" placeholder="Max" />
            </div>
            <div class="form-field">
              <label>Nachname</label>
              <input v-model="formData.last_name" type="text" placeholder="Mustermann" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Geschlecht</label>
              <select v-model="formData.gender">
                <option value="">Keine Angabe</option>
                <option value="male">Männlich</option>
                <option value="female">Weiblich</option>
                <option value="diverse">Divers</option>
              </select>
            </div>
            <div class="form-field">
              <label>Geburtsdatum</label>
              <input v-model="formData.birth_date" type="date" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Nationalität</label>
              <input v-model="formData.nationality" type="text" placeholder="Deutsch" />
            </div>
          </div>
        </div>

        <!-- Tab: Organisation -->
        <div v-show="activeTab === 'organization'" class="tab-content">
          <div class="form-row">
            <div class="form-field">
              <label>Abteilung</label>
              <select v-model="formData.department_id">
                <option value="">Keine Abteilung</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                  {{ dept.name }}
                </option>
              </select>
            </div>
            <div class="form-field">
              <label>Rolle</label>
              <select v-model="formData.role_id">
                <option value="">Keine Rolle</option>
                <option v-for="role in roles" :key="role.id" :value="role.id">
                  {{ role.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Vorgesetzter</label>
              <select v-model="formData.reports_to">
                <option value="">Kein Vorgesetzter</option>
                <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                  {{ emp.first_name }} {{ emp.last_name }} ({{ emp.employee_code }})
                </option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Beschäftigungsart</label>
              <select v-model="formData.employment_type">
                <option value="fulltime">Vollzeit</option>
                <option value="parttime">Teilzeit</option>
                <option value="intern">Praktikant</option>
                <option value="external">Extern</option>
              </select>
            </div>
            <div class="form-field">
              <label>Status</label>
              <select v-model="formData.status">
                <option value="active">Aktiv</option>
                <option value="inactive">Inaktiv</option>
                <option value="on_leave">Im Urlaub</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Eintrittsdatum</label>
              <input v-model="formData.hire_date" type="date" />
            </div>
            <div class="form-field" v-if="isEditMode">
              <label>Austrittsdatum</label>
              <input v-model="formData.termination_date" type="date" />
            </div>
          </div>
        </div>

        <!-- Tab: Kontakt -->
        <div v-show="activeTab === 'contact'" class="tab-content">
          <div class="form-row">
            <div class="form-field">
              <label>E-Mail *</label>
              <input v-model="formData.email" type="email" placeholder="max.mustermann@example.com" required />
            </div>
            <div class="form-field">
              <label>Telefon</label>
              <input v-model="formData.phone" type="tel" placeholder="+49 123 456789" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Straße & Hausnummer</label>
              <input v-model="formData.address_street" type="text" placeholder="Musterstraße 123" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>PLZ</label>
              <input v-model="formData.address_zip" type="text" placeholder="12345" />
            </div>
            <div class="form-field">
              <label>Stadt</label>
              <input v-model="formData.address_city" type="text" placeholder="Berlin" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Land</label>
              <input v-model="formData.address_country" type="text" placeholder="Deutschland" />
            </div>
          </div>
        </div>

        <!-- Tab: Einstellungen -->
        <div v-show="activeTab === 'settings'" class="tab-content">
          <div class="form-row">
            <div class="form-field">
              <label>Zeitzone</label>
              <select v-model="formData.timezone">
                <option value="Europe/Berlin">Europe/Berlin (MEZ/MESZ)</option>
                <option value="Europe/London">Europe/London (GMT/BST)</option>
                <option value="America/New_York">America/New_York (EST/EDT)</option>
                <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
              </select>
            </div>
            <div class="form-field">
              <label>Sprache</label>
              <select v-model="formData.language">
                <option value="de">Deutsch</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label>Theme</label>
              <select v-model="formData.theme">
                <option value="catppuccin-frappe">Catppuccin Frappé (Standard)</option>
                <option value="catppuccin-mocha">Catppuccin Mocha</option>
                <option value="catppuccin-macchiato">Catppuccin Macchiato</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="checkbox-label">
                <input v-model="formData.notifications_enabled" type="checkbox" />
                <span>Benachrichtigungen aktiviert</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="dialog-actions">
          <button type="button" @click="$emit('close')" class="btn-secondary">
            Abbrechen
          </button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save v-if="!saving" :size="18" />
            <span v-if="!saving">{{ isEditMode ? 'Änderungen speichern' : 'Mitarbeiter erstellen' }}</span>
            <span v-else>Wird gespeichert...</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { X, Save } from 'lucide-vue-next';
import type { EmployeeCreate, EmployeeUpdate, Department, Role } from '@/composables/useEmployees';

interface Employee {
  id: string;
  employee_code: string;
  first_name?: string;
  last_name?: string;
  email: string;
  phone?: string;
  gender?: string;
  birth_date?: string;
  nationality?: string;
  address_street?: string;
  address_zip?: string;
  address_city?: string;
  address_country?: string;
  department_id?: string;
  role_id?: string;
  reports_to?: string;
  employment_type?: string;
  hire_date?: string;
  termination_date?: string;
  status?: string;
  timezone?: string;
  language?: string;
  theme?: string;
  notifications_enabled?: boolean;
}

const props = defineProps<{
  employee?: Employee | null;
  departments: Department[];
  roles: Role[];
  employees: Employee[];
}>();

const emit = defineEmits<{
  close: [];
  save: [data: EmployeeCreate | EmployeeUpdate];
}>();

const activeTab = ref('personal');
const saving = ref(false);

const tabs = [
  { id: 'personal', label: 'Persönlich' },
  { id: 'organization', label: 'Organisation' },
  { id: 'contact', label: 'Kontakt' },
  { id: 'settings', label: 'Einstellungen' },
];

const isEditMode = computed(() => !!props.employee);

const formData = ref<EmployeeCreate | EmployeeUpdate>({
  employee_code: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  gender: '',
  birth_date: '',
  nationality: '',
  address_street: '',
  address_zip: '',
  address_city: '',
  address_country: '',
  department_id: '',
  role_id: '',
  reports_to: '',
  employment_type: 'fulltime',
  hire_date: '',
  termination_date: '',
  status: 'active',
  timezone: 'Europe/Berlin',
  language: 'de',
  theme: 'catppuccin-frappe',
  notifications_enabled: true,
});

onMounted(() => {
  if (props.employee) {
    // Pre-fill form with employee data for edit mode
    formData.value = {
      ...formData.value,
      ...props.employee,
    };
  }
});

function handleSubmit() {
  saving.value = true;
  try {
    // Clean up empty strings to undefined
    const cleanData = Object.fromEntries(
      Object.entries(formData.value).map(([key, value]) => [
        key,
        value === '' ? undefined : value,
      ])
    );

    emit('save', cleanData as EmployeeCreate | EmployeeUpdate);
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.dialog-large {
  background: var(--color-bg-primary);
  border-radius: 12px;
  border: 1px solid var(--color-border-light);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0.75rem 1.5rem 0;
  border-bottom: 1px solid var(--color-border-light);
  overflow-x: auto;
}

.tab {
  padding: 0.625rem 1rem;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-hover);
  border-radius: 6px 6px 0 0;
}

.tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.dialog-content {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.tab-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.form-field label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.form-field input,
.form-field select {
  padding: 0.625rem;
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.form-field input:focus,
.form-field select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-field input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.field-hint {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.dialog-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border-light);
}

.btn-icon {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-border-medium);
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: var(--color-primary);
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
