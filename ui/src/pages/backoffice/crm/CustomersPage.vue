<template>
  <div class="customers-page">
    <!-- Page Container - wie MainPage -->
    <div class="page-container">
      <!-- Header Panel - im Welcome Panel Style -->
      <kitPanel variant="glass" class="header-panel">
        <div class="header-content">
          <div class="header-text">
            <h1 class="page-title">Customers</h1>
            <p class="page-description">
              Manage your customer relationships and track interactions
            </p>
          </div>

          <kitButtons
            label="New Customer"
            variant="primary"
            size="md"
            :icon="Plus"
            @click="showCreateModal = true"
            class="create-btn"
          />
        </div>
      </kitPanel>

      <!-- Search & Filter Panel -->
      <kitPanel variant="default" class="search-panel">
        <div class="search-content">
          <!-- Search Input -->
          <div class="search-wrapper">
            <Search class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search customers by name, email, or company..."
              class="search-input"
              @input="debouncedSearch"
            />
          </div>

          <!-- Status Filter -->
          <div class="filter-group">
            <label class="filter-label">Status</label>
            <select
              v-model="statusFilter"
              @change="loadCustomers"
              class="filter-select"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="lead">Lead</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>

          <!-- Quick Stats (Optional) -->
          <div class="quick-stats">
            <div class="stat-item">
              <div class="stat-value">{{ customers.length }}</div>
              <div class="stat-label">Total</div>
            </div>
          </div>
        </div>
      </kitPanel>

      <!-- Customer Table Panel -->
      <kitPanel variant="default" class="table-panel">
        <template #title>
          <div class="panel-header">
            <svg class="header-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span>Customer List</span>
          </div>
        </template>

        <CustomerTable
          :customers="customers"
          :loading="loading"
          :error="error"
          @view="viewCustomer"
          @edit="editCustomer"
          @delete="confirmDelete"
          @retry="loadCustomers"
        />
      </kitPanel>
    </div>

    <!-- Create/Edit Modal -->
    <CustomerFormModal
      v-if="showCreateModal"
      :customer="selectedCustomer"
      @close="closeModal"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Plus, Search } from "lucide-vue-next";
import kitPanel from "@/components/system/kit-panel.vue";
import kitButtons from "@/components/system/kit-buttons.vue";
import CustomerTable from "@/components/backoffice/crm/CustomerTable.vue";
import CustomerFormModal from "@/components/backoffice/crm/CustomerFormModal.vue";
import { useCustomers } from "@/composables/useCustomers";
import type { Customer } from "@/types/api";

const router = useRouter();
const { customers, loading, error, fetchCustomers, deleteCustomer } =
  useCustomers();

const searchQuery = ref("");
const statusFilter = ref("");
const showCreateModal = ref(false);
const selectedCustomer = ref<Customer | null>(null);

let searchTimeout: ReturnType<typeof setTimeout>;
const debouncedSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadCustomers();
  }, 300);
};

const loadCustomers = async () => {
  await fetchCustomers({
    search: searchQuery.value || undefined,
    status: statusFilter.value || undefined,
  });
};

const viewCustomer = (customerId: string) => {
  router.push(`/backoffice/crm/customers/${customerId}`);
};

const editCustomer = (customer: Customer) => {
  selectedCustomer.value = customer;
  showCreateModal.value = true;
};

const confirmDelete = async (customer: Customer) => {
  if (confirm(`Are you sure you want to delete ${customer.name}?`)) {
    try {
      await deleteCustomer(customer.id);
    } catch (err) {
      console.error("Delete failed:", err);
    }
  }
};

const closeModal = () => {
  showCreateModal.value = false;
  selectedCustomer.value = null;
};

const handleSuccess = () => {
  closeModal();
  loadCustomers();
};

onMounted(() => {
  loadCustomers();
});
</script>

<style scoped>
/* ============================================================
   PAGE CONTAINER
   ============================================================ */
.customers-page {
  height: 100%;
  background: var(--color-bg-primary);
  overflow-y: auto;
}

/* Zentrierter Container wie MainPage */
.page-container {
  max-width: 1920px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* Custom Scrollbar */
.customers-page::-webkit-scrollbar {
  width: 8px;
}

.customers-page::-webkit-scrollbar-track {
  background: transparent;
}

.customers-page::-webkit-scrollbar-thumb {
  background: var(--color-border-primary);
  border-radius: 4px;
}

.customers-page::-webkit-scrollbar-thumb:hover {
  background: var(--color-accent-primary);
}

/* ============================================================
   HEADER PANEL
   ============================================================ */
.header-panel {
  margin-bottom: 1.5rem;
  padding: 2rem !important;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.page-description {
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.create-btn {
  flex-shrink: 0;
}

/* ============================================================
   SEARCH PANEL
   ============================================================ */
.search-panel {
  margin-bottom: 1.5rem;
  padding: 1.5rem !important;
}

.search-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Search Input */
.search-wrapper {
  position: relative;
  flex: 1;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-text-secondary);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--color-border-light);
  border-radius: 0.625rem;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  transition: all 200ms;
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 3px rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.1);
}

/* Filter Group */
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-select {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--color-border-light);
  border-radius: 0.625rem;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 200ms;
  min-width: 150px;
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  background: rgba(255, 255, 255, 0.06);
}

/* Quick Stats */
.quick-stats {
  display: flex;
  gap: 1.5rem;
  margin-left: auto;
  padding-left: 1.5rem;
  border-left: 1px solid var(--color-border-light);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-accent-primary);
  line-height: 1.2;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ============================================================
   TABLE PANEL
   ============================================================ */
.table-panel {
  padding: 1.5rem !important;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
}

.header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-accent-primary);
}

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 1200px) {
  .page-container {
    padding: 1.25rem;
  }

  .header-panel {
    padding: 1.75rem !important;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }

  .header-panel {
    padding: 1.5rem !important;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .create-btn {
    width: 100%;
  }

  .search-content {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    max-width: none;
  }

  .filter-group {
    width: 100%;
  }

  .quick-stats {
    margin-left: 0;
    padding-left: 0;
    border-left: none;
    border-top: 1px solid var(--color-border-light);
    padding-top: 1rem;
    width: 100%;
    justify-content: space-around;
  }

  .page-title {
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 0.75rem;
  }

  .header-panel,
  .search-panel,
  .table-panel {
    padding: 1.25rem !important;
  }

  .page-title {
    font-size: 1.125rem;
  }

  .page-description {
    font-size: 0.875rem;
  }
}
</style>
