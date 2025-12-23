<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useCustomers } from '../composables/useCustomers';
import type { Customer } from '../types/customer';
import {
  ChevronLeft,
  Save,
  Loader2,
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  customerId?: string; // Optional: wenn gesetzt = Edit-Mode
}>();

// Emits
const emit = defineEmits<{
  back: [];
  saved: [id: string];
}>();

// Composables
const { currentCustomer, loading, createCustomer, updateCustomer, loadCustomer } = useCustomers();

// Customer Type Options
const customerTypes = [
  { value: 'creator', label: 'Creator / Freelancer' },
  { value: 'individual', label: 'Privatperson' },
  { value: 'business', label: 'Unternehmen' },
  { value: 'government', label: 'Behörde' },
];

// Customer Status Options
const customerStatuses = [
  { value: 'active', label: 'Aktiv' },
  { value: 'inactive', label: 'Inaktiv' },
  { value: 'lead', label: 'Lead' },
  { value: 'blocked', label: 'Blockiert' },
];

// State
const formData = ref({
  name: '',
  customer_number: '',
  type: 'business',
  email: '',
  phone: '',
  tax_id: '',
  website: '',
  notes: '',
  status: 'active',

  // Address fields
  street: '',
  zip_code: '',
  city: '',
  country: 'Deutschland',
});

const saving = ref(false);
const errors = ref<Record<string, string>>({});

// Computed
const isEditMode = computed(() => !!props.customerId);
const pageTitle = computed(() => isEditMode.value ? 'Kunde bearbeiten' : 'Neuer Kunde');

// Lifecycle
onMounted(async () => {
  if (props.customerId) {
    await loadCustomer(props.customerId);
    if (currentCustomer.value) {
      // Populate form with customer data
      formData.value = {
        name: currentCustomer.value.name || '',
        customer_number: currentCustomer.value.customer_number || '',
        type: currentCustomer.value.type || 'business',
        email: currentCustomer.value.email || '',
        phone: currentCustomer.value.phone || '',
        tax_id: currentCustomer.value.tax_id || '',
        website: currentCustomer.value.website || '',
        notes: currentCustomer.value.notes || '',
        status: currentCustomer.value.status || 'active',

        // Address fields
        street: currentCustomer.value.street || '',
        zip_code: currentCustomer.value.zip_code || '',
        city: currentCustomer.value.city || '',
        country: currentCustomer.value.country || 'Deutschland',
      };
    }
  }
});

// Actions
function validate(): boolean {
  errors.value = {};

  if (!formData.value.name || formData.value.name.trim() === '') {
    errors.value.name = 'Name ist erforderlich';
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
    let result: Customer | null = null;

    if (isEditMode.value && props.customerId) {
      // Update existing customer
      result = await updateCustomer(props.customerId, formData.value);
    } else {
      // Create new customer
      result = await createCustomer(formData.value);
    }

    if (result) {
      emit('saved', result.id);
    }
  } catch (e: any) {
    console.error('Error saving customer:', e);
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
        <h1 class="text-2xl font-bold text-white">{{ pageTitle }}</h1>
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
        <p class="text-white/60">Lade Kundendaten...</p>
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

      <!-- Section 1: Allgemeine Informationen -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Allgemeine Informationen</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Name -->
          <div>
            <label class="kit-label">
              Name <span class="text-red-400">*</span>
            </label>
            <input
              v-model="formData.name"
              type="text"
              placeholder="z.B. Musterfirma GmbH"
              class="kit-input"
              :class="{ 'border-red-400': errors.name }"
            />
            <p v-if="errors.name" class="text-xs text-red-300 mt-1">{{ errors.name }}</p>
          </div>

          <!-- Kundennummer -->
          <div>
            <label class="kit-label">Kundennummer</label>
            <input
              v-model="formData.customer_number"
              type="text"
              placeholder="Wird automatisch generiert"
              class="kit-input"
              :class="{ 'border-red-400': errors.customer_number }"
              :disabled="true"
            />
            <p class="text-xs text-white/40 mt-1">Wird automatisch generiert</p>
          </div>

          <!-- Kundentyp -->
          <div>
            <label class="kit-label">Kundentyp</label>
            <select
              v-model="formData.type"
              class="kit-input"
            >
              <option v-for="type in customerTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>

          <!-- Status -->
          <div>
            <label class="kit-label">Status</label>
            <select v-model="formData.status" class="kit-input">
              <option v-for="status in customerStatuses" :key="status.value" :value="status.value">
                {{ status.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Section 2: Kontaktdaten -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Kontaktdaten</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- E-Mail -->
          <div>
            <label class="kit-label">E-Mail</label>
            <input
              v-model="formData.email"
              type="email"
              placeholder="kontakt@firma.de"
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
        </div>
      </div>

      <!-- Section 3: Adresse -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Adresse</h3>
        <div class="grid grid-cols-1 gap-4">
          <!-- Straße -->
          <div>
            <label class="kit-label">Straße und Hausnummer</label>
            <input
              v-model="formData.address"
              type="text"
              placeholder="Musterstraße 123"
              class="kit-input"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- PLZ -->
            <div>
              <label class="kit-label">Postleitzahl</label>
              <input
                v-model="formData.zip"
                type="text"
                placeholder="12345"
                class="kit-input"
              />
            </div>

            <!-- Stadt -->
            <div>
              <label class="kit-label">Stadt</label>
              <input
                v-model="formData.city"
                type="text"
                placeholder="Musterstadt"
                class="kit-input"
              />
            </div>

            <!-- Land -->
            <div>
              <label class="kit-label">Land</label>
              <input
                v-model="formData.country"
                type="text"
                placeholder="Deutschland"
                class="kit-input"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Section 4: Zusatzinformationen -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Zusatzinformationen</h3>
        <div>
          <label class="kit-label">Notizen (Optional)</label>
          <textarea
            v-model="formData.notes"
            rows="4"
            placeholder="Interne Notizen zum Kunden..."
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
