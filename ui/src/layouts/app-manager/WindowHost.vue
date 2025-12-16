<!-- src/layouts/app-manager/WindowHost.vue -->
<template>
  <div class="window-host">
    <WindowFrame
      v-for="w in windows"
      :key="w.id"
      :win="w"
    >
      <!-- 🔥 HIER wird die App gerendert -->
      <component
        :is="w.component"
        v-bind="w.props"
      />
    </WindowFrame>
  </div>
</template>

<script setup lang="ts">
import WindowFrame from "./WindowFrame.vue";
import { useAppManager } from "./useAppManager";

const { windows } = useAppManager();
</script>

<style scoped>
.window-host {
  position: fixed;
  inset: 0;
  overflow: hidden;
}

@media (min-width: 1025px) {
  .window-host {
    position: relative;
  }
}
</style>
