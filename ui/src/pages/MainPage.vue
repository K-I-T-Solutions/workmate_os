<template>
  <div class="main-page flex h-screen w-full overflow-hidden">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content Area -->
    <div
      class="flex flex-col flex-1 h-full transition-all duration-300"
      :style="{
        marginLeft:
          (sidebarStore.isOpen || sidebarStore.isHovered) && isDesktop
            ? 'var(--os-sidebar-width)'
            : isDesktop
            ? '64px'
            : '0',
      }"
    >
      <!-- Topbar -->
      <Topbar :title="dashboardTitle" />

      <!-- Content -->
      <main
        class="flex-1 overflow-y-auto bg-bg-primary"
        style="
          padding: calc(var(--os-topbar-height) + 1.5rem) 1.5rem
            calc(var(--os-dock-height) + 1.5rem) 1.5rem;
        "
      >
        <div class="max-w-[1920px] mx-auto">
          <!-- Welcome Panel -->
          <kitPanel
            v-if="!loading && dashboard"
            title="Welcome to WorkmateOS ⚡"
            variant="glass"
            padding="lg"
            class="welcome-panel mb-8"
          >
            <div class="welcome-content space-y-5">
              <div class="flex items-start justify-between gap-6">
                <div class="flex-1">
                  <p class="text-text-secondary leading-relaxed text-base mb-4">
                    {{ welcomeMessage }}
                  </p>
                  <div class="flex flex-wrap gap-4 text-sm text-text-secondary">
                    <span class="inline-flex items-center gap-2">
                      <svg
                        class="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      {{ currentTime }}
                    </span>
                    <span class="text-text-secondary/50">•</span>
                    <span>{{ currentDate }}</span>
                    <span class="text-text-secondary/50">•</span>
                    <span>{{ activeWidgetCount }} Widgets aktiv</span>
                  </div>
                </div>

                <!-- Quick Stats -->
                <div v-if="stats" class="flex gap-6 flex-shrink-0">
                  <div class="stat-item">
                    <div class="stat-value">
                      {{ stats.employees_count || 0 }}
                    </div>
                    <div class="stat-label">Mitarbeiter</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">
                      {{ stats.projects_count || 0 }}
                    </div>
                    <div class="stat-label">Projekte</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">
                      {{ stats.reminders_count || 0 }}
                    </div>
                    <div class="stat-label">Erinnerungen</div>
                  </div>
                </div>
              </div>
            </div>
          </kitPanel>

          <!-- Loading State -->
          <div v-if="loading" class="space-y-6">
            <div v-for="i in 3" :key="`skeleton-${i}`" class="animate-pulse">
              <kitPanel variant="default">
                <div class="h-32 bg-bg-secondary/30 rounded"></div>
              </kitPanel>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="mb-6">
            <kitPanel title="Fehler beim Laden" variant="highlight">
              <div class="flex items-start gap-4">
                <svg
                  class="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5"
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
                <div class="flex-1">
                  <p class="text-text-secondary text-sm mb-3">{{ error }}</p>
                  <kitButtons
                    label="Erneut versuchen"
                    variant="primary"
                    size="sm"
                    @click="loadDashboardFull"
                  />
                </div>
              </div>
            </kitPanel>
          </div>

          <!-- Widget Grid -->
          <WidgetRenderer
            v-if="dashboard && !loading && widgets"
            :widgets="widgets || {}"
            :layout="layout || {}"
            :loading="loading"
          />

          <!-- Dashboard Settings -->
          <div v-if="!loading && dashboard" class="mt-8 text-center">
            <button
              class="dashboard-settings-btn"
              @click="openDashboardSettings"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span>Dashboard anpassen</span>
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- Dock -->
    <Dock />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import Sidebar from "@/components/layout/Sidebar.vue";
import Topbar from "@/components/os/Topbar.vue";
import Dock from "@/components/os/Dock.vue";
import WidgetRenderer from "@/components/core/dashboards/WidgetRenderer.vue";

import kitPanel from "@/components/system/kit-panel.vue";
import kitButtons from "@/components/system/kit-buttons.vue";

import { useSidebarStore } from "@/stores/sidebar";
import { useDashboardFull } from "@/composables/useDashboard";

