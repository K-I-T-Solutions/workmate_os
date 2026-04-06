<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Plus, Search, Edit, Trash2, Mail, Phone, Calendar } from 'lucide-vue-next';
import md5 from 'md5';
import { getEmployees, createEmployee, updateEmployee, deleteEmployee, getDepartments } from '../services/hr.service';
import type { Employee, EmployeeCreate, EmploymentType, Department } from '../types';
import { useToast } from '@/composables/useToast';

const toast = useToast();

const router = useRouter();

function viewEmployee(id: string) {
  router.push(`/app/hr/employees/${id}`);
}

function gravatarUrl(email?: string, size = 40): string {
  if (!email) return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=${size}`;
  return `https://www.gravatar.com/avatar/${md5(email.toLowerCase().trim())}?d=mp&s=${size}`;
}

const loading = ref(true);
const error = ref<string | null>(null);
const employees = ref<Employee[]>([]);
const departments = ref<Department[]>([]);
const showCreateForm = ref(false);
const showEditForm = ref(false);
const selectedEmployee = ref<Employee | null>(null);
const searchQuery = ref('');
const filterDepartment = ref('');
const filterEmploymentType = ref<EmploymentType | ''>('');

// Form data
const newEmployee = ref<EmployeeCreate>({
  employee_code: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  bio: '',
  department_id: '',
  employment_type: 'full_time',
  hire_date: '',
  status: 'active',
});

onMounted(async () => {
  await Promise.all([
    loadEmployees(),
    loadDepartments(),
  ]);
});

async function loadDepartments() {
  try {
    departments.value = await getDepartments();
  } catch (error) {
    console.error('Failed to load departments:', error);
  }
}

async function loadEmployees() {
  loading.value = true;
  error.value = null;
  try {
    const response = await getEmployees({
      department: filterDepartment.value || undefined,
      employment_type: filterEmploymentType.value || undefined,
      search: searchQuery.value || undefined,
    });
    employees.value = response.items;
  } catch (e) {
    error.value = 'Daten konnten nicht geladen werden.';
  } finally {
    loading.value = false;
  }
}

async function handleCreateEmployee() {
  try {
    await createEmployee(newEmployee.value);
    showCreateForm.value = false;
    resetForm();
    await loadEmployees();
  } catch (error) {
    console.error('Failed to create employee:', error);
    toast.error('Fehler beim Erstellen des Mitarbeiters');
  }
}

async function handleUpdateEmployee() {
  if (!selectedEmployee.value) return;

  try {
    await updateEmployee(selectedEmployee.value.id, {
      first_name: selectedEmployee.value.first_name,
      last_name: selectedEmployee.value.last_name,
      email: selectedEmployee.value.email,
      phone: selectedEmployee.value.phone,
      bio: selectedEmployee.value.bio,
      department_id: selectedEmployee.value.department_id,
      employment_type: selectedEmployee.value.employment_type,
      hire_date: selectedEmployee.value.hire_date,
      status: selectedEmployee.value.status,
    });
    showEditForm.value = false;
    selectedEmployee.value = null;
    await loadEmployees();
  } catch (error) {
    console.error('Failed to update employee:', error);
    toast.error('Fehler beim Aktualisieren des Mitarbeiters');
  }
}

async function handleDeleteEmployee(id: string) {
  if (!confirm('Möchten Sie diesen Mitarbeiter wirklich löschen?')) return;

  try {
    await deleteEmployee(id);
    await loadEmployees();
  } catch (error) {
    console.error('Failed to delete employee:', error);
    toast.error('Fehler beim Löschen des Mitarbeiters');
  }
}

function resetForm() {
  newEmployee.value = {
    employee_code: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    bio: '',
    department_id: '',
    employment_type: 'full_time',
    hire_date: '',
    status: 'active',
  };
}

function startEdit(employee: Employee) {
  selectedEmployee.value = { ...employee };
  showEditForm.value = true;
}

const getEmploymentTypeLabel = (type?: string): string => {
  if (!type) return 'Keine Angabe';
  const labels: Record<string, string> = {
    fulltime: 'Vollzeit',
    parttime: 'Teilzeit',
    intern: 'Praktikant',
    external: 'Freelancer',
    contract: 'Vertrag',
    // Legacy support
    full_time: 'Vollzeit',
    part_time: 'Teilzeit',
    freelance: 'Freelancer',
  };
  return labels[type] || type;
};

