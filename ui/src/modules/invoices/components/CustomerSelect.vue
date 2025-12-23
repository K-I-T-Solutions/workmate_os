<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useCustomers } from '../composables/useCustomers';
import { ChevronDown, Loader2 } from 'lucide-vue-next';

// Props & Emits
const props = defineProps<{
  modelValue: string;
  error?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

// Composables
const { customers, loading, loadCustomers } = useCustomers();

// Lifecycle
onMounted(() => {
  loadCustomers();
});

// Computed
const selectedCustomer = computed(() => {
  return customers.value.find((c) => c.id === props.modelValue);
});
</script>

<template>
  <div class="relative">
    <label class="kit-label">
      Kunde <span class="text-red-400">*</span>
    </label>

    <!-- Loading State -->
    <div v-if="loading" class="kit-input flex items-center gap-2">
      <Loader2 :size="16" class="animate-spin" />
      <span class="text-white/60">Lade Kunden...</span>
    </div>

    <!-- Dropdown -->
    <select
      v-else
      :value="modelValue"
      @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      class="kit-input"
      :class="{ 'border-red-400': error }"
    >
      <option value="">-- Kunde auswählen --</option>
      <option
        v-for="customer in customers"
        :key="customer.id"
        :value="customer.id"
      >
        {{ customer.name }}{{ customer.company ? ` (${customer.company})` : '' }}
      </option>
    </select>

    <!-- Error Message -->
    <p v-if="error" class="text-xs text-red-300 mt-1">
      {{ error }}
    </p>

    <!-- Selected Customer Info -->
    <p v-if="selectedCustomer" class="text-xs text-white/60 mt-1">
      {{ selectedCustomer.email || 'Keine E-Mail' }}
    </p>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
