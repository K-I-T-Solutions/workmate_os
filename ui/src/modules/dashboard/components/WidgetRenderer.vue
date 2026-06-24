<template>
  <div class="widget-grid-container">

    <!-- Loading -->
    <div v-if="loading" class="grid gap-6" :style="gridStyle">
      <div
        v-for="i in 3"
        :key="i"
        class="widget-skeleton"
        :style="skeletonStyle"
      >
        <div class="skeleton-center">
          <div class="spinner"></div>
        </div>
      </div>
    </div>

    <!-- Widget Grid -->
    <div v-else-if="hasActiveWidgets" class="grid gap-6" :style="gridStyle">
      <div
        v-for="(widget, key) in activeWidgets"
        :key="key"
        class="widget-container"
        :style="itemStyle(String(key))"
      >
        <Suspense>
          <template #default>
            <component
              :is="loadComponent(String(key))"
              :data="resolveWidgetData(String(key))"
              :settings="widget.settings ?? {}"
              class="widget-box"
              @error="captureError(String(key), $event)"
            />
          </template>

          <template #fallback>
            <div class="widget-loading">
              <div class="spinner sm"></div>
            </div>
          </template>
        </Suspense>

        <!-- Error Overlay -->
        <div
          v-if="errors[key]"
          class="widget-error-overlay"
        >
          <div class="widget-error-text">Widget Fehler</div>
          <button
            @click="retry(String(key))"
            class="widget-retry"
          >
            Erneut versuchen
          </button>
        </div>
      </div>
    </div>

    <!-- No Widgets Active -->
    <div v-else class="empty-state">
      <p class="empty-title">Keine Widgets aktiv</p>
      <p class="empty-desc">Füge Widgets in den Dashboard-Einstellungen hinzu.</p>
    </div>

  </div>
<DebugOverlay
  v-if="DEBUG"
  :widgets="props.widgets"
  :layout="props.layout"
  :activeWidgets="activeWidgets"
  :dataMap="props.dataMap"
  :loading="props.loading"
/>

</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, ref } from "vue";
import { widgetRegistry } from "@/modules/dashboard/services/widgetRegistry";
import type { Component } from "vue";
import DebugOverlay from "@/components/system/DebugOverlay.vue";

interface Props {
  widgets: Record<string, any>;
  layout: Record<string, any>;
  loading?: boolean;
  dataMap?: Record<string, any>;
}
const DEBUG = import.meta.env.VITE_DEBUG_MODE === "true";

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  dataMap: () => ({})
});

// Shorthands (damit wir im Template keine props.xyz tippen müssen)

const componentCache = ref<Record<string, Component>>({});
const errors = ref<Record<string, Error | null>>({});

/* -----------------------------
   ACTIVE WIDGETS
----------------------------- */
const activeWidgets = computed(() =>
  Object.fromEntries(
    Object.entries(props.widgets ?? {}).filter(([key, value]: any) => {
      if (!value) return false;

      // enabled not provided → treat as active
      if (value.enabled === undefined) return true;

      // Boolean
      if (value.enabled === true) return true;

      // Number (timestamp)
      if (typeof value.enabled === "number") return true;

      return false;
    })
  )
);

const hasActiveWidgets = computed(
  () => Object.keys(activeWidgets.value).length > 0
);

/* -----------------------------
   GRID LAYOUT
----------------------------- */
const gridStyle = computed(() => ({
  display: "grid",
  gridTemplateColumns: "repeat(6, 1fr)",
  gridAutoRows: "140px",
  gap: "1.5rem"
}));

const skeletonStyle = {
  gridColumn: "span 3",
  gridRow: "span 2"
};

/* -----------------------------
   POSITIONING
----------------------------- */
const itemStyle = (key: string) => {
  const pos = props.layout?.[key];

  if (!pos) {
    return { gridColumn: "span 3", gridRow: "span 2" };
  }

  return {
    gridColumn: `${pos.x + 1} / span ${pos.w}`,
    gridRow: `${pos.y + 1} / span ${pos.h}`
  };
};

/* -----------------------------
   DATA RESOLVER
----------------------------- */
const resolveWidgetData = (key: string) => {
  const widget = activeWidgets.value[key];

  if (widget?.data !== undefined && widget?.data !== null) {
    return widget.data;
  }

  if (props.dataMap && props.dataMap[key] !== undefined) {
    return props.dataMap[key];
  }

  switch (key) {
    case "stats":
      return props.dataMap.stats ?? {};
    case "recentReminders":
      return props.dataMap.recentReminders ?? [];
    case "notifications":
      return props.dataMap.notifications ?? [];
    case "activityFeed":
      return props.dataMap.activityFeed ?? [];
  }

  return {};
};

/* -----------------------------
   DYNAMIC COMPONENT LOADER
----------------------------- */
const loadComponent = (key: string): Component => {
  if (componentCache.value[key]) return componentCache.value[key];

  const widgetDef = widgetRegistry[key];
  if (!widgetDef) {
    return createErrorComponent(`Unbekanntes Widget "${key}"`);
  }

  const asyncComp = defineAsyncComponent({
    loader: widgetDef.component,
    delay: 100,
    timeout: 10000,
    onError(error) {
      errors.value[key] = error;
    }
  });

  componentCache.value[key] = asyncComp;
  return asyncComp;
};

/* -----------------------------
   ERROR HANDLING
----------------------------- */
const captureError = (key: string, err: Error) => {
  errors.value[key] = err;
};

const retry = (key: string) => {
  errors.value[key] = null;
  delete componentCache.value[key];
};

/* -----------------------------
   FALLBACK COMPONENT
----------------------------- */
function createErrorComponent(message: string): Component {
  return {
    template: `<div class="widget-box error">${message}</div>`
  };
}
</script>

<style scoped>
.widget-grid-container {
  width: 100%;
}

.widget-container {
  position: relative;
  min-height: 140px;
}

.widget-box {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border-primary);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(8px);
  padding: 1rem;
}

.widget-loading {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid transparent;
  border-bottom-color: var(--color-accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner.sm {
  width: 1.25rem;
  height: 1.25rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.widget-error-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 80, 80, 0.15);
  border-radius: 0.5rem;
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.widget-error-text {
  color: #ff5555;
  margin-bottom: 0.5rem;
}

.widget-retry {
  color: var(--color-accent-primary);
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 2rem 0;
}

.empty-title {
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
}
</style>
