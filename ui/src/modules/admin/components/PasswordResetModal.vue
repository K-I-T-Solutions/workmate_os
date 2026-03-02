<template>
  <div class="dialog-overlay" @click.self="$emit('close')">
    <div class="dialog">
      <div class="dialog-header">
        <h3>Passwort zurücksetzen</h3>
        <button @click="$emit('close')" class="btn-icon">
          <X :size="20" />
        </button>
      </div>

      <div class="dialog-content">
        <p class="employee-info">
          Passwort zurücksetzen für: <strong>{{ employee.first_name }} {{ employee.last_name }}</strong>
          <br />
          <span class="employee-email">{{ employee.email }}</span>
        </p>

        <form @submit.prevent="handleReset">
          <div class="form-field">
            <label>Neues Passwort *</label>
            <div class="password-input-wrapper">
              <input
                v-model="newPassword"
                :type="showPassword ? 'text' : 'password'"
                class="password-input"
                placeholder="Mindestens 8 Zeichen"
                required
                minlength="8"
                @input="validatePassword"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="btn-icon password-toggle"
                tabindex="-1"
              >
                <Eye v-if="!showPassword" :size="18" />
                <EyeOff v-if="showPassword" :size="18" />
              </button>
            </div>
            <div v-if="passwordError" class="validation-error">
              {{ passwordError }}
            </div>
            <div v-if="newPassword.length > 0" class="password-strength">
              <div class="strength-bar" :class="passwordStrength.class">
                <div class="strength-fill" :style="{ width: passwordStrength.width }"></div>
              </div>
              <span class="strength-label">{{ passwordStrength.label }}</span>
            </div>
          </div>

          <div class="form-field">
            <label class="checkbox-label">
              <input v-model="sendNotification" type="checkbox" />
              <span>E-Mail-Benachrichtigung an Mitarbeiter senden</span>
            </label>
            <p class="field-hint">
              Der Mitarbeiter erhält eine E-Mail mit der Bestätigung der Passwortänderung.
            </p>
          </div>

          <div class="dialog-actions">
            <button type="button" @click="$emit('close')" class="btn-secondary">
              Abbrechen
            </button>
            <button
              type="submit"
              class="btn-primary"
              :disabled="!isValid || resetting"
            >
              <Key v-if="!resetting" :size="18" />
              <span v-if="!resetting">Passwort zurücksetzen</span>
              <span v-else>Wird zurückgesetzt...</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { X, Eye, EyeOff, Key } from 'lucide-vue-next';

interface Employee {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

const props = defineProps<{
  employee: Employee;
}>();

const emit = defineEmits<{
  close: [];
  reset: [{ newPassword: string; sendNotification: boolean }];
}>();

const newPassword = ref('');
const showPassword = ref(false);
const sendNotification = ref(true);
const passwordError = ref('');
const resetting = ref(false);

function validatePassword() {
  passwordError.value = '';

  if (newPassword.value.length > 0 && newPassword.value.length < 8) {
    passwordError.value = 'Passwort muss mindestens 8 Zeichen lang sein';
    return false;
  }

  return true;
}

const isValid = computed(() => {
  return newPassword.value.length >= 8 && !passwordError.value;
});

const passwordStrength = computed(() => {
  const password = newPassword.value;
  if (password.length === 0) {
    return { width: '0%', label: '', class: '' };
  }

  let strength = 0;

  // Length
  if (password.length >= 8) strength += 25;
  if (password.length >= 12) strength += 25;

  // Complexity
  if (/[a-z]/.test(password)) strength += 12;
  if (/[A-Z]/.test(password)) strength += 13;
  if (/[0-9]/.test(password)) strength += 12;
  if (/[^A-Za-z0-9]/.test(password)) strength += 13;

  if (strength < 40) {
    return { width: '33%', label: 'Schwach', class: 'weak' };
  } else if (strength < 70) {
    return { width: '66%', label: 'Mittel', class: 'medium' };
  } else {
    return { width: '100%', label: 'Stark', class: 'strong' };
  }
});

async function handleReset() {
  if (!isValid.value) return;

  resetting.value = true;
  try {
    emit('reset', {
      newPassword: newPassword.value,
      sendNotification: sendNotification.value,
    });
  } finally {
    resetting.value = false;
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.dialog {
  background: var(--color-bg-primary);
  border-radius: 12px;
  border: 1px solid var(--color-border-light);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.dialog-content {
  padding: 1.5rem;
  overflow-y: auto;
}

.employee-info {
  margin: 0 0 1.5rem 0;
  padding: 1rem;
  background: var(--color-bg-secondary);
  border-radius: 8px;
  border-left: 3px solid var(--color-primary);
}

.employee-email {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.form-field {
  margin-bottom: 1.5rem;
}

.form-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  flex: 1;
  padding: 0.75rem;
  padding-right: 3rem;
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.password-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.password-toggle {
  position: absolute;
  right: 0.5rem;
  color: var(--color-text-secondary);
}

.validation-error {
  margin-top: 0.5rem;
  color: #ef4444;
  font-size: 0.875rem;
}

.password-strength {
  margin-top: 0.5rem;
}

.strength-bar {
  height: 4px;
  background: var(--color-border-light);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-bar.weak .strength-fill {
  background: #ef4444;
}

.strength-bar.medium .strength-fill {
  background: #f59e0b;
}

.strength-bar.strong .strength-fill {
  background: #10b981;
}

.strength-label {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.field-hint {
  margin: 0.5rem 0 0 1.675rem;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  line-height: 1.4;
}

.dialog-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border-light);
}

.btn-icon {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-border-medium);
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: var(--color-primary);
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
