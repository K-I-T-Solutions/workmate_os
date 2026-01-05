<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useProjects } from '../composables/useProjects';
import type { ProjectCreateRequest, ProjectUpdateRequest } from '../types/project';
import { apiClient } from '@/services/api/client';
import {
  ChevronLeft,
  Save,
  Loader2,
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  projectId?: string; // Optional: wenn gesetzt = Edit-Mode
  prefilledCustomerId?: string; // Für Create aus CRM
}>();

// Emits
const emit = defineEmits<{
  back: [];
  saved: [id: string];
}>();

// Composables
const { currentProject, loading, createProject, updateProject, loadProject } = useProjects();

// Status Options
const statusOptions = [
  { value: 'planning', label: 'Planung' },
  { value: 'active', label: 'Aktiv' },
  { value: 'on_hold', label: 'Pausiert' },
  { value: 'completed', label: 'Abgeschlossen' },
  { value: 'cancelled', label: 'Abgebrochen' },
];

// Priority Options
const priorityOptions = [
  { value: '', label: 'Normal' },
  { value: 'low', label: 'Niedrig' },
  { value: 'medium', label: 'Mittel' },
  { value: 'high', label: 'Hoch' },
  { value: 'urgent', label: 'Dringend' },
];

// State
const formData = ref<ProjectCreateRequest>({
  title: '',
  description: '',
  status: 'planning',
  priority: null,
  start_date: null,
  end_date: null,
  deadline: null,
  budget: null,
  hourly_rate: null,
  customer_id: props.prefilledCustomerId || '',
  department_id: null,
  project_manager_id: null,
});

const saving = ref(false);
const errors = ref<Record<string, string>>({});

// Dropdown Data
const employees = ref<any[]>([]);
const departments = ref<any[]>([]);
const loadingDropdowns = ref(false);

// Computed
const isEditMode = computed(() => !!props.projectId);
const pageTitle = computed(() => isEditMode.value ? 'Projekt bearbeiten' : 'Neues Projekt');

// Data Loading
async function loadDropdownData() {
  loadingDropdowns.value = true;
  try {
    const [employeesResponse, departmentsResponse] = await Promise.all([
      apiClient.get('/api/employees'),
      apiClient.get('/api/departments'),
    ]);

    employees.value = employeesResponse.data.employees || [];
    departments.value = departmentsResponse.data || [];
  } catch (error) {
    console.error('Error loading dropdown data:', error);
  } finally {
    loadingDropdowns.value = false;
  }
}

// Lifecycle
onMounted(async () => {
  // Load dropdown data first
  await loadDropdownData();

  if (props.projectId) {
    await loadProject(props.projectId);
    if (currentProject.value) {
      // Populate form with project data
      formData.value = {
        title: currentProject.value.title || '',
        description: currentProject.value.description || '',
        status: currentProject.value.status || 'planning',
        priority: currentProject.value.priority || null,
        start_date: currentProject.value.start_date || null,
        end_date: currentProject.value.end_date || null,
        deadline: currentProject.value.deadline || null,
        budget: currentProject.value.budget || null,
        hourly_rate: currentProject.value.hourly_rate || null,
        customer_id: currentProject.value.customer_id,
        department_id: currentProject.value.department_id || null,
        project_manager_id: currentProject.value.project_manager_id || null,
      };
    }
  }
});

// Actions
function validate(): boolean {
  errors.value = {};

  if (!formData.value.title || formData.value.title.trim() === '') {
    errors.value.title = 'Titel ist erforderlich';
  }

  if (!formData.value.customer_id) {
    errors.value.customer_id = 'Kunde ist erforderlich';
  }

  // Date validation
  if (formData.value.start_date && formData.value.end_date) {
    const start = new Date(formData.value.start_date);
    const end = new Date(formData.value.end_date);
    if (end < start) {
      errors.value.end_date = 'Enddatum muss nach Startdatum liegen';
    }
  }

  // Budget validation
  if (formData.value.budget !== null && formData.value.budget < 0) {
    errors.value.budget = 'Budget muss positiv sein';
  }

  // Hourly rate validation
  if (formData.value.hourly_rate !== null && formData.value.hourly_rate < 0) {
    errors.value.hourly_rate = 'Stundensatz muss positiv sein';
  }

  return Object.keys(errors.value).length === 0;
}

