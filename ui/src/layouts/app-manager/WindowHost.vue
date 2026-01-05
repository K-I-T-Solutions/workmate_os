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
  position: absolute;
  inset: 0;
  z-index: 10;
  pointer-events: none;
  overflow: hidden;
}

@media (max-width: 1024px) {
  .window-host {
    position: fixed;
    top: var(--os-topbar-height);
    bottom: var(--os-dock-height);
    left: 0;
    right: 0;
    z-index: 100;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    pointer-events: auto;
  }
}
</style>
