<template>
  <kitPanel variant="default" class="shortcuts-compact">
    <template #title>
      <div class="widget-header">
        <Zap class="header-icon" />
        <span>Schnellzugriff</span>
      </div>
    </template>

    <div class="shortcuts-list">
      <button
        v-for="shortcut in shortcuts"
        :key="shortcut.id"
        class="shortcut-item"
        @click="navigate(shortcut.action)"
      >
        <!-- Icon -->
        <div
          class="icon-badge"
          :style="{
            backgroundColor: shortcut.color + '15',
            color: shortcut.color
          }"
        >
          <component :is="shortcut.icon" class="w-4 h-4" />
        </div>

        <!-- Label -->
        <span class="shortcut-label">
          {{ shortcut.label }}
        </span>

        <!-- Arrow -->
        <ChevronRight class="arrow-icon" />
      </button>
    </div>
  </kitPanel>
</template>

<script setup lang="ts">
import { markRaw } from "vue";
import { useRouter } from "vue-router";
import kitPanel from "@/components/system/kit-panel.vue";

/* Lucide Icons */
import {
  UserPlus,
  FileUp,
  FolderPlus,
  BarChart3,
  ChevronRight,
  Zap,
} from "lucide-vue-next";

const router = useRouter();

interface Shortcut {
  id: number;
  label: string;
  icon: any;
  color: string;
  action: string;
}

const shortcuts: Shortcut[] = [
  {
    id: 1,
    label: "Neuer Mitarbeiter",
    icon: markRaw(UserPlus),
    color: "#3B82F6",
    action: "/employees/new",
  },
  {
    id: 2,
    label: "Dokument hochladen",
    icon: markRaw(FileUp),
    color: "#A855F7",
    action: "/documents/new",
  },
  {
    id: 3,
    label: "Projekt anlegen",
    icon: markRaw(FolderPlus),
    color: "#22C55E",
    action: "/projects/new",
  },
  {
    id: 4,
    label: "Berichte",
    icon: markRaw(BarChart3),
    color: "#6366F1",
    action: "/reports",
  },
];

function navigate(route: string) {
  router.push(route);
}
</script>
