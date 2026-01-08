<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Calendar, Users, Clock, TrendingUp } from 'lucide-vue-next';
import { getLeaveStatistics, getEmployeeStatistics } from '../services/hr.service';
import type { LeaveStatistics, EmployeeStatistics } from '../types';

const loading = ref(true);
const leaveStats = ref<LeaveStatistics | null>(null);
const employeeStats = ref<EmployeeStatistics | null>(null);

onMounted(async () => {
  try {
    const [leave, employees] = await Promise.all([
      getLeaveStatistics(),
      getEmployeeStatistics(),
    ]);
    leaveStats.value = leave;
    employeeStats.value = employees;
  } catch (error) {
    console.error('Failed to load HR statistics:', error);
  } finally {
    loading.value = false;
  }
});

const getLeaveTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
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
</script>

<template>
  <div class="hr-dashboard">
    <h1 class="text-3xl font-bold text-white mb-6">HR Dashboard</h1>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-white/60">Lade Statistiken...</div>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="space-y-6">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Total Employees -->
        <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <Users :size="32" class="text-blue-400" />
          </div>
          <h3 class="text-white/60 text-sm mb-1">Mitarbeiter</h3>
          <p class="text-3xl font-bold text-white">
            {{ employeeStats?.total_employees || 0 }}
          </p>
          <p class="text-green-400 text-sm mt-2">
            {{ employeeStats?.active_employees || 0 }} aktiv
          </p>
        </div>

        <!-- Pending Leave Requests -->
        <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <Clock :size="32" class="text-yellow-400" />
          </div>
          <h3 class="text-white/60 text-sm mb-1">Offene Anträge</h3>
          <p class="text-3xl font-bold text-white">
            {{ leaveStats?.pending_requests || 0 }}
          </p>
          <p class="text-white/60 text-sm mt-2">
            Warten auf Genehmigung
          </p>
        </div>

        <!-- Approved Requests -->
        <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <TrendingUp :size="32" class="text-green-400" />
          </div>
          <h3 class="text-white/60 text-sm mb-1">Genehmigte Anträge</h3>
          <p class="text-3xl font-bold text-white">
            {{ leaveStats?.approved_requests || 0 }}
          </p>
          <p class="text-white/60 text-sm mt-2">
            Dieses Jahr
          </p>
        </div>

        <!-- Total Requests -->
        <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <Calendar :size="32" class="text-purple-400" />
          </div>
          <h3 class="text-white/60 text-sm mb-1">Anträge Gesamt</h3>
          <p class="text-3xl font-bold text-white">
            {{ leaveStats?.total_requests || 0 }}
          </p>
          <p class="text-white/60 text-sm mt-2">
            Alle Status
          </p>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Leave Requests by Type -->
        <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <h3 class="text-xl font-semibold text-white mb-4">Anträge nach Typ</h3>
          <div v-if="leaveStats?.by_type" class="space-y-3">
            <div
              v-for="(count, type) in leaveStats.by_type"
              :key="type"
              class="flex items-center justify-between"
            >
              <span class="text-white/80">{{ getLeaveTypeLabel(type) }}</span>
              <span class="text-white font-semibold">{{ count }}</span>
            </div>
          </div>
          <div v-else class="text-white/60">Keine Daten verfügbar</div>
        </div>

        <!-- Employees by Department -->
        <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <h3 class="text-xl font-semibold text-white mb-4">Mitarbeiter nach Abteilung</h3>
          <div v-if="employeeStats?.by_department" class="space-y-3">
            <div
              v-for="(count, dept) in employeeStats.by_department"
              :key="dept"
              class="flex items-center justify-between"
            >
              <span class="text-white/80">{{ dept }}</span>
              <span class="text-white font-semibold">{{ count }}</span>
            </div>
          </div>
          <div v-else class="text-white/60">Keine Daten verfügbar</div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
        <h3 class="text-xl font-semibold text-white mb-4">Schnellzugriff</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            class="bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 px-4 py-3 rounded-lg transition-colors border border-blue-500/30"
          >
            🌴 Neuer Urlaubsantrag
          </button>
          <button
            class="bg-green-500/20 hover:bg-green-500/30 text-green-300 px-4 py-3 rounded-lg transition-colors border border-green-500/30"
          >
            ✅ Anträge genehmigen
          </button>
          <button
            class="bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 px-4 py-3 rounded-lg transition-colors border border-purple-500/30"
          >
            👥 Neuer Mitarbeiter
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hr-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
