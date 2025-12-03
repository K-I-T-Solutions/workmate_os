<template>
  <div class="widget-grid-container">
    <!-- Loading State -->
    <div v-if="isLoading" class="grid gap-6" :style="gridStyle">
      <div
        v-for="i in 3"
        :key="`skeleton-${i}`"
        class="widget-skeleton animate-pulse rounded-lg bg-bg-secondary/50 backdrop-blur"
        :style="skeletonStyle"
      >
        <div class="h-full flex items-center justify-center">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"
          ></div>
        </div>
      </div>
    </div>

    <!-- Widget Grid -->
    <div v-else-if="hasActiveWidgets" class="grid gap-6" :style="gridStyle">
      <div
        v-for="(widget, key) in activeWidgets"
        :key="key"
        class="widget-container"
        :style="itemStyle(key)"
      >
        <!-- Widget Error Boundary -->
        <Suspense>
          <template #default>
            <component
              :is="getWidgetComponent(key)"
              :data="widget.data"
              :settings="widget.settings"
              class="widget-content rounded-lg border border-border-primary bg-[rgba(255,255,255,0.05)] p-4 backdrop-blur transition-all hover:border-accent-primary/50"
              @error="handleWidgetError(key, $event)"
            />
          </template>

          <!-- Loading Fallback -->
          <template #fallback>
            <div
              class="widget-loading rounded-lg border border-border-primary bg-bg-secondary/30 backdrop-blur p-4 flex items-center justify-center"
            >
              <div
                class="animate-spin rounded-full h-6 w-6 border-b-2 border-accent-primary"
              ></div>
            </div>
          </template>
        </Suspense>

        <!-- Widget Error State -->
        <div
          v-if="widgetErrors[key]"
          class="widget-error rounded-lg border border-red-500/50 bg-red-500/10 backdrop-blur p-4 absolute inset-0 flex items-center justify-center"
        >
          <div class="text-center p-4">
            <svg
              class="w-8 h-8 mx-auto mb-2 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p class="text-sm text-red-500 mb-2">Widget-Fehler</p>
            <button
              @click="retryWidget(key)"
              class="text-xs text-accent-primary hover:text-accent-secondary"
            >
              Erneut versuchen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state text-center py-12">
      <svg
        class="w-16 h-16 mx-auto mb-4 text-text-secondary opacity-50"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z"
        />
      </svg>
      <p class="text-lg font-medium text-text-primary mb-2">
        Keine Widgets aktiv
      </p>
      <p class="text-sm text-text-secondary">
        Füge Widgets hinzu, um dein Dashboard zu personalisieren
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, defineAsyncComponent, onErrorCaptured } from "vue";
import { widgetRegistry } from "@/widgets/widgetRegistry";
import type { Component } from "vue";

