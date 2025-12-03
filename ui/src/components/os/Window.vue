<template>
  <div class="wm-overlay" @click.self="closeOnBackdrop">
    <div class="wm-window" :class="widthClass">
      <!-- Titlebar -->
      <div class="wm-titlebar">
        <div class="titlebar-content">
          <!-- Title with Icon (optional) -->
          <div class="title-wrapper">
            <slot name="icon">
              <!-- Optional: Icon slot -->
            </slot>
            <h2 class="window-title">{{ title }}</h2>
          </div>

          <!-- Close Button -->
          <button @click="emit('close')" class="close-btn" aria-label="Schließen">
            <X class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="wm-body">
        <slot />
      </div>

      <!-- Footer (optional) -->
      <div v-if="$slots.footer" class="wm-footer">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { X } from "lucide-vue-next";

interface Props {
  title: string;
  width?: "sm" | "md" | "lg" | "xl" | "2xl";
  persistent?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  width: "md",
  persistent: false,
});

const emit = defineEmits(["close"]);

const widthClass = computed(() => {
  const widths = {
    sm: "window-sm",
    md: "window-md",
    lg: "window-lg",
    xl: "window-xl",
    "2xl": "window-2xl",
  };
  return widths[props.width];
});

const closeOnBackdrop = () => {
  if (!props.persistent) emit("close");
};
</script>

<style scoped>
/* ============================================================
   OVERLAY
   ============================================================ */
.wm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 80;
  padding: 1.5rem;
  animation: overlay-fade-in 250ms cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes overlay-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* ============================================================
   WINDOW CONTAINER
   ============================================================ */
.wm-window {
  background: rgba(35, 34, 35, 0.92);
  backdrop-filter: blur(16px);
  border: 1px solid var(--color-border-light);
  border-radius: 1rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3),
              0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 3rem);
  overflow: hidden;
  animation: window-scale-in 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes window-scale-in {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Window Sizes */
.window-sm {
  width: 100%;
  max-width: 400px;
}

.window-md {
  width: 100%;
  max-width: 540px;
}

.window-lg {
  width: 100%;
  max-width: 720px;
}

.window-xl {
  width: 100%;
  max-width: 900px;
}

.window-2xl {
  width: 100%;
  max-width: 1200px;
}

/* ============================================================
   TITLEBAR
   ============================================================ */
.wm-titlebar {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.titlebar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

/* Window Title */
.window-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
  line-height: 1.4;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ============================================================
   CLOSE BUTTON
   ============================================================ */
.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: transparent;
  border: 1px solid transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--color-border-primary);
  color: var(--color-text-primary);
  transform: scale(1.05);
}

.close-btn:active {
  transform: scale(0.95);
}

/* ============================================================
   BODY
   ============================================================ */
.wm-body {
  padding: 2rem;
  color: var(--color-text-secondary);
  font-size: 0.9375rem;
  line-height: 1.6;
  overflow-y: auto;
  flex: 1;
}

/* Custom Scrollbar */
.wm-body::-webkit-scrollbar {
  width: 8px;
}

.wm-body::-webkit-scrollbar-track {
  background: transparent;
}

.wm-body::-webkit-scrollbar-thumb {
  background: var(--color-border-primary);
  border-radius: 4px;
}

.wm-body::-webkit-scrollbar-thumb:hover {
  background: var(--color-accent-primary);
}

/* ============================================================
   FOOTER (OPTIONAL)
   ============================================================ */
.wm-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.1);
}

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 768px) {
  .wm-overlay {
    padding: 1rem;
  }

  .wm-window {
    max-height: calc(100vh - 2rem);
  }

  .wm-titlebar {
    padding: 1.25rem 1.5rem;
  }

  .window-title {
    font-size: 1rem;
  }

  .wm-body {
    padding: 1.5rem;
  }

  .wm-footer {
    padding: 1.25rem 1.5rem;
  }
}

@media (max-width: 480px) {
  .wm-overlay {
    padding: 0.5rem;
  }

  .wm-window {
    border-radius: 0.75rem;
    max-height: calc(100vh - 1rem);
  }

  .wm-titlebar {
    padding: 1rem 1.25rem;
  }

  .window-title {
    font-size: 0.9375rem;
  }

  .wm-body {
    padding: 1.25rem;
    font-size: 0.875rem;
  }

  .wm-footer {
    padding: 1rem 1.25rem;
  }
}

/* ============================================================
   DARK MODE ENHANCEMENTS
   ============================================================ */
@media (prefers-color-scheme: dark) {
  .wm-overlay {
    background: rgba(0, 0, 0, 0.6);
  }

  .wm-window {
    background: rgba(20, 20, 25, 0.95);
  }
}

/* ============================================================
   UTILITY CLASSES (für Content im Body)
   ============================================================ */
.wm-body :deep(p) {
  margin-bottom: 1rem;
}

.wm-body :deep(p:last-child) {
  margin-bottom: 0;
}

.wm-body :deep(h3) {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.75rem;
}

.wm-body :deep(ul),
.wm-body :deep(ol) {
  margin-left: 1.25rem;
  margin-bottom: 1rem;
}

.wm-body :deep(li) {
  margin-bottom: 0.5rem;
}
</style>
