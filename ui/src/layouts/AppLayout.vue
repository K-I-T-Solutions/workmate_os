<template>
  <div class="w-screen h-screen overflow-hidden flex flex-col bg-bg-primary">
    <!-- Topbar -->
    <Topbar />

    <!-- Main Area -->
    <div class="flex flex-1 overflow-hidden">
      <Sidebar />

      <!-- Fenstersystem -->
      <WindowHost class="flex-1" />
    </div>

    <!-- Dock -->
    <Dock />
  </div>
</template>

<script setup lang="ts">
import Topbar from "@/layouts/components/Topbar.vue";
import Sidebar from "@/layouts/components/Sidebar.vue";
import Dock from "@/layouts/components/Dock.vue";
import WindowHost from "@/layouts/app-manager/WindowHost.vue";
</script>
