<script setup lang="ts">
import { onMounted, watch, computed } from "vue";
import { useDashboardFull } from "@/composables/useDashboard";
import WidgetRenderer from "../components/WidgetRenderer.vue";

const DEBUG = import.meta.env.VITE_DEBUG_MODE === "true";

const {
  widgets,
  layout,
  stats,
  recentReminders,
  notifications,
  activityFeed,
  loading,
  loadDashboardFull
} = useDashboardFull();

// Datenmap für Widgets
const dataMap = computed(() => ({
  stats: stats.value,
  recentReminders: recentReminders.value,
  notifications: notifications.value,
  activityFeed: activityFeed.value,
}));

// Dashboard laden
onMounted(() => {
  console.log("🔄 DashboardPage mounted — lade Dashboard…");
  loadDashboardFull();
});

// Debug Logs
if (DEBUG) {
  watch(widgets, (v) => console.log("📦 widgets:", JSON.stringify(v)));
  watch(layout, (v) => console.log("📐 layout:", JSON.stringify(v)));
  watch(dataMap, (v) => console.log("🗺 dataMap:", JSON.stringify(v)));
  watch(loading, (v) => console.log("⏳ loading:", v));
}
</script>

<template>
  <!-- FIX: Dashboard braucht volle Höhe -->
  <div class="dashboard-page w-full h-full min-h-full text-white">

    <!-- Debug -->
    <pre
      v-if="DEBUG"
      class="p-4 bg-black/40 rounded mb-4 text-xs"
    >
widgets: {{ widgets }}
layout: {{ layout }}
dataMap: {{ dataMap }}
loading: {{ loading }}
    </pre>

    <!-- Widgets -->
    <WidgetRenderer
      :widgets="widgets"
      :layout="layout"
      :dataMap="dataMap"
      :loading="loading"
    />

  </div>
</template>

<style scoped>
/* FIX: DashboardPage sichtbar machen */
.dashboard-page {
  display: block;
}
</style>
