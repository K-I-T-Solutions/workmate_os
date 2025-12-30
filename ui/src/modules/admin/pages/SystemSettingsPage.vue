<template>
  <div class="settings-page">
    <!-- Header -->
    <div class="page-header">
      <h2 class="page-title">System-Einstellungen</h2>
      <button @click="saveSettings" class="btn-primary" :disabled="saving">
        <Save :size="18" />
        {{ saving ? 'Speichern...' : 'Änderungen speichern' }}
      </button>
    </div>

    <!-- Settings Form -->
    <div class="settings-form">
      <!-- Company Information -->
      <h3 class="form-section-title">
        <Building2 :size="18" />
        Firmeninformationen
      </h3>

      <div class="form-field">
        <label>Firmenname</label>
        <input v-model="settings.company_name" type="text" placeholder="K.I.T IT-Solutions" />
      </div>

      <div class="form-field">
        <label>Rechtsform</label>
        <input v-model="settings.company_legal" type="text" placeholder="GmbH" />
      </div>

      <div class="form-field">
        <label>Steuernummer</label>
        <input v-model="settings.tax_number" type="text" placeholder="DE123456789" />
      </div>

      <div class="form-field">
        <label>Handelsregisternummer</label>
        <input v-model="settings.registration_number" type="text" placeholder="HRB 12345" />
      </div>

      <div class="form-field">
        <label>Straße & Hausnummer</label>
        <input v-model="settings.address_street" type="text" placeholder="Musterstraße 123" />
      </div>

      <div class="form-row">
        <div class="form-field">
          <label>PLZ</label>
          <input v-model="settings.address_zip" type="text" placeholder="56068" />
        </div>
        <div class="form-field">
          <label>Stadt</label>
          <input v-model="settings.address_city" type="text" placeholder="Koblenz" />
        </div>
      </div>

      <div class="form-field">
        <label>Land</label>
        <input v-model="settings.address_country" type="text" placeholder="Deutschland" />
      </div>

      <div class="form-field">
        <label>E-Mail</label>
        <input v-model="settings.company_email" type="email" placeholder="info@kit-it-koblenz.de" />
      </div>

      <div class="form-field">
        <label>Telefon</label>
        <input v-model="settings.company_phone" type="tel" placeholder="+49 261 ..." />
      </div>

      <div class="form-field">
        <label>Website</label>
        <input v-model="settings.company_website" type="url" placeholder="https://kit-it-koblenz.de" />
      </div>

      <!-- Localization -->
      <h3 class="form-section-title">
        <Globe :size="18" />
        Lokalisierung
      </h3>

      <div class="form-field">
        <label>Standard-Zeitzone</label>
        <select v-model="settings.default_timezone">
          <option value="Europe/Berlin">Europa/Berlin (CET/CEST)</option>
          <option value="Europe/London">Europa/London (GMT/BST)</option>
          <option value="America/New_York">Amerika/New York (EST/EDT)</option>
          <option value="Asia/Tokyo">Asien/Tokyo (JST)</option>
        </select>
      </div>

      <div class="form-field">
        <label>Standard-Sprache</label>
        <select v-model="settings.default_language">
          <option value="de">Deutsch</option>
          <option value="en">English</option>
          <option value="fr">Français</option>
        </select>
      </div>

      <div class="form-field">
        <label>Währung</label>
        <select v-model="settings.default_currency">
          <option value="EUR">EUR (€)</option>
          <option value="USD">USD ($)</option>
          <option value="GBP">GBP (£)</option>
        </select>
      </div>

      <div class="form-field">
        <label>Datumsformat</label>
        <select v-model="settings.date_format">
          <option value="DD.MM.YYYY">DD.MM.YYYY (31.12.2025)</option>
          <option value="MM/DD/YYYY">MM/DD/YYYY (12/31/2025)</option>
          <option value="YYYY-MM-DD">YYYY-MM-DD (2025-12-31)</option>
        </select>
      </div>

      <!-- Working Hours -->
      <h3 class="form-section-title">
        <Clock :size="18" />
        Arbeitszeiten
      </h3>

      <div class="form-field">
        <label>Arbeitsstunden pro Tag</label>
        <input v-model.number="settings.working_hours_per_day" type="number" step="0.5" min="1" max="24" />
      </div>

      <div class="form-field">
        <label>Arbeitstage pro Woche</label>
        <input v-model.number="settings.working_days_per_week" type="number" min="1" max="7" />
      </div>

      <div class="form-field">
        <label>Urlaubstage pro Jahr</label>
        <input v-model.number="settings.vacation_days_per_year" type="number" min="0" max="365" />
      </div>

      <div class="form-field">
        <label class="checkbox-label">
          <input v-model="settings.weekend_saturday" type="checkbox" />
          <span>Samstag ist Wochenende</span>
        </label>
      </div>

      <div class="form-field">
        <label class="checkbox-label">
          <input v-model="settings.weekend_sunday" type="checkbox" />
          <span>Sonntag ist Wochenende</span>
        </label>
      </div>

      <!-- System -->
      <h3 class="form-section-title">
        <Settings :size="18" />
        System
      </h3>

      <div class="form-field">
        <label class="checkbox-label">
          <input v-model="settings.maintenance_mode" type="checkbox" />
          <span>Wartungsmodus aktiv (System für normale User nicht verfügbar)</span>
        </label>
      </div>

      <div class="form-field">
        <label class="checkbox-label">
          <input v-model="settings.allow_registration" type="checkbox" />
          <span>Selbstregistrierung erlauben</span>
        </label>
      </div>

      <div class="form-field">
        <label class="checkbox-label">
          <input v-model="settings.require_email_verification" type="checkbox" />
          <span>E-Mail-Verifizierung erforderlich</span>
        </label>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="saveSuccess" class="success-message">
      <CheckCircle :size="20" />
      Einstellungen erfolgreich gespeichert!
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Building2, Globe, Clock, Settings, Save, CheckCircle } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

