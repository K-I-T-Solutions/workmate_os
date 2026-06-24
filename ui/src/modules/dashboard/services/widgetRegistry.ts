/**
 * WorkmateOS - Widget Registry
 * -----------------------------------------
 * Zentraler Ort zum Registrieren aller Desktop-Widgets.
 * Widgets werden dynamisch per Lazy-Loading geladen.
 */

import type { WidgetDefinition } from "../components/widgets/widgetTypes";

export const widgetRegistry: Record<string, WidgetDefinition> = {
  stats: {
    key: "stats",
    name: "Quick Stats",
    category: "dashboard",
    description: "Zeigt wichtige Statistiken auf einen Blick",
    icon: "BarChart",
    component: () => import("../components/widgets/StatsWidget.vue"),
    defaultSize: { w: 3, h: 2 },
    minSize: { w: 2, h: 2 },
    maxSize: { w: 6, h: 4 },
    resizable: true,
    configurable: true,
  },

  recentReminders: {
    key: "recentReminders",
    name: "Recent Reminders",
    category: "activity",
    description: "Aktuelle Erinnerungen und Aufgaben",
    icon: "Clock",
    component: () => import("../components/widgets/RemindersWidget.vue"),
    defaultSize: { w: 3, h: 2 },
    minSize: { w: 2, h: 2 },
    maxSize: { w: 6, h: 4 },
    resizable: true,
    configurable: true,
  },

  shortcuts: {
    key: "shortcuts",
    name: "Shortcuts",
    category: "actions",
    description: "Schnellzugriff auf häufige Aktionen",
    icon: "Zap",
    component: () => import("../components/widgets/ShortcutsWidget.vue"),
    defaultSize: { w: 6, h: 1 },
    minSize: { w: 3, h: 1 },
    maxSize: { w: 6, h: 2 },
    resizable: true,
    configurable: false,
  },

  activityFeed: {
    key: "activityFeed",
    name: "Activity Feed",
    category: "activity",
    description: "Letzte Aktivitäten im System",
    icon: "Activity",
    component: () => import("../components/widgets/ActivityFeedWidget.vue"),
    defaultSize: { w: 3, h: 3 },
    minSize: { w: 2, h: 2 },
    maxSize: { w: 6, h: 6 },
    resizable: true,
    configurable: true,
  },

  notifications: {
    key: "notifications",
    name: "Notifications",
    category: "communication",
    description: "System-Benachrichtigungen",
    icon: "Bell",
    component: () => import("../components/widgets/NotificationsWidget.vue"),
    defaultSize: { w: 2, h: 2 },
    minSize: { w: 2, h: 2 },
    maxSize: { w: 4, h: 4 },
    resizable: true,
    configurable: true,
  },

  calendar: {
    key: "calendar",
    name: "Calendar",
    category: "dashboard",
    description: "Monatskalender mit Terminen",
    icon: "Calendar",
    component: () => import("../components/widgets/CalendarWidget.vue"),
    defaultSize: { w: 3, h: 3 },
    minSize: { w: 3, h: 3 },
    maxSize: { w: 6, h: 6 },
    resizable: true,
    configurable: true,
  },

  weather: {
    key: "weather",
    name: "Weather",
    category: "dashboard",
    description: "Wetter-Widget für deinen Standort",
    icon: "Cloud",
    component: () => import("../components/widgets/WeatherWidget.vue"),
    defaultSize: { w: 2, h: 2 },
    minSize: { w: 2, h: 2 },
    maxSize: { w: 3, h: 3 },
    resizable: true,
    configurable: true,
  },

  chart: {
    key: "chart",
    name: "Analytics Chart",
    category: "stats",
    description: "Diagramme und Analysen",
    icon: "TrendingUp",
    component: () => import("../components/widgets/ChartWidget.vue"),
    defaultSize: { w: 4, h: 3 },
    minSize: { w: 3, h: 2 },
    maxSize: { w: 6, h: 6 },
    resizable: true,
    configurable: true,
  },

  systemMonitor: {
    key: "systemMonitor",
    name: "System Monitor",
    category: "monitoring",
    description: "S.T.A.R. Labs System-Status",
    icon: "Monitor",
    component: () => import("../components/widgets/SystemMonitorWidget.vue"),
    defaultSize: { w: 3, h: 2 },
    minSize: { w: 2, h: 2 },
    maxSize: { w: 6, h: 4 },
    resizable: true,
    configurable: true,
  },
};
