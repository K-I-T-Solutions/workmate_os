<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Check, X, Clock, Calendar, User, FileText, ChevronRight } from 'lucide-vue-next';
import md5 from 'md5';
import { getLeaveRequests, approveLeaveRequest, rejectLeaveRequest, getEmployee } from '../services/hr.service';
import type { LeaveRequest, Employee } from '../types';

const router = useRouter();
const loading = ref(true);
const pendingRequests = ref<LeaveRequest[]>([]);
const employeeCache = ref<Record<string, Employee>>({});
const showRejectDialog = ref(false);
const selectedRequest = ref<LeaveRequest | null>(null);
const rejectionReason = ref('');
const submitting = ref(false);

const leaveTypeLabels: Record<string, string> = {
  vacation: 'Urlaub', sick: 'Krankheit', personal: 'Persönlich',
  unpaid: 'Unbezahlt', parental: 'Elternzeit', bereavement: 'Trauerfall',
  training: 'Weiterbildung', remote: 'Remote', other: 'Sonstiges',
};

onMounted(async () => {
  await loadPendingRequests();
});

async function loadPendingRequests() {
  loading.value = true;
  try {
    const response = await getLeaveRequests({ status: 'pending' });
    pendingRequests.value = response.items;
    // Lade alle benötigten Employees
    const ids = [...new Set(response.items.map(r => r.employee_id).filter(Boolean))];
    await Promise.all(ids.map(async id => {
      if (!employeeCache.value[id]) {
        try { employeeCache.value[id] = await getEmployee(id); } catch { /* ignore */ }
      }
    }));
  } finally {
    loading.value = false;
  }
}

function emp(request: LeaveRequest): Employee | null {
  return employeeCache.value[request.employee_id] || null;
}

function empName(request: LeaveRequest): string {
  const e = emp(request);
  if (!e) return '–';
  return [e.first_name, e.last_name].filter(Boolean).join(' ') || e.email;
}

