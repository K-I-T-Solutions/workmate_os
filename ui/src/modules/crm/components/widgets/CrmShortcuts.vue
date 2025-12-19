<script setup lang="ts">
import { UserPlus, Contact } from "lucide-vue-next";

const emit = defineEmits<{
  (e: "create-customer"): void;
  (e: "create-contact"): void;
}>();
</script>

<template>
  <div class="bg-white/5 border border-white/10 rounded-lg p-4">
    <h3 class="text-white font-semibold mb-4">
      Schnellzugriffe
    </h3>

    <div class="flex gap-3">
      <button
        class="kit-btn-primary"
        @click="emit('create-customer')"
      >
        <UserPlus class="w-4 h-4" />
        Neuer Kunde
      </button>

      <button
        class="kit-btn-secondary"
        @click="emit('create-contact')"
      >
        <Contact class="w-4 h-4" />
        Neuer Kontakt
      </button>
    </div>
  </div>
</template>
