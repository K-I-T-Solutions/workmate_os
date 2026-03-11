<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  ChevronLeft, Mail, Phone, MapPin, Briefcase, Calendar,
  CheckCircle, Clock, XCircle, Ban, Building2, User, Hash,
} from 'lucide-vue-next';
import md5 from 'md5';

function gravatarUrl(email?: string, size = 56): string {
  if (!email) return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=${size}`;
  return `https://www.gravatar.com/avatar/${md5(email.toLowerCase().trim())}?d=mp&s=${size}`;
}
import {
  getEmployee,
  getLeaveRequests,
  getLeaveBalances,
} from '../services/hr.service';
import type { Employee, LeaveRequest } from '../types';

const props = defineProps<{ employeeId: string }>();
const router = useRouter();

const loading = ref(true);
const employee = ref<Employee | null>(null);
const leaveRequests = ref<LeaveRequest[]>([]);
const leaveBalance = ref<any>(null);
const activeTab = ref<'overview' | 'leave'>('overview');

const currentYear = new Date().getFullYear();

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

const employmentTypeLabels: Record<string, string> = {
  full_time: 'Vollzeit', part_time: 'Teilzeit', contract: 'Vertrag',
  intern: 'Praktikant', freelance: 'Freelancer',
};

const statusBadge = computed(() => {
  const s = employee.value?.status;
  if (s === 'active') return { label: 'Aktiv', class: 'text-green-300 bg-green-500/10 border-green-500/30' };
  if (s === 'on_leave') return { label: 'Im Urlaub', class: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30' };
  return { label: 'Inaktiv', class: 'text-white/40 bg-white/5 border-white/10' };
});

const fullName = computed(() =>
  [employee.value?.first_name, employee.value?.last_name].filter(Boolean).join(' ') || employee.value?.email || '–'
);

const vacationPercent = computed(() => {
  if (!leaveBalance.value?.length) return 0;
  const vac = leaveBalance.value.find((b: any) => b.leave_type === 'vacation');
  if (!vac || !vac.total_days) return 0;
  return Math.min(100, Math.round((vac.used_days / vac.total_days) * 100));
});

const vacationBalance = computed(() => leaveBalance.value?.find((b: any) => b.leave_type === 'vacation'));
const sickBalance = computed(() => leaveBalance.value?.find((b: any) => b.leave_type === 'sick'));

onMounted(async () => {
  await Promise.all([loadEmployee(), loadLeaveHistory(), loadBalance()]);
  loading.value = false;
});

async function loadEmployee() {
  try {
    employee.value = await getEmployee(props.employeeId);
  } catch {
    employee.value = null;
  }
}

async function loadLeaveHistory() {
  try {
    const data = await getLeaveRequests({ employee_id: props.employeeId, limit: 100 });
    leaveRequests.value = (data.items || data as any).sort(
      (a: LeaveRequest, b: LeaveRequest) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
    );
  } catch {
    leaveRequests.value = [];
  }
}

async function loadBalance() {
  try {
    const data = await getLeaveBalances({ employee_id: props.employeeId, year: currentYear });
    leaveBalance.value = data.items || data;
  } catch {
    leaveBalance.value = null;
  }
}

function formatDate(d?: string) {
  if (!d) return '–';
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function goBack() {
  router.push('/app/hr/employees');
}
</script>

<template>
  <div class="space-y-4">

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <template v-else-if="employee">

      <!-- Back + Header -->
      <div class="flex items-start gap-4">
        <button @click="goBack" class="mt-1 p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
          <ChevronLeft :size="20" />
        </button>

        <div class="flex-1 flex items-center gap-4">
          <!-- Avatar -->
          <img
            :src="gravatarUrl(employee.email, 56)"
            :alt="fullName"
            class="w-14 h-14 rounded-xl border border-white/10 flex-shrink-0 object-cover"
          />

          <div class="min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h2 class="text-lg font-semibold text-white">{{ fullName }}</h2>
              <span class="text-xs px-2 py-0.5 rounded border" :class="statusBadge.class">
                {{ statusBadge.label }}
              </span>
            </div>
            <div class="flex items-center gap-3 text-sm text-white/50 mt-0.5 flex-wrap">
              <span v-if="employee.bio" class="flex items-center gap-1">
                <Briefcase :size="13" />{{ employee.bio }}
              </span>
              <span v-if="employee.department?.name" class="flex items-center gap-1">
                <Building2 :size="13" />{{ employee.department.name }}
              </span>
              <span class="flex items-center gap-1">
                <Hash :size="13" />{{ employee.employee_code }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 border-b border-white/10 pb-0">
        <button
          v-for="tab in [{ id: 'overview', label: 'Überblick' }, { id: 'leave', label: 'Urlaub & Abwesenheit' }]"
          :key="tab.id"
          @click="activeTab = tab.id as any"
          :class="[
            'px-4 py-2 text-sm rounded-t-lg transition-colors -mb-px border-b-2',
            activeTab === tab.id
              ? 'text-blue-300 border-blue-400 bg-blue-500/10'
              : 'text-white/50 border-transparent hover:text-white hover:bg-white/5'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- TAB: Überblick -->
      <div v-if="activeTab === 'overview'" class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <!-- Kontakt -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
          <h3 class="text-sm font-medium text-white/60 uppercase tracking-wide">Kontakt</h3>
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-sm text-white/80">
              <Mail :size="14" class="text-white/40 flex-shrink-0" />
              <a :href="`mailto:${employee.email}`" class="hover:text-blue-300 truncate">{{ employee.email }}</a>
            </div>
            <div v-if="employee.phone" class="flex items-center gap-2 text-sm text-white/80">
              <Phone :size="14" class="text-white/40 flex-shrink-0" />
              <span>{{ employee.phone }}</span>
            </div>
            <div v-if="employee.address_city" class="flex items-center gap-2 text-sm text-white/80">
              <MapPin :size="14" class="text-white/40 flex-shrink-0" />
              <span>{{ [employee.address_street, employee.address_zip, employee.address_city].filter(Boolean).join(', ') }}</span>
            </div>
            <div v-if="employee.matrix_username" class="flex items-center gap-2 text-sm text-white/80">
              <span class="text-white/40 text-xs font-mono flex-shrink-0">[m]</span>
              <span class="font-mono text-xs">{{ employee.matrix_username }}</span>
            </div>
          </div>
        </div>

        <!-- Anstellung -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
          <h3 class="text-sm font-medium text-white/60 uppercase tracking-wide">Anstellung</h3>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-white/50">Typ</span>
              <span class="text-white/80">{{ employmentTypeLabels[employee.employment_type || ''] || employee.employment_type || '–' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/50">Eintrittsdatum</span>
              <span class="text-white/80">{{ formatDate(employee.hire_date) }}</span>
            </div>
            <div v-if="employee.termination_date" class="flex justify-between text-sm">
              <span class="text-white/50">Austrittsdatum</span>
              <span class="text-red-300">{{ formatDate(employee.termination_date) }}</span>
            </div>
            <div v-if="employee.role?.name" class="flex justify-between text-sm">
              <span class="text-white/50">Rolle</span>
              <span class="text-white/80">{{ employee.role.name }}</span>
            </div>
            <div v-if="employee.last_login" class="flex justify-between text-sm">
              <span class="text-white/50">Letzter Login</span>
              <span class="text-white/80">{{ formatDate(employee.last_login) }}</span>
            </div>
          </div>
        </div>

        <!-- Urlaubskonto aktuelles Jahr -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3 sm:col-span-2">
          <h3 class="text-sm font-medium text-white/60 uppercase tracking-wide">Urlaubskonto {{ currentYear }}</h3>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div v-if="vacationBalance">
              <div class="text-xs text-white/40 mb-1">Urlaub</div>
              <div class="text-2xl font-bold text-white">{{ vacationBalance.available_days ?? (vacationBalance.total_days - vacationBalance.used_days) }}</div>
              <div class="text-xs text-white/40">von {{ vacationBalance.total_days }} verbleibend</div>
              <div class="mt-2 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-blue-400 rounded-full" :style="{ width: `${vacationPercent}%` }" />
              </div>
            </div>
            <div v-if="sickBalance">
              <div class="text-xs text-white/40 mb-1">Krankheit</div>
              <div class="text-2xl font-bold text-white">{{ sickBalance.used_days }}</div>
              <div class="text-xs text-white/40">von {{ sickBalance.total_days }} genutzt</div>
            </div>
            <div v-if="!vacationBalance && !sickBalance" class="text-sm text-white/40 col-span-2">
              Kein Urlaubskonto für {{ currentYear }} vorhanden
            </div>
          </div>
        </div>

      </div>

      <!-- TAB: Urlaub & Abwesenheit -->
      <div v-if="activeTab === 'leave'" class="space-y-3">
        <div v-if="leaveRequests.length === 0" class="text-center py-10 text-white/40">
          <Calendar :size="32" class="mx-auto mb-2 opacity-50" />
          <p>Keine Urlaubsanträge vorhanden</p>
        </div>

        <div
          v-for="req in leaveRequests"
          :key="req.id"
          class="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between gap-4"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-2 h-2 rounded-full flex-shrink-0"
              :class="{
                'bg-yellow-400': req.status === 'pending',
                'bg-green-400': req.status === 'approved',
                'bg-red-400': req.status === 'rejected',
                'bg-white/20': req.status === 'cancelled',
              }"
            />
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap text-sm">
                <span class="font-medium text-white">{{ leaveTypeLabels[req.leave_type] || req.leave_type }}</span>
                <span class="text-white/40">{{ formatDate(req.start_date) }} – {{ formatDate(req.end_date) }}</span>
                <span class="text-white/40">{{ req.total_days }} Tag(e)</span>
              </div>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="text-xs px-2 py-0.5 rounded border" :class="statusConfig[req.status]?.class">
                  {{ statusConfig[req.status]?.label || req.status }}
                </span>
                <span v-if="req.reason" class="text-xs text-white/40 truncate">{{ req.reason }}</span>
              </div>
              <div v-if="req.rejection_reason" class="text-xs text-red-400 mt-1">
                Abgelehnt: {{ req.rejection_reason }}
              </div>
            </div>
          </div>
          <span class="text-xs text-white/30 flex-shrink-0">{{ formatDate(req.created_at) }}</span>
        </div>
      </div>

    </template>

    <!-- Not found -->
    <div v-else class="text-center py-20 text-white/40">
      <User :size="40" class="mx-auto mb-3 opacity-40" />
      <p>Mitarbeiter nicht gefunden</p>
      <button @click="goBack" class="mt-4 text-sm text-blue-400 hover:text-blue-300">Zurück zur Liste</button>
    </div>

  </div>
</template>
