<!-- src/layouts/app-manager/WindowHost.vue -->
<template>
  <div class="window-host">

    <!-- BLUR / DIM LAYER – aktiv sobald ein Fenster existiert -->
    <div
      v-if="windows.length > 0"
      class="workspace-blur"
    ></div>

    <!-- WINDOW INSTANCES -->
    <WindowFrame
      v-for="w in windows"
      :key="w.id"
      :win="w"
      class="wm-frame-instance"
    />
  </div>
</template>

<script setup lang="ts">
import { useAppManager } from "./useAppManager";
import WindowFrame from "./WindowFrame.vue";

const { windows } = useAppManager();
</script>

<style scoped>
.window-host {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--color-bg-primary);
}

/* ============================================
   BLUR-LAYER (liegt unter allen Fenstern)
============================================ */
.workspace-blur {
  position: absolute;
  inset: 0;

  /* Frosted Glass Effekt */
  backdrop-filter: blur(22px) brightness(1.03);

  /* leichtes Dimmen, wirkt sehr clean */
  background: rgba(0, 0, 0, 0.18);

  /* Blur darf nie anklickbar sein */
  pointer-events: none;

  z-index: 1;
}

/* Fenster dürfen über dem Blur liegen */
.wm-frame-instance {
  position: absolute;
  z-index: 2;
}
</style>
