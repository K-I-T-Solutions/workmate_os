<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import {
  Mail,
  Lock,
  Loader2,
  AlertCircle,
  Eye,
  EyeOff,
} from 'lucide-vue-next';
import { WorkmateAssets } from '@/services/assets';

// Router
const router = useRouter();
const route = useRoute();

// Composable
const { login, loading, error: authError } = useAuth();

// State
const email = ref('');
const password = ref('');
const showPassword = ref(false);
const rememberMe = ref(false);
const formError = ref('');

// Assets
const logo = ref<string | null>(WorkmateAssets.workmateFavicon);

// Actions
async function handleSubmit() {
  formError.value = '';

  // Validation
  if (!email.value || !email.value.trim()) {
    formError.value = 'Bitte geben Sie Ihre E-Mail-Adresse ein';
    return;
  }

  if (!password.value || !password.value.trim()) {
    formError.value = 'Bitte geben Sie Ihr Passwort ein';
    return;
  }

  // Attempt login
  const success = await login({
    email: email.value,
    password: password.value,
  });

  if (success) {
    // Redirect to original route or dashboard
    const redirect = route.query.redirect as string || '/app';
    router.push(redirect);
  } else {
    formError.value = authError.value || 'Login fehlgeschlagen';
  }
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
}

// Focus email input on mount
onMounted(() => {
  // Auto-focus email field
  const emailInput = document.querySelector('input[type="email"]') as HTMLInputElement;
  if (emailInput) {
    emailInput.focus();
  }
});
</script>

<template>
  <div class="login-container">
    <!-- Background Pattern -->
    <div class="login-background"></div>

    <!-- Login Card -->
    <div class="login-card">
      <!-- Logo & Title -->
      <div class="login-header">
        <div class="logo-container">
          <img
            v-if="logo"
            :src="logo"
            alt="WorkmateOS"
            class="logo"
          />
          <div v-else class="logo-fallback">W</div>
        </div>
        <h1 class="login-title">WorkmateOS</h1>
        <p class="login-subtitle">Willkommen zurück</p>
      </div>

      <!-- Error Message -->
      <div v-if="formError || authError" class="error-banner">
        <AlertCircle :size="18" />
        <span>{{ formError || authError }}</span>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleSubmit" class="login-form">
        <!-- Email Field -->
        <div class="form-group">
          <label for="email" class="form-label">
            <Mail :size="16" />
            E-Mail-Adresse
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-input"
            placeholder="name@example.com"
            autocomplete="email"
            :disabled="loading"
            required
          />
        </div>

        <!-- Password Field -->
        <div class="form-group">
          <label for="password" class="form-label">
            <Lock :size="16" />
            Passwort
          </label>
          <div class="password-input-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="••••••••"
              autocomplete="current-password"
              :disabled="loading"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="togglePasswordVisibility"
              :disabled="loading"
              tabindex="-1"
            >
              <Eye v-if="!showPassword" :size="18" />
              <EyeOff v-else :size="18" />
            </button>
          </div>
        </div>

        <!-- Remember Me & Forgot Password -->
        <div class="form-options">
          <label class="checkbox-label">
            <input
              v-model="rememberMe"
              type="checkbox"
              class="checkbox"
              :disabled="loading"
            />
            <span>Angemeldet bleiben</span>
          </label>
          <!-- <a href="#" class="forgot-password-link">Passwort vergessen?</a> -->
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="submit-button"
          :disabled="loading"
        >
          <Loader2 v-if="loading" :size="20" class="animate-spin" />
          <span v-else>Anmelden</span>
        </button>
      </form>

      <!-- Footer -->
      <div class="login-footer">
        <p class="footer-text">
          WorkmateOS v1.0 • K.I.T. Solutions
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Container */
.login-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-primary);
  overflow: hidden;
}

/* Background Pattern */
.login-background {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
  animation: backgroundMove 20s ease-in-out infinite;
}

@keyframes backgroundMove {
  0%, 100% {
    transform: scale(1) translate(0, 0);
  }
  50% {
    transform: scale(1.1) translate(2%, 2%);
  }
}

/* Login Card */
.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  background: var(--color-bg-secondary);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-light);
  border-radius: 1.5rem;
  padding: 2.5rem;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 0 1px var(--color-border-light);
  animation: cardSlideIn 0.6s ease-out;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-container {
  display: inline-block;
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
}

.logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.logo-fallback {
  width: 100%;
  height: 100%;
  border-radius: 1rem;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: white;
}

.login-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.75rem;
  color: rgb(252, 165, 165);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
  animation: errorSlideIn 0.3s ease-out;
}

@keyframes errorSlideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  background: var(--color-panel-glass);
  border: 1px solid var(--color-border-light);
  border-radius: 0.75rem;
  color: var(--color-text-primary);
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  background: var(--color-panel-glass-hover);
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 3px rgba(255, 145, 0, 0.1);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-input::placeholder {
  color: var(--color-text-muted);
}

/* Password Input */
.password-input-wrapper {
  position: relative;
}

.password-input-wrapper .form-input {
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover:not(:disabled) {
  color: var(--color-text-secondary);
  background: var(--color-panel-glass);
}

.password-toggle:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* Form Options */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.checkbox {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
  accent-color: var(--color-accent-primary);
}

.forgot-password-link {
  font-size: 0.875rem;
  color: var(--color-accent-primary);
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password-link:hover {
  color: var(--color-accent-primary-hover);
}

/* Submit Button */
.submit-button {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Footer */
.login-footer {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border-light);
  text-align: center;
}

.footer-text {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin: 0;
}

/* Responsive */
@media (max-width: 480px) {
  .login-card {
    max-width: 90%;
    padding: 2rem 1.5rem;
  }

  .login-title {
    font-size: 1.5rem;
  }
}
</style>
