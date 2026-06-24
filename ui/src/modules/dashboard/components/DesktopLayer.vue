<template>
  <div class="desktop-layer absolute inset-0 overflow-auto z-0">
    <DashboardPage />
  </div>
</template>

<script setup>
import DashboardPage from '@/modules/dashboard/pages/DashboardPage.vue';
</script>

<style scoped>
.desktop-layer {
  pointer-events: auto; /* Dashboard Widgets brauchen Klicks */
}
</style>
