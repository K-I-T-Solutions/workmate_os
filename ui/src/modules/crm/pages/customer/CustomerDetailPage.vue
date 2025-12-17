<template>
  <div class="space-y-6">

    <!-- HEADER / HERO -->
    <section class="kit-panel">
      <div class="flex justify-between items-start gap-6">
        <div class="space-y-1">
          <h1 class="text-2xl font-bold">
            {{ customer?.name ?? "Kunde" }}
          </h1>

          <p class="text-white/60 text-sm flex flex-wrap gap-x-2">
            <span v-if="customer?.email">{{ customer.email }}</span>
            <span v-if="customer?.phone">· {{ customer.phone }}</span>
            <span v-if="customer?.city">· {{ customer.city }}</span>
          </p>

          <p v-if="customer?.notes" class="text-white/50 text-sm mt-2">
            {{ customer.notes }}
          </p>
        </div>

        <div class="flex gap-2 shrink-0">
          <button class="btn-secondary" @click="$emit('back')">
            ← Zurück
          </button>
          <button
              class="btn-secondary"
              @click="$emit('openContacts', customerId)"
            >
              Kontakte
          </button>
          <button class="btn-primary" @click="openEdit">
            Bearbeiten
          </button>
        </div>
      </div>
    </section>


    <!-- CONTENT GRID -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- LEFT: CONTACTS -->
      <div class="lg:col-span-2 space-y-4">
        <h2 class="text-lg font-semibold">Kontakte</h2>

        <div v-if="isLoading" class="text-white/60">
          Kontakte werden geladen…
        </div>

        <div
          v-else-if="contacts.length === 0"
          class="text-white/50"
        >
          Keine Kontakte vorhanden.
        </div>

        <div v-else class="grid md:grid-cols-2 gap-4">
          <ContactCard
            v-for="c in customerContacts"
            :key="c.id"
            :contact="c"
            :customer-id="customerId"
            :is-primary="primaryContact?.id === c.id"
            @openDetail="onOpenContact"
            @edit="openEdit"
          />

        </div>
      </div>
      
      <!-- RIGHT: ACTIVITIES -->
      <aside class="space-y-4">
        <h2 class="text-lg font-semibold">Aktivitäten</h2>

        <div class="kit-card text-white/60">
          Rechnungen, Projekte & Events kommen hier rein.
        </div>
      </aside>

    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import type { Customer } from "../../types/customer";
import type { Contact } from "../../types/contact";
import { crmService } from "../../services/crm.service";
import { ContactCard } from "../../components";


const props = defineProps<{
  customerId: string;
}>();

const emit = defineEmits<{
  (e: "back"): void;
  (e: "openContacts", customerId: string): void;
  (e: "editCustomer", customerId: string): void;
  (e: "openContact", contactId: string):void;
}>();

const customer = ref<Customer | null>(null);
const contacts = ref<Contact[]>([]);
const primaryContact = ref<Contact | null>(null);
const isLoading = ref(true);

const customerContacts = computed(() =>
  contacts.value.filter(c => c.customer_id === props.customerId)
);

async function load() {
  try {
    isLoading.value = true;
    customer.value = await crmService.getCustomer(props.customerId);
    contacts.value = await crmService.getContacts();
    primaryContact.value =
      await crmService.getPrimaryContact(props.customerId);
  } finally {
    isLoading.value = false;
  }
}

function openEdit() {
  emit("editCustomer", props.customerId);
}
function onOpenContact(contactId: string) {
  emit("openContact", contactId);
}
onMounted(load);
</script>
