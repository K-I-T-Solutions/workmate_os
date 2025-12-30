<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { handleZitadelCallback, getPostLoginRedirect } from '@/services/zitadel';
import { Loader2 } from 'lucide-vue-next';

const router = useRouter();
const { loginWithOIDC } = useAuth();
const status = ref('Authentifizierung läuft...');
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    // Get code and state from URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (!code || !state) {
      error.value = 'Ungültige OAuth-Antwort';
      return;
    }

    status.value = 'Token wird abgerufen...';

    // Exchange code for tokens
    const tokens = await handleZitadelCallback(code, state);

    if (!tokens) {
      error.value = 'Fehler beim Token-Austausch';
      return;
    }

    status.value = 'Anmeldung wird verarbeitet...';

    // Login with OIDC tokens (both id_token and access_token)
    const success = await loginWithOIDC(tokens.id_token, tokens.access_token);

    if (!success) {
      error.value = 'Anmeldung fehlgeschlagen';
      return;
    }

    // Redirect to original destination or dashboard
    const redirect = getPostLoginRedirect() || '/app';
    router.push(redirect);
  } catch (err: any) {
    console.error('Auth callback error:', err);
    error.value = err.message || 'Ein unerwarteter Fehler ist aufgetreten';
  }
});
</script>

<template>
  <div class="callback-container">
    <div class="callback-card">
      <div v-if="!error" class="loading-state">
        <Loader2 :size="48" class="spinner" />
        <h2>{{ status }}</h2>
        <p>Bitte warten Sie einen Moment...</p>
      </div>

      <div v-else class="error-state">
        <div class="error-icon">⚠️</div>
        <h2>Authentifizierung fehlgeschlagen</h2>
        <p>{{ error }}</p>
        <button @click="router.push('/login')" class="back-button">
          Zurück zum Login
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.callback-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-primary);
}

.callback-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 1.5rem;
  padding: 3rem 2.5rem;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.loading-state h2,
.error-state h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 1rem 0 0.5rem 0;
}

.loading-state p,
.error-state p {
  color: var(--color-text-secondary);
  margin: 0;
}

.spinner {
  color: var(--color-accent-primary);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.back-button {
  margin-top: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.back-button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
}
</style>
