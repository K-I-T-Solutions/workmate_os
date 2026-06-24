<!-- src/layouts/sidebar/Sidebar.vue -->
<template>
  <!-- Mobile Overlay -->
  <div
    v-if="sidebarStore.isOpen"
    @click="sidebarStore.close"
    class="mobile-overlay"
  ></div>

  <aside
    class="os-sidebar"
    :class="[
      sidebarStore.isOpen || sidebarStore.isHovered
        ? 'sidebar-expanded'
        : 'sidebar-collapsed',
      sidebarStore.isOpen ? 'sidebar-mobile-open' : 'sidebar-mobile-closed',
    ]"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <!-- Header -->
    <div class="sidebar-header">
      <div class="brand-wrapper">
        <div class="logo-container">
          <img
            v-if="logo"
            :src="logo"
            class="logo-image"
            @error="handleLogoError"
          />
          <div v-else class="logo-fallback">W</div>
        </div>

        <span class="brand-text">WorkmateOS</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <button
        v-for="item in navItems"
        :key="item.id"
        @click="navigate(item.id)"
        class="nav-item"
        :class="{ 'nav-item-active': isActive(item.id) }"
        :title="!(sidebarStore.isOpen || sidebarStore.isHovered) ? item.label : ''"
      >
        <div v-if="isActive(item.id)" class="active-indicator"></div>
        <component :is="item.icon" class="nav-icon" />
        <span class="nav-label">
          {{ item.label }}
        </span>
      </button>
    </nav>

    <!-- Footer / Toggle -->
    <div class="sidebar-footer">
      <button
        @click="sidebarStore.toggle"
        class="toggle-btn"
        :title="sidebarStore.isOpen ? 'Sidebar einklappen' : 'Sidebar ausklappen'"
      >
        <ChevronLeft class="toggle-icon" />
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  Users,
  Briefcase,
  Timer,
  Receipt,
  Wallet,
  MessageSquare,
  ChevronLeft,
} from "lucide-vue-next";
import { WorkmateAssets } from "@/services/assets";
import { useSidebarStore } from "@/stores/sidebar";
import { useAppManager } from "@/layouts/app-manager/useAppManager";
import { apps } from "@/layouts/app-manager/appRegistry";

const sidebarStore = useSidebarStore();
const { openWindow, activeWindow } = useAppManager();

const logo = ref<string | null>(WorkmateAssets.workmateFavicon);

const handleLogoError = () => {
  logo.value = null;
};

function navigate(appId: string) {
  const app = apps.find((a) => a.id === appId);
  if (!app) return;

  openWindow(app.id, app.title, app.startRoute);

  if (window.innerWidth < 768) sidebarStore.close();
}

const isActive = (appId: string) => {
  const winId = activeWindow.value;
  if (!winId) return false;

  const app = apps.find((a) => a.id === appId);
  if (!app) return false;

  const win = useAppManager().windows.find((w) => w.id === winId);
  return win?.appId === app.id;
};

const onMouseEnter = () => {
  if (window.innerWidth >= 768) sidebarStore.setHovered(true);
};

const onMouseLeave = () => {
  if (window.innerWidth >= 768) sidebarStore.setHovered(false);
};

const navItems = [
  { id: "crm", label: "CRM", icon: Users },
  { id: "projects", label: "Projects", icon: Briefcase },
  { id: "time", label: "Time Tracking", icon: Timer },
  { id: "invoices", label: "Invoices", icon: Receipt },
  { id: "finance", label: "Finance", icon: Wallet },
  { id: "notes", label: "Notes", icon: MessageSquare },
];
</script>
