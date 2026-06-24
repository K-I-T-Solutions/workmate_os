<template>
  <div class="space-y-8 pb-10">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-white">Kunden</h1>

      <button
        class="px-4 py-2 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
        @click="openCreateModal"
      >
        + Neuer Kunde
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="i in 6"
        :key="i"
        class="h-24 rounded-xl bg-bg-secondary/40 animate-pulse"
      />
    </div>

    <!-- Empty -->
    <div v-else-if="customers.length === 0" class="text-white/60">
      Keine Kunden vorhanden.
    </div>

    <!-- Customers Grid -->
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <CustomerCard
        v-for="c in customers"
        :key="c.id"
        :customer="c"
        @click="openCustomer(c.id)"
      />
    </div>

    <!-- Modal -->
    <CustomerForm
      v-if="showModal"
      :customer="selectedCustomer"
      @close="showModal = false"
      @saved="reload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { crmService } from "../services/crm.service";

import type { Customer } from "../types/customer";
import CustomerCard from "../components/CustomerCard.vue";
import CustomerForm from "../components/CustomerForm.vue";

const router = useRouter();

const customers = ref<Customer[]>([]);
const isLoading = ref(true);

// Modal state
const showModal = ref(false);
const selectedCustomer = ref<Customer | null>(null);

function openCreateModal() {
  selectedCustomer.value = null;
  showModal.value = true;
}

function openCustomer(id: string) {
  router.push(`/app/crm/customers/${id}`);
}

async function reload() {
  await load();
}

async function load() {
  try {
    isLoading.value = true;
    customers.value = await crmService.getCustomers();
    console.log(customers.value);
  } finally {
    isLoading.value = false;
  }
}

onMounted(load);
</script>
