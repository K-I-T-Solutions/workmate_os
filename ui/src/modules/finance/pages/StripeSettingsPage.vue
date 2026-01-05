<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useStripe } from '../composables';
import type { StripeConfigRequest } from '../types/stripe';

const {
  config,
  loading,
  error,
  isConfigured,
  isTestMode,
  fetchConfig,
  saveConfig,
  deactivateConfig,
} = useStripe();

// Form state
const showConfigForm = ref(false);
const publishableKey = ref('');
const secretKey = ref('');
const webhookSecret = ref('');
const testMode = ref(true);

// Toast messages
const successMessage = ref<string | null>(null);
const errorMessage = ref<string | null>(null);

onMounted(async () => {
  await fetchConfig();
  if (config.value) {
    testMode.value = config.value.test_mode;
  }
});

function clearMessages() {
  successMessage.value = null;
  errorMessage.value = null;
}

async function handleSaveConfig() {
  clearMessages();

  // Validate inputs
  if (!publishableKey.value || !secretKey.value) {
    errorMessage.value = 'Publishable Key und Secret Key sind erforderlich';
    return;
  }

  // Validate key formats
  if (!publishableKey.value.startsWith('pk_')) {
    errorMessage.value = 'Publishable Key muss mit pk_test_ oder pk_live_ beginnen';
    return;
  }

  if (!secretKey.value.startsWith('sk_')) {
    errorMessage.value = 'Secret Key muss mit sk_test_ oder sk_live_ beginnen';
    return;
  }

  try {
    const configData: StripeConfigRequest = {
      publishable_key: publishableKey.value,
      secret_key: secretKey.value,
      webhook_secret: webhookSecret.value || undefined,
      test_mode: testMode.value,
    };

    const response = await saveConfig(configData);
    successMessage.value = 'Stripe Konfiguration erfolgreich gespeichert';
    showConfigForm.value = false;

    // Clear sensitive data
    publishableKey.value = '';
    secretKey.value = '';
    webhookSecret.value = '';
  } catch (e: any) {
    errorMessage.value = e.message || 'Fehler beim Speichern der Konfiguration';
  }
}

async function handleDeactivateConfig() {
  if (!confirm('Möchten Sie die Stripe-Konfiguration wirklich deaktivieren?')) {
    return;
  }

  clearMessages();
  try {
    await deactivateConfig();
    successMessage.value = 'Stripe Konfiguration deaktiviert';
    showConfigForm.value = false;
  } catch (e: any) {
    errorMessage.value = e.message || 'Fehler beim Deaktivieren der Konfiguration';
  }
}

function formatDateTime(dateString?: string) {
  if (!dateString) return 'Nie';
  return new Date(dateString).toLocaleString('de-DE');
}
</script>

