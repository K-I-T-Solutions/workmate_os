<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useTimeTracking } from '../../composables/useTimeTracking';
import type { TimeEntryCreateRequest } from '../../types/timeEntry';
import { apiClient } from '@/services/api/client';
import {
  ChevronLeft,
  Save,
  X,
  Calendar,
  Clock,
  FileText,
  DollarSign,
  Briefcase,
  User,
} from 'lucide-vue-next';

// Props & Emits
const props = defineProps<{
  entryId?: string;
}>();

const emit = defineEmits<{
  back: [];
  saved: [id: string];
}>();

// Composables
const { currentEntry, loading, error, loadEntry, createEntry, updateEntry } = useTimeTracking();

// Form State
const employeeId = ref('current-user-id');
const projectId = ref<string | null>(null);
const startDate = ref('');
const startTime = ref('');
const endDate = ref('');
const endTime = ref('');
const note = ref('');
const taskType = ref<string>('');
const billable = ref(true);
const hourlyRate = ref<number | null>(null);

// UI State
const validationError = ref<string | null>(null);

// Dropdown Data
const employees = ref<any[]>([]);
const projects = ref<any[]>([]);
const loadingDropdowns = ref(false);

// Computed
const isEditMode = computed(() => !!props.entryId);

const pageTitle = computed(() => {
  return isEditMode.value ? 'Zeiteintrag bearbeiten' : 'Manueller Zeiteintrag';
});

const taskTypeOptions = [
  { value: 'development', label: 'Entwicklung' },
  { value: 'meeting', label: 'Meeting' },
  { value: 'support', label: 'Support' },
  { value: 'documentation', label: 'Dokumentation' },
  { value: 'testing', label: 'Testing' },
  { value: 'planning', label: 'Planung' },
  { value: 'other', label: 'Sonstiges' },
];

// Data Loading
async function loadDropdownData() {
  loadingDropdowns.value = true;
  try {
    const [employeesResponse, projectsResponse] = await Promise.all([
      apiClient.get('/api/employees'),
      apiClient.get('/api/projects'),
    ]);

    employees.value = employeesResponse.data.employees || [];
    projects.value = projectsResponse.data || [];
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

  if (isEditMode.value && props.entryId) {
    await loadEntry(props.entryId);
    if (currentEntry.value) {
      populateForm();
    }
  } else {
    // Set defaults for create mode
    const now = new Date();
    startDate.value = now.toISOString().split('T')[0];
    startTime.value = now.toTimeString().slice(0, 5);
  }
});

// Actions
function populateForm() {
  if (!currentEntry.value) return;

  employeeId.value = currentEntry.value.employee_id;
  projectId.value = currentEntry.value.project_id;
  note.value = currentEntry.value.note || '';
  taskType.value = currentEntry.value.task_type || '';
  billable.value = currentEntry.value.billable;
  hourlyRate.value = currentEntry.value.hourly_rate;

  // Parse start_time
  const start = new Date(currentEntry.value.start_time);
  startDate.value = start.toISOString().split('T')[0];
  startTime.value = start.toTimeString().slice(0, 5);

  // Parse end_time
  if (currentEntry.value.end_time) {
    const end = new Date(currentEntry.value.end_time);
    endDate.value = end.toISOString().split('T')[0];
    endTime.value = end.toTimeString().slice(0, 5);
  }
}

function validate(): boolean {
  validationError.value = null;

  if (!startDate.value || !startTime.value) {
    validationError.value = 'Startdatum und -zeit sind erforderlich';
    return false;
  }

  if (endDate.value && endTime.value) {
    const start = new Date(`${startDate.value}T${startTime.value}`);
    const end = new Date(`${endDate.value}T${endTime.value}`);

    if (end <= start) {
      validationError.value = 'Endzeit muss nach der Startzeit liegen';
      return false;
    }
  }

  if (hourlyRate.value !== null && hourlyRate.value < 0) {
    validationError.value = 'Stundensatz kann nicht negativ sein';
    return false;
  }

  return true;
}

async function handleSave() {
  if (!validate()) return;

  const startDateTime = `${startDate.value}T${startTime.value}:00`;
  const endDateTime = endDate.value && endTime.value
    ? `${endDate.value}T${endTime.value}:00`
    : null;

  const data: TimeEntryCreateRequest = {
    employee_id: employeeId.value,
    project_id: projectId.value,
    start_time: startDateTime,
    end_time: endDateTime,
    note: note.value || null,
    task_type: taskType.value || null,
    billable: billable.value,
    hourly_rate: hourlyRate.value,
  };

  if (isEditMode.value && props.entryId) {
    const updated = await updateEntry(props.entryId, data);
    if (updated) {
      emit('saved', updated.id);
    }
  } else {
    const created = await createEntry(data);
    if (created) {
      emit('saved', created.id);
    }
  }
}

