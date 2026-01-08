<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus, Search, Edit, Trash2, Mail, Phone, Calendar } from 'lucide-vue-next';
import { getEmployees, createEmployee, updateEmployee, deleteEmployee } from '../services/hr.service';
import type { Employee, EmployeeCreate, EmploymentType } from '../types';

const loading = ref(true);
const employees = ref<Employee[]>([]);
const showCreateForm = ref(false);
const showEditForm = ref(false);
const selectedEmployee = ref<Employee | null>(null);
const searchQuery = ref('');
const filterDepartment = ref('');
const filterEmploymentType = ref<EmploymentType | ''>('');

// Form data
const newEmployee = ref<EmployeeCreate>({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  employment_type: 'full_time',
  hire_date: '',
});

onMounted(async () => {
  await loadEmployees();
});

async function loadEmployees() {
  loading.value = true;
  try {
    const response = await getEmployees({
      department: filterDepartment.value || undefined,
      employment_type: filterEmploymentType.value || undefined,
      search: searchQuery.value || undefined,
    });
    employees.value = response.items;
  } catch (error) {
    console.error('Failed to load employees:', error);
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
    alert('Fehler beim Erstellen des Mitarbeiters');
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
      department: selectedEmployee.value.department,
      position: selectedEmployee.value.position,
      employment_type: selectedEmployee.value.employment_type,
      hire_date: selectedEmployee.value.hire_date,
    });
    showEditForm.value = false;
    selectedEmployee.value = null;
    await loadEmployees();
  } catch (error) {
    console.error('Failed to update employee:', error);
    alert('Fehler beim Aktualisieren des Mitarbeiters');
  }
}

async function handleDeleteEmployee(id: string) {
  if (!confirm('Möchten Sie diesen Mitarbeiter wirklich löschen?')) return;

  try {
    await deleteEmployee(id);
    await loadEmployees();
  } catch (error) {
    console.error('Failed to delete employee:', error);
    alert('Fehler beim Löschen des Mitarbeiters');
  }
}

function resetForm() {
  newEmployee.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    employment_type: 'full_time',
    hire_date: '',
  };
}

function startEdit(employee: Employee) {
  selectedEmployee.value = { ...employee };
  showEditForm.value = true;
}

