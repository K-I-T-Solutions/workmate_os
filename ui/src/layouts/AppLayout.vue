<template>
  <div class="w-screen h-screen overflow-hidden flex flex-col bg-bg-primary">
    <!-- Topbar -->
    <KitTopbar
      @open-profile="openProfile"
      @open-settings="openSettings"
      @logout="handleLogout"
    />

    <!-- Main Area -->
    <div class="flex flex-1 overflow-hidden relative">

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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { KitTopbar, KitDock } from "./components";
import { WindowHost } from "./app-manager";
import DashboardPage from "@/modules/dashboard/pages/DashboardPage.vue";
import UserProfilePage from "./pages/UserProfilePage.vue";
import SettingsPage from "./pages/SettingsPage.vue";
import { useAuth } from "@/composables/useAuth";

// Router
const router = useRouter();

// System page state
type SystemPage = 'profile' | 'settings' | null;
const currentSystemPage = ref<SystemPage>(null);

// Auth composable for logout
const { logout } = useAuth();

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
/* Dashboard Background Layer */
.dashboard-background {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: auto;
}

/* Windows float above dashboard */
.window-layer {
  position: relative;
  z-index: 10;
  pointer-events: none; /* Allow clicks to pass through to dashboard when no windows */
}

/* Re-enable pointer events for actual windows */
.window-layer :deep(.window-frame) {
  pointer-events: auto;
}

/* System Pages Overlay */
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
</style>
