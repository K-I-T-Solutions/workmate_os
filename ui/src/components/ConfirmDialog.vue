<template>
  <Teleport to="body">
    <Transition name="confirm-fade">
      <div v-if="pending" class="confirm-overlay" @mousedown.self="cancel">
        <div class="confirm-dialog" role="dialog" :aria-label="pending.title">
          <div class="confirm-header">
            <span class="confirm-title">{{ pending.title }}</span>
          </div>
          <div class="confirm-body">
            <p class="confirm-message">{{ pending.message }}</p>
          </div>
          <div class="confirm-footer">
            <button class="btn-cancel" @click="cancel">Abbrechen</button>
            <button class="btn-confirm" :class="`btn-confirm--${pending.variant}`" @click="accept" autofocus>Bestätigen</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useConfirm } from '@/composables/useConfirm'

const { pending, accept, cancel } = useConfirm()

function onKeydown(e: KeyboardEvent) {
  if (!pending.value) return
  if (e.key === 'Enter') accept()
  if (e.key === 'Escape') cancel()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-dialog {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-medium);
  border-radius: 12px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
  min-width: 360px;
  max-width: 480px;
  width: 90%;
  overflow: hidden;
}

.confirm-header {
  padding: 1.25rem 1.5rem 0;
}

.confirm-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.confirm-body {
  padding: 0.75rem 1.5rem 1.25rem;
}

.confirm-message {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
}

.confirm-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-secondary);
}

.btn-cancel {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--color-border-medium);
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.btn-confirm {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  border: none;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-confirm--default {
  background: var(--color-accent-primary);
}

.btn-confirm--default:hover {
  filter: brightness(1.1);
}

.btn-confirm--danger {
  background: var(--color-error);
}

.btn-confirm--danger:hover {
  filter: brightness(1.1);
}

.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity 0.15s ease;
}

.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}

.confirm-fade-enter-active .confirm-dialog,
.confirm-fade-leave-active .confirm-dialog {
  transition: transform 0.15s ease;
}

.confirm-fade-enter-from .confirm-dialog {
  transform: scale(0.95);
}

.confirm-fade-leave-to .confirm-dialog {
  transform: scale(0.95);
}
</style>