// ==============================
// State Management
// ==============================

const sidebarStore = useSidebarStore();
const router = useRouter();
const isDesktop = ref(window.innerWidth >= 768);

const {
  dashboard,
  osPreferences,
  userSettings,
  stats,
  recentReminders,
  notifications,
  activityFeed,
  widgets,
  layout,
  loading,
  error,
  loadDashboardFull,
} = useDashboardFull();

// Time Display
const currentTime = ref("");
const currentDate = ref("");

// ==============================
// Computed Properties
// ==============================

/**
 * Dashboard-Titel
 */
const dashboardTitle = computed(() => {
  return dashboard.value?.name || "Dashboard";
});

/**
 * Welcome Message basierend auf Tageszeit
 */
const welcomeMessage = computed(() => {
  const hour = new Date().getHours();
  let greeting = "Guten Tag";

  if (hour < 12) greeting = "Guten Morgen";
  else if (hour < 18) greeting = "Guten Tag";
  else greeting = "Guten Abend";

  return `${greeting}! Dies ist dein zentraler Hub für WorkmateOS.`;
});

/**
 * Anzahl aktiver Widgets
 */
const activeWidgetCount = computed(() => {
  if (!widgets.value) return 0;
  return Object.values(widgets.value).filter((w: any) => w?.enabled !== false)
    .length;
});

// ==============================
// Methods
// ==============================

/**
 * Aktualisiert Zeit und Datum
 */
const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });
  currentDate.value = now.toLocaleDateString("de-DE", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
};

/**
 * Window Resize Handler
 */
const handleResize = () => {
  isDesktop.value = window.innerWidth >= 768;
};

/**
 * Dashboard-Einstellungen öffnen
 */
const openDashboardSettings = () => {
  console.log("Dashboard Settings öffnen");
  // router.push("/dashboard/settings");
};

// ==============================
// Lifecycle
// ==============================

onMounted(async () => {
  // Event Listeners
  window.addEventListener("resize", handleResize);

  // Zeit/Datum Updates
  updateTime();
  const timeInterval = setInterval(updateTime, 1000);

  // Dashboard laden
  console.log("🔍 Lade Dashboard...");
  await loadDashboardFull();
  console.log("✅ Dashboard geladen:", dashboard.value);
  console.log("📊 Widgets:", widgets.value);
  console.log("📐 Layout:", layout.value);

  // Cleanup
  onUnmounted(() => {
    window.removeEventListener("resize", handleResize);
    clearInterval(timeInterval);
  });
});
</script>

<style scoped>
.main-page {
  background: var(--color-bg-primary);
}

/* Welcome Panel - Extra Spacing */
.welcome-panel {
  padding: 2rem !important;
}

.welcome-panel :deep(h3) {
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.welcome-content {
  font-size: 0.95rem;
}

/* Quick Stats Styling */
.stat-item {
  text-align: center;
  min-width: 80px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-accent-primary);
  line-height: 1.2;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Dashboard Settings Button */
.dashboard-settings-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: 0.5rem;
  background: transparent;
  transition: all 200ms;
  cursor: pointer;
}

.dashboard-settings-btn:hover {
  color: var(--color-accent-primary);
  border-color: var(--color-accent-primary);
  background: rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.1);
  transform: translateY(-1px);
}

.dashboard-settings-btn svg {
  transition: transform 200ms;
}

.dashboard-settings-btn:hover svg {
  transform: rotate(90deg);
}

/* Smooth Transitions */
.main-page * {
  transition-property: color, background-color, border-color;
  transition-duration: 200ms;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Custom Scrollbar */
main::-webkit-scrollbar {
  width: 8px;
}

main::-webkit-scrollbar-track {
  background: transparent;
}

main::-webkit-scrollbar-thumb {
  background: var(--color-border-primary);
  border-radius: 4px;
}

main::-webkit-scrollbar-thumb:hover {
  background: var(--color-accent-primary);
}

/* Responsive */
@media (max-width: 768px) {
  .welcome-panel {
    padding: 1.5rem !important;
  }

  .stat-item {
    min-width: 60px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .stat-label {
    font-size: 0.65rem;
  }
}
</style>
