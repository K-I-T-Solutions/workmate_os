<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useCurrentUser } from '@/composables/useCurrentUser';
import {
  ChevronLeft,
  Save,
  Loader2,
  User,
  Mail,
  Phone,
  MapPin,
  FileText,
  Briefcase,
  Calendar,
  Shield,
} from 'lucide-vue-next';

// Emits
const emit = defineEmits<{
  back: [];
}>();

// Composable
const { currentUser, fullName, getGravatarUrl, loadCurrentUser, updateProfile, loading } = useCurrentUser();

// Form State
const formData = ref({
  email: '',
  phone: '',
  bio: '',
  photo_url: '',
  address_street: '',
  address_zip: '',
  address_city: '',
  address_country: '',
  timezone: '',
  language: '',
  theme: '',
});

const saving = ref(false);
const errors = ref<Record<string, string>>({});

// Load user data on mount
onMounted(async () => {
  await loadCurrentUser();
  if (currentUser.value) {
    formData.value = {
      email: currentUser.value.email || '',
      phone: currentUser.value.phone || '',
      bio: currentUser.value.bio || '',
      photo_url: currentUser.value.photo_url || '',
      address_street: currentUser.value.address_street || '',
      address_zip: currentUser.value.address_zip || '',
      address_city: currentUser.value.address_city || '',
      address_country: currentUser.value.address_country || '',
      timezone: currentUser.value.timezone || 'Europe/Berlin',
      language: currentUser.value.language || 'de',
      theme: currentUser.value.theme || 'catppuccin-frappe',
    };
  }
});

// Computed
const hasChanges = computed(() => {
  if (!currentUser.value) return false;
  return (
    formData.value.email !== (currentUser.value.email || '') ||
    formData.value.phone !== (currentUser.value.phone || '') ||
    formData.value.bio !== (currentUser.value.bio || '') ||
    formData.value.photo_url !== (currentUser.value.photo_url || '') ||
    formData.value.address_street !== (currentUser.value.address_street || '') ||
    formData.value.address_zip !== (currentUser.value.address_zip || '') ||
    formData.value.address_city !== (currentUser.value.address_city || '') ||
    formData.value.address_country !== (currentUser.value.address_country || '')
  );
});

// Actions
function validate(): boolean {
  errors.value = {};

  if (!formData.value.email || formData.value.email.trim() === '') {
    errors.value.email = 'E-Mail ist erforderlich';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.email)) {
    errors.value.email = 'Ungültige E-Mail-Adresse';
  }

  return Object.keys(errors.value).length === 0;
}

async function handleSave() {
  if (!validate()) {
    return;
  }

  saving.value = true;

  try {
    const success = await updateProfile(formData.value);
    if (success) {
      // Show success message or notification
      console.log('Profile updated successfully');
    }
  } catch (error) {
    console.error('Error saving profile:', error);
  } finally {
    saving.value = false;
  }
}

