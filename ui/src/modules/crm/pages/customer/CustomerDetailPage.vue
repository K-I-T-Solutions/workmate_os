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
            <span v-if="customer?.city">· {{ customer.city }}</span>Was
          </p>

          <p v-if="customer?.notes" class="text-white/50 text-sm mt-2">
            {{ customer.notes }}
          </p>
        </div>

        <div class="flex gap-2 shrink-0">
          <!-- ZURÜCK -->
          <button
            class="px-4 py-2 rounded-md
                  bg-white/10
                  border border-white/20
                  text-sm text-white
                  hover:bg-white/20
                  transition"
            @click="$emit('back')"
          >
            ← Zurück
          </button>

          <!-- KONTAKTE -->
          <button
            class="px-4 py-2 rounded-md
                  bg-blue-500/20
                  border border-blue-400/30
                  text-sm text-blue-200
                  hover:bg-blue-500/30
                  transition"
            @click="$emit('openContacts', customerId)"
          >
            Kontakte
          </button>

          <!-- BEARBEITEN -->
          <button
            class="px-4 py-2 rounded-md
                  bg-orange-500/20
                  border border-orange-400/30
                  text-sm text-orange-200
                  hover:bg-orange-500/30
                  transition"
            @click="openEdit"
          >
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

        <div class="kit-card space-y-3">

          <!-- Loading -->
          <div v-if="activitiesLoading" class="text-white/50 text-sm">
            Aktivitäten werden geladen…
          </div>

          <!-- Empty -->
          <div
            v-else-if="activities.length === 0"
            class="text-white/50 text-sm"
          >
            Noch keine Aktivitäten vorhanden.
          </div>

          <!-- Timeline -->
          <ul v-else class="space-y-3">
            <li
              v-for="a in activities"
              :key="a.id"
              class="flex gap-3 text-sm"
            >
              <div class="mt-0.5 text-white/50">
                <component
                  :is="iconFor(a.type)"
                  class="w-4 h-4"
                />
              </div>

              <div>
                <div class="text-white/80 leading-snug">
                  {{ a.description }}
                </div>
                <div class="text-xs text-white/40 mt-0.5">
                  {{ formatDate(a.occurred_at) }}
                </div>
              </div>
            </li>
          </ul>

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
import { useCrmActivity } from "../../composables/useCrmActivity"; // ✅ NEU
import {
  Phone,
  Mail,
  MapPin,
  FileText,
  StickyNote,
} from "lucide-vue-next";

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
const {
  activities,
  loading: activitiesLoading,
  fetchCustomerActivities,
} = useCrmActivity();
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
    fetchCustomerActivities(props.customerId);
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
function iconFor(type: string) {
  switch (type) {
    case "call": return Phone;
    case "email": return Mail;
    case "onsite": return MapPin;
    case "remote": return FileText;
    default: return StickyNote;
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleString("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  });
}
onMounted(load);
</script>
