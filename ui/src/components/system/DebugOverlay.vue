<template>
  <div
    v-if="DEBUG"
    class="debug-overlay"
    :class="{ collapsed }"
  >
    <!-- Header -->
    <div class="debug-header" @click="toggle">
      🛠 Debug
      <span class="chevron">{{ collapsed ? "▲" : "▼" }}</span>
    </div>

    <!-- Content -->
    <div v-if="!collapsed" class="debug-content">

      <div class="debug-section">
        <h4>Dashboard Widgets</h4>
        <p>Widgets Keys: {{ Object.keys(widgets || {}) }}</p>
        <p>Active: {{ Object.keys(activeWidgets || {}) }}</p>
        <p>Layout Keys: {{ Object.keys(layout || {}) }}</p>
      </div>

      <div class="debug-section">
        <h4>Loading</h4>
        <p>{{ loading }}</p>
      </div>

      <div class="debug-section">
        <h4>DataMap</h4>
        <pre>{{ dataMap }}</pre>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  widgets: any;
  layout: any;
  activeWidgets: any;
  dataMap: any;
  loading: boolean;
}>();

const DEBUG = import.meta.env.VITE_DEBUG_MODE === "true";

const collapsed = ref(false);
const toggle = () => (collapsed.value = !collapsed.value);
</script>

<style scoped>
.debug-overlay {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  width: 260px;
  background: rgba(0, 0, 0, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 0.5rem;
  border-radius: 0.5rem;
  backdrop-filter: blur(8px);
  color: #d0d0d0;
  font-size: 0.8rem;
  z-index: 9999;
}

.debug-overlay.collapsed {
  width: 120px;
  height: auto;
  padding: 0.5rem;
}

.debug-header {
  cursor: pointer;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chevron {
  opacity: 0.7;
}

.debug-content {
  margin-top: 0.5rem;
}

.debug-section {
  margin-bottom: 0.6rem;
}

pre {
  max-height: 100px;
  overflow: auto;
  font-size: 0.7rem;
}
</style>
