<template>
  <div class="w-screen h-screen overflow-hidden flex flex-col bg-bg-primary">
    <!-- Topbar -->
    <KitTopbar />

    <!-- Main Area -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Fenstersystem -->
      <WindowHost class="flex-1" />
    </div>

    <!-- Dock -->
    <KitDock />
  </div>
</template>

<script setup lang="ts">
import { KitTopbar,KitDock } from "./components";
import { WindowHost } from "./app-manager";
</script>
