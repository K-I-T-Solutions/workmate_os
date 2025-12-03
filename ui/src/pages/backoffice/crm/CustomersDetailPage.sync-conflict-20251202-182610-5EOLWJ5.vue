<template>
  <div class="customer-detail-page h-full flex flex-col p-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-500 mb-4">{{ error }}</p>
      <kitButtons label="Back to Customers" variant="secondary" size="md" @click="goBack" />
    </div>

    <!-- Customer Details -->
    <div v-else-if="customer" class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <button
            @click="goBack"
            class="p-2 hover:bg-[rgba(255,255,255,0.1)] rounded-md transition-colors"
          >
            <ArrowLeft class="w-5 h-5 text-text-secondary" />
          </button>
          <div>
            <h1 class="text-2xl font-bold text-text-primary">{{ customer.name }}</h1>
            <p class="text-text-secondary text-sm mt-1">
              Customer ID: {{ customer.id.substring(0, 8) }}...
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <kitButtons
            label="Edit"
            variant="secondary"
            size="md"
            :icon="Edit"
            @click="showEditModal = true"
          />
          <kitButtons
            label="Delete"
            variant="ghost"
            size="md"
            :icon="Trash2"
            @click="confirmDelete"
          />
        </div>
      </div>

      <!-- Status Badge -->
      <div>
        <span
          class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
          :class="getStatusClass(customer.status)"
        >
          {{ customer.status }}
        </span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column - Customer Info -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Contact Information -->
          <kitPanel title="Contact Information" variant="default">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-text-secondary text-xs font-medium mb-1">Email</label>
                <p class="text-text-primary">{{ customer.email || '-' }}</p>
              </div>
              <div>
                <label class="block text-text-secondary text-xs font-medium mb-1">Phone</label>
                <p class="text-text-primary">{{ customer.phone || '-' }}</p>
              </div>
              <div>
                <label class="block text-text-secondary text-xs font-medium mb-1">Website</label>

                  v-if="customer.website"
                  :href="customer.website"
                  target="_blank"
                  class="text-accent-primary hover:underline"
                >
                  {{ customer.website }}
                </a>
                <p v-else class="text-text-primary">-</p>
              </div>
              <div>
                <label class="block text-text-secondary text-xs font-medium mb-1">Type</label>
                <p class="text-text-primary capitalize">{{ customer.type || '-' }}</p>
              </div>
            </div>
          </kitPanel>

          <!-- Address -->
          <kitPanel title="Address" variant="default">
            <div class="space-y-2">
              <p class="text-text-primary">{{ customer.street || '-' }}</p>
              <p class="text-text-primary">
                {{ customer.zip_code ? `${customer.zip_code} ` : '' }}{{ customer.city || '' }}
              </p>
              <p class="text-text-primary">{{ customer.country || '-' }}</p>
            </div>
          </kitPanel>

          <!-- Notes -->
          <kitPanel title="Notes" variant="default">
            <p class="text-text-secondary whitespace-pre-wrap">
              {{ customer.notes || 'No notes available.' }}
            </p>
          </kitPanel>
        </div>

        <!-- Right Column - Additional Info -->
        <div class="space-y-6">
          <!-- Business Details -->
          <kitPanel title="Business Details" variant="default">
            <div class="space-y-3">
              <div>
                <label class="block text-text-secondary text-xs font-medium mb-1">Tax ID</label>
                <p class="text-text-primary">{{ customer.tax_id || '-' }}</p>
              </div>
              <div>
                <label class="block text-text-secondary text-xs font-medium mb-1">Created</label>
                <p class="text-text-primary text-sm">
                  {{ formatDate(customer.created_at) }}
                </p>
              </div>
              <div>
                <label class="block text-text-secondary text-xs font-medium mb-1">Last Updated</label>
                <p class="text-text-primary text-sm">
                  {{ formatDate(customer.updated_at) }}
                </p>
              </div>
            </div>
          </kitPanel>

          <!-- Quick Actions -->
          <kitPanel title="Quick Actions" variant="default">
            <div class="space-y-2">
              <button
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] hover:bg-[rgba(255,255,255,0.1)] rounded-md text-text-primary text-sm transition-colors text-left flex items-center gap-2"
              >
                <FileText class="w-4 h-4" />
                Create Invoice
              </button>
              <button
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] hover:bg-[rgba(255,255,255,0.1)] rounded-md text-text-primary text-sm transition-colors text-left flex items-center gap-2"
              >
                <Briefcase class="w-4 h-4" />
                Create Project
              </button>
              <button
                class="w-full px-4 py-2 bg-[rgba(255,255,255,0.06)] hover:bg-[rgba(255,255,255,0.1)] rounded-md text-text-primary text-sm transition-colors text-left flex items-center gap-2"
              >
                <Mail class="w-4 h-4" />
                Send Email
              </button>
            </div>
          </kitPanel>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <CustomerFormModal
      v-if="showEditModal && customer"
      :customer="customer"
      @close="showEditModal = false"
      @success="handleEditSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ArrowLeft, Edit, Trash2, FileText, Briefcase, Mail } from 'lucide-vue-next';
import kitPanel from '@/components/system/kit-panel.vue';
import kitButtons from '@/components/system/kit-buttons.vue';
import CustomerFormModal from '@/components/backoffice/crm/CustomerFormModal.vue';
import { useCustomers } from '@/composables/useCustomers';

const router = useRouter();
const route = useRoute();
const { customer, loading, error, fetchCustomer, deleteCustomer } = useCustomers();

const showEditModal = ref(false);

const customerId = route.params.id as string;

const loadCustomer = async () => {
  if (customerId) {
    await fetchCustomer(customerId);
  }
};

const goBack = () => {
  router.push('/backoffice/crm');
};

const confirmDelete = async () => {
  if (!customer.value) return;

  if (confirm(`Are you sure you want to delete ${customer.value.name}?`)) {
    try {
      await deleteCustomer(customer.value.id);
      goBack();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  }
};

const handleEditSuccess = () => {
  showEditModal.value = false;
  loadCustomer();
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

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

onMounted(() => {
  loadCustomer();
});
</script>
