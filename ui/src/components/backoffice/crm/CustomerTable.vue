<template>
  <kitPanel variant="default" class="flex-1 overflow-hidden flex flex-col">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-500 mb-4">{{ error }}</p>
      <kitButtons label="Retry" variant="secondary" size="sm" @click="$emit('retry')" />
    </div>

    <!-- Empty State -->
    <div v-else-if="customers.length === 0" class="text-center py-12">
      <Users class="w-16 h-16 text-text-secondary mx-auto mb-4 opacity-50" />
      <p class="text-text-secondary text-lg mb-2">No customers found</p>
      <p class="text-text-secondary text-sm">
        Get started by creating your first customer
      </p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto flex-1">
      <table class="w-full">
        <thead class="border-b border-border-light sticky top-0 bg-[#2a2d3a]">
          <tr>
            <th class="text-left py-3 px-4 text-text-secondary text-sm font-semibold">Name</th>
            <th class="text-left py-3 px-4 text-text-secondary text-sm font-semibold">Email</th>
            <th class="text-left py-3 px-4 text-text-secondary text-sm font-semibold">Phone</th>
            <th class="text-left py-3 px-4 text-text-secondary text-sm font-semibold">City</th>
            <th class="text-left py-3 px-4 text-text-secondary text-sm font-semibold">Status</th>
            <th class="text-left py-3 px-4 text-text-secondary text-sm font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="customer in customers"
            :key="customer.id"
            class="border-b border-border-light hover:bg-[rgba(255,255,255,0.03)] transition-colors cursor-pointer"
            @click="$emit('view', customer.id)"
          >
            <td class="py-3 px-4 text-text-primary font-medium">{{ customer.name }}</td>
            <td class="py-3 px-4 text-text-secondary">{{ customer.email || '-' }}</td>
            <td class="py-3 px-4 text-text-secondary">{{ customer.phone || '-' }}</td>
            <td class="py-3 px-4 text-text-secondary">{{ customer.city || '-' }}</td>
            <td class="py-3 px-4">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusClass(customer.status)"
              >
                {{ customer.status }}
              </span>
            </td>
            <td class="py-3 px-4" @click.stop>
              <div class="flex gap-2">
                <button
                  @click="$emit('view', customer.id)"
                  class="p-1.5 hover:bg-[rgba(255,255,255,0.1)] rounded transition-colors group"
                  title="View Details"
                >
                  <Eye class="w-4 h-4 text-text-secondary group-hover:text-accent-primary transition-colors" />
                </button>
                <button
                  @click="$emit('edit', customer)"
                  class="p-1.5 hover:bg-[rgba(255,255,255,0.1)] rounded transition-colors group"
                  title="Edit Customer"
                >
                  <Edit class="w-4 h-4 text-text-secondary group-hover:text-blue-400 transition-colors" />
                </button>
                <button
                  @click="$emit('delete', customer)"
                  class="p-1.5 hover:bg-red-500/20 rounded transition-colors group"
                  title="Delete Customer"
                >
                  <Trash2 class="w-4 h-4 text-text-secondary group-hover:text-red-400 transition-colors" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </kitPanel>
</template>

<script setup lang="ts">
import { Users, Eye, Edit, Trash2 } from 'lucide-vue-next';
import kitPanel from '@/components/system/kit-panel.vue';
import kitButtons from '@/components/system/kit-buttons.vue';
import type { Customer } from '@/types/api';

defineProps<{
  customers: Customer[];
  loading: boolean;
  error: string | null;
}>();

defineEmits<{
  view: [customerId: string];
  edit: [customer: Customer];
  delete: [customer: Customer];
  retry: [];
}>();

const getStatusClass = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-500/20 text-green-400';
    case 'inactive':
      return 'bg-gray-500/20 text-gray-400';
    case 'lead':
      return 'bg-blue-500/20 text-blue-400';
    case 'blocked':
      return 'bg-red-500/20 text-red-400';
    default:
      return 'bg-gray-500/20 text-gray-400';
  }
};
</script>
