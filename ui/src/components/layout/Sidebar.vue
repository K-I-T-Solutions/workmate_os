<template>
  <!-- Mobile Overlay -->
  <div
    v-if="sidebarStore.isOpen"
    @click="sidebarStore.close"
    class="mobile-overlay"
  ></div>

  <!-- Sidebar -->
  <aside
    class="wm-sidebar"
    :class="[
      sidebarStore.isOpen || sidebarStore.isHovered
        ? 'sidebar-expanded'
        : 'sidebar-collapsed',
      sidebarStore.isOpen ? 'sidebar-mobile-open' : 'sidebar-mobile-closed'
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

    <!-- Navigation Items -->
    <nav class="sidebar-nav">
      <button
        v-for="item in navItems"
        :key="item.label"
        @click="navigate(item.to)"
        class="nav-item"
        :class="{ 'nav-item-active': isActive(item.to) }"
        :title="!(sidebarStore.isOpen || sidebarStore.isHovered) ? item.label : ''"
      >
        <!-- Active Indicator -->
        <div
          v-if="isActive(item.to)"
          class="active-indicator"
        ></div>

        <!-- Icon -->
        <component :is="item.icon" class="nav-icon" />

        <!-- Label -->
        <span class="nav-label">
          {{ item.label }}
        </span>

        <!-- Badge (optional - für später) -->
        <!-- <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span> -->
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
import { useRouter, useRoute } from "vue-router";
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

const router = useRouter();
const route = useRoute();
const sidebarStore = useSidebarStore();

const logo = ref<string | null>(WorkmateAssets.workmateFavicon);

const handleLogoError = () => {
  logo.value = null;
};

const navigate = (to: string) => {
  router.push(to);
  if (window.innerWidth < 768) sidebarStore.close();
};

const isActive = (path: string) => route.path.startsWith(path);

const onMouseEnter = () => {
  if (window.innerWidth >= 768) sidebarStore.setHovered(true);
};

const onMouseLeave = () => {
  if (window.innerWidth >= 768) sidebarStore.setHovered(false);
};

const navItems = [
  { label: "CRM", icon: Users, to: "/backoffice/crm" },
  { label: "Projects", icon: Briefcase, to: "/backoffice/projects" },
  { label: "Time Tracking", icon: Timer, to: "/backoffice/time-tracking" },
  { label: "Invoices", icon: Receipt, to: "/backoffice/invoices" },
  { label: "Finance", icon: Wallet, to: "/backoffice/finance" },
  { label: "Notes", icon: MessageSquare, to: "/backoffice/chat" },
];
</script>

<style scoped>
/* ============================================================
   MOBILE OVERLAY
   ============================================================ */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 30;
  transition: opacity 200ms;
}

@media (min-width: 768px) {
  .mobile-overlay {
    display: none;
  }
}

/* ============================================================
   SIDEBAR CONTAINER
   ============================================================ */
.wm-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  z-index: 40;
  background: rgba(255, 255, 255, 0.04);
  border-right: 1px solid var(--color-border-light);
  backdrop-filter: blur(12px);
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
  padding: 1.5rem 0;
}

/* Expanded State */
.sidebar-expanded {
  width: var(--os-sidebar-width);
  padding-left: 1rem;
  padding-right: 1rem;
}

/* Collapsed State */
.sidebar-collapsed {
  width: 64px;
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

/* Mobile States */
@media (max-width: 768px) {
  .sidebar-mobile-closed {
    transform: translateX(-100%);
  }

  .sidebar-mobile-open {
    transform: translateX(0);
  }
}

/* ============================================================
   HEADER / BRAND
   ============================================================ */
.sidebar-header {
  margin-bottom: 2rem;
  padding: 0 0.5rem;
  overflow: hidden;
}

.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 300ms;
}

.sidebar-collapsed .brand-wrapper {
  justify-content: center;
}

/* Logo Container */
.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 300ms;
}

