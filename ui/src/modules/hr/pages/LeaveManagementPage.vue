<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus, Calendar, Search, Filter } from 'lucide-vue-next';
import { getLeaveRequests, createLeaveRequest, deleteLeaveRequest } from '../services/hr.service';
import type { LeaveRequest, LeaveRequestCreate, LeaveType, LeaveStatus } from '../types';

const loading = ref(true);
const leaveRequests = ref<LeaveRequest[]>([]);
const showCreateForm = ref(false);
const searchQuery = ref('');
const filterStatus = ref<LeaveStatus | ''>('');
const filterType = ref<LeaveType | ''>('');

// Form data
const newRequest = ref<LeaveRequestCreate>({
  employee_id: '', // TODO: Get from current user
  leave_type: 'vacation',
  start_date: '',
  end_date: '',
  reason: '',
});

onMounted(async () => {
  await loadLeaveRequests();
});

async function loadLeaveRequests() {
  loading.value = true;
  try {
    const response = await getLeaveRequests({
      status: filterStatus.value || undefined,
      leave_type: filterType.value || undefined,
    });
    leaveRequests.value = response.items;
  } catch (error) {
    console.error('Failed to load leave requests:', error);
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
    alert('Fehler beim Erstellen des Antrags');
  }
}

async function handleDeleteRequest(id: string) {
  if (!confirm('Möchten Sie diesen Antrag wirklich löschen?')) return;

  try {
    await deleteLeaveRequest(id);
    await loadLeaveRequests();
  } catch (error) {
    console.error('Failed to delete leave request:', error);
    alert('Fehler beim Löschen des Antrags');
  }
}

function resetForm() {
  newRequest.value = {
    employee_id: '',
    leave_type: 'vacation',
    start_date: '',
    end_date: '',
    reason: '',
  };
}

const getStatusColor = (status: LeaveStatus): string => {
  const colors: Record<LeaveStatus, string> = {
    pending: 'text-yellow-400 bg-yellow-500/20',
    approved: 'text-green-400 bg-green-500/20',
    rejected: 'text-red-400 bg-red-500/20',
    cancelled: 'text-gray-400 bg-gray-500/20',
  };
  return colors[status] || 'text-gray-400 bg-gray-500/20';
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
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
      >
        <Plus :size="20" />
        Neuer Antrag
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20 mb-6">
      <h3 class="text-xl font-semibold text-white mb-4">Neuer Urlaubsantrag</h3>
      <form @submit.prevent="handleCreateRequest" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Leave Type -->
          <div>
            <label class="block text-white/80 mb-2">Typ</label>
            <select
              v-model="newRequest.leave_type"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
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

          <!-- Employee ID (Temp) -->
          <div>
            <label class="block text-white/80 mb-2">Mitarbeiter ID</label>
            <input
              v-model="newRequest.employee_id"
              type="text"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              placeholder="UUID des Mitarbeiters"
              required
            />
          </div>

          <!-- Start Date -->
          <div>
            <label class="block text-white/80 mb-2">Startdatum</label>
            <input
              v-model="newRequest.start_date"
              type="date"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              required
            />
          </div>

          <!-- End Date -->
          <div>
            <label class="block text-white/80 mb-2">Enddatum</label>
            <input
              v-model="newRequest.end_date"
              type="date"
              class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
              required
            />
          </div>
        </div>

        <!-- Reason -->
        <div>
          <label class="block text-white/80 mb-2">Grund (optional)</label>
          <textarea
            v-model="newRequest.reason"
            class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
            rows="3"
            placeholder="Grund für den Antrag..."
          ></textarea>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Antrag erstellen
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
        <!-- Search -->
        <div class="relative">
          <Search :size="20" class="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Suchen..."
            class="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-2 text-white placeholder-white/40"
          />
        </div>

        <!-- Status Filter -->
        <div>
          <select
            v-model="filterStatus"
            @change="loadLeaveRequests"
            class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
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
            class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
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

    <div v-else-if="leaveRequests.length === 0" class="bg-white/10 backdrop-blur-lg rounded-lg p-12 border border-white/20 text-center">
      <Calendar :size="64" class="mx-auto text-white/40 mb-4" />
      <p class="text-white/60 text-lg">Keine Urlaubsanträge gefunden</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
      <div
        v-for="request in leaveRequests"
        :key="request.id"
        class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20 hover:bg-white/15 transition-colors"
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
          </div>
          <span
            :class="[
              'px-3 py-1 rounded-full text-sm font-semibold',
              getStatusColor(request.status)
            ]"
          >
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
            @click="handleDeleteRequest(request.id)"
            class="text-red-400 hover:text-red-300 transition-colors"
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
