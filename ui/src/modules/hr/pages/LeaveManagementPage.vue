<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Plus, Calendar, Search } from 'lucide-vue-next';
import { getLeaveRequests, createLeaveRequest, deleteLeaveRequest, getEmployees } from '../services/hr.service';
import type { LeaveRequest, LeaveRequestCreate, LeaveType, LeaveStatus, Employee } from '../types';
import { useToast } from '@/composables/useToast';

const toast = useToast();

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref<string | null>(null);
const leaveRequests = ref<LeaveRequest[]>([]);
const employees = ref<Employee[]>([]);
const showCreateForm = ref(false);
const searchQuery = ref('');
const filterStatus = ref<LeaveStatus | ''>('');
const filterType = ref<LeaveType | ''>('');
const highlightedRequestId = ref<string | null>(null);

// Form data
const newRequest = ref<LeaveRequestCreate>({
  employee_id: '', // TODO: Get from current user
  leave_type: 'vacation',
  start_date: '',
  end_date: '',
  half_day_start: false,
  half_day_end: false,
  reason: '',
});

onMounted(async () => {
  // Load data first
  await Promise.all([
    loadLeaveRequests(),
    loadEmployees(),
  ]);

  // Handle deeplink AFTER data is loaded
  handleDeeplink();
});

