<template>
  <div class="space-y-8 pb-10">

    <!-- Action Bar -->
    <div class="flex justify-between items-center gap-4">
      <!-- LEFT -->
      <h1 class="text-2xl font-bold text-white">Kontakte von {{ customer?.name }}</h1>

      <!-- RIGHT -->
      <div class="flex gap-2">
        <button
          class="px-4 py-2 rounded-md
                bg-blue-500/20 border border-blue-400/30
                text-sm text-blue-200
                hover:bg-blue-500/30 transition"
          @click="openCreateModal"
        >
          + Kontakt
        </button>

        <button
          class="px-4 py-2 rounded-md
                bg-white/10 border border-white/20
                text-sm text-white
                hover:bg-white/20 transition"
          @click="emit('back')"
        >
          ← Zurück
        </button>
      </div>
    </div>
    <div class="flex gap-3 items-center">
    <input
      v-model="search"
      type="text"
      placeholder="Suche nach Name oder E-Mail…"
      class="px-3 py-2 rounded-md
            bg-white/5 border border-white/10
            text-sm text-white placeholder:text-white/40
            focus:outline-none focus:border-white/30"
    />

    <label class="flex items-center gap-2 text-sm text-white/70">
      <input type="checkbox" v-model="showPrimaryOnly" />
      Nur Primary
    </label>
  </div>


    <!-- Loading -->
    <div v-if="isLoading" class="text-white/70">
      Kontakte werden geladen…
    </div>

    <div v-else-if="!filteredContacts.length" class="text-white/50">
      Keine Kontakte für diesen Kunden.
    </div>


    <!-- Contacts Grid -->
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <ContactCard
        v-for="c in paginatedContacts"
        :key="c.id"
        :contact="c"
        :customer-id="customerId"
        :is-primary="primaryContact?.id === c.id"
        @openContact="emit('openContact',c.id)"
        @edit="emit('openContact', c.id)"
        @delete="removeContact(c.id)"
        @setPrimary="setPrimary(c.id)"
      />


    </div>
    <div
      v-if="totalPages > 1"
      class="flex justify-center gap-2 mt-6"
    >
      <button
        v-for="p in totalPages"
        :key="p"
        @click="page = p"
        class="px-3 py-1.5 rounded-md text-sm
              border border-white/10
              hover:bg-white/10"
        :class="p === page ? 'bg-white/20 text-white' : 'text-white/60'"
      >
        {{ p }}
      </button>
    </div>

    <!-- Contact Modal -->
    <ContactForm
      v-if="showModal"
      :contact="selectedContact"
      :customer-id="customerId"
      @close="closeModal"
      @saved="reload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import type { Contact } from "../../types/contact";
import type { Customer } from "../../types/customer";
import { ContactForm, ContactCard } from "../../components";
import { crmService } from "../../services/crm.service";


const props = defineProps<{
  customerId : string;
}>();

const emit = defineEmits<{
  (e: "back"): void;
  (e: "openContact", contactId: string): void;
}>();

const contacts = ref<Contact[]>([]);
const customer = ref<Customer| null>(null);
const primaryContact = ref<Contact | null>(null);
const selectedContact = ref<Contact | null>(null);
const showModal = ref(false);
const isLoading = ref(true);
const search = ref("");
const showPrimaryOnly = ref(false);
const page = ref(1);
const pageSize = 6;


const filteredContacts = computed(() => {
  return contacts.value
    .filter(c => c.customer_id === props.customerId)
    .filter(c => {
      if (showPrimaryOnly.value && !c.is_primary) return false;

      if (!search.value) return true;
      const q = search.value.toLowerCase();
      return (
        c.firstname.toLowerCase().includes(q) ||
        c.lastname.toLowerCase().includes(q) ||
        c.email?.toLowerCase().includes(q)
      );
    });
});
const paginatedContacts = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filteredContacts.value.slice(start, start + pageSize);
});

const totalPages = computed(() =>
  Math.ceil(filteredContacts.value.length / pageSize)
);


function openCreateModal() {
  selectedContact.value = null;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
}

async function load() {
  try {
    isLoading.value = true;
    contacts.value = await crmService.getContacts();
    customer.value = await crmService.getCustomer(props.customerId);
    primaryContact.value = await crmService.getPrimaryContact(props.customerId);
  } finally {
    isLoading.value = false;
  }
}

async function reload() {
  await load();
}

async function removeContact(id: string) {
  if (!confirm("Kontakt wirklich löschen?")) return;
  await crmService.deleteContact(id);
  await load();
}

async function setPrimary(id: string) {
  await crmService.setPrimaryContact(props.customerId, id);
  await load();
}
watch([search, showPrimaryOnly], () => {
  page.value = 1;
});
onMounted(load);
</script>