const getEmploymentTypeLabel = (type: EmploymentType): string => {
  const labels: Record<EmploymentType, string> = {
    full_time: 'Vollzeit',
    part_time: 'Teilzeit',
    contract: 'Vertrag',
    intern: 'Praktikant',
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
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
      >
        <Plus :size="20" />
        Neuer Mitarbeiter
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20 mb-6">
      <h3 class="text-xl font-semibold text-white mb-4">Neuer Mitarbeiter</h3>
      <form @submit.prevent="handleCreateEmployee" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-white/80 mb-2">Vorname</label>
            <input
              v-model="newEmployee.first_name"
              type="text"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              required
            />
          </div>
          <div>
            <label class="block text-white/80 mb-2">Nachname</label>
            <input
              v-model="newEmployee.last_name"
              type="text"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              required
            />
          </div>
          <div>
            <label class="block text-white/80 mb-2">E-Mail</label>
            <input
              v-model="newEmployee.email"
              type="email"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              required
            />
          </div>
          <div>
            <label class="block text-white/80 mb-2">Telefon</label>
            <input
              v-model="newEmployee.phone"
              type="tel"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
            />
          </div>
          <div>
            <label class="block text-white/80 mb-2">Abteilung</label>
            <input
              v-model="newEmployee.department"
              type="text"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
            />
          </div>
          <div>
            <label class="block text-white/80 mb-2">Position</label>
            <input
              v-model="newEmployee.position"
              type="text"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
            />
          </div>
          <div>
            <label class="block text-white/80 mb-2">Beschäftigungsart</label>
            <select
              v-model="newEmployee.employment_type"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
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
            <label class="block text-white/80 mb-2">Eintrittsdatum</label>
            <input
              v-model="newEmployee.hire_date"
              type="date"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              required
            />
          </div>
        </div>

        <div class="flex gap-2">
          <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Mitarbeiter erstellen
          </button>
          <button
            type="button"
            @click="showCreateForm = false; resetForm()"
            class="bg-white/10 hover:bg-white/20 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Abbrechen
          </button>
        </div>
      </form>
    </div>

    <!-- Filters -->
    <div class="bg-white/10 backdrop-blur-lg rounded-lg p-4 border border-white/20 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="relative">
          <Search :size="20" class="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40" />
          <input
            v-model="searchQuery"
            @input="loadEmployees"
            type="text"
            placeholder="Name oder E-Mail suchen..."
            class="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-2 text-white placeholder-white/40"
          />
        </div>
        <div>
          <input
            v-model="filterDepartment"
            @input="loadEmployees"
            type="text"
            placeholder="Abteilung filtern..."
            class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/40"
          />
        </div>
        <div>
          <select
            v-model="filterEmploymentType"
            @change="loadEmployees"
            class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
          >
            <option value="">Alle Beschäftigungsarten</option>
            <option value="full_time">Vollzeit</option>
            <option value="part_time">Teilzeit</option>
            <option value="contract">Vertrag</option>
            <option value="intern">Praktikant</option>
            <option value="freelance">Freelancer</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Employees List -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-white/60">Lade Mitarbeiter...</div>
    </div>

    <div v-else-if="employees.length === 0" class="bg-white/10 backdrop-blur-lg rounded-lg p-12 border border-white/20 text-center">
      <p class="text-white/60 text-lg">Keine Mitarbeiter gefunden</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="employee in employees"
        :key="employee.id"
        class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20 hover:bg-white/15 transition-colors"
      >
        <div class="mb-4">
          <h3 class="text-xl font-semibold text-white mb-1">
            {{ employee.first_name }} {{ employee.last_name }}
          </h3>
          <p class="text-blue-400 text-sm">{{ employee.position || 'Keine Position' }}</p>
          <p class="text-white/60 text-sm">{{ employee.department || 'Keine Abteilung' }}</p>
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
          <span class="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-xs font-semibold">
            {{ getEmploymentTypeLabel(employee.employment_type) }}
          </span>
          <span
            :class="[
              'px-3 py-1 rounded-full text-xs font-semibold',
              employee.is_active
                ? 'bg-green-500/20 text-green-300'
                : 'bg-gray-500/20 text-gray-300'
            ]"
          >
            {{ employee.is_active ? 'Aktiv' : 'Inaktiv' }}
          </span>
        </div>

        <div class="flex gap-2">
          <button
            @click="startEdit(employee)"
            class="flex-1 bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <Edit :size="16" />
            Bearbeiten
          </button>
          <button
            @click="handleDeleteEmployee(employee.id)"
            class="bg-red-500/20 hover:bg-red-500/30 text-red-300 px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
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
      <div class="bg-slate-800 rounded-lg p-6 w-full max-w-2xl border border-white/20 max-h-screen overflow-y-auto">
        <h3 class="text-xl font-semibold text-white mb-4">Mitarbeiter bearbeiten</h3>
        <form @submit.prevent="handleUpdateEmployee" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-white/80 mb-2">Vorname</label>
              <input
                v-model="selectedEmployee.first_name"
                type="text"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
                required
              />
            </div>
            <div>
              <label class="block text-white/80 mb-2">Nachname</label>
              <input
                v-model="selectedEmployee.last_name"
                type="text"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
                required
              />
            </div>
            <div>
              <label class="block text-white/80 mb-2">E-Mail</label>
              <input
                v-model="selectedEmployee.email"
                type="email"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
                required
              />
            </div>
            <div>
              <label class="block text-white/80 mb-2">Telefon</label>
              <input
                v-model="selectedEmployee.phone"
                type="tel"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              />
            </div>
            <div>
              <label class="block text-white/80 mb-2">Abteilung</label>
              <input
                v-model="selectedEmployee.department"
                type="text"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              />
            </div>
            <div>
              <label class="block text-white/80 mb-2">Position</label>
              <input
                v-model="selectedEmployee.position"
                type="text"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              />
            </div>
            <div>
              <label class="block text-white/80 mb-2">Beschäftigungsart</label>
              <select
                v-model="selectedEmployee.employment_type"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
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
              <label class="block text-white/80 mb-2">Eintrittsdatum</label>
              <input
                v-model="selectedEmployee.hire_date"
                type="date"
                class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
                required
              />
            </div>
          </div>

          <div class="flex gap-2">
            <button
              type="submit"
              class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Speichern
            </button>
            <button
              type="button"
              @click="showEditForm = false"
              class="bg-white/10 hover:bg-white/20 text-white px-6 py-2 rounded-lg transition-colors"
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
