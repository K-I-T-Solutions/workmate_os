<template>
  <!-- Modal Overlay -->
  <div
    class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    @click.self="$emit('close')"
  >
    <!-- Modal Content -->
    <div class="bg-[#2a2d3a] rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-border-light">
        <h2 class="text-xl font-bold text-text-primary">
          {{ isEdit ? 'Edit Customer' : 'New Customer' }}
        </h2>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-[rgba(255,255,255,0.1)] rounded-md transition-colors"
        >
          <X class="w-5 h-5 text-text-secondary" />
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
        <!-- Error Message -->
        <div v-if="error" class="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-md">
          <p class="text-red-400 text-sm">{{ error }}</p>
        </div>

        <div class="space-y-4">
          <!-- Name (Required) -->
          <div>
            <label class="block text-text-primary text-sm font-medium mb-1">
              Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] border border-border-light rounded-md text-text-primary placeholder-text-secondary focus:outline-none focus:border-accent-primary transition-colors"
              placeholder="Company or person name"
            />
          </div>

          <!-- Type & Status -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-text-primary text-sm font-medium mb-1">Type</label>
              <select
                v-model="form.type"
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] border border-border-light rounded-md text-text-primary focus:outline-none focus:border-accent-primary transition-colors"
              >
                <option value="business">Business</option>
                <option value="individual">Individual</option>
                <option value="government">Government</option>
              </select>
            </div>
            <div>
              <label class="block text-text-primary text-sm font-medium mb-1">Status</label>
              <select
                v-model="form.status"
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] border border-border-light rounded-md text-text-primary focus:outline-none focus:border-accent-primary transition-colors"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="lead">Lead</option>
                <option value="blocked">Blocked</option>
              </select>
            </div>
          </div>

          <!-- Email & Phone -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-text-primary text-sm font-medium mb-1">Email</label>
              <input
                v-model="form.email"
                type="email"
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] border border-border-light rounded-md text-text-primary placeholder-text-secondary focus:outline-none focus:border-accent-primary transition-colors"
                placeholder="customer@example.com"
              />
            </div>
            <div>
              <label class="block text-text-primary text-sm font-medium mb-1">Phone</label>
              <input
                v-model="form.phone"
                type="tel"
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] border border-border-light rounded-md text-text-primary placeholder-text-secondary focus:outline-none focus:border-accent-primary transition-colors"
                placeholder="+49 123 456789"
              />
            </div>
          </div>


            <div>
              <label class="block text-text-primary text-sm font-medium mb-1">City</label>
              <input
                v-model="form.city"
                type="text"
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] border border-border-light rounded-md text-text-primary placeholder-text-secondary focus:outline-none focus:border-accent-primary transition-colors"
                placeholder="Berlin"
              />
            </div>
        </div>

</form>
      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-border-light">
        <kitButtons
          label="Cancel"
          variant="ghost"
          size="md"
          @click="$emit('close')"
          :disabled="loading"
        />
        <kitButtons
          :label="isEdit ? 'Update Customer' : 'Create Customer'"
          variant="primary"
          size="md"
          @click="handleSubmit"
          :loading="loading"
          :disabled="loading"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { X } from 'lucide-vue-next';
import kitButtons from '@/components/system/kit-buttons.vue';
import { useCustomers } from '@/composables/useCustomers';
import type { Customer } from '@/types/api';

const props = defineProps<{
  customer?: Customer | null;
}>();

const emit = defineEmits<{
  close: [];
  success: [];
}>();

const { createCustomer, updateCustomer } = useCustomers();

const isEdit = computed(() => !!props.customer);

const loading = ref(false);
const error = ref<string | null>(null);

const form = ref({
  name: '',
  type: 'business',
  status: 'active',
  email: '',
  phone: '',
  city: ''
})
// Load customer data if editing
onMounted(() => {
  if (props.customer) {
    form.value = {
      name: props.customer.name || '',
      type: props.customer.type || 'business',
      status: props.customer.status || 'active',
      email: props.customer.email || '',
      phone: props.customer.phone || '',
      city: props.customer.city || '',
    };
  }
});

const handleSubmit = async () => {
  loading.value = true;
  error.value = null;

  try {
    if (isEdit.value && props.customer) {
      await updateCustomer(props.customer.id, form.value);
    } else {
      await createCustomer(form.value);
    }
    emit('success');
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'An error occurred';
  } finally {
    loading.value = false;
  }
};
</script>
