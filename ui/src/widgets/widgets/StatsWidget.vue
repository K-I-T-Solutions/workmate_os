<template>
  <kitPanel title="Quick Stats" variant="default">
    <ul class="text-text-secondary text-sm space-y-2">
      <li class="flex items-center gap-2">
        <span class="text-accent-primary">●</span>
        <span
          >Active Projects: <strong>{{ data.activeProjects }}</strong></span
        >
      </li>
      <li class="flex items-center gap-2">
        <span class="text-accent-primary">●</span>
        <span
          >Pending Invoices: <strong>{{ data.pendingInvoices }}</strong></span
        >
      </li>
      <li class="flex items-center gap-2">
        <span class="text-accent-primary">●</span>
        <span
          >Customers: <strong>{{ data.registeredCustomers }}</strong></span
        >
      </li>
    </ul>
  </kitPanel>
</template>

<script setup lang="ts">
const props = defineProps({
  data: Object,
});
</script>
