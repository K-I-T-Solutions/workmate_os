<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useUserSettings } from '@/composables/useUserSettings';
import { useCurrentUser } from '@/composables/useCurrentUser';
import { useTheme } from '@/composables/useTheme';
import { apiClient } from '@/services/api/client';
import {
  ChevronLeft,
  Save,
  Loader2,
  Globe,
  Clock,
  Bell,
  BellOff,
  RotateCcw,
  Lock,
  Eye,
  EyeOff,
  CheckCircle,
  Palette,
} from 'lucide-vue-next';

// Emits
const emit = defineEmits<{
  back: [];
}>();

// Composables
const { settings, loading, loadSettings, updateSettings, resetToDefaults } = useUserSettings();
const { currentUser } = useCurrentUser();
const { availableThemes, currentTheme, updateUserTheme, applyTheme } = useTheme();

// Tab State
const activeTab = ref<'general' | 'password'>('general');

// Form State
const formData = ref({
  language: 'de-DE',
  timezone: 'Europe/Berlin',
  notifications_enabled: true,
  theme: 'kit-standard',
});

// Password Form State
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);
const passwordErrors = ref<Record<string, string>>({});
const passwordSuccess = ref(false);

const saving = ref(false);
const resetting = ref(false);
const changingPassword = ref(false);

// Load settings on mount
onMounted(async () => {
  await loadSettings();
  if (settings.value) {
    formData.value = {
      language: settings.value.language,
      timezone: settings.value.timezone,
      notifications_enabled: settings.value.notifications_enabled,
      theme: currentUser.value?.theme || currentTheme.value || 'kit-standard',
    };
  }
});

// Computed
const hasChanges = computed(() => {
  if (!settings.value) return false;
  const currentUserTheme = currentUser.value?.theme || 'kit-standard';
  return (
    formData.value.language !== settings.value.language ||
    formData.value.timezone !== settings.value.timezone ||
    formData.value.notifications_enabled !== settings.value.notifications_enabled ||
    formData.value.theme !== currentUserTheme
  );
});

// Language Options
const languageOptions = [
  { value: 'de-DE', label: 'Deutsch' },
  { value: 'en-US', label: 'English' },
  { value: 'fr-FR', label: 'Français' },
  { value: 'es-ES', label: 'Español' },
];

// Timezone Options (common European timezones)
const timezoneOptions = [
  { value: 'Europe/Berlin', label: 'Berlin (CET/CEST)' },
  { value: 'Europe/London', label: 'London (GMT/BST)' },
  { value: 'Europe/Paris', label: 'Paris (CET/CEST)' },
  { value: 'Europe/Rome', label: 'Rome (CET/CEST)' },
  { value: 'Europe/Madrid', label: 'Madrid (CET/CEST)' },
  { value: 'Europe/Vienna', label: 'Vienna (CET/CEST)' },
  { value: 'Europe/Amsterdam', label: 'Amsterdam (CET/CEST)' },
  { value: 'Europe/Brussels', label: 'Brussels (CET/CEST)' },
  { value: 'Europe/Zurich', label: 'Zurich (CET/CEST)' },
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
];

// Actions
async function handleSave() {
  saving.value = true;

  try {
    // Update settings
    const success = await updateSettings(formData.value);

    // Update theme if changed
    if (currentUser.value && formData.value.theme !== currentUser.value.theme) {
      await updateUserTheme(formData.value.theme, currentUser.value.id);
    }

    if (success) {
      console.log('Settings updated successfully');
    }
  } catch (error) {
    console.error('Error saving settings:', error);
  } finally {
    saving.value = false;
  }
}

// Theme Preview on Change
function handleThemeChange() {
  // Apply theme immediately for preview
  applyTheme(formData.value.theme);
}

async function handleReset() {
  if (!confirm('Möchten Sie wirklich alle Einstellungen auf die Standardwerte zurücksetzen?')) {
    return;
  }

  resetting.value = true;

  try {
    const success = await resetToDefaults();
    if (success && settings.value) {
      formData.value = {
        language: settings.value.language,
        timezone: settings.value.timezone,
        notifications_enabled: settings.value.notifications_enabled,
      };
    }
  } catch (error) {
    console.error('Error resetting settings:', error);
  } finally {
    resetting.value = false;
  }
}

