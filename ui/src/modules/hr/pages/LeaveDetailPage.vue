<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ChevronLeft, Calendar, User, Clock, FileText, CheckCircle, AlertCircle, Hash } from 'lucide-vue-next';
import md5 from 'md5';
import { getLeaveRequest, deleteLeaveRequest, getEmployee } from '../services/hr.service';
import type { LeaveRequest, Employee } from '../types';

const props = defineProps<{ requestId: string }>();
const router = useRouter();

const loading = ref(true);
const request = ref<LeaveRequest | null>(null);
const employee = ref<Employee | null>(null);

const leaveTypeLabels: Record<string, string> = {
  vacation: 'Urlaub', sick: 'Krankheit', personal: 'Persönlich',
  unpaid: 'Unbezahlt', parental: 'Elternzeit', bereavement: 'Trauerfall',
  training: 'Weiterbildung', remote: 'Remote', other: 'Sonstiges',
};

const statusConfig: Record<string, { label: string; class: string }> = {
  pending:   { label: 'Ausstehend', class: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30' },
  approved:  { label: 'Genehmigt',  class: 'text-green-300 bg-green-500/10 border-green-500/30' },
  rejected:  { label: 'Abgelehnt', class: 'text-red-300 bg-red-500/10 border-red-500/30' },
  cancelled: { label: 'Storniert', class: 'text-white/40 bg-white/5 border-white/10' },
};

const emp = computed(() => employee.value || request.value?.employee || null);

const employeeName = computed(() => {
  if (!emp.value) return '–';
  return [emp.value.first_name, emp.value.last_name].filter(Boolean).join(' ') || emp.value.email;
});

function gravatarUrl(email?: string, size = 56): string {
  if (!email) return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=${size}`;
  return `https://www.gravatar.com/avatar/${md5(email.toLowerCase().trim())}?d=mp&s=${size}`;
}

function formatDate(d?: string) {
  if (!d) return '–';
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function formatDateTime(d?: string) {
  if (!d) return '–';
  return new Date(d).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

onMounted(async () => {
  try {
    request.value = await getLeaveRequest(props.requestId);
    if (request.value?.employee_id) {
      employee.value = await getEmployee(request.value.employee_id);
    }
  } catch {
    request.value = null;
  } finally {
    loading.value = false;
  }
});

async function handleDelete() {
  if (!confirm('Antrag wirklich löschen?')) return;
  await deleteLeaveRequest(props.requestId);
  goBack();
}

function goBack() {
  router.push('/app/hr/leave/requests');
}

function openEmployee() {
  if (request.value?.employee_id) {
    router.push(`/app/hr/employees/${request.value.employee_id}`);
  }
}
</script>

<template>
  <div class="space-y-4">

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <template v-else-if="request">

      <!-- Back + Header -->
      <div class="flex items-start gap-4">
        <button @click="goBack" class="mt-1 p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
          <ChevronLeft :size="20" />
        </button>

        <div class="flex-1 flex items-center gap-4">
          <!-- Employee Gravatar -->
          <img
            :src="gravatarUrl(emp?.email, 56)"
            :alt="employeeName"
            class="w-14 h-14 rounded-xl border border-white/10 object-cover flex-shrink-0 cursor-pointer hover:opacity-80 transition-opacity"
            @click="openEmployee"
          />

          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <h2 class="text-lg font-semibold text-white">
                {{ leaveTypeLabels[request.leave_type] || request.leave_type }}
              </h2>
              <span class="text-xs px-2 py-0.5 rounded border" :class="statusConfig[request.status]?.class">
                {{ statusConfig[request.status]?.label || request.status }}
              </span>
            </div>
            <div class="flex items-center gap-3 text-sm text-white/50 mt-0.5 flex-wrap">
              <span
                class="hover:text-blue-300 cursor-pointer transition-colors"
                @click="openEmployee"
              >{{ employeeName }}</span>
              <span v-if="emp?.department?.name" class="text-white/30">·</span>
              <span v-if="emp?.department?.name">{{ emp.department.name }}</span>
              <span class="text-white/30">·</span>
              <span class="flex items-center gap-1">
                <Hash :size="12" />{{ request.id.substring(0, 8) }}
              </span>
            </div>
          </div>

          <button
            v-if="request.status === 'pending'"
            @click="handleDelete"
            class="flex-shrink-0 px-3 py-1.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 border border-red-500/20 rounded-lg transition-colors"
          >
            Löschen
          </button>
        </div>
      </div>

      <!-- Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <!-- Zeitraum -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
          <div class="flex items-center gap-2 text-white/60 text-sm font-medium uppercase tracking-wide">
            <Calendar :size="14" />Zeitraum
          </div>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-white/50">Von</span>
              <span class="text-white font-medium">{{ formatDate(request.start_date) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/50">Bis</span>
              <span class="text-white font-medium">{{ formatDate(request.end_date) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/50">Dauer</span>
              <span class="text-white font-medium">{{ request.total_days }} Tag(e)</span>
            </div>
            <div v-if="request.half_day_start || request.half_day_end" class="flex gap-2 pt-1">
              <span v-if="request.half_day_start" class="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
                ½ Tag Start
              </span>
              <span v-if="request.half_day_end" class="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
                ½ Tag Ende
              </span>
            </div>
          </div>
        </div>

        <!-- Mitarbeiter -->
        <div
          class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3 cursor-pointer hover:bg-white/8 transition-colors"
          @click="openEmployee"
        >
          <div class="flex items-center gap-2 text-white/60 text-sm font-medium uppercase tracking-wide">
            <User :size="14" />Mitarbeiter
          </div>
          <div class="flex items-center gap-3">
            <img
              :src="gravatarUrl(emp?.email, 36)"
              :alt="employeeName"
              class="w-9 h-9 rounded-lg border border-white/10 object-cover flex-shrink-0"
            />
            <div class="min-w-0">
              <div class="text-sm font-medium text-white truncate">{{ employeeName }}</div>
              <div class="text-xs text-white/40 truncate">{{ emp?.email }}</div>
              <div v-if="emp?.bio" class="text-xs text-blue-400 truncate">{{ emp.bio }}</div>
            </div>
          </div>
        </div>

        <!-- Begründung -->
        <div v-if="request.reason" class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
          <div class="flex items-center gap-2 text-white/60 text-sm font-medium uppercase tracking-wide">
            <FileText :size="14" />Begründung
          </div>
          <p class="text-sm text-white/80 leading-relaxed">{{ request.reason }}</p>
        </div>

        <!-- Zeitstempel -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
          <div class="flex items-center gap-2 text-white/60 text-sm font-medium uppercase tracking-wide">
            <Clock :size="14" />Zeitstempel
          </div>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-white/50">Erstellt</span>
              <span class="text-white/80">{{ formatDateTime(request.created_at) }}</span>
            </div>
            <div v-if="request.approved_at" class="flex justify-between text-sm">
              <span class="text-white/50">Genehmigt</span>
              <span class="text-green-300">{{ formatDateTime(request.approved_at) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/50">Aktualisiert</span>
              <span class="text-white/80">{{ formatDateTime(request.updated_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Ablehnungsgrund -->
        <div
          v-if="request.status === 'rejected' && request.rejection_reason"
          class="p-4 rounded-xl bg-red-500/10 border border-red-500/30 space-y-2 sm:col-span-2"
        >
          <div class="flex items-center gap-2 text-red-400 text-sm font-medium uppercase tracking-wide">
            <AlertCircle :size="14" />Ablehnungsgrund
          </div>
          <p class="text-sm text-white/80">{{ request.rejection_reason }}</p>
        </div>

        <!-- Genehmigt Info -->
        <div
          v-if="request.status === 'approved'"
          class="p-4 rounded-xl bg-green-500/10 border border-green-500/30 space-y-2 sm:col-span-2"
        >
          <div class="flex items-center gap-2 text-green-400 text-sm font-medium uppercase tracking-wide">
            <CheckCircle :size="14" />Genehmigt
          </div>
          <p class="text-sm text-white/60">Antrag wurde genehmigt am {{ formatDate(request.approved_at) }}</p>
        </div>

      </div>
    </template>

    <div v-else class="text-center py-20 text-white/40">
      <Calendar :size="40" class="mx-auto mb-3 opacity-40" />
      <p>Urlaubsantrag nicht gefunden</p>
      <button @click="goBack" class="mt-4 text-sm text-blue-400 hover:text-blue-300">Zurück zur Liste</button>
    </div>

  </div>
</template>
