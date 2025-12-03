<template>
  <div
    class="p-4 rounded-xl bg-bg-secondary border border-white/10 text-white shadow-soft space-y-2 relative cursor-pointer hover:bg-bg-secondary/80 transition"
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

      <!-- Primary Tag -->
      <span
        v-if="isPrimary"
        class="text-xs px-2 py-1 rounded bg-orange-500/20 text-orange-400 border border-orange-500/40"
      >
        Primary
      </span>
    </div>

    <div class="flex gap-2 pt-2">
      <button
        class="px-3 py-1 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
        @click.stop="$emit('edit')"
      >
        Bearbeiten
      </button>

      <button
        class="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700 transition"
        @click.stop="$emit('delete')"
      >
        Löschen
      </button>

      <button
        v-if="!isPrimary"
        class="px-3 py-1 rounded bg-bg-secondary border border-white/10 text-white hover:bg-bg-secondary/80 transition"
        @click.stop="$emit('setPrimary')"
      >
        Als Primary setzen
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Contact } from "../types/contact";
import { useRouter } from "vue-router";

const router = useRouter();

const props = defineProps<{
  contact: Contact;
  customerId: string;
  isPrimary: boolean;
}>();

function openDetail() {
  router.push(`/app/crm/customers/${props.customerId}/contacts/${props.contact.id}`);
}

defineEmits(["edit", "delete", "setPrimary"]);
</script>
