<template>
  <div
    class="p-5 rounded-xl bg-bg-secondary border border-white/10 text-white shadow-soft cursor-pointer hover:bg-bg-secondary/80 transition space-y-2"
    @click="$emit('click')"
  >
    <!-- Name -->
    <h2 class="text-xl font-semibold leading-tight">
      {{ customer.name }}
    </h2>

    <!-- Customer Number -->
    <p class="text-white/50 text-sm">
      Kunden-Nr:
      <span class="text-white">
        {{ customer.customer_number || "– keine Nummer –" }}
      </span>
    </p>

    <!-- Email -->
    <p v-if="customer.email" class="text-white/70 text-sm">
      📧 {{ customer.email }}
    </p>

    <!-- Phone -->
    <p v-if="customer.phone" class="text-white/70 text-sm">
      📞 {{ customer.phone }}
    </p>

    <!-- Location -->
    <p v-if="customer.city || customer.zip" class="text-white/60 text-xs pt-1">
      📍 {{ customer.zip || "" }} {{ customer.city || "" }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type { Customer } from "../types/customer";

defineProps<{
  customer: Customer;
}>();

defineEmits(["click"]);
</script>
