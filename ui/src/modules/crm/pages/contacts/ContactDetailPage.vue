<template>
  <div class="w-full h-full space-y-10 pb-20">
    <!-- LOADING -->
    <div v-if="!contact" class="text-white/50">
      Kontakt wird geladen …
    </div>

    <!-- MAIN -->
    <div v-else class="space-y-8">
      <!-- HEADER -->
      <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-white leading-tight">
          {{ contact.firstname }} {{ contact.lastname }}
        </h1>

        <div class="flex gap-3">
          <button
            class="px-4 py-2 rounded bg-bg-secondary border border-white/10 text-white hover:bg-bg-secondary/80 transition"
            @click="openEdit"
          >
            Bearbeiten
          </button>

          <button
            class="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700 transition"
            @click="removeContact"
          >
            Löschen
          </button>
        </div>
      </div>

      <!-- INFO PANEL -->
      <div
        class="p-6 rounded-xl bg-bg-secondary border border-white/10 text-white shadow-soft space-y-4"
      >
        <h2 class="text-xl font-semibold">Informationen</h2>

        <div class="space-y-2">
          <p><strong>Email:</strong> {{ contact.email || "-" }}</p>
          <p><strong>Telefon:</strong> {{ contact.phone || "-" }}</p>
          <p><strong>Mobil:</strong> {{ contact.mobile || "-" }}</p>
          <p><strong>Position:</strong> {{ contact.position || "-" }}</p>
          <p><strong>Abteilung:</strong> {{ contact.department || "-" }}</p>
        </div>

        <!-- NOTES -->
        <div v-if="contact.notes" class="pt-2">
          <p class="font-semibold">Notizen:</p>
          <p class="text-white/70 leading-snug">
            {{ contact.notes }}
          </p>
        </div>

        <!-- PRIMARY STATUS -->
        <div class="pt-4">
          <span
            v-if="isPrimary"
            class="px-3 py-1 rounded-md bg-orange-500/20 text-orange-400 border border-orange-500/40 text-sm"
          >
            Primary Contact
          </span>

          <button
            v-else
            @click="setPrimary"
            class="mt-2 px-3 py-1 rounded-md bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
          >
            Als Primary setzen
          </button>
        </div>
      </div>

      <!-- BACK -->
      <button
        class="px-4 py-2 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
        @click="$emit('back')"
      >
        ← Zurück zum Kunden
      </button>

      <!-- EDIT MODAL -->
      <ContactForm
        v-if="showModal"
        :contact="contact"
        :customer-id="customerId"
        @close="showModal = false"
        @saved="reload"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import type { Contact } from "../../types/contact";
import ContactForm from "../../components/contacts/ContactForm.vue";
import { crmService } from "../../services/crm.service";

const route = useRoute();

const customerId = route.params.customerId as string;
const contactId = route.params.contactId as string;

const emit = defineEmits<{
  (e: "back"): void;
  (e: "deleted"): void;
}>();

const contact = ref<Contact | null>(null);
const primary = ref<Contact | null>(null);
const showModal = ref(false);

const isPrimary = computed(
  () => primary.value?.id === contact.value?.id
);

async function load() {
  contact.value = await crmService.getContact(contactId);
  primary.value = await crmService.getPrimaryContact(customerId);
}

function openEdit() {
  showModal.value = true;
}

async function removeContact() {
  if (!contact.value) return;
  if (!confirm("Kontakt wirklich löschen?")) return;

  await crmService.deleteContact(contactId);
  emit("deleted");
}

async function setPrimary() {
  await crmService.setPrimaryContact(customerId, contactId);
  await load();
}

function reload() {
  load();
}

onMounted(load);
</script>

