<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Plus, X, Calendar, CheckCircle, Clock, XCircle, Ban } from 'lucide-vue-next';
import {
  getMyLeaveRequests,
  createMyLeaveRequest,
  cancelMyLeaveRequest,
  getMyLeaveBalance,
} from '../services/hr.service';
import type { LeaveRequest, LeaveRequestCreate, LeaveStatus } from '../types';

const currentYear = new Date().getFullYear();

const loading = ref(true);
const requests = ref<LeaveRequest[]>([]);
const balance = ref<any>(null);
const showCreateForm = ref(false);
const filterStatus = ref<LeaveStatus | ''>('');
const submitting = ref(false);
const error = ref<string | null>(null);

const newRequest = ref<LeaveRequestCreate>({
  employee_id: '',
  leave_type: 'vacation',
  start_date: '',
  end_date: '',
  half_day_start: false,
  half_day_end: false,
  reason: '',
});

const leaveTypeLabels: Record<string, string> = {
  vacation: 'Urlaub',
  sick: 'Krankheit',
  personal: 'Persönlich',
  unpaid: 'Unbezahlt',
  parental: 'Elternzeit',
  bereavement: 'Trauerfall',
  training: 'Weiterbildung',
  remote: 'Remote',
  other: 'Sonstiges',
};

