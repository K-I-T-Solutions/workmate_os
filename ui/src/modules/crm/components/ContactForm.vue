<template>
  <!-- Modal Overlay -->
  <div
    class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
  >
    <!-- Modal Panel -->
    <div
      class="w-full max-w-lg bg-bg-secondary p-6 rounded-xl border border-white/10 shadow-soft space-y-6"
    >
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-white">
          {{ isEdit ? "Kontakt bearbeiten" : "Neuen Kontakt hinzufügen" }}
        </h2>

        <button
          @click="$emit('close')"
          class="px-3 py-1 rounded bg-bg-primary border border-white/10 text-white hover:bg-bg-primary/80 transition"
        >
          ✕
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="save">
        <div class="space-y-4">
          <!-- Firstname -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Vorname</label>
            <input
              v-model="form.firstname"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
              required
            />
          </div>

          <!-- Lastname -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Nachname</label>
            <input
              v-model="form.lastname"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
              required
            />
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Email</label>
            <input
              v-model="form.email"
              type="email"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <!-- Phone -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Telefon</label>
            <input
              v-model="form.phone"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <!-- Mobile -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Mobil</label>
            <input
              v-model="form.mobile"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <!-- Position -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Position</label>
            <input
              v-model="form.position"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <!-- Department -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Abteilung</label>
            <input
              v-model="form.department"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm text-white/70 mb-1">Notizen</label>
            <textarea
              v-model="form.notes"
              rows="3"
              class="w-full bg-bg-primary border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none"
            ></textarea>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-6">
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
import { crmService } from "../services/crm.service";
import type { Contact } from "../types/contact";

const props = defineProps<{
  contact: Contact | null;
  customerId: string;
}>();

const emit = defineEmits(["close", "saved"]);

const isEdit = computed(() => !!props.contact);

const form = reactive<Partial<Contact>>({
  firstname: props.contact?.firstname || "",
  lastname: props.contact?.lastname || "",
  email: props.contact?.email || "",
  phone: props.contact?.phone || "",
  mobile: props.contact?.mobile || "",
  position: props.contact?.position || "",
  department: props.contact?.department || "",
  notes: props.contact?.notes || "",
  customer_id: props.customerId,
});

async function save() {
  if (isEdit.value) {
    await crmService.updateContact(props.contact!.id, form);
  } else {
    await crmService.createContact(form);
  }

  emit("saved");
  emit("close");
}
</script>
