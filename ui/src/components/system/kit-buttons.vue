<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- Loading Spinner -->
    <svg
      v-if="loading"
      class="animate-spin h-4 w-4 text-current flex-shrink-0"
      :class="label ? 'mr-2' : ''"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4l3-3-3-3v4a12 12 0 00-12 12h4z"
      />
    </svg>

    <!-- Icon -->
    <component
      v-if="icon && !loading"
      :is="icon"
      class="w-4 h-4 flex-shrink-0"
      :class="label ? 'mr-2' : ''"
    />

    <!-- Label -->
    <span class="whitespace-nowrap">{{ label }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  label: string;
  icon?: any;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "md",
  disabled: false,
  loading: false,
});

const emit = defineEmits(["click"]);

const handleClick = (e: MouseEvent) => {
  if (!props.loading && !props.disabled) emit("click", e);
};

const buttonClasses = computed(() => [
  // Base
  "inline-flex items-center justify-center font-semibold rounded-[var(--radius-md)] transition-all duration-150",
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-accent-primary)]",
  "backdrop-blur-md",

  // Sizes
  props.size === "sm" && "px-[12px] py-[6px] text-sm",
  props.size === "md" && "px-[16px] py-[8px] text-base",
  props.size === "lg" && "px-[20px] py-[10px] text-lg",

  // Variants
  props.variant === "primary" &&
    "bg-[var(--color-accent-primary)] text-black shadow-soft hover:bg-[var(--color-accent-primary)]/90",

  props.variant === "secondary" &&
    "bg-[var(--color-panel-glass)] border border-[var(--color-border-light)] text-[var(--color-text-primary)] shadow-soft hover:bg-white/10",

  props.variant === "ghost" &&
    "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-white/5",

  // Disabled
  (props.disabled || props.loading) &&
    "opacity-50 cursor-not-allowed pointer-events-none",
]);
</script>
