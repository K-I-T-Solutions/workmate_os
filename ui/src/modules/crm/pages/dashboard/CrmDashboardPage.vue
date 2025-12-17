<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white">CRM - Startseite</h1>
    </div>

    <!-- 4x4 Grid -->
    <div class="grid grid-cols-4 gap-1.5 auto-rows-[140px]">
      <!-- KPI -->
      <div class="rounded-xl border border-white/10 bg-white/5 p-4">
        <KPICustomer @click="emit('openCustomers')" />
      </div>

      <!-- Platzhalter -->
      <div class="rounded-xl border border-white/10 bg-white/5 p-4" />
      <div class="rounded-xl border border-white/10 bg-white/5 p-4" />
      <div class="rounded-xl border border-white/10 bg-white/5 p-4" />

      <!-- Activity (2x2) -->
      <div
        class="col-span-2 row-span-2 rounded-xl border border-white/10 bg-white/5 p-4"
      >
        <RecentActivities />
      </div>

      <!-- Shortcuts -->
      <div class="col-span-2 rounded-xl border border-white/10 bg-white/5 p-4">
        <Shortcuts />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { KPICustomer, RecentActivities, Shortcuts } from "../../components";

const emit = defineEmits<{
  (e: "openCustomers"): void;
}>();
</script>
