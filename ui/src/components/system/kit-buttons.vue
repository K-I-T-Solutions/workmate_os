<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- Loading Spinner -->
    <svg
      v-if="loading"
      class="animate-spin h-5 w-5 mr-2 text-white"
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
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4l3-3-3-3v4a12 12 0 00-12 12h4z"
      ></path>
    </svg>

    <!-- Icon (optional) -->
    <component v-if="icon && !loading" :is="icon" class="w-5 h-5 mr-2" />

    <!-- Label -->
    <span>{{ label }}</span>
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

const buttonClasses = computed(() => {
  return [
    // Base
    "inline-flex items-center justify-center rounded-md font-medium transition-all duration-150",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",

    // Size
    props.size === "sm" && "px-3 py-1 text-sm",
    props.size === "md" && "px-4 py-2 text-base",
    props.size === "lg" && "px-6 py-3 text-lg",

    // Variants
    props.variant === "primary" &&
      "bg-accent-primary text-black hover:opacity-90 shadow-soft",

    props.variant === "secondary" &&
      "bg-[rgba(255,255,255,0.1)] text-white border border-[rgba(255,255,255,0.2)] hover:bg-[rgba(255,255,255,0.15)]",

    props.variant === "ghost" &&
      "text-secondary hover:text-white hover:bg-[rgba(255,255,255,0.05)]",

    // Disabled
    (props.disabled || props.loading) && "opacity-50 cursor-not-allowed",
  ];
});
</script>

<style scoped>
button {
  backdrop-filter: blur(10px);
}
</style>
