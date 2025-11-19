//pages/UnderConstruction.vue

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-[#232223] text-white text-center px-6">
    <div class="w-14 h-14 border-4 border-white/20 border-t-[#ff9100] rounded-full animate-spin mb-6"></div>
    <h1 class="text-3xl font-semibold mb-2">🚧 Wir bemühen uns gerade</h1>
    <p class="max-w-md text-white/80">
      Diese Seite befindet sich noch im Aufbau.<br />
      Unser Team von <span class="text-[#ff9100] font-medium">K.I.T. Solutions</span> arbeitet mit Hochdruck daran,
      sie bald für dich bereitzustellen.
    </p>
    <footer class="absolute bottom-6 flex flex-col items-center text-xs text-white/40">
  <router-link
    to="/linktree"
    class="text-[#ff9100] text-sm font-medium hover:underline mb-2"
  >
    👉 Zu unseren Links
  </router-link>
  <span>© {{ new Date().getFullYear() }} K.I.T. Solutions · All Rights Reserved</span>
</footer>
  </div>
</template>

<script setup lang="ts">
// Optional: du kannst hier noch MetaTitle, Logging etc. setzen
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
