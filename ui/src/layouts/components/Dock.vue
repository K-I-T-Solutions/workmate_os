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
          @click="openApp(item.id)"
          class="dock-item"
          :class="{ 'dock-item-active': isActive(item.id) }"
        >
          <!-- Icon Container -->
          <div class="dock-icon-wrapper">
            <!-- Active Indicator Dot -->
            <div v-if="isActive(item.id)" class="active-dot"></div>
            <component :is="item.icon" class="dock-icon" />
          </div>

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
import {
  Briefcase,
  Users,
  Timer,
  Receipt,
  Wallet,
  MessageSquare,
} from "lucide-vue-next";

import { useAppManager } from "../app-manager/useAppManager";
import { apps } from "../app-manager/appRegistry";
import { markRaw } from "vue";

const { openWindow,activeWindow, windows } = useAppManager();


// Öffnet eine App als Fenster
function openApp(appId: string) {
  const app = apps.find(a => a.id === appId);
  if (!app) return;
  openWindow(app.id);
}


// Dock items (App-Zuweisungen)
const dockItems = [
  { id: "crm", label: "Kunden", icon: markRaw(Users) },
  { id: "projects", label: "Projekte", icon: markRaw(Briefcase) },
  { id: "time", label: "Zeiterfassung", icon: markRaw(Timer) },
  { id: "invoices", label: "Rechnungen", icon: markRaw(Receipt) },
  { id: "finance", label: "Finanzen", icon: markRaw(Wallet) },
  { id: "notes", label: "Chat", icon: markRaw(MessageSquare) },
];

// Active State
const isActive = (appId: string) => {
  const winId = activeWindow.value;
  if (!winId) return false;
  return windows.some(
    (w) => w.id === winId && w.appId === appId
  );
};

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
  background: rgba(255, 255, 255, 0.04);
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
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.dock-item:hover .dock-icon-wrapper {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--color-border-primary);
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
   ACTIVE DOT INDICATOR
   ============================================================ */
.active-dot {
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: var(--color-accent-primary);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.6);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
  50% {
    opacity: 0.7;
    transform: translateX(-50%) scale(1.2);
  }
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