function gravatarUrl(email?: string, size = 40): string {
  if (!email) return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=${size}`;
  return `https://www.gravatar.com/avatar/${md5(email.toLowerCase().trim())}?d=mp&s=${size}`;
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

async function handleApprove(request: LeaveRequest) {
  submitting.value = true;
  try {
    await approveLeaveRequest(request.id, {});
    await loadPendingRequests();
  } catch {
    // ignore
  } finally {
    submitting.value = false;
  }
}

function openRejectDialog(request: LeaveRequest) {
  selectedRequest.value = request;
  rejectionReason.value = '';
  showRejectDialog.value = true;
}

async function handleReject() {
  if (!selectedRequest.value || !rejectionReason.value.trim()) return;
  submitting.value = true;
  try {
    await rejectLeaveRequest(selectedRequest.value.id, { rejection_reason: rejectionReason.value });
    showRejectDialog.value = false;
    selectedRequest.value = null;
    await loadPendingRequests();
  } finally {
    submitting.value = false;
  }
}

function openDetail(request: LeaveRequest) {
  router.push(`/app/hr/leave/requests/${request.id}`);
}
</script>

<template>
  <div class="space-y-4 max-w-4xl">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-white">Genehmigungen</h1>
        <p class="text-sm text-white/50 mt-0.5">Ausstehende Urlaubsanträge</p>
      </div>
      <span v-if="!loading" class="text-sm px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-300">
        {{ pendingRequests.length }} ausstehend
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <!-- Empty -->
    <div v-else-if="pendingRequests.length === 0" class="text-center py-16 text-white/40">
      <Clock :size="40" class="mx-auto mb-3 opacity-40" />
      <p class="font-medium">Keine ausstehenden Anträge</p>
      <p class="text-sm mt-1">Alle Anträge wurden bearbeitet</p>
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="request in pendingRequests"
        :key="request.id"
        class="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/8 transition-colors"
      >
        <div class="flex items-start gap-4">

          <!-- Gravatar -->
          <img
            :src="gravatarUrl(emp(request)?.email, 40)"
            :alt="empName(request)"
            class="w-10 h-10 rounded-lg border border-white/10 object-cover flex-shrink-0 mt-0.5 cursor-pointer"
            @click="openDetail(request)"
          />

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span
                    class="text-sm font-semibold text-white hover:text-blue-300 cursor-pointer transition-colors"
                    @click="openDetail(request)"
                  >{{ empName(request) }}</span>
                  <span v-if="emp(request)?.department?.name" class="text-xs text-white/40">
                    {{ emp(request)?.department?.name }}
                  </span>
                </div>
                <div class="flex items-center gap-2 mt-1 flex-wrap">
                  <span class="text-xs px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-300">
                    {{ leaveTypeLabels[request.leave_type] || request.leave_type }}
                  </span>
                  <span class="text-xs text-white/50 flex items-center gap-1">
                    <Calendar :size="11" />
                    {{ formatDate(request.start_date) }} – {{ formatDate(request.end_date) }}
                  </span>
                  <span class="text-xs font-medium text-white/80">{{ request.total_days }} Tag(e)</span>
                  <span v-if="request.half_day_start" class="text-xs text-white/40">½ Start</span>
                  <span v-if="request.half_day_end" class="text-xs text-white/40">½ Ende</span>
                </div>
                <div v-if="request.reason" class="mt-1.5 text-xs text-white/50 flex items-center gap-1">
                  <FileText :size="11" />{{ request.reason }}
                </div>
              </div>

              <button @click="openDetail(request)" class="text-white/30 hover:text-white/60 transition-colors flex-shrink-0">
                <ChevronRight :size="16" />
              </button>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 mt-3">
              <button
                @click="handleApprove(request)"
                :disabled="submitting"
                class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-green-500/15 hover:bg-green-500/25 border border-green-500/25 text-green-300 rounded-lg transition-colors disabled:opacity-50"
              >
                <Check :size="13" />Genehmigen
              </button>
              <button
                @click="openRejectDialog(request)"
                :disabled="submitting"
                class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-red-500/15 hover:bg-red-500/25 border border-red-500/25 text-red-300 rounded-lg transition-colors disabled:opacity-50"
              >
                <X :size="13" />Ablehnen
              </button>
              <span class="text-xs text-white/30 ml-auto">{{ formatDate(request.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Dialog -->
    <div
      v-if="showRejectDialog && selectedRequest"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="showRejectDialog = false"
    >
      <div class="w-full max-w-md p-5 rounded-xl bg-slate-800 border border-white/10 shadow-2xl">
        <div class="flex items-center gap-3 mb-4">
          <img
            :src="gravatarUrl(emp(selectedRequest)?.email, 36)"
            class="w-9 h-9 rounded-lg border border-white/10 object-cover"
          />
          <div>
            <div class="text-sm font-semibold text-white">{{ empName(selectedRequest) }}</div>
            <div class="text-xs text-white/50">
              {{ leaveTypeLabels[selectedRequest.leave_type] }} · {{ selectedRequest.total_days }} Tag(e)
            </div>
          </div>
        </div>
        <label class="text-xs text-white/60 mb-1.5 block">Ablehnungsgrund *</label>
        <textarea
          v-model="rejectionReason"
          class="kit-input w-full resize-none mb-4"
          rows="3"
          placeholder="Grund für die Ablehnung..."
          autofocus
        />
        <div class="flex gap-2">
          <button
            @click="handleReject"
            :disabled="submitting || !rejectionReason.trim()"
            class="flex-1 flex items-center justify-center gap-1.5 py-2 text-sm bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 text-red-300 rounded-lg transition-colors disabled:opacity-50"
          >
            <X :size="14" />Ablehnen
          </button>
          <button
            @click="showRejectDialog = false"
            class="px-4 py-2 text-sm text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            Abbrechen
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
