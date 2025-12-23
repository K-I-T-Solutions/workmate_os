<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useCustomers } from '../../composables/useCustomers';
import type { CustomerFilters } from '../../composables/useCustomers';
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Filter,
  Users,
  Mail,
  Phone,
  MapPin,
  Trash2,
  Eye,
  X,
} from 'lucide-vue-next';

// Props & Emits
const emit = defineEmits<{
  openCustomer: [id: string];
  openDashboard: [];
}>();

// Composables
const {
  customers,
  total,
  page: currentPage,
  pages,
  limit,
  loading,
  error,
  isEmpty,
  loadCustomers,
  deleteCustomer,
} = useCustomers();

// ─── FILTER STATE ─────────────────────────────────────────
const searchQuery = ref('');
const selectedStatus = ref<string>('');

// ─── LIFECYCLE ────────────────────────────────────────────
onMounted(() => {
  applyFilters();
});

// ─── COMPUTED ─────────────────────────────────────────────
const hasFilters = computed(() => {
  return !!(selectedStatus.value || searchQuery.value);
});

// ─── ACTIONS ──────────────────────────────────────────────
async function applyFilters() {
  const filters: CustomerFilters = {
    skip: (currentPage.value - 1) * limit.value,
    limit: limit.value,
  };

  if (selectedStatus.value) {
    filters.status = selectedStatus.value;
  }

  if (searchQuery.value) {
    filters.search = searchQuery.value;
  }

  await loadCustomers(filters);
}

function clearFilters() {
  selectedStatus.value = '';
  searchQuery.value = '';
  applyFilters();
}

function goToPage(pageNum: number) {
  if (pageNum >= 1 && pageNum <= pages.value) {
    applyFilters();
  }
}

// Delete confirmation
const deleteConfirmId = ref<string | null>(null);

function showDeleteConfirm(customerId: string) {
  deleteConfirmId.value = customerId;
}

async function confirmDelete() {
  if (deleteConfirmId.value) {
    const success = await deleteCustomer(deleteConfirmId.value);
    if (success) {
      deleteConfirmId.value = null;
      applyFilters();
    }
  }
}

// ─── HELPERS ──────────────────────────────────────────────
function getStatusBadge(status: string) {
  const badges = {
    active: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    inactive: 'bg-white/5 border-white/10 text-white/60',
    lead: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    blocked: 'bg-red-500/20 border-red-400/30 text-red-200',
  };
  return badges[status as keyof typeof badges] || badges.inactive;
}

function getStatusLabel(status: string): string {
  const labels = {
    active: 'Aktiv',
    inactive: 'Inaktiv',
    lead: 'Lead',
    blocked: 'Blockiert',
  };
  return labels[status as keyof typeof labels] || 'Inaktiv';
}

function getTypeBadge(type: string | null) {
  const badges = {
    creator: 'bg-purple-500/20 border-purple-400/30 text-purple-200',
    individual: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    business: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    government: 'bg-orange-500/20 border-orange-400/30 text-orange-200',
  };
  return type ? (badges[type as keyof typeof badges] || badges.business) : badges.business;
}

