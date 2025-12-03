<template>
  <div class="widget-grid-container">
    <!-- Loading State -->
    <div v-if="isLoading" class="grid gap-6" :style="gridStyle">
      <div
        v-for="i in 3"
        :key="`skeleton-${i}`"
        class="widget-skeleton"
        :style="skeletonStyle"
      >
        <div class="skeleton-content">
          <div class="skeleton-spinner"></div>
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
              class="widget-content"
              @error="handleWidgetError(key, $event)"
            />
          </template>

          <!-- Loading Fallback -->
          <template #fallback>
            <div class="widget-loading">
              <div class="loading-spinner"></div>
            </div>
          </template>
        </Suspense>

        <!-- Widget Error State -->
        <div v-if="widgetErrors[key]" class="widget-error-overlay">
          <div class="error-content">
            <svg
              class="error-icon"
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
            <p class="error-text">Widget-Fehler</p>
            <button @click="retryWidget(key)" class="error-retry">
              Erneut versuchen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <svg
        class="empty-icon"
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
      <p class="empty-title">Keine Widgets aktiv</p>
      <p class="empty-description">
        Füge Widgets hinzu, um dein Dashboard zu personalisieren
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, defineAsyncComponent, onErrorCaptured } from "vue";
import { widgetRegistry } from "@/modules/dashboard/services/widgetRegistry";
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
  if (!props.widgets || typeof props.widgets !== "object") {
    return {};
  }

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
  if (!props.layout || typeof props.layout !== "object") {
    return {
      gridColumn: "span 3",
      gridRow: "span 2",
    };
  }

  const pos = props.layout[key];
  if (!pos) {
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
  if (widgetComponents.value[key]) {
    return widgetComponents.value[key];
  }

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
  delete widgetComponents.value[key];
};

/**
 * Global Error Capture
 */
onErrorCaptured((error, instance, info) => {
  console.error("Widget error captured:", error, info);
  return false;
});

/**
 * Helper: Error-Komponente erstellen
 */
function createErrorComponent(message: string): Component {
  return {
    template: `
      <div class="widget-error">
        <svg class="widget-error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="widget-error-message">${message}</p>
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
      <div class="widget-loading">
        <div class="loading-spinner"></div>
      </div>
    `,
  };
}
</script>

<style scoped>
/* Container */
.widget-grid-container {
  width: 100%;
}

/* Widget Container */
.widget-container {
  position: relative;
  min-height: 140px;
}

/* Widget Content */
.widget-content {
  height: 100%;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border-primary);
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  backdrop-filter: blur(8px);
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

.widget-content:hover {
  border-color: var(--color-accent-primary);
  opacity: 0.8;
}

/* Loading Skeleton */
.widget-skeleton {
  position: relative;
  overflow: hidden;
  border-radius: 0.5rem;
  background: rgba(var(--color-bg-secondary-rgb, 30, 30, 40), 0.5);
  backdrop-filter: blur(8px);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skeleton-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid transparent;
  border-top-color: var(--color-accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
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

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Widget Loading */
.widget-loading {
  border-radius: 0.5rem;
  border: 1px solid var(--color-border-primary);
  background: rgba(var(--color-bg-secondary-rgb, 30, 30, 40), 0.3);
  backdrop-filter: blur(8px);
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid transparent;
  border-top-color: var(--color-accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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

.error-content {
  text-align: center;
  padding: 1rem;
}

.error-icon {
  width: 2rem;
  height: 2rem;
  margin: 0 auto 0.5rem;
  color: rgb(239, 68, 68);
}

.error-text {
  font-size: 0.875rem;
  color: rgb(239, 68, 68);
  margin-bottom: 0.5rem;
}

.error-retry {
  font-size: 0.75rem;
  color: var(--color-accent-primary);
  cursor: pointer;
  transition: color 200ms;
}

.error-retry:hover {
  color: var(--color-accent-secondary);
}

/* Widget Error Component */
.widget-error {
  border-radius: 0.5rem;
  border: 1px solid rgba(239, 68, 68, 0.5);
  background: rgba(239, 68, 68, 0.1);
  backdrop-filter: blur(8px);
  padding: 1rem;
  text-align: center;
}

.widget-error-icon {
  width: 2rem;
  height: 2rem;
  margin: 0 auto 0.5rem;
  color: rgb(239, 68, 68);
}

.widget-error-message {
  font-size: 0.875rem;
  color: rgb(239, 68, 68);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 0;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  color: var(--color-text-secondary);
  opacity: 0.5;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.empty-description {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
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
