<template>
  <div
    class="p-4 rounded-xl bg-bg-secondary border border-white/10 text-white shadow-soft space-y-2 transition"
  >
    <!-- CLICKABLE DETAIL AREA -->
    <div
      class="cursor-pointer hover:bg-bg-secondary/80 rounded-lg p-2 -m-2"
      @click="openDetail"
    >
      <div class="flex justify-between items-start">
        <div>
          <h3 class="text-lg font-semibold">
            {{ contact.firstname }} {{ contact.lastname }}
          </h3>
          <p class="text-white/70 text-sm">{{ contact.email }}</p>
          <p class="text-white/70 text-sm">{{ contact.phone }}</p>
        </div>

        <span
          v-if="isPrimary"
          class="text-xs px-2 py-1 rounded bg-orange-500/20 text-orange-400 border border-orange-500/40"
        >
          Primary
        </span>
      </div>
    </div>

    <!-- ACTION BAR (NOT CLICKABLE FOR DETAIL) -->
    <div class="flex gap-2 pt-2">
      <button
        class="px-3 py-1 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
        @click="$emit('edit')"
      >
        Bearbeiten
      </button>

      <button
        class="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700 transition"
        @click="$emit('delete')"
      >
        Löschen
      </button>

      <button
        v-if="!isPrimary"
        class="px-3 py-1 rounded bg-bg-secondary border border-white/10 text-white hover:bg-bg-secondary/80 transition"
        @click="$emit('setPrimary')"
      >
        Als Primary setzen
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Contact } from "../../types/contact";

const props = defineProps<{
  contact: Contact;
  customerId: string;
  isPrimary: boolean;
}>();

const emit = defineEmits<{
  (e: "openDetail", contactId: string): void;
  (e: "edit"): void;
  (e: "delete"): void;
  (e: "setPrimary"): void;
}>();

function openDetail() {
  emit("openDetail", props.contact.id);
}
</script>
