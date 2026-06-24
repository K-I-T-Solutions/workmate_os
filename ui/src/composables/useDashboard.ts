import { ref, computed, watch } from "vue";
import { apiClient } from "@/services/api/client";

const TEST_EMPLOYEE_ID = "ef8192d3-9334-4256-ab01-a406307ede2a";

export function useDashboardFull() {
  const dashboard = ref<any>(null);
  const osPreferences = ref<any>(null);
  const userSettings = ref<any>(null);

  const stats = ref({
    activeProjects: 0,
    pendingInvoices: 0,
    registeredCustomers: 0,
    openReminders: 0,
  });

  const recentReminders = ref<any[]>([]);
  const notifications = ref<any[]>([]);
  const activityFeed = ref<any[]>([]);

  const loading = ref(false);
  const error = ref<string | null>(null);

  const loadDashboardFull = async () => {
    loading.value = true;

    try {
      const { data } = await apiClient.get("/api/dashboards/my-dashboard", {
        params: { owner_id: TEST_EMPLOYEE_ID },
      });

      console.log("🛰 API RESPONSE:", JSON.parse(JSON.stringify(data)));

      dashboard.value = data.dashboard ?? {};
      osPreferences.value = data.os_preferences ?? {};
      userSettings.value = data.user_settings ?? {};

      stats.value = data.stats ?? stats.value;
      recentReminders.value = data.recent_reminders ?? [];
      notifications.value = data.notifications ?? [];
      activityFeed.value = data.activity_feed ?? [];

      console.log("📦 WidgetsJSON:", dashboard.value.widgets_json);
      console.log("📐 LayoutJSON:", dashboard.value.layout_json);

    } catch (err: any) {
      console.error("❌ Dashboard Load Error:", err);
      error.value = err?.message ?? "Fehler beim Laden des Dashboards";
    } finally {
      loading.value = false;
      console.log("✅ Dashboard Load Complete");
    }
  };

  // FIX: Computeds dürfen NICHT leer starten
  const widgets = computed(() => {
    const w = dashboard.value?.widgets_json;
    return w && Object.keys(w).length > 0 ? w : {};
  });

  const layout = computed(() => {
    const l = dashboard.value?.layout_json;
    return l && Object.keys(l).length > 0 ? l : {};
  });

  return {
    dashboard,
    widgets,
    layout,

    stats,
    recentReminders,
    notifications,
    activityFeed,

    loading,
    error,
    loadDashboardFull,
  };
}
