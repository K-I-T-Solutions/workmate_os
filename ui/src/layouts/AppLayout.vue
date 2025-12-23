<template>
  <div class="w-screen h-screen overflow-hidden flex flex-col bg-bg-primary">
    <!-- Topbar -->
    <KitTopbar />

    <!-- Main Area -->
    <div class="flex flex-1 overflow-hidden relative">

      <!-- Dashboard Background Layer -->
      <div class="dashboard-background">
        <DashboardPage />
      </div>

      <!-- Window System (floating above dashboard) -->
      <WindowHost class="flex-1 window-layer" />
    </div>

    <!-- Dock -->
    <KitDock />
  </div>
</template>

<script setup lang="ts">
import { KitTopbar, KitDock } from "./components";
import { WindowHost } from "./app-manager";
import DashboardPage from "@/modules/dashboard/pages/DashboardPage.vue";
</script>

<style scoped>
/* Dashboard Background Layer */
.dashboard-background {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: auto;
}

/* Windows float above dashboard */
.window-layer {
  position: relative;
  z-index: 10;
  pointer-events: none; /* Allow clicks to pass through to dashboard when no windows */
}

/* Re-enable pointer events for actual windows */
.window-layer :deep(.window-frame) {
  pointer-events: auto;
}
</style>