function handleDeeplink() {
  const requestId = route.params.id as string;
  if (!requestId) return;

  // Find the request and open details modal
  const request = leaveRequests.value.find(r => r.id === requestId);

  if (request) {
    selectedRequest.value = request;
    showDetailsModal.value = true;

    // Also highlight the request
    highlightedRequestId.value = requestId;

    // Scroll to request after a short delay
    setTimeout(() => {
      const element = document.getElementById(`request-${requestId}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 300);

    // Clear highlight after 3 seconds (but keep modal open)
    setTimeout(() => {
      highlightedRequestId.value = null;
    }, 3000);
  }
}

async function loadEmployees() {
  try {
    const response = await getEmployees({ limit: 500 }); // Backend max is 500
    employees.value = response.items;
  } catch (error) {
    console.error('Failed to load employees:', error);
  }
}

async function loadLeaveRequests() {
  loading.value = true;
  error.value = null;
  try {
    const response = await getLeaveRequests({
      status: filterStatus.value || undefined,
      leave_type: filterType.value || undefined,
    });
    leaveRequests.value = response.items;
  } catch (e) {
    error.value = 'Daten konnten nicht geladen werden.';
  } finally {
    loading.value = false;
  }
}

async function handleCreateRequest() {
  try {
    await createLeaveRequest(newRequest.value);
    showCreateForm.value = false;
    resetForm();
    await loadLeaveRequests();
  } catch (error) {
    console.error('Failed to create leave request:', error);
    toast.error('Fehler beim Erstellen des Antrags');
  }
}

async function handleDeleteRequest(id: string) {
  if (!confirm('Möchten Sie diesen Antrag wirklich löschen?')) return;

  try {
    await deleteLeaveRequest(id);
    await loadLeaveRequests();
  } catch (error) {
    console.error('Failed to delete leave request:', error);
    toast.error('Fehler beim Löschen des Antrags');
  }
}

function resetForm() {
  newRequest.value = {
    employee_id: '',
    leave_type: 'vacation',
    start_date: '',
    end_date: '',
    half_day_start: false,
    half_day_end: false,
    reason: '',
  };
}

function openDetails(request: LeaveRequest) {
  router.push(`/app/hr/leave/requests/${request.id}`);
}

const getStatusColor = (status: LeaveStatus): string => {
  const colors: Record<LeaveStatus, string> = {
    pending:   'badge badge-amber',
    approved:  'badge badge-green',
    rejected:  'badge badge-red',
    cancelled: 'badge badge-gray',
  };
  return colors[status] || 'badge badge-gray';
};

const getStatusLabel = (status: LeaveStatus): string => {
  const labels: Record<LeaveStatus, string> = {
    pending: 'Ausstehend',
    approved: 'Genehmigt',
    rejected: 'Abgelehnt',
    cancelled: 'Storniert',
  };
  return labels[status] || status;
};

const getLeaveTypeLabel = (type: LeaveType): string => {
  const labels: Record<LeaveType, string> = {
    vacation: 'Urlaub',
    sick: 'Krankheit',
    personal: 'Persönlich',
    unpaid: 'Unbezahlt',
    parental: 'Elternzeit',
    bereavement: 'Trauerfall',
    other: 'Sonstiges',
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
  <div class="leave-management">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-white">Urlaubsverwaltung</h1>
      <button
        @click="showCreateForm = !showCreateForm"
        class="kit-btn-primary"
      >
        <Plus :size="20" />
        Neuer Antrag
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="kit-card p-6 mb-6">
      <h3 class="text-xl font-semibold text-white mb-4">Neuer Urlaubsantrag</h3>
      <form @submit.prevent="handleCreateRequest" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Leave Type -->
          <div>
            <label class="kit-label">Typ</label>
            <select
              v-model="newRequest.leave_type"
              class="kit-input"
              required
            >
              <option value="vacation">Urlaub</option>
              <option value="sick">Krankheit</option>
              <option value="personal">Persönlich</option>
              <option value="unpaid">Unbezahlt</option>
              <option value="parental">Elternzeit</option>
              <option value="bereavement">Trauerfall</option>
              <option value="other">Sonstiges</option>
            </select>
          </div>

          <!-- Employee Selection -->
          <div>
            <label class="kit-label">Mitarbeiter ({{ employees.length }} verfügbar)</label>
            <select
              v-model="newRequest.employee_id"
              class="kit-input"
              required
            >
              <option value="">Mitarbeiter auswählen</option>
              <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                {{ emp.first_name }} {{ emp.last_name }} - {{ emp.employee_code }}
              </option>
            </select>
          </div>

          <!-- Start Date -->
          <div>
            <label class="kit-label">Startdatum</label>
            <input
              v-model="newRequest.start_date"
              type="date"
              class="kit-input"
              required
            />
          </div>

          <!-- End Date -->
          <div>
            <label class="kit-label">Enddatum</label>
            <input
              v-model="newRequest.end_date"
              type="date"
              class="kit-input"
              required
            />
          </div>
        </div>

        <!-- Half Day Options -->
        <div class="flex gap-6">
          <label class="flex items-center gap-2 text-white cursor-pointer">
            <input
              v-model="newRequest.half_day_start"
              type="checkbox"
              class="w-4 h-4 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-2 focus:ring-blue-500"
            />
            <span>Halber Tag am Start (Nachmittag)</span>
          </label>
          <label class="flex items-center gap-2 text-white cursor-pointer">
            <input
              v-model="newRequest.half_day_end"
              type="checkbox"
              class="w-4 h-4 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-2 focus:ring-blue-500"
            />
            <span>Halber Tag am Ende (Vormittag)</span>
          </label>
        </div>

        <!-- Reason -->
        <div>
          <label class="kit-label">Grund (optional)</label>
          <textarea
            v-model="newRequest.reason"
            class="kit-input"
            rows="3"
            placeholder="Grund für den Antrag..."
          ></textarea>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <button type="submit" class="kit-btn-success">
            Antrag erstellen
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
        <!-- Search -->
        <div class="relative">
          <Search :size="20" class="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Suchen..."
            class="kit-input pl-10"
          />
        </div>

        <!-- Status Filter -->
        <div>
          <select
            v-model="filterStatus"
            @change="loadLeaveRequests"
            class="kit-input"
          >
            <option value="">Alle Status</option>
            <option value="pending">Ausstehend</option>
            <option value="approved">Genehmigt</option>
            <option value="rejected">Abgelehnt</option>
            <option value="cancelled">Storniert</option>
          </select>
        </div>

        <!-- Type Filter -->
        <div>
          <select
            v-model="filterType"
            @change="loadLeaveRequests"
            class="kit-input"
          >
            <option value="">Alle Typen</option>
            <option value="vacation">Urlaub</option>
            <option value="sick">Krankheit</option>
            <option value="personal">Persönlich</option>
            <option value="unpaid">Unbezahlt</option>
            <option value="parental">Elternzeit</option>
            <option value="bereavement">Trauerfall</option>
            <option value="other">Sonstiges</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Leave Requests List -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-white/60">Lade Anträge...</div>
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="kit-card p-6 text-center">
      <p class="text-red-400 text-sm">{{ error }}</p>
      <button class="kit-btn-secondary mt-3 text-xs" @click="loadLeaveRequests()">Erneut versuchen</button>
    </div>

    <div v-else-if="leaveRequests.length === 0" class="kit-card p-12 text-center">
      <Calendar :size="64" class="mx-auto text-white/40 mb-4" />
      <p class="text-white/60 text-lg">Keine Urlaubsanträge gefunden</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
      <div
        v-for="request in leaveRequests"
        :key="request.id"
        :id="`request-${request.id}`"
        @click="openDetails(request)"
        :class="[
          'kit-card p-6 hover:bg-white/15 transition-all duration-500 cursor-pointer',
          highlightedRequestId === request.id ? 'ring-4 ring-blue-500 bg-blue-500/20 scale-105' : ''
        ]"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-semibold text-white mb-2">
              {{ getLeaveTypeLabel(request.leave_type) }}
            </h3>
            <p class="text-white/60">
              {{ formatDate(request.start_date) }} - {{ formatDate(request.end_date) }}
              <span class="text-white/80 ml-2">({{ request.total_days }} Tage)</span>
            </p>
            <div v-if="request.half_day_start || request.half_day_end" class="flex gap-2 mt-2">
              <span v-if="request.half_day_start" class="badge badge-blue">
                ½ Tag Start
              </span>
              <span v-if="request.half_day_end" class="badge badge-blue">
                ½ Tag Ende
              </span>
            </div>
          </div>
          <span :class="getStatusColor(request.status)">
            {{ getStatusLabel(request.status) }}
          </span>
        </div>

        <div v-if="request.reason" class="text-white/80 mb-4">
          <strong>Grund:</strong> {{ request.reason }}
        </div>

        <div class="flex justify-between items-center text-sm text-white/60">
          <span>Erstellt: {{ formatDate(request.created_at) }}</span>
          <button
            v-if="request.status === 'pending'"
            @click.stop="handleDeleteRequest(request.id)"
            class="kit-btn-danger text-sm py-1"
          >
            Löschen
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.leave-management {
  max-width: 1200px;
  margin: 0 auto;
}

select option {
  background-color: #1e293b;
  color: white;
}
</style>
