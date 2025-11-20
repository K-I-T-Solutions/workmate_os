<template>
  <div class="window-overlay" @click.self="closeOnBackdrop">
    <div :class="windowClasses">
      <!-- Titlebar -->
      <div class="window-titlebar flex items-center justify-between mb-4">
        <h2 class="text-white font-semibold text-base">{{ title }}</h2>
        <button @click="emit('close')" class="close-btn">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Body Content -->
      <div class="window-body">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { X } from "lucide-vue-next";

interface Props {
  title: string;
  width?: "sm" | "md" | "lg" | "xl";
  persistent?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  width: "md",
  persistent: false,
});

const emit = defineEmits(["close"]);

const windowClasses = computed(() => [
  "window-container rounded-md p-6 shadow-soft border border-[rgba(255,255,255,0.1)] backdrop-blur-lg",
  props.width === "sm" && "w-[320px]",
  props.width === "md" && "w-[480px]",
  props.width === "lg" && "w-[640px]",
  props.width === "xl" && "w-[800px]",
]);

const closeOnBackdrop = () => {
  if (!props.persistent) emit("close");
};
</script>

<style scoped>
.window-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 80;
}

.window-container {
  background: rgba(20, 24, 33, 0.9);
  animation: wm-fade-in 0.2s ease-out;
}

.window-titlebar {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
}

.close-btn {
  color: var(--color-text-secondary);
  padding: 4px;
  border-radius: 6px;
  transition: 0.15s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

@keyframes wm-fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
