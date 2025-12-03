<template>
  <kitPanel title="Activity Feed" variant="default">
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"
      ></div>
    </div>

    <!-- Activity List -->
    <div v-else-if="activities.length > 0" class="space-y-3">
      <div
        v-for="activity in activities"
        :key="activity.id"
        class="activity-item group"
      >
        <div class="flex items-start gap-3">
          <!-- Icon -->
          <div
            class="mt-1 w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            :class="getActivityIconBg(activity.type)"
          >
            <component
              :is="getActivityIcon(activity.type)"
              class="w-4 h-4"
              :class="getActivityIconColor(activity.type)"
            />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p class="text-sm text-text-primary">
              <span class="font-medium">{{ activity.actor }}</span>
              <span class="text-text-secondary"> {{ activity.action }}</span>
            </p>
            <p class="text-xs text-text-secondary mt-1">
              {{ formatTimestamp(activity.timestamp) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <svg
        class="w-12 h-12 mx-auto mb-3 text-text-secondary opacity-50"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
      <p class="text-sm text-text-secondary">Keine Aktivitäten</p>
    </div>
  </kitPanel>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from "vue";
import kitPanel from "@/components/system/kit-panel.vue";

// Icons
const FileIcon = {
  render: () =>
    h(
      "svg",
      {
        class: "w-4 h-4",
        fill: "none",
        stroke: "currentColor",
        viewBox: "0 0 24 24",
      },
      [
        h("path", {
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
          "stroke-width": "2",
          d: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
        }),
      ]
    ),
};

const UserIcon = {
  render: () =>
    h(
      "svg",
      {
        class: "w-4 h-4",
        fill: "none",
        stroke: "currentColor",
        viewBox: "0 0 24 24",
      },
      [
        h("path", {
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
          "stroke-width": "2",
          d: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
        }),
      ]
    ),
};

const CheckIcon = {
  render: () =>
    h(
      "svg",
      {
        class: "w-4 h-4",
        fill: "none",
        stroke: "currentColor",
        viewBox: "0 0 24 24",
      },
      [
        h("path", {
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
          "stroke-width": "2",
          d: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
        }),
      ]
    ),
};

const EditIcon = {
  render: () =>
    h(
      "svg",
      {
        class: "w-4 h-4",
        fill: "none",
        stroke: "currentColor",
        viewBox: "0 0 24 24",
      },
      [
        h("path", {
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
          "stroke-width": "2",
          d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z",
        }),
      ]
    ),
};

interface Props {
  data?: any[];
}

const props = defineProps<Props>();

const loading = ref(false);

const activities = computed(() => {
  return props.data || [];
});

/**
 * Icon für Activity-Typ
 */
const getActivityIcon = (type: string) => {
  const icons: Record<string, any> = {
    document: FileIcon,
    user: UserIcon,
    task: CheckIcon,
    edit: EditIcon,
  };
  return icons[type] || FileIcon;
};

/**
 * Icon Background für Activity-Typ
 */
const getActivityIconBg = (type: string): string => {
  const backgrounds: Record<string, string> = {
    document: "bg-blue-500/10",
    user: "bg-green-500/10",
    task: "bg-purple-500/10",
    edit: "bg-yellow-500/10",
  };
  return backgrounds[type] || "bg-gray-500/10";
};

/**
 * Icon Farbe für Activity-Typ
 */
const getActivityIconColor = (type: string): string => {
  const colors: Record<string, string> = {
    document: "text-blue-500",
    user: "text-green-500",
    task: "text-purple-500",
    edit: "text-yellow-500",
  };
  return colors[type] || "text-gray-500";
};

/**
 * Formatiert Zeitstempel relativ
 */
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Gerade eben";
  if (diffMins < 60) return `vor ${diffMins} Min.`;
  if (diffHours < 24) return `vor ${diffHours} Std.`;
  if (diffDays === 1) return "Gestern";
  if (diffDays < 7) return `vor ${diffDays} Tagen`;

  return date.toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
  });
};

onMounted(() => {
  // Optional: Lade Aktivitäten wenn keine Props übergeben
  if (!props.data) {
    loading.value = false;
  }
});
</script>

<style scoped>
.activity-item {
  @apply p-3 rounded-lg border border-transparent hover:border-border-primary
         hover:bg-bg-secondary/30 transition-all duration-200;
}
</style>