async function handleSubmit() {
  if (!validate()) {
    return;
  }

  saving.value = true;

  try {
    let savedProject;

    if (isEditMode.value && props.projectId) {
      // Update existing project
      const updateData: ProjectUpdateRequest = { ...formData.value };
      delete (updateData as any).customer_id; // Customer kann nicht geändert werden
      savedProject = await updateProject(props.projectId, updateData);
    } else {
      // Create new project
      savedProject = await createProject(formData.value);
    }

    if (savedProject) {
      emit('saved', savedProject.id);
    }
  } catch (error) {
    console.error('Error saving project:', error);
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-3 sm:gap-4 p-3 sm:p-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <h1 class="text-2xl font-bold text-white">{{ pageTitle }}</h1>
      </div>

      <div class="flex gap-2 w-full sm:w-auto">
        <button @click="emit('back')" class="kit-btn-ghost flex-1 sm:flex-none" :disabled="saving">
          Abbrechen
        </button>
        <button @click="handleSubmit" class="kit-btn-primary flex-1 sm:flex-none" :disabled="saving">
          <Loader2 v-if="saving" :size="18" class="animate-spin" />
          <Save v-else :size="18" />
          Speichern
        </button>
      </div>
    </div>

    <!-- Form Content -->
    <div class="flex-1 overflow-y-auto space-y-4">
      <!-- Section 1: Allgemeine Informationen -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Allgemeine Informationen</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <!-- Titel -->
          <div class="sm:col-span-2">
            <label class="kit-label">Titel *</label>
            <input
              v-model="formData.title"
              type="text"
              class="kit-input"
              :class="{ 'border-red-400': errors.title }"
              placeholder="z.B. Website-Relaunch"
            />
            <p v-if="errors.title" class="text-xs text-red-300 mt-1">{{ errors.title }}</p>
          </div>

          <!-- Status -->
          <div>
            <label class="kit-label">Status</label>
            <select v-model="formData.status" class="kit-input">
              <option v-for="status in statusOptions" :key="status.value" :value="status.value">
                {{ status.label }}
              </option>
            </select>
          </div>

          <!-- Priorität -->
          <div>
            <label class="kit-label">Priorität</label>
            <select v-model="formData.priority" class="kit-input">
              <option v-for="priority in priorityOptions" :key="priority.value" :value="priority.value || null">
                {{ priority.label }}
              </option>
            </select>
          </div>

          <!-- Projekt-Manager -->
          <div>
            <label class="kit-label">Projekt-Manager</label>
            <select v-model="formData.project_manager_id" class="kit-input" :disabled="loadingDropdowns">
              <option :value="null">Kein Projekt-Manager</option>
              <option v-for="employee in employees" :key="employee.id" :value="employee.id">
                {{ employee.first_name }} {{ employee.last_name }} ({{ employee.employee_code }})
              </option>
            </select>
            <p v-if="loadingDropdowns" class="text-xs text-white/40 mt-1">Lade Mitarbeiter...</p>
          </div>

          <!-- Abteilung -->
          <div>
            <label class="kit-label">Abteilung</label>
            <select v-model="formData.department_id" class="kit-input" :disabled="loadingDropdowns">
              <option :value="null">Keine Abteilung</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }} ({{ dept.code }})
              </option>
            </select>
            <p v-if="loadingDropdowns" class="text-xs text-white/40 mt-1">Lade Abteilungen...</p>
          </div>

          <!-- Beschreibung -->
          <div class="sm:col-span-2">
            <label class="kit-label">Beschreibung</label>
            <textarea
              v-model="formData.description"
              rows="4"
              class="kit-input"
              placeholder="Projektbeschreibung..."
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Section 2: Zeitplanung -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Zeitplanung</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <!-- Startdatum -->
          <div>
            <label class="kit-label">Startdatum</label>
            <input
              v-model="formData.start_date"
              type="date"
              class="kit-input"
            />
          </div>

          <!-- Enddatum -->
          <div>
            <label class="kit-label">Enddatum (geplant)</label>
            <input
              v-model="formData.end_date"
              type="date"
              class="kit-input"
              :class="{ 'border-red-400': errors.end_date }"
            />
            <p v-if="errors.end_date" class="text-xs text-red-300 mt-1">{{ errors.end_date }}</p>
          </div>

          <!-- Deadline -->
          <div>
            <label class="kit-label">Deadline</label>
            <input
              v-model="formData.deadline"
              type="date"
              class="kit-input"
            />
          </div>
        </div>
      </div>

      <!-- Section 3: Finanzen -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Finanzen</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <!-- Budget -->
          <div>
            <label class="kit-label">Budget (€)</label>
            <input
              v-model.number="formData.budget"
              type="number"
              step="0.01"
              min="0"
              class="kit-input"
              :class="{ 'border-red-400': errors.budget }"
              placeholder="0.00"
            />
            <p v-if="errors.budget" class="text-xs text-red-300 mt-1">{{ errors.budget }}</p>
          </div>

          <!-- Stundensatz -->
          <div>
            <label class="kit-label">Stundensatz (€)</label>
            <input
              v-model.number="formData.hourly_rate"
              type="number"
              step="0.01"
              min="0"
              class="kit-input"
              :class="{ 'border-red-400': errors.hourly_rate }"
              placeholder="0.00"
            />
            <p v-if="errors.hourly_rate" class="text-xs text-red-300 mt-1">{{ errors.hourly_rate }}</p>
          </div>
        </div>
      </div>

      <!-- Section 4: Zuordnung (Hinweis) -->
      <div class="rounded-lg border border-blue-400/30 bg-blue-500/10 p-4">
        <p class="text-sm text-blue-200">
          <strong>Hinweis:</strong> Der Kunde {{ isEditMode ? 'kann nach der Erstellung nicht mehr geändert werden' : 'wird beim Speichern automatisch zugeordnet' }}.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Mobile Optimizations */
@media (max-width: 640px) {
  .rounded-lg.border {
    padding: 0.75rem;
  }

  .text-lg {
    font-size: 1rem;
  }
}
</style>
