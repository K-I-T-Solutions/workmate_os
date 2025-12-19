<template>
  <!-- Modal Overlay -->
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">

    <!-- Modal Panel -->
    <div
      class="w-full max-w-xl max-h-[85vh]
             bg-bg-secondary rounded-xl border border-white/10
             shadow-soft flex flex-col"
    >

      <!-- Header -->
      <div
        class="px-6 py-4 border-b border-white/10
               grid grid-cols-[1fr_auto_1fr] items-center"
      >
        <div />

        <h2 class="text-lg font-semibold text-white text-center">
          {{ isEdit ? "Kunden bearbeiten" : "Neuen Kunden hinzufügen" }}
        </h2>

        <button
          @click="$emit('close')"
          class="kit-btn-close justify-self-end"
          aria-label="Schließen"
        >
          ✕
        </button>
      </div>

      <!-- Scrollbarer Inhalt -->
      <form @submit.prevent="save" class="flex flex-col flex-1">

        <div class="px-6 py-4 overflow-y-auto space-y-3">

          <!-- Name -->
          <div>
            <label class="kit-label">Name</label>
            <input
              v-model="form.name"
              required
              class="kit-input"
            />
          </div>

          <!-- Email -->
          <div>
            <label class="kit-label">Email</label>
            <input
              v-model="form.email"
              type="email"
              class="kit-input"
            />
          </div>

          <!-- Telefon -->
          <div>
            <label class="kit-label">Telefon</label>
            <input
              v-model="form.phone"
              class="kit-input"
            />
          </div>

          <!-- Adresse -->
          <div>
            <label class="kit-label">Adresse</label>
            <input
              v-model="form.address"
              class="kit-input"
            />
          </div>

          <!-- PLZ / Ort -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="kit-label">PLZ</label>
              <input
                v-model="form.zip"
                class="kit-input"
              />
            </div>

            <div>
              <label class="kit-label">Ort</label>
              <input
                v-model="form.city"
                class="kit-input"
              />
            </div>
          </div>

          <!-- Land -->
          <div>
            <label class="kit-label">Land</label>
            <input
              v-model="form.country"
              class="kit-input"
            />
          </div>

          <!-- Notizen -->
          <div>
            <label class="kit-label">Notizen</label>
            <textarea
              v-model="form.notes"
              rows="2"
              class="kit-input resize-none"
            />
          </div>

        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-white/10 flex justify-end gap-3">
          <button
            type="button"
            @click="$emit('close')"
            class="kit-btn-ghost"
          >
            Abbrechen
          </button>

          <button
            type="submit"
            class="kit-btn-success"
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
import type { Customer } from "../../types/customer";
import { crmService } from "../../services/crm.service";

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
