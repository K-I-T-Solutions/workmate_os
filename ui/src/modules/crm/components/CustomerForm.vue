<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="w-full max-w-xl bg-bg-secondary p-6 rounded-xl border border-white/10 shadow-soft space-y-6">

      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-white">
          {{ isEdit ? "Kunden bearbeiten" : "Neuen Kunden hinzufügen" }}
        </h2>

        <button
          class="px-3 py-1 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="save" class="space-y-4">

        <!-- Name -->
        <div>
          <label class="block text-sm text-white/70 mb-1">Name</label>
          <input
            v-model="form.name"
            required
            class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white"
          />
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm text-white/70 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white"
          />
        </div>

        <!-- Phone -->
        <div>
          <label class="block text-sm text-white/70 mb-1">Telefon</label>
          <input
            v-model="form.phone"
            class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white"
          />
        </div>

        <!-- Address -->
        <div>
          <label class="block text-sm text-white/70 mb-1">Adresse</label>
          <input
            v-model="form.address"
            class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-white/70 mb-1">PLZ</label>
            <input
              v-model="form.zip"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white"
            />
          </div>

          <div>
            <label class="block text-sm text-white/70 mb-1">Ort</label>
            <input
              v-model="form.city"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white"
            />
          </div>
        </div>

        <!-- Country -->
        <div>
          <label class="block text-sm text-white/70 mb-1">Land</label>
          <input
            v-model="form.country"
            class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white"
          />
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm text-white/70 mb-1">Notizen</label>
          <textarea
            v-model="form.notes"
            rows="3"
            class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white resize-none"
          ></textarea>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 rounded bg-bg-secondary border border-white/10 text-white hover:bg-bg-secondary/80 transition"
          >
            Abbrechen
          </button>

          <button
            type="submit"
            class="px-4 py-2 rounded bg-orange-600 text-white hover:bg-orange-700 transition"
          >
            {{ isEdit ? "Speichern" : "Erstellen" }}
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from "vue";
import type { Customer } from "../types/customer";
import { crmService } from "../services/crm.service";

const props = defineProps<{
  customer: Customer | null;
}>();

const emit = defineEmits(["close", "saved"]);

const isEdit = computed(() => !!props.customer);

const form = reactive<Partial<Customer>>({
  name: props.customer?.name || "",
  email: props.customer?.email || "",
  phone: props.customer?.phone || "",
  address: props.customer?.address || "",
  zip: props.customer?.zip || "",
  city: props.customer?.city || "",
  country: props.customer?.country || "",
  notes: props.customer?.notes || "",
});

async function save() {
  if (isEdit.value) {
    await crmService.updateCustomer(props.customer!.id, form);
  } else {
    await crmService.createCustomer(form);
  }

  emit("saved");
  emit("close");
}
</script>
