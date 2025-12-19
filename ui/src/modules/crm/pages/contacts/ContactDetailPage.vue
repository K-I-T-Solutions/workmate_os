<template>
  <div class="space-y-8 pb-20">

    <!-- HERO -->
    <section v-if="contact" class="flex justify-between items-start gap-6">
      <div>
        <h1 class="text-3xl font-bold text-white">
          {{ contact.firstname }} {{ contact.lastname }}
        </h1>

        <p class="text-white/60 text-sm">
          {{ contact.position || "Kontakt" }}
          <span v-if="contact.department"> · {{ contact.department }}</span>
        </p>
      </div>

      <div class="flex gap-2 shrink-0">
        <button class="kit-btn-secondary" @click="openEdit">
          Bearbeiten
        </button>
        <button class="kit-btn-danger" @click="removeContact">
          Löschen
        </button>
      </div>
    </section>

    <!-- LOADING -->
    <div v-else class="text-white/60">
      Kontakt wird geladen…
    </div>

    <!-- CONTENT GRID -->
    <section v-if="contact" class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- LEFT: CONTACT INFO -->
      <div class="lg:col-span-2 space-y-6">
        <div class="kit-panel space-y-4">
          <h2 class="text-lg font-semibold">Kontaktinformationen</h2>

          <div class="space-y-2 text-sm text-white/80">
            <p>
                <strong>Email: </strong>
                  <a
                  v-if="contact.email"
                  :href="`mailto:${contact.email}`"
                  class="text-blue-300 hover:underline"
                >
                  {{ contact.email }}
                </a>
                <span v-else class="text-white/40">–</span>
              </p>

              <p>
                <strong>Telefon: </strong>
                <a
                  v-if="contact.phone"
                  :href="telHref(contact.phone)"
                  class="text-blue-300 hover:underline"
                >
                  {{ contact.phone }}
                </a>
                <span v-else class="text-white/40">–</span>
              </p>

              <p>
                <strong>Mobil: </strong>
                <a
                  v-if="contact.mobile"
                  :href="telHref(contact.mobile)"
                  class="text-blue-300 hover:underline"
                >
                  {{ contact.mobile }}
                </a>
                <span v-else class="text-white/40">–</span>
              </p>

            <p><strong>Position:</strong> {{ contact.position || "-" }}</p>
            <p><strong>Abteilung:</strong> {{ contact.department || "-" }}</p>
          </div>

          <div v-if="contact.notes" class="pt-3 text-white/70">
            <p class="font-semibold mb-1">Notizen</p>
            <p>{{ contact.notes }}</p>
          </div>

          <!-- PRIMARY -->
          <div class="pt-4">
            <span
              v-if="isPrimary"
              class="px-3 py-1 rounded-md
                     bg-orange-500/20 text-orange-400
                     border border-orange-500/40 text-sm"
            >
              Primary Contact
            </span>

            <button
              v-else
              class="px-4 py-2 rounded-md
                bg-orange-500/20 border border-orange-500/40
                text-sm text-orange-400
                hover:border-orange-500/40transition"
              @click="setPrimary"
            >
              Als Primary setzen
            </button>
          </div>
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

    <!-- BACK -->
    <div class="pt-4">
      <button class="kit-btn-ghost" @click="$emit('back')">
        ← Zurück zu Kontakten
      </button>
    </div>

    <!-- EDIT MODAL -->
    <ContactForm
      v-if="showModal"
      :contact="contact"
      :customer-id="customerId"
      @close="showModal = false"
      @saved="reload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { Contact } from "../../types/contact";
import ContactForm from "../../components/contacts/ContactForm.vue";
import { crmService } from "../../services/crm.service";
import type { CrmActivity } from "../../types/activity";
import {
  Phone,
  Mail,
  MapPin,
  FileText,
  StickyNote,
} from "lucide-vue-next";


const props = defineProps<{
  customerId: string,
  contactId: string
}>();
const emit = defineEmits<{
  (e: "back"): void;
  (e: "deleted"): void;
}>();

const activities = ref<CrmActivity[]>([]);
const activitiesLoading = ref(false);
const contact = ref<Contact | null>(null);
const primary = ref<Contact | null>(null);
const showModal = ref(false);

const isPrimary = computed(
  () => primary.value?.id === contact.value?.id
);

async function load() {
  contact.value = await crmService.getContact(props.contactId);
  primary.value = await crmService.getPrimaryContact(props.customerId);
  activitiesLoading.value =true;
  try {
    activities.value = await crmService.getCustomerActivities(
      props.customerId,{
        contactId: props.contactId,
        limit: 10,
      }
    );
  }finally{
    activitiesLoading.value=false;
  }
}

function openEdit() {
  showModal.value = true;
}

async function removeContact() {
  if (!contact.value) return;
  if (!confirm("Kontakt wirklich löschen?")) return;

  await crmService.deleteContact(props.contactId);
  emit("deleted");
}

async function setPrimary() {
  await crmService.setPrimaryContact(props.customerId, props.contactId);
  await load();
}
function telHref(value: string) {
  return `tel:${value.replace(/\s+/g, "")}`;
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
function reload() {
  load();
}

onMounted(load);
</script>

