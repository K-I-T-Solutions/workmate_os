<template>
  <div :class="panelClasses">
    <header v-if="title" class="mb-3">
      <h2 class="text-heading text-primary">{{ title }}</h2>
      <slot name="actions"></slot>
    </header>

    <div class="text-secondary">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  title?: string;
  variant?: "default" | "glass" | "highlight";
  padding?: "sm" | "md" | "lg";
}

const props = withDefaults(defineProps<Props>(), {
  variant: "default",
  padding: "md",
});

const panelClasses = computed(() => {
  const paddingMap: Record<string, string> = {
    sm: "p-[var(--space-sm)]",
    md: "p-[var(--space-md)]",
    lg: "p-[var(--space-lg)]",
  };

  return [
    "rounded-[var(--radius-md)] border w-full shadow-soft",
    paddingMap[props.padding],

    props.variant === "default" &&
      "bg-[var(--color-bg-primary)] border-[var(--color-border-light)]",

    props.variant === "glass" &&
      "bg-[var(--color-panel-glass)] backdrop-blur-md border-[var(--color-border-light)]",

    props.variant === "highlight" &&
      "bg-[rgba(255,145,0,0.10)] border-[var(--color-accent-primary)]",
  ];
});
</script>