<template>
  <div class="max-w-screen-lg mx-auto py-6 px-4">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-white mb-2">Stripe Payment Integration</h1>
      <p class="text-white/60">
        Konfigurieren Sie Stripe für Online-Zahlungen per Kreditkarte
      </p>
    </div>

    <!-- Toast Messages -->
    <div v-if="successMessage" class="mb-4 p-4 rounded-lg bg-green-500/20 text-green-300 border border-green-500/30">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="mb-4 p-4 rounded-lg bg-red-500/20 text-red-300 border border-red-500/30">
      {{ errorMessage }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-white/60">Lade Konfiguration...</div>
    </div>

    <!-- Configuration Status -->
    <div v-else-if="!showConfigForm" class="space-y-6">
      <!-- Status Card -->
      <div class="p-6 rounded-lg border" :class="isConfigured ? 'bg-green-500/10 border-green-500/30' : 'bg-white/5 border-white/10'">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div v-if="isConfigured" class="text-3xl">💳</div>
            <div v-else class="text-3xl">⚙️</div>
            <div>
              <h2 class="text-xl font-semibold text-white">
                {{ isConfigured ? 'Konfiguriert' : 'Nicht konfiguriert' }}
              </h2>
              <p class="text-white/60 text-sm">
                {{ isConfigured ? 'Stripe ist verbunden und aktiv' : 'Bitte Stripe API Keys eingeben' }}
              </p>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="showConfigForm = true"
              class="px-4 py-2 rounded-lg bg-blue-500/20 text-blue-300 hover:bg-blue-500/30 transition-colors"
            >
              {{ isConfigured ? 'Bearbeiten' : 'Konfigurieren' }}
            </button>
            <button
              v-if="isConfigured"
              @click="handleDeactivateConfig"
              class="px-4 py-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition-colors"
            >
              Deaktivieren
            </button>
          </div>
        </div>

        <!-- Config Details -->
        <div v-if="isConfigured && config" class="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
          <div>
            <div class="text-white/60 text-sm mb-1">Modus</div>
            <div class="text-white font-medium">
              <span v-if="isTestMode" class="inline-flex items-center gap-1">
                🧪 Test Mode
              </span>
              <span v-else class="inline-flex items-center gap-1">
                🚀 Live Mode
              </span>
            </div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Status</div>
            <div class="text-white font-medium">
              <span v-if="config.is_active" class="text-green-400">✓ Aktiv</span>
              <span v-else class="text-red-400">✗ Inaktiv</span>
            </div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Erstellt</div>
            <div class="text-white">{{ formatDateTime(config.created_at) }}</div>
          </div>
          <div>
            <div class="text-white/60 text-sm mb-1">Aktualisiert</div>
            <div class="text-white">{{ formatDateTime(config.updated_at) }}</div>
          </div>
        </div>
      </div>

      <!-- Info Card -->
      <div class="p-6 rounded-lg bg-blue-500/10 border border-blue-500/30">
        <h3 class="text-lg font-semibold text-white mb-3">ℹ️ Über Stripe Integration</h3>
        <div class="space-y-2 text-white/80 text-sm">
          <p>
            <strong>Payment Intents:</strong> Ermöglicht Custom Checkout mit Stripe Elements in Ihrer Anwendung.
          </p>
          <p>
            <strong>Payment Links:</strong> Erstellt einen Link zu einer Stripe Checkout-Seite für einfache Zahlungen.
          </p>
          <p>
            <strong>Webhooks:</strong> Automatische Zahlungsbestätigung durch Stripe Webhook Events.
          </p>
          <p>
            <strong>Sicherheit:</strong> Stripe verarbeitet Kreditkartendaten PCI-compliant, keine Kartendaten auf Ihrem Server.
          </p>
        </div>
      </div>

      <!-- Setup Instructions -->
      <div class="p-6 rounded-lg bg-white/5 border border-white/10">
        <h3 class="text-lg font-semibold text-white mb-3">🔧 Setup-Anleitung</h3>
        <ol class="space-y-2 text-white/80 text-sm list-decimal list-inside">
          <li>Erstellen Sie ein Stripe-Konto auf <a href="https://stripe.com" target="_blank" class="text-blue-400 hover:underline">stripe.com</a></li>
          <li>Navigieren Sie zu <strong>Developers → API Keys</strong></li>
          <li>Kopieren Sie den <strong>Publishable Key</strong> (pk_test_... oder pk_live_...)</li>
          <li>Kopieren Sie den <strong>Secret Key</strong> (sk_test_... oder sk_live_...)</li>
          <li>Optional: Konfigurieren Sie Webhooks für automatische Zahlungsbestätigung</li>
          <li>Geben Sie die Keys hier ein und speichern Sie die Konfiguration</li>
        </ol>
      </div>
    </div>

    <!-- Configuration Form -->
    <div v-else class="space-y-6">
      <div class="p-6 rounded-lg bg-white/5 border border-white/10">
        <h2 class="text-xl font-semibold text-white mb-6">
          {{ isConfigured ? 'Stripe Konfiguration bearbeiten' : 'Stripe Konfiguration' }}
        </h2>

        <form @submit.prevent="handleSaveConfig" class="space-y-4">
          <!-- Test Mode Toggle -->
          <div class="flex items-center gap-3 p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <input
              type="checkbox"
              id="testMode"
              v-model="testMode"
              class="w-5 h-5 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-blue-500"
            />
            <label for="testMode" class="text-white cursor-pointer flex-1">
              <div class="font-medium">Test Mode</div>
              <div class="text-sm text-white/60">
                Verwenden Sie Test-Keys (pk_test_... / sk_test_...) für Entwicklung
              </div>
            </label>
          </div>

          <!-- Publishable Key -->
          <div>
            <label for="publishableKey" class="block text-sm font-medium text-white mb-2">
              Publishable Key *
            </label>
            <input
              type="text"
              id="publishableKey"
              v-model="publishableKey"
              :placeholder="testMode ? 'pk_test_...' : 'pk_live_...'"
              required
              class="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="mt-1 text-xs text-white/60">
              Öffentlicher Key für Frontend (sicher)
            </p>
          </div>

          <!-- Secret Key -->
          <div>
            <label for="secretKey" class="block text-sm font-medium text-white mb-2">
              Secret Key *
            </label>
            <input
              type="password"
              id="secretKey"
              v-model="secretKey"
              :placeholder="testMode ? 'sk_test_...' : 'sk_live_...'"
              required
              class="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="mt-1 text-xs text-white/60">
              Privater Key für Backend (vertraulich!)
            </p>
          </div>

          <!-- Webhook Secret -->
          <div>
            <label for="webhookSecret" class="block text-sm font-medium text-white mb-2">
              Webhook Secret (Optional)
            </label>
            <input
              type="password"
              id="webhookSecret"
              v-model="webhookSecret"
              placeholder="whsec_..."
              class="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="mt-1 text-xs text-white/60">
              Signing Secret für Webhook-Verifizierung
            </p>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-4">
            <button
              type="submit"
              :disabled="loading"
              class="px-6 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ loading ? 'Speichern...' : 'Speichern' }}
            </button>
            <button
              type="button"
              @click="showConfigForm = false"
              class="px-6 py-2 rounded-lg bg-white/5 text-white hover:bg-white/10 transition-colors"
            >
              Abbrechen
            </button>
          </div>
        </form>
      </div>

      <!-- Security Warning -->
      <div class="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
        <div class="flex items-start gap-3">
          <div class="text-2xl">⚠️</div>
          <div class="text-sm text-yellow-300">
            <strong>Sicherheitshinweis:</strong> Der Secret Key ist vertraulich und sollte niemals im Frontend verwendet werden.
            Er wird nur auf dem Server verwendet und sollte sicher gespeichert werden (z.B. verschlüsselt in der Datenbank).
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
