<template>
  <div class="h-full flex flex-col">
    <h3 class="text-white font-semibold mb-3">
      Letzte Aktivitäten
    </h3>

    <!-- Loading -->
    <div
      v-if="loading"
      class="flex-1 flex items-center justify-center text-white/40 text-sm"
    >
      Lade Aktivitäten …
    </div>

    <!-- Empty -->
    <div
      v-else-if="activities.length === 0"
      class="flex-1 flex items-center justify-center text-white/40 text-sm"
    >
      Noch keine Aktivitäten
    </div>

    <!-- List -->
    <ul
      v-else
      class="space-y-3 text-sm text-white/80 overflow-hidden"
    >
      <li
        v-for="activity in activities"
        :key="activity.id"
        class="flex gap-3"
      >
        <!-- Icon -->
        <div class="mt-0.5 text-white/50">
          <component
            :is="iconFor(activity.type)"
            class="w-4 h-4"
          />
        </div>

        <!-- Content -->
        <div class="flex-1">
          <div class="text-white/90 leading-snug">
            {{ activity.description }}
          </div>

          <div class="text-xs text-white/40 mt-0.5">
            {{ formatDate(activity.occurred_at) }}
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import {
  Phone,
  Mail,
  MapPin,
  FileText,
  StickyNote,
} from "lucide-vue-next";

import { useCrmActivity } from "../../composables/useCrmActivity";
import type { ActivityType } from "../../types/activity";

const { activities, loading, fetchLatestActivities } = useCrmActivity();

onMounted(() => {
  fetchLatestActivities(5);
});

function iconFor(type: ActivityType) {
  switch (type) {
    case "call":
      return Phone;
    case "email":
      return Mail;
    case "onsite":
      return MapPin;
    case "remote":
      return FileText;
    case "note":
      return StickyNote;
    default:
      return StickyNote;
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleString("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  });
}
</script>
