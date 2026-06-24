<template>
  <div class="space-y-8 pb-10">

    <!-- Loading State -->
    <div v-if="isLoading" class="text-white/70">Kunde wird geladen...</div>

    <!-- Not Found -->
    <div v-else-if="!customer" class="text-red-400">
      Kunde nicht gefunden.
    </div>

    <!-- Content -->
    <div v-else class="space-y-10">
      <!-- Page Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-3xl font-bold text-white leading-tight">
            {{ customer.name }}
          </h1>

          <p class="text-white/50 text-sm mt-1">
            Kunden-Nr:
            <span class="text-white">
              {{ customer.customer_number || "Keine Nummer" }}
            </span>
          </p>
        </div>

        <div class="flex gap-3">
          <button
            class="px-4 py-2 rounded bg-bg-secondary border border-white/10 text-white hover:bg-bg-secondary/80 transition"
            @click="editCustomer"
          >
            Bearbeiten
          </button>

          <button
            class="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700 transition"
            @click="deleteCustomer"
          >
            Löschen
          </button>
        </div>
      </div>

      <!-- Info Panel -->
      <div class="p-5 rounded-xl bg-bg-secondary border border-white/10 text-white space-y-2 shadow-soft">
        <h2 class="text-lg font-semibold mb-2">Informationen</h2>

        <p><strong>Email:</strong> {{ customer.email || "-" }}</p>
        <p><strong>Telefon:</strong> {{ customer.phone || "-" }}</p>
        <p><strong>Adresse:</strong> {{ customer.address || "-" }}</p>
        <p><strong>Ort:</strong> {{ customer.zip || "-" }} {{ customer.city || "" }}</p>
        <p><strong>Land:</strong> {{ customer.country || "-" }}</p>
      </div>

      <!-- Primary Contact Panel -->
      <div class="p-5 rounded-xl bg-bg-secondary border border-white/10 text-white space-y-4 shadow-soft">
        <h2 class="text-lg font-semibold">Primary Contact</h2>

        <div v-if="!primaryContact" class="text-white/60">
          Kein primärer Kontakt gesetzt.
        </div>

        <div v-else class="space-y-1">
          <p class="font-medium">
            {{ primaryContact.firstname }} {{ primaryContact.lastname }}
          </p>
          <p class="text-white/70 text-sm">{{ primaryContact.email }}</p>
          <p class="text-white/70 text-sm">{{ primaryContact.phone }}</p>
        </div>

        <button
          class="px-4 py-2 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
          @click="goToContacts"
        >
          Kontakte verwalten
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { crmService } from "../services/crm.service";
import type { Customer } from "../types/customer";
import type { Contact } from "../types/contact";

const route = useRoute();
const router = useRouter();

// 🔥 Customer ID
const customerId = route.params.customerId as string;

// State
const customer = ref<Customer | null>(null);
const primaryContact = ref<Contact | null>(null);
const isLoading = ref(true);

async function load() {
  try {
    isLoading.value = true;

    // Kunde laden
    customer.value = await crmService.getCustomer(customerId);

    // Primary Kontakt laden
    primaryContact.value = await crmService.getPrimaryContact(customerId);

  } finally {
    isLoading.value = false;
  }
}

function editCustomer() {
  alert("TODO: CustomerForm – später mit Joshua bauen 😎");
}

async function deleteCustomer() {
  if (!confirm("Diesen Kunden wirklich löschen?")) return;

  await crmService.deleteCustomer(customerId);
  router.push("/app/crm/customers");
}

function goToContacts() {
  router.push(`/app/crm/customers/${customerId}/contacts`);
}

onMounted(load);
</script>
