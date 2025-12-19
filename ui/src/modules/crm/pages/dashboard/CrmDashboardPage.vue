<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white">CRM - Startseite</h1>
    </div>

    <!-- 4x4 Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-1.5 auto-rows-[140px]">
      <!-- KPI -->
      <div class="rounded-xl border border-white/10 bg-white/5 p-4">
        <div
            class="cursor-pointer hover:bg-white/10 transition rounded-xl h-full"
            @click="emit('openCustomers')"
          >
            <KPICustomer />
          </div>

      </div>

      <!-- Platzhalter -->
      <div
          class="rounded-xl border border-dashed border-white/10
                bg-white/2 p-4 flex items-center justify-center
                text-xs text-white/30"
        >
          Coming soon
        </div>

      <div
          class="rounded-xl border border-dashed border-white/10
                bg-white/2 p-4 flex items-center justify-center
                text-xs text-white/30"
        >
          Coming soon
        </div>
      <div
          class="rounded-xl border border-dashed border-white/10
                bg-white/2 p-4 flex items-center justify-center
                text-xs text-white/30"
        >
          Coming soon
        </div>

      <!-- Activity (2x2) -->
      <div
        class="col-span-2 row-span-2 rounded-xl border border-white/10 bg-white/5 p-4"
      >
        <RecentActivities />
      </div>

      <!-- Shortcuts -->
      <div class="col-span-2 rounded-xl border border-white/10 bg-white/5 p-4">
        <Shortcuts
         @create-customer="emit('create-customer')"
    @create-contact="emit('create-contact')"/>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { KPICustomer, RecentActivities, Shortcuts } from "../../components";

const emit = defineEmits<{
  (e: "openCustomers"): void;
  (e: "create-customer"): void;
  (e: "create-contact"): void;
}>();
</script>