// State
const settings = ref({
  // Company
  company_name: '',
  company_legal: '',
  tax_number: '',
  registration_number: '',
  address_street: '',
  address_zip: '',
  address_city: '',
  address_country: '',
  company_email: '',
  company_phone: '',
  company_website: '',

  // Localization
  default_timezone: 'Europe/Berlin',
  default_language: 'de',
  default_currency: 'EUR',
  date_format: 'DD.MM.YYYY',

  // Working Hours
  working_hours_per_day: 8,
  working_days_per_week: 5,
  vacation_days_per_year: 30,
  weekend_saturday: true,
  weekend_sunday: true,

  // System
  maintenance_mode: false,
  allow_registration: false,
  require_email_verification: true,
});

const saving = ref(false);
const saveSuccess = ref(false);

// Load settings
async function loadSettings() {
  try {
    // TODO: Backend endpoint noch nicht vorhanden
    // const response = await apiClient.get('/api/settings');
    // settings.value = { ...settings.value, ...response.data };

    // Temporary: Load from localStorage
    const stored = localStorage.getItem('system_settings');
    if (stored) {
      settings.value = { ...settings.value, ...JSON.parse(stored) };
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
  }
}

// Save settings
async function saveSettings() {
  saving.value = true;
  saveSuccess.value = false;

  try {
    // TODO: Backend endpoint noch nicht vorhanden
    // await apiClient.put('/api/settings', settings.value);

    // Temporary: Save to localStorage
    localStorage.setItem('system_settings', JSON.stringify(settings.value));

    saveSuccess.value = true;
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (error) {
    console.error('Failed to save settings:', error);
    alert('Fehler beim Speichern der Einstellungen');
  } finally {
    saving.value = false;
  }
}

// Initial load
onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

/* Buttons */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Settings Form */
.settings-form {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
}

/* Section Titles */
.form-section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 2rem 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-border-light);
}

.form-section-title:first-child {
  margin-top: 0;
}

.form-section-title svg {
  color: var(--color-primary);
}

/* Form Fields */
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-field label:not(.checkbox-label) {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-field input[type="text"],
.form-field input[type="email"],
.form-field input[type="tel"],
.form-field input[type="url"],
.form-field input[type="number"],
.form-field select {
  padding: 0.625rem 0.875rem;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
  width: 100%;
}

.form-field input:focus,
.form-field select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
  cursor: pointer;
  padding: 0.5rem 0;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* Success Message */
.success-message {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
  z-index: 100;
}

@keyframes slideIn {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .settings-form {
    padding: 1rem;
  }

  .form-section-title {
    font-size: 0.9375rem;
    margin: 1.5rem 0 0.75rem 0;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .form-field label:not(.checkbox-label) {
    font-size: 0.8125rem;
  }

  .form-field input,
  .form-field select {
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
  }

  .success-message {
    bottom: 1rem;
    right: 1rem;
    left: 1rem;
    font-size: 0.8125rem;
    padding: 0.875rem 1rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.125rem;
  }

  .btn-primary {
    padding: 0.5rem 0.875rem;
    font-size: 0.8125rem;
    width: 100%;
    justify-content: center;
  }

  .settings-form {
    padding: 0.875rem;
  }

  .form-section-title {
    font-size: 0.875rem;
  }

  .checkbox-label {
    font-size: 0.8125rem;
    padding: 0.375rem 0;
  }

  .checkbox-label input[type="checkbox"] {
    width: 16px;
    height: 16px;
  }

  .success-message {
    padding: 0.75rem 0.875rem;
    font-size: 0.75rem;
  }
}
</style>
