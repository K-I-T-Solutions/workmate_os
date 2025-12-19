<template>
  <!-- Modal Overlay -->
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">

    <!-- Modal Panel -->
    <div
      class="w-full max-w-lg max-h-[85vh]
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
          {{ isEdit ? "Kontakt bearbeiten" : "Neuen Kontakt hinzufügen" }}
        </h2>

        <button
          @click="$emit('close')"
          class="kit-btn-close justify-center py-1"
          aria-label="Schließen"
        >
          ✕
        </button>
      </div>

      <!-- Scrollbarer Inhalt -->
      <form @submit.prevent="save" class="flex flex-col flex-1">

        <div class="px-6 py-4 overflow-y-auto space-y-3">

          <!-- Kunde -->
          <div class="relative">
            <label class="kit-label">Kunde</label>

            <input
              v-model="customerSearch"
              placeholder="Kunde suchen…"
              class="kit-input"
            />

            <!-- Suggestions -->
            <div
              v-if="customerResults && customerResults.length"
              class="absolute z-20 mt-1 w-full bg-bg-primary
                     border border-white/10 rounded shadow-lg overflow-hidden"
            >
              <button
                v-for="customer in customerResults || []"
                :key="customer.id"
                type="button"
                @click="selectCustomer(customer)"
                class="w-full text-left px-3 py-2 hover:bg-white/5 transition"
              >
                <div class="text-white font-medium">
                  {{ customer.name }}
                </div>
                <div class="text-xs text-white/50">
                  {{ customer.email }}
                </div>
              </button>
            </div>
          </div>

          <!-- Vorname / Nachname -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="kit-label">Vorname</label>
              <input v-model="form.firstname" class="kit-input" required />
            </div>
            <div>
              <label class="kit-label">Nachname</label>
              <input v-model="form.lastname" class="kit-input" required />
            </div>
          </div>

          <!-- Email -->
          <div>
            <label class="kit-label">Email</label>
            <input v-model="form.email" type="email" class="kit-input" />
          </div>

          <!-- Telefon / Mobil -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="kit-label">Telefon</label>
              <input v-model="form.phone" class="kit-input" />
            </div>
            <div>
              <label class="kit-label">Mobil</label>
              <input v-model="form.mobile" class="kit-input" />
            </div>
          </div>

          <!-- Position / Abteilung -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="kit-label">Position</label>
              <input v-model="form.position" class="kit-input" />
            </div>
            <div>
              <label class="kit-label">Abteilung</label>
              <input v-model="form.department" class="kit-input" />
            </div>
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

          <button type="submit" class="kit-btn-success">
            {{ isEdit ? "Speichern" : "Erstellen" }}
          </button>
        </div>

      </form>
    </div>
  </div>
</template>


<script setup lang="ts">
import { reactive, computed, watch, ref } from "vue";
import { crmService } from "../../services/crm.service";
import type { Contact } from "../../types/contact";
import type { Customer } from "../../types/customer";

const props = defineProps<{
  contact: Contact | null;
  customerId?: string;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "saved", customerId: string): void;
}>();

const isEdit = computed(() => !!props.contact);

const customerSearch = ref("");
const customerResults = ref<Customer[]>([]);

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

function selectCustomer(customer: Customer) {
  customerSearch.value = customer.name;
  customerResults.value = [];
  form.customer_id = customer.id;
}

let searchTimeout: number | undefined;

watch(customerSearch, (value) => {
  if (!value || value.length < 2) {
    customerResults.value = [];
    return;
  }

  clearTimeout(searchTimeout);

  searchTimeout = window.setTimeout(async () => {
    const { data } = await crmService.searchCustomers(value);
    customerResults.value = data;
  }, 300);
});

async function save() {
  if (!form.customer_id) {
    alert("Bitte zuerst einen Kunden auswählen.");
    return;
  }

  if (isEdit.value) {
    await crmService.updateContact(props.contact!.id, form);
  } else {
    await crmService.createContact(form);
  }

  emit("saved", form.customer_id);
  emit("close");
}
</script>