const statusConfig: Record<string, { label: string; icon: any; class: string }> = {
  pending:   { label: 'Ausstehend',  icon: Clock,        class: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30' },
  approved:  { label: 'Genehmigt',   icon: CheckCircle,  class: 'text-green-300 bg-green-500/10 border-green-500/30' },
  rejected:  { label: 'Abgelehnt',   icon: XCircle,      class: 'text-red-300 bg-red-500/10 border-red-500/30' },
  cancelled: { label: 'Storniert',   icon: Ban,          class: 'text-white/40 bg-white/5 border-white/10' },
};

const filteredRequests = computed(() =>
  filterStatus.value
    ? requests.value.filter(r => r.status === filterStatus.value)
    : requests.value
);

const vacationPercent = computed(() => {
  if (!balance.value || !balance.value.vacation_total) return 0;
  return Math.round((Number(balance.value.vacation_used) / Number(balance.value.vacation_total)) * 100);
});

onMounted(async () => {
  await Promise.all([loadRequests(), loadBalance()]);
  loading.value = false;
});

async function loadRequests() {
  try {
    const data = await getMyLeaveRequests({ limit: 100 });
    requests.value = (data.items || data as any).sort(
      (a: LeaveRequest, b: LeaveRequest) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  } catch {
    requests.value = [];
  }
}

async function loadBalance() {
  try {
    balance.value = await getMyLeaveBalance(currentYear);
  } catch {
    balance.value = null;
  }
}

async function submitRequest() {
  if (!newRequest.value.start_date || !newRequest.value.end_date) return;
  submitting.value = true;
  error.value = null;
  try {
    await createMyLeaveRequest(newRequest.value);
    showCreateForm.value = false;
    newRequest.value = { employee_id: '', leave_type: 'vacation', start_date: '', end_date: '', half_day_start: false, half_day_end: false, reason: '' };
    await Promise.all([loadRequests(), loadBalance()]);
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Fehler beim Erstellen des Antrags';
  } finally {
    submitting.value = false;
  }
}

async function cancelRequest(id: string) {
  try {
    await cancelMyLeaveRequest(id);
    await Promise.all([loadRequests(), loadBalance()]);
  } catch {
    // ignore
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
</script>

<template>
  <div class="space-y-6">

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <template v-else>

      <!-- Balance Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">

        <!-- Urlaub -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-white/60">Urlaubstage {{ currentYear }}</span>
            <span class="text-xs text-white/40">{{ balance ? `${balance.vacation_used} / ${balance.vacation_total}` : '–' }}</span>
          </div>
          <div class="text-3xl font-bold text-white mb-2">
            {{ balance ? balance.vacation_remaining : '–' }}
            <span class="text-sm font-normal text-white/50 ml-1">verbleibend</span>
          </div>
          <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div
              class="h-full bg-blue-400 rounded-full transition-all"
              :style="{ width: `${vacationPercent}%` }"
            />
          </div>
        </div>

        <!-- Krankheit -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-white/60">Krankheitstage {{ currentYear }}</span>
            <span class="text-xs text-white/40">{{ balance ? `${balance.sick_used} / ${balance.sick_total}` : '–' }}</span>
          </div>
          <div class="text-3xl font-bold text-white">
            {{ balance ? Number(balance.sick_total) - Number(balance.sick_used) : '–' }}
            <span class="text-sm font-normal text-white/50 ml-1">verbleibend</span>
          </div>
        </div>

        <!-- Anträge -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-white/60">Meine Anträge</span>
          </div>
          <div class="flex gap-3 text-sm">
            <span class="text-yellow-300">{{ requests.filter(r => r.status === 'pending').length }} ausstehend</span>
            <span class="text-green-300">{{ requests.filter(r => r.status === 'approved').length }} genehmigt</span>
          </div>
        </div>
      </div>

      <!-- Header + Actions -->
      <div class="flex items-center justify-between">
        <div class="flex gap-2">
          <select v-model="filterStatus" class="kit-input">
            <option value="">Alle Status</option>
            <option value="pending">Ausstehend</option>
            <option value="approved">Genehmigt</option>
            <option value="rejected">Abgelehnt</option>
            <option value="cancelled">Storniert</option>
          </select>
        </div>
        <button
          @click="showCreateForm = true"
          class="flex items-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 text-blue-300 rounded-lg transition-colors text-sm"
        >
          <Plus :size="16" />
          Neuer Antrag
        </button>
      </div>

      <!-- Create Form -->
      <div v-if="showCreateForm" class="p-5 rounded-xl bg-white/5 border border-blue-400/20">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-white">Urlaubsantrag stellen</h3>
          <button @click="showCreateForm = false" class="text-white/40 hover:text-white">
            <X :size="18" />
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-white/60 mb-1 block">Art</label>
            <select v-model="newRequest.leave_type" class="kit-input w-full">
              <option v-for="(label, type) in leaveTypeLabels" :key="type" :value="type">{{ label }}</option>
            </select>
          </div>
          <div class="flex items-end gap-2">
            <div class="flex-1">
              <label class="text-xs text-white/60 mb-1 block">Von</label>
              <input v-model="newRequest.start_date" type="date" class="kit-input w-full" />
            </div>
            <div class="flex-1">
              <label class="text-xs text-white/60 mb-1 block">Bis</label>
              <input v-model="newRequest.end_date" type="date" class="kit-input w-full" />
            </div>
          </div>
          <div class="sm:col-span-2">
            <label class="text-xs text-white/60 mb-1 block">Begründung (optional)</label>
            <textarea
              v-model="newRequest.reason"
              rows="2"
              placeholder="Kurze Begründung..."
              class="kit-input w-full resize-none placeholder-white/30"
            />
          </div>
          <div class="sm:col-span-2 flex gap-4">
            <label class="flex items-center gap-2 text-sm text-white/70 cursor-pointer">
              <input v-model="newRequest.half_day_start" type="checkbox" class="rounded" />
              Halber erster Tag
            </label>
            <label class="flex items-center gap-2 text-sm text-white/70 cursor-pointer">
              <input v-model="newRequest.half_day_end" type="checkbox" class="rounded" />
              Halber letzter Tag
            </label>
          </div>
        </div>

        <div v-if="error" class="mt-3 text-sm text-red-400">{{ error }}</div>

        <div class="flex justify-end gap-3 mt-4">
          <button
            @click="showCreateForm = false"
            class="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors"
          >
            Abbrechen
          </button>
          <button
            @click="submitRequest"
            :disabled="submitting || !newRequest.start_date || !newRequest.end_date"
            class="px-4 py-2 bg-blue-500/30 hover:bg-blue-500/40 border border-blue-400/30 text-blue-300 rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ submitting ? 'Wird gesendet...' : 'Antrag stellen' }}
          </button>
        </div>
      </div>

      <!-- Request List -->
      <div class="space-y-3">
        <div v-if="filteredRequests.length === 0" class="text-center py-10 text-white/40">
          <Calendar :size="32" class="mx-auto mb-2 opacity-50" />
          <p>Keine Anträge vorhanden</p>
        </div>

        <div
          v-for="req in filteredRequests"
          :key="req.id"
          class="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between gap-4"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div
              class="w-2 h-2 rounded-full flex-shrink-0"
              :class="{
                'bg-yellow-400': req.status === 'pending',
                'bg-green-400': req.status === 'approved',
                'bg-red-400': req.status === 'rejected',
                'bg-white/20': req.status === 'cancelled',
              }"
            />
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-sm font-medium text-white">{{ leaveTypeLabels[req.leave_type] || req.leave_type }}</span>
                <span class="text-xs text-white/40">{{ formatDate(req.start_date) }} – {{ formatDate(req.end_date) }}</span>
                <span class="text-xs text-white/40">{{ req.total_days }} Tag(e)</span>
              </div>
              <div class="flex items-center gap-2 mt-0.5">
                <span
                  class="text-xs px-2 py-0.5 rounded border"
                  :class="statusConfig[req.status]?.class"
                >
                  {{ statusConfig[req.status]?.label || req.status }}
                </span>
                <span v-if="req.reason" class="text-xs text-white/40 truncate">{{ req.reason }}</span>
              </div>
              <div v-if="req.rejection_reason" class="text-xs text-red-400 mt-1">
                Ablehnungsgrund: {{ req.rejection_reason }}
              </div>
            </div>
          </div>

          <button
            v-if="req.status === 'pending'"
            @click="cancelRequest(req.id)"
            class="flex-shrink-0 text-xs text-white/40 hover:text-red-400 transition-colors px-2 py-1 rounded hover:bg-red-500/10"
          >
            Stornieren
          </button>
        </div>
      </div>

    </template>
  </div>
</template>