// Password Change Actions
function validatePasswordForm(): boolean {
  passwordErrors.value = {};

  if (!passwordForm.value.currentPassword) {
    passwordErrors.value.currentPassword = 'Aktuelles Passwort ist erforderlich';
  }

  if (!passwordForm.value.newPassword) {
    passwordErrors.value.newPassword = 'Neues Passwort ist erforderlich';
  } else if (passwordForm.value.newPassword.length < 8) {
    passwordErrors.value.newPassword = 'Passwort muss mindestens 8 Zeichen lang sein';
  }

  if (!passwordForm.value.confirmPassword) {
    passwordErrors.value.confirmPassword = 'Passwortbestätigung ist erforderlich';
  } else if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordErrors.value.confirmPassword = 'Passwörter stimmen nicht überein';
  }

  return Object.keys(passwordErrors.value).length === 0;
}

async function handleChangePassword() {
  if (!validatePasswordForm()) {
    return;
  }

  changingPassword.value = true;
  passwordSuccess.value = false;

  try {
    await apiClient.post('/api/auth/change-password', {
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword,
    });

    // Success
    passwordSuccess.value = true;
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    };
    passwordErrors.value = {};

    // Reset success message after 5 seconds
    setTimeout(() => {
      passwordSuccess.value = false;
    }, 5000);
  } catch (error: any) {
    console.error('Error changing password:', error);
    const errorMessage = error.response?.data?.detail || 'Fehler beim Ändern des Passworts';
    passwordErrors.value.general = errorMessage;
  } finally {
    changingPassword.value = false;
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Loading State -->
    <div v-if="loading && !settings" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Einstellungen...</p>
      </div>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button @click="emit('back')" class="kit-btn-ghost">
            <ChevronLeft :size="18" />
          </button>
          <h1 class="text-2xl font-bold text-white">Einstellungen</h1>
        </div>

        <div class="flex gap-2" v-if="activeTab === 'general'">
          <button
            @click="handleReset"
            class="kit-btn-ghost"
            :disabled="saving || resetting"
          >
            <RotateCcw :size="18" :class="{ 'animate-spin': resetting }" />
            Zurücksetzen
          </button>
          <button
            @click="handleSave"
            class="kit-btn-primary"
            :disabled="saving || !hasChanges || resetting"
          >
            <Loader2 v-if="saving" :size="18" class="animate-spin" />
            <Save v-else :size="18" />
            Speichern
          </button>
        </div>

        <div class="flex gap-2" v-if="activeTab === 'password'">
          <button
            @click="handleChangePassword"
            class="kit-btn-primary"
            :disabled="changingPassword"
          >
            <Loader2 v-if="changingPassword" :size="18" class="animate-spin" />
            <Lock v-else :size="18" />
            Passwort ändern
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2 border-b border-white/10">
        <button
          @click="activeTab = 'general'"
          class="px-4 py-2 font-medium text-sm transition-colors"
          :class="
            activeTab === 'general'
              ? 'text-blue-200 border-b-2 border-blue-400'
              : 'text-white/60 hover:text-white/80'
          "
        >
          Allgemein
        </button>
        <button
          @click="activeTab = 'password'"
          class="px-4 py-2 font-medium text-sm transition-colors"
          :class="
            activeTab === 'password'
              ? 'text-blue-200 border-b-2 border-blue-400'
              : 'text-white/60 hover:text-white/80'
          "
        >
          Passwort
        </button>
      </div>

      <!-- Settings Content -->
      <div class="flex-1 overflow-y-auto space-y-4">
        <!-- General Settings Tab -->
        <template v-if="activeTab === 'general'">
        <!-- Language Settings -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-4">
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
              <Globe :size="18" class="text-blue-200" />
            </div>
            <h3 class="text-lg font-semibold text-white">Sprache</h3>
          </div>

          <div>
            <label class="kit-label">Bevorzugte Sprache</label>
            <select v-model="formData.language" class="kit-input">
              <option v-for="lang in languageOptions" :key="lang.value" :value="lang.value">
                {{ lang.label }}
              </option>
            </select>
            <p class="text-xs text-white/50 mt-2">
              Legt die Sprache für die Benutzeroberfläche fest.
            </p>
          </div>
        </div>

        <!-- Timezone Settings -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-4">
            <div class="p-2 bg-purple-500/20 rounded-lg border border-purple-400/30">
              <Clock :size="18" class="text-purple-200" />
            </div>
            <h3 class="text-lg font-semibold text-white">Zeitzone</h3>
          </div>

          <div>
            <label class="kit-label">Zeitzone</label>
            <select v-model="formData.timezone" class="kit-input">
              <option v-for="tz in timezoneOptions" :key="tz.value" :value="tz.value">
                {{ tz.label }}
              </option>
            </select>
            <p class="text-xs text-white/50 mt-2">
              Bestimmt, wie Datum und Uhrzeit angezeigt werden.
            </p>
          </div>
        </div>

        <!-- Notification Settings -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-4">
            <div class="p-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30">
              <Bell :size="18" class="text-emerald-200" />
            </div>
            <h3 class="text-lg font-semibold text-white">Benachrichtigungen</h3>
          </div>

          <div class="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
            <div class="flex items-center gap-3">
              <div
                class="p-2 rounded-lg"
                :class="
                  formData.notifications_enabled
                    ? 'bg-emerald-500/20 border border-emerald-400/30'
                    : 'bg-white/5 border border-white/10'
                "
              >
                <Bell
                  v-if="formData.notifications_enabled"
                  :size="16"
                  class="text-emerald-200"
                />
                <BellOff v-else :size="16" class="text-white/40" />
              </div>
              <div>
                <div class="text-white font-medium">System-Benachrichtigungen</div>
                <div class="text-xs text-white/50 mt-1">
                  Erhalte Benachrichtigungen über wichtige Ereignisse
                </div>
              </div>
            </div>

            <!-- Toggle Switch -->
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                v-model="formData.notifications_enabled"
                type="checkbox"
                class="sr-only peer"
              />
              <div
                class="w-11 h-6 bg-white/10 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-400 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"
              ></div>
            </label>
          </div>
        </div>

        <!-- Theme Settings -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 mb-4">
            <div class="p-2 bg-orange-500/20 rounded-lg border border-orange-400/30">
              <Palette :size="18" class="text-orange-200" />
            </div>
            <h3 class="text-lg font-semibold text-white">Theme</h3>
          </div>

          <div>
            <label class="kit-label">Farbschema</label>
            <select
              v-model="formData.theme"
              @change="handleThemeChange"
              class="kit-input"
            >
              <option
                v-for="theme in availableThemes"
                :key="theme.id"
                :value="theme.id"
              >
                {{ theme.name }}
              </option>
            </select>
            <p class="text-xs text-white/50 mt-2">
              {{ availableThemes.find(t => t.id === formData.theme)?.description || 'Wähle ein Farbschema' }}
            </p>
          </div>

          <!-- Theme Preview Cards -->
          <div class="grid grid-cols-2 gap-3 mt-4">
            <button
              v-for="theme in availableThemes"
              :key="theme.id"
              @click="formData.theme = theme.id; handleThemeChange()"
              class="relative p-4 rounded-lg border-2 transition-all group"
              :class="
                formData.theme === theme.id
                  ? 'border-orange-400 bg-orange-500/10'
                  : 'border-white/10 hover:border-white/20 bg-white/5'
              "
            >
              <!-- Preview -->
              <div
                class="h-16 rounded-md mb-2"
                :style="{ background: theme.preview }"
              ></div>

              <!-- Name -->
              <div
                class="text-sm font-medium transition-colors"
                :class="formData.theme === theme.id ? 'text-orange-200' : 'text-white/80'"
              >
                {{ theme.name }}
              </div>

              <!-- Selected Badge -->
              <div
                v-if="formData.theme === theme.id"
                class="absolute top-2 right-2 w-5 h-5 rounded-full bg-orange-500 flex items-center justify-center"
              >
                <CheckCircle :size="14" class="text-white" />
              </div>
            </button>
          </div>
        </div>

        <!-- Info Box -->
        <div class="rounded-lg border border-blue-400/30 bg-blue-500/10 p-4">
          <p class="text-sm text-blue-200">
            <strong>Hinweis:</strong> Änderungen werden sofort übernommen, nachdem Sie auf "Speichern" geklickt haben.
            Einige Einstellungen erfordern möglicherweise ein Neuladen der Seite, um vollständig wirksam zu werden.
          </p>
        </div>
        </template>

        <!-- Password Settings Tab -->
        <template v-if="activeTab === 'password'">
          <!-- Success Message -->
          <div
            v-if="passwordSuccess"
            class="rounded-lg border border-emerald-400/30 bg-emerald-500/10 p-4 flex items-center gap-3"
          >
            <CheckCircle :size="20" class="text-emerald-200" />
            <p class="text-sm text-emerald-200">
              <strong>Erfolg!</strong> Ihr Passwort wurde erfolgreich geändert.
            </p>
          </div>

          <!-- General Error Message -->
          <div
            v-if="passwordErrors.general"
            class="rounded-lg border border-red-400/30 bg-red-500/10 p-4"
          >
            <p class="text-sm text-red-200">{{ passwordErrors.general }}</p>
          </div>

          <!-- Password Change Form -->
          <div class="rounded-lg border border-white/10 bg-white/5 p-4">
            <div class="flex items-center gap-2 mb-4">
              <div class="p-2 bg-orange-500/20 rounded-lg border border-orange-400/30">
                <Lock :size="18" class="text-orange-200" />
              </div>
              <h3 class="text-lg font-semibold text-white">Passwort ändern</h3>
            </div>

            <div class="space-y-4">
              <!-- Current Password -->
              <div>
                <label class="kit-label">Aktuelles Passwort *</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.currentPassword"
                    :type="showCurrentPassword ? 'text' : 'password'"
                    class="kit-input pr-10"
                    :class="{ 'border-red-400': passwordErrors.currentPassword }"
                    placeholder="Aktuelles Passwort eingeben"
                  />
                  <button
                    type="button"
                    @click="showCurrentPassword = !showCurrentPassword"
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80 transition"
                  >
                    <Eye v-if="!showCurrentPassword" :size="18" />
                    <EyeOff v-else :size="18" />
                  </button>
                </div>
                <p v-if="passwordErrors.currentPassword" class="text-xs text-red-300 mt-1">
                  {{ passwordErrors.currentPassword }}
                </p>
              </div>

              <!-- New Password -->
              <div>
                <label class="kit-label">Neues Passwort *</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.newPassword"
                    :type="showNewPassword ? 'text' : 'password'"
                    class="kit-input pr-10"
                    :class="{ 'border-red-400': passwordErrors.newPassword }"
                    placeholder="Neues Passwort eingeben"
                  />
                  <button
                    type="button"
                    @click="showNewPassword = !showNewPassword"
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80 transition"
                  >
                    <Eye v-if="!showNewPassword" :size="18" />
                    <EyeOff v-else :size="18" />
                  </button>
                </div>
                <p v-if="passwordErrors.newPassword" class="text-xs text-red-300 mt-1">
                  {{ passwordErrors.newPassword }}
                </p>
                <p v-else class="text-xs text-white/50 mt-1">
                  Mindestens 8 Zeichen
                </p>
              </div>

              <!-- Confirm New Password -->
              <div>
                <label class="kit-label">Neues Passwort bestätigen *</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    class="kit-input pr-10"
                    :class="{ 'border-red-400': passwordErrors.confirmPassword }"
                    placeholder="Neues Passwort erneut eingeben"
                  />
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80 transition"
                  >
                    <Eye v-if="!showConfirmPassword" :size="18" />
                    <EyeOff v-else :size="18" />
                  </button>
                </div>
                <p v-if="passwordErrors.confirmPassword" class="text-xs text-red-300 mt-1">
                  {{ passwordErrors.confirmPassword }}
                </p>
              </div>
            </div>
          </div>

          <!-- Security Notice -->
          <div class="rounded-lg border border-yellow-400/30 bg-yellow-500/10 p-4">
            <p class="text-sm text-yellow-200">
              <strong>Sicherheitshinweis:</strong> Stellen Sie sicher, dass Ihr Passwort sicher ist und verwenden Sie eine Kombination aus Groß- und Kleinbuchstaben, Zahlen und Sonderzeichen.
            </p>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>