function handleCancel() {
  emit('back');
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="handleCancel" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <h1 class="text-2xl font-bold text-white">{{ pageTitle }}</h1>
      </div>
      <div class="flex gap-2">
        <button @click="handleCancel" class="kit-btn-ghost">
          <X :size="18" />
          Abbrechen
        </button>
        <button @click="handleSave" class="kit-btn-primary" :disabled="loading">
          <Save :size="18" />
          {{ isEditMode ? 'Speichern' : 'Erstellen' }}
        </button>
      </div>
    </div>

    <!-- Validation Error -->
    <div v-if="validationError" class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
      <p class="text-red-200">{{ validationError }}</p>
    </div>

    <!-- API Error -->
    <div v-if="error" class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
      <p class="text-red-200">{{ error }}</p>
    </div>

    <!-- Form Content -->
    <div class="flex-1 overflow-y-auto space-y-4">
      <!-- Zeitraum Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-4">
          <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
            <Clock :size="18" class="text-blue-200" />
          </div>
          <h3 class="font-semibold text-white">Zeitraum</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Start Date -->
          <div>
            <label class="kit-label flex items-center gap-1">
              <Calendar :size="14" />
              Startdatum *
            </label>
            <input
              v-model="startDate"
              type="date"
              class="kit-input"
              required
            />
          </div>

          <!-- Start Time -->
          <div>
            <label class="kit-label flex items-center gap-1">
              <Clock :size="14" />
              Startzeit *
            </label>
            <input
              v-model="startTime"
              type="time"
              class="kit-input"
              required
            />
          </div>

          <!-- End Date -->
          <div>
            <label class="kit-label flex items-center gap-1">
              <Calendar :size="14" />
              Enddatum
            </label>
            <input
              v-model="endDate"
              type="date"
              class="kit-input"
            />
          </div>

          <!-- End Time -->
          <div>
            <label class="kit-label flex items-center gap-1">
              <Clock :size="14" />
              Endzeit
            </label>
            <input
              v-model="endTime"
              type="time"
              class="kit-input"
            />
          </div>
        </div>

        <p class="text-xs text-white/40 mt-2">
          * Pflichtfelder
        </p>
      </div>

      <!-- Details Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-4">
          <div class="p-2 bg-purple-500/20 rounded-lg border border-purple-400/30">
            <FileText :size="18" class="text-purple-200" />
          </div>
          <h3 class="font-semibold text-white">Details</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Task Type -->
          <div>
            <label class="kit-label">Aufgabentyp</label>
            <select v-model="taskType" class="kit-input">
              <option value="">Nicht festgelegt</option>
              <option
                v-for="option in taskTypeOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- Project -->
          <div>
            <label class="kit-label flex items-center gap-1">
              <Briefcase :size="14" />
              Projekt
            </label>
            <select v-model="projectId" class="kit-input" :disabled="loadingDropdowns">
              <option :value="null">Kein Projekt</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.title }} ({{ project.customer_name || 'Kein Kunde' }})
              </option>
            </select>
            <p v-if="loadingDropdowns" class="text-xs text-white/40 mt-1">Lade Projekte...</p>
          </div>

          <!-- Employee -->
          <div>
            <label class="kit-label flex items-center gap-1">
              <User :size="14" />
              Mitarbeiter
            </label>
            <select v-model="employeeId" class="kit-input" :disabled="loadingDropdowns">
              <option v-for="employee in employees" :key="employee.id" :value="employee.id">
                {{ employee.first_name }} {{ employee.last_name }} ({{ employee.employee_code }})
              </option>
            </select>
            <p v-if="loadingDropdowns" class="text-xs text-white/40 mt-1">Lade Mitarbeiter...</p>
          </div>

          <!-- Billable Checkbox -->
          <div class="flex items-center gap-2 pt-6">
            <input
              v-model="billable"
              type="checkbox"
              id="billable"
              class="w-4 h-4 rounded border-white/20 bg-white/5 text-blue-500 focus:ring-2 focus:ring-blue-500"
            />
            <label for="billable" class="text-sm text-white cursor-pointer">
              Abrechenbar
            </label>
          </div>
        </div>
      </div>

      <!-- Finanzen Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-4">
          <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
            <DollarSign :size="18" class="text-emerald-200" />
          </div>
          <h3 class="font-semibold text-white">Finanzen</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Hourly Rate -->
          <div>
            <label class="kit-label">Stundensatz (€)</label>
            <input
              v-model.number="hourlyRate"
              type="number"
              step="0.01"
              min="0"
              class="kit-input"
              placeholder="0.00"
            />
          </div>
        </div>
      </div>

      <!-- Notiz Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center gap-2 mb-4">
          <FileText :size="18" class="text-white/60" />
          <h3 class="font-semibold text-white">Notiz</h3>
        </div>

        <textarea
          v-model="note"
          rows="4"
          class="kit-input"
          placeholder="Woran wurde gearbeitet?"
        ></textarea>
      </div>
    </div>
  </div>
</template>
