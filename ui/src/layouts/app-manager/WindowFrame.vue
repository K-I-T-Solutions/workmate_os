<!-- src/layouts/app-manager/WindowFrame.vue -->
<template>
  <div
    class="window-frame"
    :class="{ 'window-frame--active': isActive }"
    :style="frameStyleString"
    @mousedown="focus"
  >
    <!-- TITLEBAR -->
    <div
      class="window-titlebar"
      @mousedown.stop="startDrag"
    >
      <span class="window-title">
        {{ win.title }}
      </span>

      <div class="window-controls">
        <button class="window-minimize" @click.stop="minimize" title="Minimieren">
          −
        </button>
        <button class="window-close" @click.stop="close" title="Schließen">
          ✕
        </button>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="window-content">
      <slot />
    </div>

    <!-- RESIZE HANDLE (nur Desktop) -->
    <div class="resize-handle" @mousedown.stop="startResize" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useAppManager } from "./useAppManager";
import type { WindowApp } from "./useAppManager";

const props = defineProps<{
  win: WindowApp;
}>();

const { activeWindow, closeWindow, minimizeWindow, focusWindow, startDragFor, startResizeFor } =
  useAppManager();

const isActive = computed(() => activeWindow.value === props.win.id);

const frameStyleString = computed(() =>
  `
    top: ${props.win.y}px;
    left: ${props.win.x}px;
    width: ${props.win.width}px;
    height: ${props.win.height}px;
    z-index: ${props.win.z};
  `
);


function startDrag(e: MouseEvent) {
  // auf Mobile nicht draggen
  if (window.innerWidth <= 1024) return;
  startDragFor(props.win.id, e);
}

function startResize(e: MouseEvent) {
  if (window.innerWidth <= 1024) return;
  startResizeFor(props.win.id, e);
}

function focus() {
  focusWindow(props.win.id);
}

function minimize() {
  minimizeWindow(props.win.id);
}

function close() {
  closeWindow(props.win.id);
}
</script>

<style scoped>
.window-frame {
  position: absolute;
  background: #050509;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow 0.2s ease, border-color 0.2s ease,
    transform 0.15s ease;
}

.window-frame--active {
  border-color: var(--color-accent-primary, #ff9100);
  box-shadow: 0 20px 70px rgba(0, 0, 0, 0.75);
}

/* TITLEBAR */
.window-titlebar {
  height: 44px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.06),
    rgba(255, 255, 255, 0.02)
  );
  cursor: move;
  user-select: none;
}

.window-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #ffffff;
}

.window-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.window-minimize,
.window-close {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  border: none;
  color: white;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.window-minimize {
  background: #facc15;
}

.window-minimize:hover {
  opacity: 0.8;
}

.window-close {
  background: #ef4444;
}

.window-close:hover {
  opacity: 0.8;
}

/* CONTENT */
.window-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: #050509;
}

/* RESIZE HANDLE */
.resize-handle {
  position: absolute;
  width: 16px;
  height: 16px;
  right: 4px;
  bottom: 4px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-top: none;
  border-left: none;
  cursor: se-resize;
  opacity: 0.7;
}

/* =========================================
   MOBILE / TABLET: FULLSCREEN WINDOWS
   ========================================= */
@media (max-width: 1024px) {
  .window-frame {
    position: fixed !important;
    top: var(--os-topbar-height, 48px) !important;
    left: 0 !important;
    width: 100vw !important;
    height: calc(
      100vh - var(--os-topbar-height, 48px) - var(--os-dock-height, 72px)
    ) !important;
    border-radius: 0 !important;
    max-width: 100vw !important;
    max-height: 100vh !important;
    box-shadow: none;
  }

  .window-titlebar {
    height: 40px;
    padding: 0 12px;
    font-size: 0.85rem;
  }

  .window-content {
    padding: 16px;
  }

  .resize-handle {
    display: none !important;
  }
}
</style>
