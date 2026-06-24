<template>
  <div class="w-screen h-screen overflow-hidden flex flex-col bg-bg-primary">

    <!-- Topbar (ganz oben) -->
    <Topbar class="relative z-40" />

    <!-- Main Screen -->
    <div class="relative flex-1 overflow-hidden">

      <!-- Dashboard / Desktop -->
      <DesktopLayer class="absolute inset-0 z-10" />

      <!-- Fenster liegen über dem Dashboard -->
      <WindowHost class="absolute inset-0 z-20" />

    </div>

    <!-- Dock (ganz oben) -->
    <Dock class="relative z-40" />
  </div>
</template>

<script setup lang="ts">
import Topbar from "@/layouts/components/Topbar.vue";
import Dock from "@/layouts/components/Dock.vue";
import WindowHost from "@/layouts/app-manager/WindowHost.vue";
import DesktopLayer from "@/modules/dashboard/components/DesktopLayer.vue";
</script>
