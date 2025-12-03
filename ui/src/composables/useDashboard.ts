// src/composables/useDashboard.ts
import { ref, computed } from "vue";
import { apiClient } from "@/services/api/client";

// TODO: später durch Keycloak ersetzen
const TEST_EMPLOYEE_ID = "ef8192d3-9334-4256-ab01-a406307ede2a";

// ============================================================
// 🚀 FULL DASHBOARD COMPOSABLE
// ============================================================

export function useDashboardFull() {
  const dashboard = ref<any>(null);
  const osPreferences = ref<any>(null);
  const userSettings = ref<any>(null);

  const stats = ref<any>(null);
  const recentReminders = ref<any[]>([]);
  const notifications = ref<any[]>([]);
  const activityFeed = ref<any[]>([]);

  const loading = ref(false);
  const error = ref<string | null>(null);

  const loadDashboardFull = async () => {
    loading.value = true;
    error.value = null;

    try {
      const { data } = await apiClient.get("/api/dashboards/my-dashboard", {
        params: { owner_id: TEST_EMPLOYEE_ID },
      });

      // Core
      dashboard.value = data.dashboard;
      osPreferences.value = data.os_preferences;
      userSettings.value = data.user_settings;

      // Live data
      stats.value = data.stats ?? {};
      recentReminders.value = data.recent_reminders ?? [];
      notifications.value = data.notifications ?? [];
      activityFeed.value = data.activity_feed ?? [];
    } catch (err: any) {
      console.error("❌ Dashboard Load Error:", err);
      error.value = err?.message ?? "Fehler beim Laden des Dashboards";
    } finally {
      loading.value = false;
    }
  };

  // ==============================
  // Helpers / Computed Values
  // ==============================

  const isSidebarCollapsed = computed(
    () => osPreferences.value?.sidebar_collapsed ?? false
  );

  const themeMode = computed(() => osPreferences.value?.theme_mode ?? "system");

  const widgets = computed(() => {
    return dashboard.value?.widgets_json ?? {};
  });

  const layout = computed(() => {
    return dashboard.value?.layout_json ?? {};
  });

  return {
    // core dashboard data
    dashboard,
    osPreferences,
    userSettings,

    // live data
    stats,
    recentReminders,
    notifications,
    activityFeed,

    // computed
    widgets,
    layout,
    isSidebarCollapsed,
    themeMode,

    // status
    loading,
    error,

    // functions
    loadDashboardFull,
  };
}
