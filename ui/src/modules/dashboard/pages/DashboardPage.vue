<template>
  <div class="w-full h-full p-6 space-y-8 text-white">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">Dashboard</h1>
    </div>

    <!-- Widgets Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">

      <!-- Stat Widget Placeholder -->
      <div class="p-5 rounded-xl bg-bg-secondary border border-white/10 shadow-soft">
        <h2 class="text-xl font-semibold mb-3">Statistik</h2>
        <p class="text-white/60">Widget Placeholder</p>
      </div>

      <!-- Reminder Widget Placeholder -->
      <div class="p-5 rounded-xl bg-bg-secondary border border-white/10 shadow-soft">
        <h2 class="text-xl font-semibold mb-3">Erinnerungen</h2>
        <p class="text-white/60">Widget Placeholder</p>
      </div>

      <!-- Module Shortcuts -->
      <div class="p-5 rounded-xl bg-bg-secondary border border-white/10 shadow-soft">
        <h2 class="text-xl font-semibold mb-3">Schnellzugriffe</h2>
        <ul class="space-y-2 text-white/70">
          <li>→ CRM</li>
          <li>→ Projekte</li>
          <li>→ Rechnungen</li>
          <li>→ Finance</li>
        </ul>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
// Dashboard 0.1 – UI only.
// Widgets, Renderer & Registry kommen in 0.2.
</script>