function formatDate(dateString: string | null): string {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Loading State -->
    <div v-if="loading && !currentUser" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Profil...</p>
      </div>
    </div>

    <!-- Content -->
    <template v-else-if="currentUser">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button @click="emit('back')" class="kit-btn-ghost">
            <ChevronLeft :size="18" />
          </button>
          <h1 class="text-2xl font-bold text-white">Mein Profil</h1>
        </div>

        <div class="flex gap-2">
          <button @click="emit('back')" class="kit-btn-ghost" :disabled="saving">
            Abbrechen
          </button>
          <button
            @click="handleSave"
            class="kit-btn-primary"
            :disabled="saving || !hasChanges"
          >
            <Loader2 v-if="saving" :size="18" class="animate-spin" />
            <Save v-else :size="18" />
            Speichern
          </button>
        </div>
      </div>

      <!-- Profile Content -->
      <div class="flex-1 overflow-y-auto space-y-4">
        <!-- Profile Header with Avatar -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-6">
          <div class="flex items-center gap-6">
            <!-- Gravatar -->
            <img
              :src="getGravatarUrl(128)"
              :alt="fullName"
              class="w-32 h-32 rounded-xl object-cover border border-white/10"
            />
            <div class="flex-1">
              <h2 class="text-2xl font-bold text-white">{{ fullName }}</h2>
              <p class="text-white/60 mt-1">{{ currentUser.employee_code }}</p>
              <p v-if="currentUser.email" class="text-white/50 text-sm mt-2">{{ currentUser.email }}</p>
            </div>
          </div>
        </div>

        <!-- Non-Editable Info (Display Only) -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-lg font-semibold text-white mb-4">Stammdaten (nicht editierbar)</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Name -->
            <div>
              <div class="flex items-center gap-2 text-xs text-white/50 mb-1">
                <User :size="14" />
                Name
              </div>
              <div class="text-white/80">{{ fullName }}</div>
            </div>

            <!-- Employee Code -->
            <div>
              <div class="flex items-center gap-2 text-xs text-white/50 mb-1">
                <Shield :size="14" />
                Mitarbeiternummer
              </div>
              <div class="text-white/80">{{ currentUser.employee_code }}</div>
            </div>

            <!-- Birth Date -->
            <div>
              <div class="flex items-center gap-2 text-xs text-white/50 mb-1">
                <Calendar :size="14" />
                Geburtsdatum
              </div>
              <div class="text-white/80">{{ formatDate(currentUser.birth_date) }}</div>
            </div>

            <!-- Department -->
            <div>
              <div class="flex items-center gap-2 text-xs text-white/50 mb-1">
                <Briefcase :size="14" />
                Abteilung
              </div>
              <div class="text-white/80">
                {{ currentUser.department?.name || '-' }}
                <span v-if="currentUser.department" class="text-white/50">({{ currentUser.department.code }})</span>
              </div>
            </div>

            <!-- Role -->
            <div>
              <div class="flex items-center gap-2 text-xs text-white/50 mb-1">
                <Shield :size="14" />
                Rolle
              </div>
              <div class="text-white/80">{{ currentUser.role?.name || '-' }}</div>
            </div>

            <!-- Hire Date -->
            <div>
              <div class="flex items-center gap-2 text-xs text-white/50 mb-1">
                <Calendar :size="14" />
                Einstellungsdatum
              </div>
              <div class="text-white/80">{{ formatDate(currentUser.hire_date) }}</div>
            </div>
          </div>
        </div>

        <!-- Editable: Contact Information -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-lg font-semibold text-white mb-4">Kontaktdaten</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Email -->
            <div>
              <label class="kit-label">
                <Mail :size="14" class="inline mr-1" />
                E-Mail *
              </label>
              <input
                v-model="formData.email"
                type="email"
                class="kit-input"
                :class="{ 'border-red-400': errors.email }"
                placeholder="name@example.com"
              />
              <p v-if="errors.email" class="text-xs text-red-300 mt-1">{{ errors.email }}</p>
            </div>

            <!-- Phone -->
            <div>
              <label class="kit-label">
                <Phone :size="14" class="inline mr-1" />
                Telefon
              </label>
              <input
                v-model="formData.phone"
                type="tel"
                class="kit-input"
                placeholder="+49 123 456789"
              />
            </div>
          </div>
        </div>

        <!-- Editable: Address -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-lg font-semibold text-white mb-4">
            <MapPin :size="18" class="inline mr-2" />
            Adresse
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Street -->
            <div class="md:col-span-2">
              <label class="kit-label">Straße und Hausnummer</label>
              <input
                v-model="formData.address_street"
                type="text"
                class="kit-input"
                placeholder="Musterstraße 123"
              />
            </div>

            <!-- ZIP -->
            <div>
              <label class="kit-label">PLZ</label>
              <input
                v-model="formData.address_zip"
                type="text"
                class="kit-input"
                placeholder="12345"
              />
            </div>

            <!-- City -->
            <div>
              <label class="kit-label">Stadt</label>
              <input
                v-model="formData.address_city"
                type="text"
                class="kit-input"
                placeholder="Berlin"
              />
            </div>

            <!-- Country -->
            <div class="md:col-span-2">
              <label class="kit-label">Land</label>
              <input
                v-model="formData.address_country"
                type="text"
                class="kit-input"
                placeholder="Deutschland"
              />
            </div>
          </div>
        </div>

        <!-- Editable: Bio -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <h3 class="text-lg font-semibold text-white mb-4">
            <FileText :size="18" class="inline mr-2" />
            Über mich
          </h3>
          <textarea
            v-model="formData.bio"
            rows="4"
            class="kit-input"
            placeholder="Erzähl ein bisschen über dich..."
          ></textarea>
        </div>

        <!-- Editable: Photo URL (optional) -->
        <div class="rounded-lg border border-blue-400/30 bg-blue-500/10 p-4">
          <h3 class="text-sm font-semibold text-blue-200 mb-2">
            Profilbild URL (optional)
          </h3>
          <p class="text-xs text-blue-200/80 mb-3">
            Standardmäßig wird dein Gravatar-Bild angezeigt. Du kannst hier eine alternative Bild-URL eingeben.
          </p>
          <input
            v-model="formData.photo_url"
            type="url"
            class="kit-input"
            placeholder="https://example.com/avatar.jpg"
          />
        </div>
      </div>
    </template>
  </div>
</template>
