<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useContacts } from '../../composables/useContacts';
import { useCustomers } from '../../composables/useCustomers';
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Filter,
  User,
  Mail,
  Phone,
  Trash2,
  Edit,
  X,
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  customerId: string;
}>();

// Emits
const emit = defineEmits<{
  openContact: [id: string];
  createContact: [];
  editContact: [id: string];
  back: [];
}>();

// Composables
const {
  contacts,
  loading: contactsLoading,
  error,
  loadContacts,
  deleteContact,
  setPrimaryContact,
  primaryContact,
} = useContacts();
const { currentCustomer, loadCustomer } = useCustomers();

// ─── FILTER STATE ─────────────────────────────────────────
const searchQuery = ref('');
const showPrimaryOnly = ref(false);
const currentPage = ref(1);
const pageSize = 10;

// ─── LIFECYCLE ────────────────────────────────────────────
onMounted(async () => {
  await loadCustomer(props.customerId);
  await loadContacts({ customerId: props.customerId });
});

// ─── COMPUTED ─────────────────────────────────────────────
const hasFilters = computed(() => {
  return !!(showPrimaryOnly.value || searchQuery.value);
});

const filteredContacts = computed(() => {
  let result = contacts.value;

  // Primary filter
  if (showPrimaryOnly.value) {
    result = result.filter((c) => c.is_primary);
  }

  // Search filter
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(
      (c) =>
        c.firstname.toLowerCase().includes(q) ||
        c.lastname.toLowerCase().includes(q) ||
        c.email?.toLowerCase().includes(q) ||
        c.phone?.toLowerCase().includes(q)
    );
  }

  return result;
});

const paginatedContacts = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return filteredContacts.value.slice(start, start + pageSize);
});

const totalPages = computed(() => Math.ceil(filteredContacts.value.length / pageSize));

const isEmpty = computed(() => filteredContacts.value.length === 0);

const customerName = computed(() => currentCustomer.value?.name || 'Kunde');

// ─── ACTIONS ──────────────────────────────────────────────
function clearFilters() {
  searchQuery.value = '';
  showPrimaryOnly.value = false;
  currentPage.value = 1;
}

function goToPage(pageNum: number) {
  if (pageNum >= 1 && pageNum <= totalPages.value) {
    currentPage.value = pageNum;
  }
}

// Delete confirmation
const deleteConfirmId = ref<string | null>(null);

function showDeleteConfirm(contactId: string) {
  deleteConfirmId.value = contactId;
}

async function confirmDelete() {
  if (deleteConfirmId.value) {
    const success = await deleteContact(deleteConfirmId.value);
    if (success) {
      deleteConfirmId.value = null;
      await loadContacts({ customerId: props.customerId });
    }
  }
}

async function handleSetPrimary(contactId: string) {
  await setPrimaryContact(props.customerId, contactId);
}

// ─── HELPERS ──────────────────────────────────────────────
function getFullName(contact: any): string {
  return `${contact.firstname} ${contact.lastname}`;
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white">Kontakte</h1>
          <p class="text-sm text-white/60 mt-1">von {{ customerName }}</p>
        </div>
      </div>
      <button @click="emit('createContact')" class="kit-btn-primary">
        <Plus :size="18" />
        Neuer Kontakt
      </button>
    </div>

    <!-- Filters -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <!-- Search -->
        <div>
          <label class="kit-label">Suche</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Name, E-Mail oder Telefon..."
            class="kit-input"
          />
        </div>

        <!-- Primary Filter -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Filter :size="14" />
            Filter
          </label>
          <label class="flex items-center gap-2 h-10 px-3 rounded-lg border border-white/10 bg-white/5 text-sm text-white cursor-pointer hover:bg-white/10 transition">
            <input
              v-model="showPrimaryOnly"
              type="checkbox"
              class="rounded"
            />
            Nur Primärkontakte anzeigen
          </label>
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
    <div v-if="contactsLoading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Kontakte...</p>
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
        <User :size="64" class="mx-auto text-white/20 mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Keine Kontakte gefunden</h3>
        <p class="text-white/60 mb-6">
          {{ hasFilters ? 'Keine Kontakte entsprechen den Filterkriterien' : 'Erstellen Sie den ersten Kontakt für diesen Kunden' }}
        </p>
        <button v-if="!hasFilters" @click="emit('createContact')" class="kit-btn-primary">
          <Plus :size="18" />
          Ersten Kontakt erstellen
        </button>
      </div>
    </div>

    <!-- Contacts List -->
    <div v-else class="flex-1 overflow-auto">
      <div class="space-y-3">
        <div
          v-for="contact in paginatedContacts"
          :key="contact.id"
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="emit('openContact', contact.id)"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Contact Info -->
            <div class="flex-1 min-w-0">
              <!-- Name + Primary Badge -->
              <div class="flex items-center gap-3 mb-3">
                <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
                  <User :size="18" class="text-blue-200" />
                </div>
                <span class="font-semibold text-lg text-white truncate">
                  {{ getFullName(contact) }}
                </span>
                <span
                  v-if="contact.is_primary"
                  class="px-2 py-1 rounded text-xs font-medium border bg-emerald-500/20 border-emerald-400/30 text-emerald-200"
                >
                  Primär
                </span>
              </div>

              <!-- 3-column info grid -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                <div v-if="contact.email">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Mail :size="12" />
                    E-Mail
                  </div>
                  <div class="font-medium text-white truncate">{{ contact.email }}</div>
                </div>

                <div v-if="contact.phone">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Phone :size="12" />
                    Telefon
                  </div>
                  <div class="font-medium text-white">{{ contact.phone }}</div>
                </div>

                <div v-if="contact.position">
                  <div class="text-white/50 text-xs">Position</div>
                  <div class="font-medium text-white truncate">{{ contact.position }}</div>
                </div>

                <div v-if="contact.department">
                  <div class="text-white/50 text-xs">Abteilung</div>
                  <div class="font-medium text-white truncate">{{ contact.department }}</div>
                </div>

                <div v-if="contact.mobile">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Phone :size="12" />
                    Mobil
                  </div>
                  <div class="font-medium text-white">{{ contact.mobile }}</div>
                </div>
              </div>
            </div>

            <!-- Right: Actions -->
            <div class="flex items-start gap-2">
              <button
                v-if="!contact.is_primary"
                @click.stop="handleSetPrimary(contact.id)"
                class="p-2 hover:bg-emerald-500/20 rounded-lg transition text-xs text-emerald-200"
                title="Als Primär setzen"
              >
                Als Primär
              </button>
              <button
                @click.stop="emit('editContact', contact.id)"
                class="p-2 hover:bg-blue-500/20 rounded-lg transition"
                title="Kontakt bearbeiten"
              >
                <Edit :size="18" class="text-blue-200" />
              </button>
              <button
                @click.stop="showDeleteConfirm(contact.id)"
                class="p-2 hover:bg-red-500/20 rounded-lg transition"
                title="Kontakt löschen"
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
      v-if="!contactsLoading && !isEmpty"
      class="flex items-center justify-between text-sm text-white/60"
    >
      <div>
        Seite {{ currentPage }} von {{ totalPages }} ({{ filteredContacts.length }} Kontakte)
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
          :disabled="currentPage === totalPages"
          :class="[
            'px-3 py-2 rounded-lg transition flex items-center gap-1',
            currentPage === totalPages
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
        <h3 class="text-xl font-bold text-white mb-2">Kontakt löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie diesen Kontakt wirklich löschen? Diese Aktion kann nicht
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
