<template>
  <div class="h-full flex flex-col gap-4 p-4">

    <!-- HEADER -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-white">
        Kundenliste - K.I.T.
      </h1>

      <button
        class="px-4 py-2 rounded bg-blue-500 border border-white/10 text-sm hover:bg-white/5"
        @click="openCreateModal"
      >
        + Neuer Kunde
      </button>
      <button class="px-4 py-2 rounded bg-orange-400 border border-white/10 text-sm hover:bg-white/5"
      @click="openDashboard">
      <- Startseite
      </button>
    </div>

    <!-- SEARCH / FILTER -->
    <div class="flex gap-3">
      <input
        v-model="search"
        type="text"
        placeholder="Kunde suchen…"
        class="flex-1 px-3 py-2 rounded bg-white/5 border border-white/10 text-sm text-white placeholder-white/40 focus:outline-none focus:border-accent"
      />

      <select
        class="px-3 py-2 rounded bg-white/5 border border-white/10 text-sm text-white"
      >
        <option>Alle</option>
        <option>Aktiv</option>
        <option>Inaktiv</option>
      </select>
    </div>

    <!-- GRID -->
    <div class="flex-1 overflow-auto">
      <div
        v-if="isLoading"
        class="grid grid-cols-4 gap-2"
      >
        <div
          v-for="i in 8"
          :key="i"
          class="h-24 rounded bg-white/5 animate-pulse"
        />
      </div>

      <div
        v-else
        class="grid grid-cols-4 gap-2"
      >
        <div
          v-for="c in pagedCustomers"
          :key="c.id"
          class="p-3 rounded border border-white/10 bg-white/5 hover:bg-white/10 cursor-pointer transition"
          @click="openCustomer(c.id)"
        >
          <div class="font-medium text-white truncate">
            {{ c.name }}
          </div>
          <div class="text-xs text-white/50 truncate">
            {{ c.email ?? '—' }}
          </div>
        </div>
      </div>
    </div>

    <!-- PAGINATION -->
    <div class="flex items-center justify-between text-sm text-white/60">
      <button
        class="px-2 py-1 hover:text-white disabled:opacity-30"
        :disabled="page === 1"
        @click="page--"
      >
        ← Zurück
      </button>

      <span>
        {{ page }} / {{ totalPages }}
      </span>

      <button
        class="px-2 py-1 hover:text-white disabled:opacity-30"
        :disabled="page === totalPages"
        @click="page++"
      >
        Weiter →
      </button>
    </div>

    <!-- MODAL -->
    <CustomerForm
      v-if="showModal"
      :customer="selectedCustomer"
      @close="showModal = false"
      @saved="reload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { crmService } from "../../services/crm.service";
import { CustomerForm } from "../../components";
import type { Customer } from "../../types/customer";

const emit = defineEmits<{
  (e: "openCustomer",id:string):void;
  (e: "openDashboard"):void;
}>();
const customers = ref<Customer[]>([]);
const selectedCustomer = ref <Customer | null>(null);
const isLoading = ref(true);

const search = ref("");
const page = ref(1);
const pageSize = 8;

const showModal = ref(false);

/* ---------------------------
   DATA
---------------------------- */
async function load() {
  isLoading.value = true;
  customers.value = await crmService.getCustomers();
  isLoading.value = false;
}

onMounted(load);

/* ---------------------------
   FILTER + PAGINATION
---------------------------- */
const filtered = computed(() =>
  customers.value.filter(c =>
    c.name.toLowerCase().includes(search.value.toLowerCase())
  )
);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filtered.value.length / pageSize))
);

const pagedCustomers = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filtered.value.slice(start, start + pageSize);
});

/* ---------------------------
   ACTIONS
---------------------------- */
function openCustomer(id: string) {
  emit("openCustomer",id);
}

function openCreateModal() {
  showModal.value = true;
}

async function reload() {
  await load();
}
function openDashboard(){
  emit("openDashboard")
}
</script>
