<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useContacts } from '../composables/useContacts';
import { useCustomers } from '../composables/useCustomers';
import type { Contact } from '../types/contact';
import {
  ChevronLeft,
  Save,
  Loader2,
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  customerId: string; // Erforderlich: Kunde dem der Kontakt zugeordnet ist
  contactId?: string; // Optional: wenn gesetzt = Edit-Mode
}>();

// Emits
const emit = defineEmits<{
  back: [];
  saved: [id: string];
}>();

// Composables
const { currentContact, loading, createContact, updateContact, loadContact } = useContacts();
const { currentCustomer, loadCustomer } = useCustomers();

// State
const formData = ref({
  customer_id: props.customerId,
  firstname: '',
  lastname: '',
  email: '',
  phone: '',
  mobile: '',
  position: '',
  department: '',
  is_primary: false,
  notes: '',
});

const saving = ref(false);
const errors = ref<Record<string, string>>({});

// Computed
const isEditMode = computed(() => !!props.contactId);
const pageTitle = computed(() => isEditMode.value ? 'Kontakt bearbeiten' : 'Neuer Kontakt');
const customerName = computed(() => currentCustomer.value?.name || 'Kunde');

// Lifecycle
onMounted(async () => {
  // Kunde laden für Anzeige
  await loadCustomer(props.customerId);

  if (props.contactId) {
    await loadContact(props.contactId);
    if (currentContact.value) {
      // Populate form with contact data
      formData.value = {
        customer_id: currentContact.value.customer_id,
        firstname: currentContact.value.firstname || '',
        lastname: currentContact.value.lastname || '',
        email: currentContact.value.email || '',
        phone: currentContact.value.phone || '',
        mobile: currentContact.value.mobile || '',
        position: currentContact.value.position || '',
        department: currentContact.value.department || '',
        is_primary: currentContact.value.is_primary,
        notes: currentContact.value.notes || '',
      };
    }
  }
});

// Actions
function validate(): boolean {
  errors.value = {};

  if (!formData.value.firstname || formData.value.firstname.trim() === '') {
    errors.value.firstname = 'Vorname ist erforderlich';
  }

  if (!formData.value.lastname || formData.value.lastname.trim() === '') {
    errors.value.lastname = 'Nachname ist erforderlich';
  }

  // Email validation (optional, but wenn angegeben dann valid)
  if (formData.value.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.email)) {
    errors.value.email = 'Ungültige E-Mail-Adresse';
  }

  return Object.keys(errors.value).length === 0;
}

async function handleSubmit() {
  if (!validate()) {
    return;
  }

  saving.value = true;

  try {
    let result: Contact | null = null;

    if (isEditMode.value && props.contactId) {
      // Update existing contact
      result = await updateContact(props.contactId, formData.value);
    } else {
      // Create new contact
      result = await createContact(formData.value);
    }

    if (result) {
      emit('saved', result.id);
    }
  } catch (e: any) {
    console.error('Error saving contact:', e);
    errors.value.general = e.message || 'Fehler beim Speichern';
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white">{{ pageTitle }}</h1>
          <p class="text-sm text-white/60 mt-1">für {{ customerName }}</p>
        </div>
      </div>

      <div class="flex gap-2">
        <button @click="emit('back')" class="kit-btn-ghost">
          Abbrechen
        </button>
        <button
          @click="handleSubmit"
          :disabled="saving || loading"
          class="kit-btn-primary"
        >
          <Loader2 v-if="saving" :size="18" class="animate-spin" />
          <Save v-else :size="18" />
          {{ saving ? 'Speichere...' : 'Speichern' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <Loader2 :size="40" class="animate-spin text-white/40 mx-auto mb-2" />
        <p class="text-white/60">Lade Kontaktdaten...</p>
      </div>
    </div>

    <!-- Form Content -->
    <div v-else class="flex-1 overflow-auto space-y-4">
      <!-- Error Message -->
      <div
        v-if="errors.general"
        class="rounded-lg border border-red-400/30 bg-red-500/20 p-4"
      >
        <p class="text-red-200">{{ errors.general }}</p>
      </div>

      <!-- Section 1: Basis-Informationen -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Basis-Informationen</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Vorname -->
          <div>
            <label class="kit-label">
              Vorname <span class="text-red-400">*</span>
            </label>
            <input
              v-model="formData.firstname"
              type="text"
              placeholder="z.B. Max"
              class="kit-input"
              :class="{ 'border-red-400': errors.firstname }"
            />
            <p v-if="errors.firstname" class="text-xs text-red-300 mt-1">{{ errors.firstname }}</p>
          </div>

          <!-- Nachname -->
          <div>
            <label class="kit-label">
              Nachname <span class="text-red-400">*</span>
            </label>
            <input
              v-model="formData.lastname"
              type="text"
              placeholder="z.B. Mustermann"
              class="kit-input"
              :class="{ 'border-red-400': errors.lastname }"
            />
            <p v-if="errors.lastname" class="text-xs text-red-300 mt-1">{{ errors.lastname }}</p>
          </div>

          <!-- Position -->
          <div>
            <label class="kit-label">Position</label>
            <input
              v-model="formData.position"
              type="text"
              placeholder="z.B. Geschäftsführer"
              class="kit-input"
            />
          </div>

          <!-- Abteilung -->
          <div>
            <label class="kit-label">Abteilung</label>
            <input
              v-model="formData.department"
              type="text"
              placeholder="z.B. Vertrieb"
              class="kit-input"
            />
          </div>
        </div>
      </div>

      <!-- Section 2: Kontaktdaten -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Kontaktdaten</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- E-Mail -->
          <div class="md:col-span-2">
            <label class="kit-label">E-Mail</label>
            <input
              v-model="formData.email"
              type="email"
              placeholder="m.mustermann@firma.de"
              class="kit-input"
              :class="{ 'border-red-400': errors.email }"
            />
            <p v-if="errors.email" class="text-xs text-red-300 mt-1">{{ errors.email }}</p>
          </div>

          <!-- Telefon -->
          <div>
            <label class="kit-label">Telefon</label>
            <input
              v-model="formData.phone"
              type="tel"
              placeholder="+49 123 456789"
              class="kit-input"
            />
          </div>

          <!-- Mobil -->
          <div>
            <label class="kit-label">Mobil</label>
            <input
              v-model="formData.mobile"
              type="tel"
              placeholder="+49 160 1234567"
              class="kit-input"
            />
          </div>
        </div>
      </div>

      <!-- Section 3: Einstellungen -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Einstellungen</h3>
        <div class="flex items-center gap-2">
          <input
            v-model="formData.is_primary"
            type="checkbox"
            id="is_primary"
            class="rounded"
          />
          <label for="is_primary" class="text-sm text-white cursor-pointer">
            Als Primärkontakt markieren
          </label>
        </div>
        <p class="text-xs text-white/40 mt-2">
          Der Primärkontakt wird als Hauptansprechpartner für diesen Kunden verwendet
        </p>
      </div>

      <!-- Section 4: Notizen -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Notizen</h3>
        <div>
          <label class="kit-label">Notizen (Optional)</label>
          <textarea
            v-model="formData.notes"
            rows="4"
            placeholder="Interne Notizen zum Kontakt..."
            class="kit-input resize-none"
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Zusätzliche Styles falls benötigt */
</style>
