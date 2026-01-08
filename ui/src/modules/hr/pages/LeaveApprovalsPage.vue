<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Check, X, Clock } from 'lucide-vue-next';
import { getLeaveRequests, approveLeaveRequest, rejectLeaveRequest } from '../services/hr.service';
import type { LeaveRequest, LeaveType } from '../types';

const loading = ref(true);
const pendingRequests = ref<LeaveRequest[]>([]);
const showRejectDialog = ref(false);
const selectedRequest = ref<LeaveRequest | null>(null);
const rejectionReason = ref('');

onMounted(async () => {
  await loadPendingRequests();
});

async function loadPendingRequests() {
  loading.value = true;
  try {
    const response = await getLeaveRequests({
      status: 'pending',
    });
    pendingRequests.value = response.items;
  } catch (error) {
    console.error('Failed to load pending requests:', error);
  } finally {
    loading.value = false;
  }
}

async function handleApprove(request: LeaveRequest) {
  if (!confirm(`Möchten Sie den Antrag von ${request.employee?.first_name} ${request.employee?.last_name} genehmigen?`)) {
    return;
  }

  try {
    await approveLeaveRequest(request.id, {
      approver_id: 'current-user-id', // TODO: Get from auth
    });
    await loadPendingRequests();
  } catch (error) {
    console.error('Failed to approve request:', error);
    alert('Fehler beim Genehmigen des Antrags');
  }
}

function showRejectForm(request: LeaveRequest) {
  selectedRequest.value = request;
  showRejectDialog.value = true;
  rejectionReason.value = '';
}

async function handleReject() {
  if (!selectedRequest.value || !rejectionReason.value.trim()) {
    alert('Bitte geben Sie einen Grund für die Ablehnung an');
    return;
  }

  try {
    await rejectLeaveRequest(selectedRequest.value.id, {
      approver_id: 'current-user-id', // TODO: Get from auth
      rejection_reason: rejectionReason.value,
    });
    showRejectDialog.value = false;
    selectedRequest.value = null;
    rejectionReason.value = '';
    await loadPendingRequests();
  } catch (error) {
    console.error('Failed to reject request:', error);
    alert('Fehler beim Ablehnen des Antrags');
  }
}

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
  <div class="leave-approvals">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-white mb-2">Genehmigungen</h1>
      <p class="text-white/60">Ausstehende Urlaubsanträge genehmigen oder ablehnen</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-white/60">Lade ausstehende Anträge...</div>
    </div>

    <!-- Empty State -->
    <div v-else-if="pendingRequests.length === 0" class="bg-white/10 backdrop-blur-lg rounded-lg p-12 border border-white/20 text-center">
      <Clock :size="64" class="mx-auto text-white/40 mb-4" />
      <p class="text-white/60 text-lg">Keine ausstehenden Anträge</p>
      <p class="text-white/40 text-sm mt-2">Alle Urlaubsanträge wurden bereits bearbeitet</p>
    </div>

    <!-- Pending Requests List -->
    <div v-else class="grid grid-cols-1 gap-4">
      <div
        v-for="request in pendingRequests"
        :key="request.id"
        class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20"
      >
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1">
            <h3 class="text-xl font-semibold text-white mb-1">
              {{ request.employee?.first_name }} {{ request.employee?.last_name }}
            </h3>
            <p class="text-white/60 text-sm mb-3">
              {{ request.employee?.department }} • {{ request.employee?.position }}
            </p>
            <div class="flex items-center gap-4 text-white/80">
              <span class="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm font-semibold">
                {{ getLeaveTypeLabel(request.leave_type) }}
              </span>
              <span>{{ formatDate(request.start_date) }} - {{ formatDate(request.end_date) }}</span>
              <span class="text-white font-semibold">{{ request.total_days }} Tage</span>
            </div>
          </div>

          <span class="bg-yellow-500/20 text-yellow-300 px-3 py-1 rounded-full text-sm font-semibold">
            Ausstehend
          </span>
        </div>

        <!-- Reason -->
        <div v-if="request.reason" class="bg-white/5 rounded-lg p-4 mb-4">
          <h4 class="text-white/60 text-sm mb-2">Grund:</h4>
          <p class="text-white">{{ request.reason }}</p>
        </div>

        <!-- Metadata -->
        <div class="text-white/60 text-sm mb-4">
          <span>Beantragt am: {{ formatDate(request.created_at) }}</span>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button
            @click="handleApprove(request)"
            class="bg-green-500/20 hover:bg-green-500/30 text-green-300 px-6 py-2 rounded-lg transition-colors border border-green-500/30 flex items-center gap-2"
          >
            <Check :size="18" />
            Genehmigen
          </button>
          <button
            @click="showRejectForm(request)"
            class="bg-red-500/20 hover:bg-red-500/30 text-red-300 px-6 py-2 rounded-lg transition-colors border border-red-500/30 flex items-center gap-2"
          >
            <X :size="18" />
            Ablehnen
          </button>
        </div>
      </div>
    </div>

    <!-- Reject Dialog -->
    <div
      v-if="showRejectDialog"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showRejectDialog = false"
    >
      <div class="bg-slate-800 rounded-lg p-6 w-full max-w-md border border-white/20">
        <h3 class="text-xl font-semibold text-white mb-4">Antrag ablehnen</h3>
        <p class="text-white/60 mb-4">
          Bitte geben Sie einen Grund für die Ablehnung an:
        </p>
        <textarea
          v-model="rejectionReason"
          class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white mb-4"
          rows="4"
          placeholder="Grund für die Ablehnung..."
          autofocus
        ></textarea>
        <div class="flex gap-3">
          <button
            @click="handleReject"
            class="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg transition-colors flex-1"
          >
            Ablehnen
          </button>
          <button
            @click="showRejectDialog = false"
            class="bg-white/10 hover:bg-white/20 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Abbrechen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.leave-approvals {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
