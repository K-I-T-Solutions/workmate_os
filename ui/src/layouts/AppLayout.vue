<template>
  <div class="wm-app-root">
    <!-- Loading Skeleton -->
    <template v-if="isInitialLoading">
      <!-- Skeleton Topbar -->
      <div class="skeleton-topbar">
        <div class="skeleton-box skeleton-logo"></div>
        <div class="skeleton-spacer"></div>
        <div class="skeleton-box skeleton-user"></div>
      </div>

      <!-- Skeleton Dashboard -->
      <div class="wm-main-area">
        <div class="skeleton-dashboard">
          <div class="skeleton-grid">
            <div class="skeleton-card" v-for="i in 6" :key="i">
              <div class="skeleton-box skeleton-card-title"></div>
              <div class="skeleton-box skeleton-card-value"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Skeleton Dock -->
      <div class="skeleton-dock">
        <div class="skeleton-box skeleton-dock-item" v-for="i in 5" :key="i"></div>
      </div>
    </template>

    <!-- Actual App Content -->
    <template v-else>
      <!-- Topbar -->
      <KitTopbar
        @open-profile="openProfile"
        @open-settings="openSettings"
        @logout="handleLogout"
      />

      <!-- Main Area -->
      <div class="wm-main-area">

        <!-- Dashboard Background Layer -->
        <div class="dashboard-background">
          <DashboardPage />
        </div>

        <!-- Window System (floating above dashboard) -->
        <WindowHost class="flex-1 window-layer" />

        <!-- System Pages Overlay -->
        <Transition name="system-page">
          <div v-if="currentSystemPage" class="system-page-overlay">
            <div class="system-page-container">
              <UserProfilePage v-if="currentSystemPage === 'profile'" @back="closeSystemPage" />
              <SettingsPage v-if="currentSystemPage === 'settings'" @back="closeSystemPage" />
            </div>
          </div>
        </Transition>
      </div>

      <!-- Dock -->
      <KitDock />
    </template>

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { KitTopbar, KitDock } from "./components";
import { WindowHost } from "./app-manager";
import DashboardPage from "@/modules/dashboard/pages/DashboardPage.vue";
import UserProfilePage from "./pages/UserProfilePage.vue";
import SettingsPage from "./pages/SettingsPage.vue";
import { useAuth } from "@/composables/useAuth";
import { appManager } from "./app-manager/useAppManager";
import ToastContainer from "@/components/ToastContainer.vue";

// Router
const router = useRouter();
const route = useRoute();

// System page state
type SystemPage = 'profile' | 'settings' | null;
const currentSystemPage = ref<SystemPage>(null);

// Auth composable for logout
const { logout, user } = useAuth();

// Loading state
const isInitialLoading = ref(true);

// Hide skeleton after minimum time + user loaded
onMounted(() => {
  // Show skeleton for minimum 800ms for smooth UX
  const minLoadTime = 800;
  const startTime = Date.now();

  const checkReady = () => {
    const elapsed = Date.now() - startTime;
    const hasUser = !!user.value;

    if (hasUser && elapsed >= minLoadTime) {
      isInitialLoading.value = false;
    } else {
      setTimeout(checkReady, 100);
    }
  };

  checkReady();
});

// Auto-open app windows when deeplinks are detected
watch(
  () => route.path,
  (newPath) => {
    // Only handle specific deeplinks with IDs (not just /app/hr/)
    // This prevents opening windows on general navigation
    if (newPath.match(/^\/app\/hr\/.+/)) {
      appManager.openWindow('hr');
    }
    // Additional app deeplinks can be added here
    // if (newPath.startsWith('/app/crm/')) appManager.openWindow('crm');
  }
);

// Actions
function openProfile() {
  currentSystemPage.value = 'profile';
}

function openSettings() {
  currentSystemPage.value = 'settings';
}

function closeSystemPage() {
  currentSystemPage.value = null;
}

async function handleLogout() {
  if (confirm('Möchten Sie sich wirklich abmelden?')) {
    await logout();
    // Redirect to login page
    router.push('/login');
  }
}
</script>

<style scoped>
/* ============================================
   ROOT CONTAINER & MAIN AREA
   ============================================ */
.wm-app-root {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
}

@media (max-width: 1024px) {
  .wm-app-root {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior-y: contain;
  }
}

.wm-main-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}

@media (max-width: 1024px) {
  .wm-main-area {
    min-height: calc(100vh - var(--os-topbar-height) - var(--os-dock-height));
    overflow: visible;
  }
}

/* ============================================
   DASHBOARD BACKGROUND LAYER
   ============================================ */
.dashboard-background {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: auto;
}

@media (max-width: 1024px) {
  .dashboard-background {
    position: relative;
    inset: auto;
    overflow: visible;
    min-height: 100%;
  }
}

/* ============================================
   WINDOW LAYER
   ============================================ */
/* Windows float above dashboard */
.window-layer {
  position: absolute;
  inset: 0;
  z-index: 10;
  pointer-events: none; /* Allow clicks to pass through to dashboard when no windows */
}

/* Re-enable pointer events for actual windows */
.window-layer :deep(.window-frame) {
  pointer-events: auto;
}

/* ============================================
   SYSTEM PAGES OVERLAY
   ============================================ */
.system-page-overlay {
  position: absolute;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

@media (max-width: 1024px) {
  .system-page-overlay {
    position: fixed;
    padding: 0;
    background: var(--color-bg-primary);
    backdrop-filter: none;
  }
}

.system-page-container {
  width: 100%;
  max-width: 1200px;
  height: 100%;
  max-height: 90vh;
  background: var(--color-bg-primary);
  border-radius: 1rem;
  border: 1px solid var(--color-border-light);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

@media (max-width: 1024px) {
  .system-page-container {
    max-width: 100%;
    height: calc(100vh - var(--os-topbar-height) - var(--os-dock-height));
    border-radius: 0;
    border: none;
    box-shadow: none;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
}

/* Transition */
.system-page-enter-active,
.system-page-leave-active {
  transition: all 0.3s ease;
}

.system-page-enter-from,
.system-page-leave-to {
  opacity: 0;
}

.system-page-enter-from .system-page-container,
.system-page-leave-to .system-page-container {
  transform: scale(0.95) translateY(2rem);
}

/* ============================================
   SKELETON LOADING
   ============================================ */
.skeleton-box {
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 0%,
    var(--color-bg-tertiary) 50%,
    var(--color-bg-secondary) 100%
  );
  background-size: 200% 100%;
  border-radius: 8px;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Skeleton Topbar */
.skeleton-topbar {
  height: var(--os-topbar-height, 60px);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  gap: 1rem;
}

.skeleton-logo {
  width: 180px;
  height: 32px;
}

.skeleton-spacer {
  flex: 1;
}

.skeleton-user {
  width: 120px;
  height: 36px;
  border-radius: 18px;
}

/* Skeleton Dashboard */
.skeleton-dashboard {
  padding: 2rem;
  height: 100%;
  overflow: auto;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  max-width: 1400px;
}

.skeleton-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-card-title {
  width: 60%;
  height: 20px;
}

.skeleton-card-value {
  width: 40%;
  height: 32px;
}

/* Skeleton Dock */
.skeleton-dock {
  height: var(--os-dock-height, 70px);
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0 2rem;
}

.skeleton-dock-item {
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

@media (max-width: 768px) {
  .skeleton-dashboard {
    padding: 1rem;
  }

  .skeleton-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .skeleton-dock {
    gap: 0.5rem;
    padding: 0 1rem;
  }

  .skeleton-dock-item {
    width: 44px;
    height: 44px;
  }
}
</style>