function getTypeLabel(type: string | null): string {
  const labels = {
    creator: 'Creator',
    individual: 'Privatperson',
    business: 'Unternehmen',
    government: 'Behörde',
  };
  return type ? (labels[type as keyof typeof labels] || 'Unternehmen') : 'Unternehmen';
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('openDashboard')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white">Kunden</h1>
          <p class="text-sm text-white/60 mt-1">{{ total }} Kunden insgesamt</p>
        </div>
      </div>
      <button @click="$emit('openCustomer', 'create')" class="kit-btn-primary">
        <Plus :size="18" />
        Neuer Kunde
      </button>
    </div>

    <!-- Filters -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Status Filter -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Filter :size="14" />
            Status
          </label>
          <select
            v-model="selectedStatus"
            @change="applyFilters"
            class="kit-input"
          >
            <option value="">Alle Status</option>
            <option value="active">Aktiv</option>
            <option value="inactive">Inaktiv</option>
            <option value="lead">Lead</option>
            <option value="blocked">Blockiert</option>
          </select>
        </div>

        <!-- Search -->
        <div class="sm:col-span-2">
          <label class="kit-label">Suche</label>
          <input
            v-model="searchQuery"
            @input="applyFilters"
            type="text"
            placeholder="Name, E-Mail oder Kundennummer..."
            class="kit-input"
          />
        </div>
      </div>

      <!-- Clear Filters -->
      <button
        v-if="hasFilters"
        @click="clearFilters"
        class="kit-btn-ghost mt-3 text-sm"
      >
        <X :size="16" />
        Filter zurücksetzen
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Kunden...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1">
      <div class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <p class="text-red-200">{{ error }}</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <Users :size="64" class="mx-auto text-white/20 mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Keine Kunden gefunden</h3>
        <p class="text-white/60 mb-6">
          {{ hasFilters ? 'Keine Kunden entsprechen den Filterkriterien' : 'Erstellen Sie Ihren ersten Kunden' }}
        </p>
        <button v-if="!hasFilters" @click="$emit('openCustomer', 'create')" class="kit-btn-primary">
          <Plus :size="18" />
          Ersten Kunden erstellen
        </button>
      </div>
    </div>

    <!-- Customer List -->
    <div v-else class="flex-1 overflow-auto">
      <div class="space-y-3">
        <div
          v-for="customer in customers"
          :key="customer.id"
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="emit('openCustomer', customer.id)"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Customer Info -->
            <div class="flex-1 min-w-0">
              <!-- Name + Status Badge -->
              <div class="flex items-center gap-3 mb-3">
                <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
                  <Users :size="18" class="text-blue-200" />
                </div>
                <span class="font-semibold text-lg text-white truncate">
                  {{ customer.name }}
                </span>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium border',
                    getStatusBadge(customer.status),
                  ]"
                >
                  {{ getStatusLabel(customer.status) }}
                </span>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium border',
                    getTypeBadge(customer.type),
                  ]"
                >
                  {{ getTypeLabel(customer.type) }}
                </span>
              </div>

              <!-- 3-column info grid -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                <div v-if="customer.email">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Mail :size="12" />
                    E-Mail
                  </div>
                  <div class="font-medium text-white truncate">{{ customer.email }}</div>
                </div>

                <div v-if="customer.phone">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Phone :size="12" />
                    Telefon
                  </div>
                  <div class="font-medium text-white">{{ customer.phone }}</div>
                </div>

                <div v-if="customer.city">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <MapPin :size="12" />
                    Stadt
                  </div>
                  <div class="font-medium text-white">{{ customer.city }}</div>
                </div>

                <div v-if="customer.customer_number">
                  <div class="text-white/50 text-xs">Kundennummer</div>
                  <div class="font-medium text-white font-mono text-xs">
                    {{ customer.customer_number }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Actions -->
            <div class="flex items-start gap-2">
              <button
                @click.stop="emit('openCustomer', customer.id)"
                class="p-2 hover:bg-blue-500/20 rounded-lg transition"
                title="Details anzeigen"
              >
                <Eye :size="18" class="text-blue-200" />
              </button>
              <button
                @click.stop="showDeleteConfirm(customer.id)"
                class="p-2 hover:bg-red-500/20 rounded-lg transition"
                title="Kunde löschen"
              >
                <Trash2 :size="18" class="text-red-200" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div
      v-if="!loading && !isEmpty"
      class="flex items-center justify-between text-sm text-white/60"
    >
      <div>
        Seite {{ currentPage }} von {{ pages }} ({{ total }} Kunden)
      </div>

      <div class="flex gap-2">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          :class="[
            'px-3 py-2 rounded-lg transition flex items-center gap-1',
            currentPage === 1
              ? 'opacity-30 cursor-not-allowed text-white/40'
              : 'kit-btn-ghost',
          ]"
        >
          <ChevronLeft :size="16" />
          Zurück
        </button>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === pages"
          :class="[
            'px-3 py-2 rounded-lg transition flex items-center gap-1',
            currentPage === pages
              ? 'opacity-30 cursor-not-allowed text-white/40'
              : 'kit-btn-ghost',
          ]"
        >
          Weiter
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteConfirmId"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="deleteConfirmId = null"
    >
      <div
        class="rounded-lg border border-white/10 bg-stone-900 p-6 max-w-md"
        @click.stop
      >
        <h3 class="text-xl font-bold text-white mb-2">Kunde löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie diesen Kunden wirklich löschen? Diese Aktion kann nicht
          rückgängig gemacht werden.
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="deleteConfirmId = null" class="kit-btn-ghost">
            Abbrechen
          </button>
          <button @click="confirmDelete" class="kit-btn-danger">
            <Trash2 :size="18" />
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Zusätzliche Styles falls benötigt */
</style>
