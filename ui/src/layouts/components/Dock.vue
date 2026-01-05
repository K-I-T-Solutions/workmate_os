<template>
  <div
    class="wm-dock"
  >
    <!-- Inner Container - Zentriert -->
    <div class="dock-inner">
      <div class="dock-items">
        <button
          v-for="item in dockItems"
          :key="item.id"
          @click="handleDockClick(item.id)"
          class="dock-item"
          :class="{ 'dock-item-active': isActive(item.id) }"
        >
          <!-- Icon Container -->
          <div class="dock-icon-wrapper">
            <component :is="item.icon" class="dock-icon" />
          </div>

          <!-- Active Indicator Dot (below icon, like macOS) -->
          <div v-if="isOpen(item.id)" class="active-dot"></div>

          <!-- Label -->
          <span class="dock-label">
            {{ item.label }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAppManager } from "../app-manager/useAppManager";
import { apps } from "../app-manager/appRegistry";
import { useAuth } from "@/composables/useAuth";
import { computed } from "vue";

const { openWindow, focusWindow, restoreWindow, activeWindow, windows } = useAppManager();
const { hasPermission } = useAuth();

// Generate dock items dynamically from app registry
const dockItems = computed(() => {
  return apps
    .filter(app => app.showInDock) // Only apps that should be in dock
    .filter(app => {
      // Filter by permissions
      if (!app.requiredPermission) return true;
      return hasPermission(app.requiredPermission);
    })
    .sort((a, b) => (a.dockOrder || 0) - (b.dockOrder || 0)) // Sort by dockOrder
    .map(app => ({
      id: app.id,
      label: app.title,
      icon: app.icon
    }));
});

// Check if any window of this app is open (even if minimized)
function isOpen(appId: string): boolean {
  return windows.some(w => w.appId === appId);
}

// Check if this app's window is currently active (focused)
function isActive(appId: string): boolean {
  const winId = activeWindow.value;
  if (!winId) return false;
  return windows.some(w => w.id === winId && w.appId === appId);
}

// Handle dock icon click
function handleDockClick(appId: string) {
  // Find any window of this app
  const existingWindow = windows.find(w => w.appId === appId);

  if (existingWindow) {
    // Window exists
    if (existingWindow.minimized) {
      // Restore from minimized
      restoreWindow(existingWindow.id);
    } else if (isActive(appId)) {
      // If already active, minimize it (toggle behavior like macOS)
      const appManager = useAppManager();
      appManager.minimizeWindow(existingWindow.id);
    } else {
      // Focus the existing window
      focusWindow(existingWindow.id);
    }
  } else {
    // No window exists, open new one
    openWindow(appId);
  }
}

</script>


<style scoped>
/* ============================================================
   DOCK CONTAINER
   ============================================================ */
.wm-dock {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: var(--os-dock-height);
  z-index: 50;
  background: var(--color-panel-glass);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--color-border-light);
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Inner Container - Zentriert mit Padding */
.dock-inner {
  max-width: 1920px;
  margin: 0 auto;
  height: 100%;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ============================================================
   DOCK ITEMS
   ============================================================ */
.dock-items {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Dock Item Button */
.dock-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent;
  border: none;
  padding: 0.5rem;
  border-radius: 0.75rem;
  min-width: 72px;
}

.dock-item:hover {
  transform: translateY(-2px);
}

.dock-item:active {
  transform: translateY(0);
}

/* ============================================================
   ICON WRAPPER
   ============================================================ */
.dock-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  background: var(--color-panel-glass);
  border: 1px solid var(--color-border-light);
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.dock-item:hover .dock-icon-wrapper {
  background: var(--color-panel-glass-hover);
  border-color: var(--color-border-medium);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Active State */
.dock-item-active .dock-icon-wrapper {
  background: rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.12) !important;
  border-color: var(--color-accent-primary) !important;
  box-shadow: 0 4px 16px rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.25) !important;
}

/* ============================================================
   ICON
   ============================================================ */
.dock-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--color-text-primary);
  transition: all 200ms;
}

.dock-item:hover .dock-icon {
  color: var(--color-text-primary);
  transform: scale(1.1);
}

.dock-item-active .dock-icon {
  color: var(--color-accent-primary);
}

/* ============================================================
   ACTIVE DOT INDICATOR (macOS style - below icon)
   ============================================================ */
.active-dot {
  width: 4px;
  height: 4px;
  background: var(--color-accent-primary);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.6);
  margin-top: -6px;
  transition: all 200ms;
}

.dock-item:hover .active-dot {
  transform: scale(1.2);
}

/* ============================================================
   LABEL
   ============================================================ */
.dock-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  transition: color 200ms;
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.dock-item:hover .dock-label {
  color: var(--color-text-primary);
}

.dock-item-active .dock-label {
  color: var(--color-accent-primary);
}

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 1200px) {
  .dock-inner {
    padding: 0 1.5rem;
  }

  .dock-items {
    gap: 0.75rem;
  }

  .dock-item {
    min-width: 64px;
  }

  .dock-icon-wrapper {
    width: 2.75rem;
    height: 2.75rem;
  }

  .dock-icon {
    width: 1.375rem;
    height: 1.375rem;
  }
}

@media (max-width: 768px) {
  .dock-inner {
    padding: 0 1rem;
  }

  .dock-items {
    gap: 0.5rem;
  }

  .dock-item {
    min-width: 56px;
    padding: 0.375rem;
  }

  .dock-icon-wrapper {
    width: 2.5rem;
    height: 2.5rem;
  }

  .dock-icon {
    width: 1.25rem;
    height: 1.25rem;
  }

  .dock-label {
    font-size: 0.6875rem;
  }
}

@media (max-width: 480px) {
  .dock-items {
    gap: 0.25rem;
  }

  .dock-label {
    display: none;
  }

  .dock-item {
    min-width: 48px;
  }
}

/* ============================================================
   DARK MODE
   ============================================================ */
@media (prefers-color-scheme: dark) {
  .wm-dock {
    background: rgba(0, 0, 0, 0.3);
  }

  .dock-icon-wrapper {
    background: rgba(255, 255, 255, 0.03);
  }

  .dock-item:hover .dock-icon-wrapper {
    background: rgba(255, 255, 255, 0.05);
  }
}
</style>
