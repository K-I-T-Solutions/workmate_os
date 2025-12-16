<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white">CRM</h1>
    </div>

    <!-- Grid -->
    <div class="grid grid-cols-4 gap-1.5 auto-rows-[140px]">

      <!-- Chart -->
      <div class="col-span-2 row-span-2 rounded-xl border border-white/10 bg-white/5 p-4">
        <Chart />
      </div>

      <!-- Shortcuts -->
      <div class="col-span-2 rounded-xl border border-white/10 bg-white/5 p-4">
        <Shortcuts />
      </div>

      <!-- Platzhalter / später KPI -->
      <div class="rounded-xl border border-white/10 bg-white/5" />
      <div class="rounded-xl border border-white/10 bg-white/5" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Chart, Shortcuts } from "@/modules/dashboard/components/widgets";
import type widget
</script>
