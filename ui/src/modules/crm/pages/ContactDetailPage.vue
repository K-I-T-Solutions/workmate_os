<template>
  <div class="w-full h-full space-y-10 pb-20">

    <!-- LOADING -->
    <div v-if="!contact" class="text-white/50">Kontakt wird geladen …</div>

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
      <div class="p-6 rounded-xl bg-bg-secondary border border-white/10 text-white shadow-soft space-y-4">

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

      <!-- BACK BUTTON -->
      <button
        class="px-4 py-2 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition mt-3"
        @click="goBack"
      >
        ← Zurück zum Kunden
      </button>

      <!-- EDIT MODAL -->
      <ContactForm
        v-if="showModal"
        :contact="contact"
        :customer-id="contact.customer_id"
        @close="showModal = false"
        @saved="reload"
      />
    </div>

  </div>
</template>


<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { Contact } from "../types/contact";
import ContactForm from "../components/ContactForm.vue";
import { crmService } from "../services/crm.service";

const route = useRoute();
const router = useRouter();

// 🔥 BEIDE PARAMS DIREKT HOLEN
const customerId = route.params.customerId as string;
const contactId = route.params.contactId as string;

const contact = ref<Contact | null>(null);
const primary = ref<Contact | null>(null);
const isLoading = ref(true);
const showModal = ref(false);

// Primary-State
const isPrimary = computed(() =>
  primary.value?.id === contact.value?.id
);

async function load() {
  isLoading.value = true;

  // Kontakt laden
  const c = await crmService.getContact(contactId);
  contact.value = c;

  // Immer customerId aus Route verwenden → nie mehr undefined!
  primary.value = await crmService.getPrimaryContact(customerId);

  isLoading.value = false;
}

function openEdit() {
  showModal.value = true;
}

async function removeContact() {
  if (!contact.value) return;
  if (!confirm("Kontakt wirklich löschen?")) return;

  await crmService.deleteContact(contactId);

  router.push(`/app/crm/customers/${customerId}/contacts`);
}

async function setPrimary() {
  await crmService.setPrimaryContact(customerId, contactId);
  await load();
}

function goBack() {
  router.push(`/app/crm/customers/${customerId}`);
}

function reload() {
  load();
}

onMounted(load);
</script>
