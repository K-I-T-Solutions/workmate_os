<template>
  <kitPanel title="Benachrichtigungen" variant="default">
    <!-- Header mit Badge -->
    <template #actions>
      <span
        v-if="unreadCount > 0"
        class="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-accent-primary rounded-full"
      >
        {{ unreadCount }}
      </span>
    </template>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"
      ></div>
    </div>

    <!-- Notifications List -->
    <div v-else-if="notifications.length > 0" class="space-y-2">
      <div
        v-for="notification in notifications.slice(0, 5)"
        :key="notification.id"
        class="notification-item group"
        :class="{ unread: !notification.read }"
        @click="markAsRead(notification.id)"
      >
        <div class="flex items-start gap-3">
          <!-- Icon -->
          <div
            class="mt-0.5 w-2 h-2 rounded-full flex-shrink-0"
            :class="
              notification.read ? 'bg-text-secondary/30' : 'bg-accent-primary'
            "
          ></div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p
              class="text-sm"
              :class="
                notification.read
                  ? 'text-text-secondary'
                  : 'text-text-primary font-medium'
              "
            >
              {{ notification.title }}
            </p>
            <p
              v-if="notification.message"
              class="text-xs text-text-secondary mt-1 line-clamp-2"
            >
              {{ notification.message }}
            </p>
            <p class="text-xs text-text-secondary mt-1">
              {{ formatTimestamp(notification.timestamp) }}
            </p>
          </div>

          <!-- Type Badge -->
          <span
            class="flex-shrink-0 text-xs px-2 py-0.5 rounded-md"
            :class="getTypeBadgeClass(notification.type)"
          >
            {{ getTypeLabel(notification.type) }}
          </span>
        </div>
      </div>

      <!-- View All -->
      <button
        v-if="notifications.length > 5"
        class="w-full mt-4 pt-3 border-t border-border-primary text-sm text-accent-primary hover:text-accent-secondary transition-colors"
      >
        Alle anzeigen ({{ notifications.length - 5 }} weitere)
      </button>
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
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      <p class="text-sm text-text-secondary">Keine Benachrichtigungen</p>
    </div>
  </kitPanel>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import kitPanel from "@/components/system/kit-panel.vue";

interface Notification {
  id: number | string;
  title: string;
  message?: string;
  timestamp: string;
  type: "info" | "success" | "warning" | "error";
  read: boolean;
}

interface Props {
  data?: Notification[];
}

const props = defineProps<Props>();

const loading = ref(false);

const notifications = computed(() => {
  return props.data || [];
});

/**
 * Anzahl ungelesener Benachrichtigungen
 */
const unreadCount = computed(() => {
  return notifications.value.filter((n) => !n.read).length;
});

/**
 * Type Badge Styling
 */
const getTypeBadgeClass = (type: string): string => {
  const classes: Record<string, string> = {
    info: "bg-blue-500/10 text-blue-500",
    success: "bg-green-500/10 text-green-500",
    warning: "bg-yellow-500/10 text-yellow-500",
    error: "bg-red-500/10 text-red-500",
  };
  return classes[type] || classes.info;
};

/**
 * Type Label
 */
const getTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    info: "Info",
    success: "Erfolg",
    warning: "Warnung",
    error: "Fehler",
  };
  return labels[type] || "Info";
};

/**
 * Formatiert Zeitstempel
 */
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return "Gerade eben";
  if (diffMins < 60) return `vor ${diffMins} Min.`;
  if (diffHours < 24) return `vor ${diffHours} Std.`;

  return date.toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

/**
 * Markiert Benachrichtigung als gelesen
 */
const markAsRead = (id: number | string) => {
  const notification = notifications.value.find((n) => n.id === id);
  if (notification) {
    notification.read = true;
    // TODO: API-Call zum Backend
  }
};

onMounted(() => {
  if (!props.data) {
    loading.value = false;
  }
});
</script>

<style scoped>
.notification-item {
  @apply p-3 rounded-lg border border-transparent hover:border-border-primary
         hover:bg-bg-secondary/30 transition-all duration-200 cursor-pointer;
}

.notification-item.unread {
  @apply bg-accent-primary/5;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
