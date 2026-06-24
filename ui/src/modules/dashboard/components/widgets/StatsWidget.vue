<template>
  <kitPanel title="Quick Stats" variant="default">
    <!-- Schützt vor NULL -->
    <div v-if="data">
      <ul class="text-text-secondary text-sm space-y-2">
        <li class="flex items-center gap-2">
          <span class="text-accent-primary">●</span>
          <span>Active Projects: <strong>{{ data.activeProjects }}</strong></span>
        </li>
        <li class="flex items-center gap-2">
          <span class="text-accent-primary">●</span>
          <span>Pending Invoices: <strong>{{ data.pendingInvoices }}</strong></span>
        </li>
        <li class="flex items-center gap-2">
          <span class="text-accent-primary">●</span>
          <span>Customers: <strong>{{ data.registeredCustomers }}</strong></span>
        </li>
      </ul>
    </div>

    <!-- Loading Placeholder statt Crash -->
    <div v-else class="text-text-secondary text-sm opacity-60">
      Loading stats…
    </div>
  </kitPanel>
</template>

<script setup lang="ts">
interface StatsData {
  activeProjects: number
  pendingInvoices: number
  registeredCustomers: number
}

const props = defineProps<{
  data: StatsData | null
}>()
</script>
