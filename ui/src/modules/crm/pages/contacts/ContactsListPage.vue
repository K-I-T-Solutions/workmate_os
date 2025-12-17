<template>
  <div class="space-y-8 pb-10">
    <h1 class="text-2xl font-bold text-white">Kontakte</h1>

    <!-- Action Bar -->
    <div class="flex justify-between items-center">
      <button
        class="px-4 py-2 rounded bg-blue-500 border border-white/10 text-white hover:bg-bg-primary/80 transition"
        @click="openCreateModal"
      >
        + Kontakt hinzufügen
      </button>

      <button
        class="px-4 py-2 rounded bg-orange-400 border-white/10 text-white hover:bg-bg-secondary/80 transition"
        @click="emit('back')"
      >
        ← Zurück zum Kunden
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-white/70">Kontakte werden geladen...</div>

    <!-- Empty State -->
    <div v-else-if="filteredContacts.length === 0" class="text-white/50">
      Keine Kontakte für diesen Kunden.
    </div>

    <!-- Contacts Grid -->
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <ContactCard
        v-for="c in filteredContacts"
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
import { ref, onMounted, computed } from "vue";
import type { Contact } from "../../types/contact";
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
const primaryContact = ref<Contact | null>(null);
const selectedContact = ref<Contact | null>(null);
const showModal = ref(false);
const isLoading = ref(true);

const filteredContacts = computed(() =>
  contacts.value.filter(c => c.customer_id === props.customerId)
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

onMounted(load);
</script>
