<template>
  <div :class="panelClasses">
    <header v-if="title" class="mb-3 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-white">{{ title }}</h2>
      <slot name="actions"></slot>
    </header>

    <div class="panel-body">
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

const panelClasses = computed(() => [
  "rounded-md border border-[rgba(255,255,255,0.1)] shadow-soft w-full",
  props.padding === "sm" && "p-3",
  props.padding === "md" && "p-4",
  props.padding === "lg" && "p-6",

  props.variant === "default" && "bg-[#141821]",
  props.variant === "glass" && "bg-[rgba(255,255,255,0.05)] backdrop-blur-md",
  props.variant === "highlight" &&
    "bg-[rgba(255,145,0,0.15)] border-accent-primary",
]);
</script>

<style >
@reference @/styles/base.css;
.panel-body {
  @apply text-secondary;
}
</style>