interface Props {
  widgets: Record<string, any>;
  layout: Record<string, any>;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const widgetErrors = ref<Record<string, Error | null>>({});
const widgetComponents = ref<Record<string, Component>>({});

/**
 * Filter: nur Widgets die existieren UND nicht disabled sind
 */
const activeWidgets = computed(() => {
  return Object.fromEntries(
    Object.entries(props.widgets).filter(([key, value]: any) => {
      const exists = widgetRegistry[key];
      const enabled = value?.enabled !== false;
      return exists && enabled;
    })
  );
});

/**
 * Prüft ob aktive Widgets vorhanden sind
 */
const hasActiveWidgets = computed(() => {
  return Object.keys(activeWidgets.value).length > 0;
});

/**
 * Loading State
 */
const isLoading = computed(() => props.loading);

/**
 * Grid-Styling (6-Spalten System)
 */
const gridStyle = computed(() => ({
  display: "grid",
  gridTemplateColumns: "repeat(6, 1fr)",
  gridAutoRows: "140px",
  gap: "1.5rem",
}));

/**
 * Skeleton-Styling für Loading State
 */
const skeletonStyle = {
  gridColumn: "span 2",
  gridRow: "span 2",
  minHeight: "280px",
};

/**
 * Item-Styling basierend auf Layout
 */
const itemStyle = (key: string) => {
  const pos = props.layout[key];
  if (!pos) {
    // Fallback: Standard-Position
    return {
      gridColumn: "span 3",
      gridRow: "span 2",
    };
  }

  return {
    gridColumn: `${pos.x + 1} / span ${pos.w}`,
    gridRow: `${pos.y + 1} / span ${pos.h}`,
  };
};

/**
 * Widget-Komponente abrufen (mit Caching)
 */
const getWidgetComponent = (key: string): Component => {
  // Prüfe Cache
  if (widgetComponents.value[key]) {
    return widgetComponents.value[key];
  }

  // Lade Widget async
  const widgetDef = widgetRegistry[key];
  if (!widgetDef) {
    console.error(`Widget "${key}" not found in registry`);
    return createErrorComponent(`Widget "${key}" nicht gefunden`);
  }

  try {
    const asyncComponent = defineAsyncComponent({
      loader: widgetDef.component,
      delay: 200,
      timeout: 10000,
      errorComponent: createErrorComponent(
        `Fehler beim Laden von Widget "${widgetDef.name}"`
      ),
      loadingComponent: createLoadingComponent(),
    });

    // Cache Komponente
    widgetComponents.value[key] = asyncComponent;
    return asyncComponent;
  } catch (error) {
    console.error(`Error loading widget ${key}:`, error);
    return createErrorComponent(`Fehler beim Laden von Widget "${key}"`);
  }
};

/**
 * Error Handler für Widgets
 */
const handleWidgetError = (key: string, error: Error) => {
  console.error(`Widget ${key} error:`, error);
  widgetErrors.value[key] = error;
};

/**
 * Widget erneut laden
 */
const retryWidget = (key: string) => {
  widgetErrors.value[key] = null;
  // Entferne aus Cache um Neuladung zu erzwingen
  delete widgetComponents.value[key];
};

/**
 * Global Error Capture
 */
onErrorCaptured((error, instance, info) => {
  console.error("Widget error captured:", error, info);
  return false; // Propagiere Error nicht weiter
});

/**
 * Helper: Error-Komponente erstellen
 */
function createErrorComponent(message: string): Component {
  return {
    template: `
      <div class="widget-error rounded-lg border border-red-500/50 bg-red-500/10 backdrop-blur p-4 text-center">
        <svg class="w-8 h-8 mx-auto mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-sm text-red-500">${message}</p>
      </div>
    `,
  };
}

/**
 * Helper: Loading-Komponente erstellen
 */
function createLoadingComponent(): Component {
  return {
    template: `
      <div class="widget-loading rounded-lg border border-border-primary bg-bg-secondary/30 backdrop-blur p-4 flex items-center justify-center">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-accent-primary"></div>
      </div>
    `,
  };
}
</script>

<style scoped>
.widget-grid-container {
  @apply w-full;
}

.widget-container {
  @apply relative;
  min-height: 140px;
}

.widget-content {
  @apply h-full w-full;
}

.widget-skeleton {
  @apply relative overflow-hidden;
}

.widget-skeleton::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: linear-gradient(
    to right,
    transparent,
    rgba(255, 255, 255, 0.05),
    transparent
  );
  animation: shimmer 2s infinite;
}

/* Widget Error Overlay */
.widget-error-overlay {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  border-radius: 0.5rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
}
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Responsive Adjustments */
@media (max-width: 1024px) {
  .widget-grid-container :deep(.grid) {
    grid-template-columns: repeat(4, 1fr) !important;
  }
}

@media (max-width: 768px) {
  .widget-grid-container :deep(.grid) {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 640px) {
  .widget-grid-container :deep(.grid) {
    grid-template-columns: 1fr !important;
  }
}
</style>
