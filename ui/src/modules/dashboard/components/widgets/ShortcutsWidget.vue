<template>
  <kitPanel variant="default" class="shortcuts-compact">
    <template #title>
      <div class="widget-header">
        <svg class="header-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span>Schnellzugriff</span>
      </div>
    </template>

    <div class="shortcuts-list">
      <button
        v-for="shortcut in shortcuts"
        :key="shortcut.id"
        @click="handleClick(shortcut.action)"
        class="shortcut-item"
      >
        <!-- Icon Badge -->
        <div class="icon-badge" :style="{ backgroundColor: shortcut.color + '15', color: shortcut.color }">
          <component :is="getIcon(shortcut.icon)" />
        </div>

        <!-- Text -->
        <span class="shortcut-label">{{ shortcut.label }}</span>

        <!-- Arrow -->
        <svg class="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </kitPanel>
</template>

<script setup lang="ts">
import { h } from "vue";
import { useRouter } from "vue-router";
import kitPanel from "@/components/system/kit-panel.vue";

interface Props {
  data?: any;
}

defineProps<Props>();

const router = useRouter();

const shortcuts = [
  {
    id: 1,
    label: "Neuer Mitarbeiter",
    icon: "user",
    color: "#3B82F6",
    action: "/employees/new",
  },
  {
    id: 2,
    label: "Dokument hochladen",
    icon: "document",
    color: "#A855F7",
    action: "/documents/new",
  },
  {
    id: 3,
    label: "Projekt anlegen",
    icon: "folder",
    color: "#22C55E",
    action: "/projects/new",
  },
  {
    id: 4,
    label: "Berichte",
    icon: "chart",
    color: "#6366F1",
    action: "/reports",
  },
];

const getIcon = (iconType: string) => {
  const icons: Record<string, any> = {
    user: {
      render: () =>
        h("svg", { class: "w-4 h-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24" }, [
          h("path", {
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": "2",
            d: "M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z",
          }),
        ]),
    },
    document: {
      render: () =>
        h("svg", { class: "w-4 h-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24" }, [
          h("path", {
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": "2",
            d: "M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
          }),
        ]),
    },
    folder: {
      render: () =>
        h("svg", { class: "w-4 h-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24" }, [
          h("path", {
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": "2",
            d: "M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z",
          }),
        ]),
    },
    chart: {
      render: () =>
        h("svg", { class: "w-4 h-4", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24" }, [
          h("path", {
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": "2",
            d: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
          }),
        ]),
    },
  };
  return icons[iconType] || icons.user;
};

const handleClick = (route: string) => {
  router.push(route);
};
</script>

<style scoped>
/* Widget Container */
.shortcuts-compact {
  height: 100%;
}

/* Header */
.widget-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
}

.header-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: var(--color-accent-primary);
}

/* Shortcuts List - 4 Columns */
.shortcuts-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.625rem;
  margin-top: 0.875rem;
}

/* Shortcut Item */
.shortcut-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  background: transparent;
  border: 1px solid var(--color-border-primary);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 180ms cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  min-height: 44px;
}

.shortcut-item:hover {
  background: rgba(99, 102, 241, 0.05);
  border-color: var(--color-accent-primary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.shortcut-item:active {
  transform: translateY(0);
}

/* Icon Badge - Small */
.icon-badge {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 180ms;
}

.shortcut-item:hover .icon-badge {
  transform: scale(1.08) rotate(3deg);
}

/* Label */
.shortcut-label {
  flex: 1;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 180ms;
}

.shortcut-item:hover .shortcut-label {
  color: var(--color-accent-primary);
}

/* Arrow Icon */
.arrow-icon {
  width: 1rem;
  height: 1rem;
  color: var(--color-text-secondary);
  flex-shrink: 0;
  transition: all 180ms;
  opacity: 0.5;
}

.shortcut-item:hover .arrow-icon {
  color: var(--color-accent-primary);
  transform: translateX(2px);
  opacity: 1;
}

/* Responsive - 2 Columns on smaller screens */
@media (max-width: 1400px) {
  .shortcuts-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .shortcuts-list {
    grid-template-columns: 1fr;
  }

  .shortcut-item {
    padding: 0.75rem;
  }
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
  .shortcut-item {
    background: rgba(255, 255, 255, 0.015);
  }

  .shortcut-item:hover {
    background: rgba(99, 102, 241, 0.08);
  }
}
</style>