.sidebar-expanded .logo-container {
  width: 2rem;
  height: 2rem;
}

.sidebar-collapsed .logo-container {
  width: 2.5rem;
  height: 2.5rem;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  opacity: 0.9;
  transition: opacity 200ms;
}

.logo-image:hover {
  opacity: 1;
}

.logo-fallback {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
  background: rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.15);
  color: var(--color-accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  transition: all 300ms;
}

.sidebar-expanded .logo-fallback {
  font-size: 0.875rem;
}

.sidebar-collapsed .logo-fallback {
  font-size: 1rem;
}

/* Brand Text */
.brand-text {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  white-space: nowrap;
  letter-spacing: -0.01em;
  transition: opacity 300ms;
}

.sidebar-collapsed .brand-text {
  opacity: 0;
  width: 0;
}

.sidebar-expanded .brand-text {
  opacity: 1;
  width: auto;
}

/* ============================================================
   NAVIGATION
   ============================================================ */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  flex: 1;
  overflow-y: auto;
  padding: 0 0.5rem;
}

/* Scrollbar */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: var(--color-border-primary);
  border-radius: 2px;
}

/* Nav Item */
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  border-radius: 0.625rem;
  cursor: pointer;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent;
  border: 1px solid transparent;
  color: var(--color-text-secondary);
}

.sidebar-expanded .nav-item {
  padding: 0.875rem 1rem;
  gap: 0.875rem;
  justify-content: flex-start;
}

.sidebar-collapsed .nav-item {
  padding: 0.875rem;
  justify-content: center;
}

/* Nav Item Hover */
.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary);
  border-color: var(--color-border-primary);
  transform: translateX(2px);
}

.sidebar-collapsed .nav-item:hover {
  transform: translateX(0) scale(1.05);
}

/* Active Nav Item */
.nav-item-active {
  background: rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.1) !important;
  border-color: var(--color-accent-primary) !important;
  color: var(--color-accent-primary) !important;
}

.nav-item-active .nav-icon {
  color: var(--color-accent-primary);
}

/* Active Indicator (Left Border) */
.active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--color-accent-primary);
  border-radius: 0 2px 2px 0;
  opacity: 1;
}

.sidebar-collapsed .active-indicator {
  height: 80%;
}

/* Nav Icon */
.nav-icon {
  flex-shrink: 0;
  transition: all 200ms;
  color: inherit;
}

.sidebar-expanded .nav-icon {
  width: 1.375rem;
  height: 1.375rem;
}

.sidebar-collapsed .nav-icon {
  width: 1.5rem;
  height: 1.5rem;
}

/* Nav Label */
.nav-label {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  transition: all 300ms;
  color: inherit;
}

.sidebar-collapsed .nav-label {
  opacity: 0;
  width: 0;
}

.sidebar-expanded .nav-label {
  opacity: 1;
  width: auto;
}

/* Nav Badge (Optional) */
.nav-badge {
  margin-left: auto;
  padding: 0.125rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-accent-primary);
  background: rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.15);
  border-radius: 0.375rem;
  transition: opacity 300ms;
}

.sidebar-collapsed .nav-badge {
  display: none;
}

/* ============================================================
   FOOTER / TOGGLE
   ============================================================ */
.sidebar-footer {
  margin-top: auto;
  padding: 1rem 0.5rem 0;
  border-top: 1px solid var(--color-border-light);
  display: none;
}

@media (min-width: 768px) {
  .sidebar-footer {
    display: block;
  }
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.625rem;
  border-radius: 0.5rem;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 200ms;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-accent-primary);
}

.toggle-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 300ms;
}

.sidebar-collapsed .toggle-icon {
  transform: rotate(180deg);
}

/* ============================================================
   DARK MODE
   ============================================================ */
@media (prefers-color-scheme: dark) {
  .wm-sidebar {
    background: rgba(0, 0, 0, 0.3);
  }

  .nav-item:hover {
    background: rgba(255, 255, 255, 0.03);
  }
}
</style>
