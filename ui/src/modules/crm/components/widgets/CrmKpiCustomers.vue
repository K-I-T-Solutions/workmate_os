<template>
  <div
    class="h-full flex flex-col justify-between cursor-pointer select-none"
  >
    <div class="text-sm text-white/60">
      Aktive Kunden
    </div>

    <div class="flex items-end justify-between">
      <div class="text-3xl font-semibold text-white">
        <span v-if="loading">–</span>
        <span v-else>{{ stats?.active_customers ?? 0 }}</span>
      </div>

      <div class="text-xs text-white/40">
        gesamt: {{ stats?.total_customers ?? 0 }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useCrmStats } from "../../composables/useCrmStats";

const { stats, loading, fetchStats } = useCrmStats();

onMounted(fetchStats);
</script>
