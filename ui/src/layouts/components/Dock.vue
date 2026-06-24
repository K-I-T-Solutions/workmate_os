<!-- src/layouts/components/Dock.vue -->
<template>
  <nav class="os-dock dock-root">
    <div class="dock-inner">
      <button
        v-for="item in dockItems"
        :key="item.id"
        @click="openApp(item.id)"
        class="dock-item"
        :class="{ 'dock-item-active': isActive(item.id) }"
      >
        <div class="dock-icon-wrapper">
          <!-- Active indicator -->
          <div v-if="isActive(item.id)" class="dock-active-dot" />

          <!-- Icon -->
          <component :is="item.icon" class="dock-icon" />
        </div>

        <span class="dock-label">{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import {
  Users,
  Briefcase,
  Timer,
  Receipt,
  Wallet,
  MessageSquare,
} from "lucide-vue-next";

import { useAppManager } from "@/layouts/app-manager/useAppManager";
import { apps } from "@/layouts/app-manager/appRegistry";

const { openWindow, activeWindow, windows } = useAppManager();

function openApp(appId: string) {
  const app = apps.find((a) => a.id === appId);
  if (!app) return;

  openWindow(app.id, app.title, app.startRoute);
}

const dockItems = [
  { id: "crm", label: "CRM", icon: Users },
  { id: "projects", label: "Projects", icon: Briefcase },
  { id: "time", label: "Time", icon: Timer },
  { id: "invoices", label: "Invoices", icon: Receipt },
  { id: "finance", label: "Finance", icon: Wallet },
  { id: "notes", label: "Notes", icon: MessageSquare },
];

const isActive = (appId: string) => {
  const winId = activeWindow.value;
  const app = apps.find((a) => a.id === appId);
  if (!winId || !app) return false;

  return windows.some((w) => w.id === winId && w.appId === app.id);
};
</script>

<style scoped>
/* ==============================================
   🔥 WorkmateOS Dock (Token-powered)
   ============================================== */

/* Dock-Container (os-dock kommt aus base.css) */
.dock-root {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  /* Damit Dock über Fenstern bleibt */
  position: fixed;
  bottom: 0;
  left: 0;
  z-index: 200;
}

/* Innerer Bereich für die Icons */
.dock-inner {
  display: flex;
  gap: var(--space-lg);
  padding: var(--space-sm) var(--space-lg);
  align-items: flex-end;
}

/* Dock-Item */
.dock-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  color: var(--color-text-secondary);
  transition: transform 120ms ease, color 120ms ease;
}

.dock-item:hover {
  transform: translateY(-6px) scale(1.08);
  color: var(--color-text-primary);
}

/* Aktive App */
.dock-item-active .dock-icon {
  stroke: var(--color-accent-primary);
}

/* Icon-Wrapper */
.dock-icon-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
}

/* Icon selbst */
.dock-icon {
  width: 28px;
  height: 28px;
  stroke-width: 1.5;
  transition: stroke 150ms ease;
}

/* Active Dot (unter Icon) */
.dock-active-dot {
  position: absolute;
  bottom: -6px;
  width: 6px;
  height: 6px;
  background: var(--color-accent-primary);
  border-radius: 50%;
}

/* Label unter Icon */
.dock-label {
  font-size: var(--font-caption);
  opacity: 0.7;
  transition: opacity 150ms ease;
}

.dock-item:hover .dock-label {
  opacity: 1;
}

/* Mobile — kleinere Icons */
@media (max-width: 768px) {
  .dock-icon {
    width: 22px;
    height: 22px;
  }

  .dock-inner {
    gap: var(--space-md);
  }
}
</style>
