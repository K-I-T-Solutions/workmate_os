<!-- src/layouts/app-manager/WindowHost.vue -->
<template>
  <div class="window-host">
    <WindowFrame
      v-for="w in visibleWindows"
      :key="w.id"
      :win="w"
    >
      <!-- 🔥 HIER wird die App gerendert -->
      <component
        :is="resolveComponent(w.appId)"
        v-bind="w.props"
      />
    </WindowFrame>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import WindowFrame from "./WindowFrame.vue";
import { useAppManager } from "./useAppManager";
import { apps } from "./appRegistry";

const { windows } = useAppManager();

// Only show non-minimized windows
const visibleWindows = computed(() => windows.filter(w => !w.minimized));

function resolveComponent(appID: string){
  return apps.find(a=> a.id ===appID)?.component;
}

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
