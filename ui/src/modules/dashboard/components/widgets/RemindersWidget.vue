<template>
  <kitPanel title="Erinnerungen" variant="default">
    <div v-if="!data || data.length === 0" class="text-text-secondary text-sm opacity-60 py-4">
      Keine Erinnerungen
    </div>

    <ul v-else class="space-y-2">
      <li
        v-for="reminder in data"
        :key="reminder.id"
        class="flex items-start justify-between p-2 rounded-md bg-bg-secondary/30 border border-border-primary"
      >
        <div>
          <p class="text-text-primary font-medium">
            {{ reminder.title }}
          </p>
          <p class="text-text-secondary text-xs mt-1">
            {{ formatDate(reminder.due_date) }}
          </p>
        </div>

        <div
          class="w-2 h-2 mt-2 rounded-full"
          :class="reminder.is_completed ? 'bg-green-500' : 'bg-yellow-500'"
        ></div>
      </li>
    </ul>
  </kitPanel>
</template>

<script setup lang="ts">
import kitPanel from "@/components/system/kit-panel.vue";

interface ReminderItem {
  id: string
  title: string
  due_date: string | null
  is_completed: boolean
}

const props = defineProps<{
  data: ReminderItem[] | null
}>()

function formatDate(date: string | null) {
  if (!date) return "—"
  return new Date(date).toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit"
  })
}
</script>