const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};
</script>

<template>
  <div class="employee-list">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-white">Mitarbeiter</h1>
      <button
        @click="showCreateForm = !showCreateForm"
        class="kit-btn-primary"
      >
        <Plus :size="20" />
        Neuer Mitarbeiter
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="kit-card p-6 mb-6">
      <h3 class="text-xl font-semibold text-white mb-4">Neuer Mitarbeiter</h3>
      <form @submit.prevent="handleCreateEmployee" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="kit-label">Mitarbeiter-Code *</label>
            <input
              v-model="newEmployee.employee_code"
              type="text"
              class="kit-input"
              placeholder="z.B. KIT-0001"
              required
            />
          </div>
          <div>
            <label class="kit-label">E-Mail *</label>
            <input
              v-model="newEmployee.email"
              type="email"
              class="kit-input"
              required
            />
          </div>
          <div>
            <label class="kit-label">Vorname</label>
            <input
              v-model="newEmployee.first_name"
              type="text"
              class="kit-input"
            />
          </div>
          <div>
            <label class="kit-label">Nachname</label>
            <input
              v-model="newEmployee.last_name"
              type="text"
              class="kit-input"
            />
          </div>
          <div>
            <label class="kit-label">Telefon</label>
            <input
              v-model="newEmployee.phone"
              type="tel"
              class="kit-input"
            />
          </div>
          <div>
            <label class="kit-label">Position</label>
            <input
              v-model="newEmployee.bio"
              type="text"
              class="kit-input"
              placeholder="z.B. Senior Developer"
            />
          </div>
          <div>
            <label class="kit-label">Abteilung</label>
            <select
              v-model="newEmployee.department_id"
              class="kit-input"
            >
              <option value="">Keine Abteilung</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="kit-label">Beschäftigungsart</label>
            <select
              v-model="newEmployee.employment_type"
              class="kit-input"
            >
              <option value="fulltime">Vollzeit</option>
              <option value="parttime">Teilzeit</option>
              <option value="intern">Praktikant</option>
              <option value="external">Freelancer</option>
            </select>
          </div>
          <div>
            <label class="kit-label">Eintrittsdatum</label>
            <input
              v-model="newEmployee.hire_date"
              type="date"
              class="kit-input"
            />
          </div>
        </div>

        <div class="flex gap-2">
          <button type="submit" class="kit-btn-success">
            Mitarbeiter erstellen
          </button>
          <button
            type="button"
            @click="showCreateForm = false; resetForm()"
            class="kit-btn-ghost"
          >
            Abbrechen
          </button>
        </div>
      </form>
    </div>

    <!-- Filters -->
    <div class="kit-card p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="relative">
          <Search :size="20" class="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40" />
          <input
            v-model="searchQuery"
            @input="loadEmployees"
            type="text"
            placeholder="Name oder E-Mail suchen..."
            class="kit-input pl-10"
          />
        </div>
        <div>
          <select
            v-model="filterDepartment"
            @change="loadEmployees"
            class="kit-input"
          >
            <option value="">Alle Abteilungen</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
              {{ dept.name }}
            </option>
          </select>
        </div>
        <div>
          <select
            v-model="filterEmploymentType"
            @change="loadEmployees"
            class="kit-input"
          >
            <option value="">Alle Beschäftigungsarten</option>
            <option value="fulltime">Vollzeit</option>
            <option value="parttime">Teilzeit</option>
            <option value="intern">Praktikant</option>
            <option value="external">Freelancer</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Employees List -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-white/60">Lade Mitarbeiter...</div>
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="kit-card p-6 text-center">
      <p class="text-red-400 text-sm">{{ error }}</p>
      <button class="kit-btn-secondary mt-3 text-xs" @click="loadEmployees()">Erneut versuchen</button>
    </div>

    <div v-else-if="employees.length === 0" class="kit-card p-12 text-center">
      <p class="text-white/60 text-lg">Keine Mitarbeiter gefunden</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="employee in employees"
        :key="employee.id"
        class="kit-card p-6 hover:bg-white/15 transition-colors"
      >
        <div class="mb-4 cursor-pointer flex items-center gap-3" @click="viewEmployee(employee.id)">
          <img
            :src="gravatarUrl(employee.email, 40)"
            :alt="employee.first_name"
            class="w-10 h-10 rounded-full border border-white/10 object-cover flex-shrink-0"
          />
          <div class="min-w-0">
            <h3 class="text-base font-semibold text-white hover:text-blue-300 transition-colors truncate">
              {{ employee.first_name }} {{ employee.last_name }}
            </h3>
            <p class="text-blue-400 text-sm truncate">{{ employee.bio || 'Keine Beschreibung' }}</p>
            <p class="text-white/60 text-xs">{{ employee.department?.name || 'Keine Abteilung' }}</p>
          </div>
        </div>

        <div class="space-y-2 mb-4">
          <div class="flex items-center gap-2 text-white/80 text-sm">
            <Mail :size="16" class="text-white/40" />
            <span>{{ employee.email }}</span>
          </div>
          <div v-if="employee.phone" class="flex items-center gap-2 text-white/80 text-sm">
            <Phone :size="16" class="text-white/40" />
            <span>{{ employee.phone }}</span>
          </div>
          <div class="flex items-center gap-2 text-white/80 text-sm">
            <Calendar :size="16" class="text-white/40" />
            <span>Seit {{ formatDate(employee.hire_date) }}</span>
          </div>
        </div>

        <div class="flex items-center justify-between mb-4">
          <span class="badge badge-blue">
            {{ getEmploymentTypeLabel(employee.employment_type) }}
          </span>
          <span
            :class="[
              'badge',
              employee.status === 'active'   ? 'badge-green'
              : employee.status === 'on_leave' ? 'badge-amber'
              : 'badge-gray'
            ]"
          >
            {{ employee.status === 'active' ? 'Aktiv' : (employee.status === 'on_leave' ? 'Beurlaubt' : 'Inaktiv') }}
          </span>
        </div>

        <div class="flex gap-2">
          <button
            @click="startEdit(employee)"
            class="kit-btn-ghost flex-1 justify-center"
          >
            <Edit :size="16" />
            Bearbeiten
          </button>
          <button
            @click="handleDeleteEmployee(employee.id)"
            class="kit-btn-danger"
          >
            <Trash2 :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Dialog -->
    <div
      v-if="showEditForm && selectedEmployee"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="showEditForm = false"
    >
      <div class="kit-card p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
        <h3 class="text-xl font-semibold text-white mb-4">Mitarbeiter bearbeiten</h3>
        <form @submit.prevent="handleUpdateEmployee" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="kit-label">Vorname</label>
              <input
                v-model="selectedEmployee.first_name"
                type="text"
                class="kit-input"
                required
              />
            </div>
            <div>
              <label class="kit-label">Nachname</label>
              <input
                v-model="selectedEmployee.last_name"
                type="text"
                class="kit-input"
                required
              />
            </div>
            <div>
              <label class="kit-label">E-Mail</label>
              <input
                v-model="selectedEmployee.email"
                type="email"
                class="kit-input"
                required
              />
            </div>
            <div>
              <label class="kit-label">Telefon</label>
              <input
                v-model="selectedEmployee.phone"
                type="tel"
                class="kit-input"
              />
            </div>
            <div>
              <label class="kit-label">Position</label>
              <input
                v-model="selectedEmployee.bio"
                type="text"
                class="kit-input"
                placeholder="z.B. Senior Developer"
              />
            </div>
            <div>
              <label class="kit-label">Abteilung</label>
              <select
                v-model="selectedEmployee.department_id"
                class="kit-input"
              >
                <option value="">Keine Abteilung</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                  {{ dept.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="kit-label">Beschäftigungsart</label>
              <select
                v-model="selectedEmployee.employment_type"
                class="kit-input"
                required
              >
                <option value="full_time">Vollzeit</option>
                <option value="part_time">Teilzeit</option>
                <option value="contract">Vertrag</option>
                <option value="intern">Praktikant</option>
                <option value="freelance">Freelancer</option>
              </select>
            </div>
            <div>
              <label class="kit-label">Eintrittsdatum</label>
              <input
                v-model="selectedEmployee.hire_date"
                type="date"
                class="kit-input"
                required
              />
            </div>
          </div>

          <div class="flex gap-2">
            <button type="submit" class="kit-btn-success">
              Speichern
            </button>
            <button
              type="button"
              @click="showEditForm = false"
              class="kit-btn-ghost"
            >
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.employee-list {
  max-width: 1400px;
  margin: 0 auto;
}

select option {
  background-color: #1e293b;
  color: white;
}
</style>
