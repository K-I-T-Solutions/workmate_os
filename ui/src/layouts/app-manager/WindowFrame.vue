<!-- src/layouts/app-manager/WindowFrame.vue -->
<template>
  <div
    class="window-frame"
    :class="{ 'window-active': isActive, 'window-mobile': isMobile }"
    :style="frameStyle"
    @mousedown="focus"
  >
    <!-- TITLEBAR -->
    <div
      class="window-titlebar"
      :class="{ 'window-titlebar--mobile': isMobile }"
      @mousedown.stop="startDrag"
    >
      <span class="window-title">{{ win.title }}</span>
      <button class="window-close" @click.stop="close">✕</button>
    </div>

    <!-- CONTENT -->
    <div class="window-content">
      <router-view />
    </div>

    <!-- RESIZE HANDLES (nur Desktop) -->
    <template v-if="!isMobile">
      <div class="resize-handle handle-top"    @mousedown.stop="startResize('top', $event)" />
      <div class="resize-handle handle-bottom" @mousedown.stop="startResize('bottom', $event)" />
      <div class="resize-handle handle-left"   @mousedown.stop="startResize('left', $event)" />
      <div class="resize-handle handle-right"  @mousedown.stop="startResize('right', $event)" />

      <div class="resize-handle handle-tl" @mousedown.stop="startResize('top-left', $event)" />
      <div class="resize-handle handle-tr" @mousedown.stop="startResize('top-right', $event)" />
      <div class="resize-handle handle-bl" @mousedown.stop="startResize('bottom-left', $event)" />
      <div class="resize-handle handle-br" @mousedown.stop="startResize('bottom-right', $event)" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from "vue";
import { useAppManager } from "./useAppManager";
import type { WindowApp } from "./useAppManager";

const props = defineProps<{ win: WindowApp }>();
const { activeWindow, closeWindow, focusWindow, startDragFor, startResizeFor } =
  useAppManager();

/* -------------------------------
   ACTIVE STATE
-------------------------------- */
const isActive = computed(() => activeWindow.value === props.win.id);

/* -------------------------------
   REAKTIVE MOBILE CHECK
   (≤ 768px = Mobile / Handy)
-------------------------------- */
const viewportWidth = ref(
  typeof window !== "undefined" ? window.innerWidth : 1920
);

let resizeHandler: (() => void) | null = null;

onMounted(() => {
  if (typeof window === "undefined") return;
  resizeHandler = () => {
    viewportWidth.value = window.innerWidth;
  };
  window.addEventListener("resize", resizeHandler);
});

onBeforeUnmount(() => {
  if (resizeHandler && typeof window !== "undefined") {
    window.removeEventListener("resize", resizeHandler);
  }
});

const isMobile = computed(() => viewportWidth.value <= 768);

/* -------------------------------
   FRAME STYLE
-------------------------------- */
const frameStyle = computed(() => {
  if (isMobile.value) {
    // Vollbild zwischen Topbar & Dock
    return {
      position: "fixed",
      top: "var(--os-topbar-height)",
      left: "0",
      width: "100vw",
      height:
        "calc(100vh - var(--os-topbar-height) - var(--os-dock-height))",
      zIndex: props.win.z,
    };
  }

  // Desktop: normale Window-Koordinaten aus AppManager
  return {
    position: "absolute",
    top: props.win.y + "px",
    left: props.win.x + "px",
    width: props.win.width + "px",
    height: props.win.height + "px",
    zIndex: props.win.z,
  };
});

/* -------------------------------
   WINDOW ACTIONS
-------------------------------- */
function startDrag(e: MouseEvent) {
  if (isMobile.value) return;
  startDragFor(props.win.id, e);
}

function startResize(direction: string, e: MouseEvent) {
  if (isMobile.value) return;
  startResizeFor(props.win.id, e, direction);
}

function focus() {
  focusWindow(props.win.id);
}

function close() {
  closeWindow(props.win.id);
}
</script>

<style scoped>
/* ============================================
   WINDOW FRAME
============================================ */
.window-frame {
  background: #050509;
  border-radius: 16px;
  min-width: 350px;
  min-height: 280px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.window-active {
  border-color: var(--color-accent-primary);
  box-shadow:
      0 0 0 1px var(--color-accent-primary),
      0 0 28px rgba(255, 145, 0, 0.40),
      0 0 80px rgba(255, 145, 0, 0.25),
      0 0 140px rgba(255, 145, 0, 0.15);
}

/* ============================================
   TITLEBAR
============================================ */
.window-titlebar {
  height: 44px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.06),
    rgba(255, 255, 255, 0.015)
  );
  cursor: move;
  user-select: none;
}

.window-titlebar--mobile {
  cursor: default;
}

.window-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #ffffff;
}

.window-close {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: #ef4444;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ============================================
   CONTENT
============================================ */
.window-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: #050509;
}

/* ============================================
   RESIZE HANDLES – DESKTOP
============================================ */
.resize-handle {
  position: absolute;
  z-index: 20;
}

/* Kanten */
.handle-top {
  top: -4px;
  left: 12px;
  right: 12px;
  height: 8px;
  cursor: ns-resize;
}
.handle-bottom {
  bottom: -4px;
  left: 12px;
  right: 12px;
  height: 8px;
  cursor: ns-resize;
}
.handle-left {
  left: -4px;
  top: 12px;
  bottom: 12px;
  width: 8px;
  cursor: ew-resize;
}
.handle-right {
  right: -4px;
  top: 12px;
  bottom: 12px;
  width: 8px;
  cursor: ew-resize;
}

/* Ecken */
.handle-tl {
  top: -4px;
  left: -4px;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
}
.handle-tr {
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  cursor: nesw-resize;
}
.handle-bl {
  bottom: -4px;
  left: -4px;
  width: 16px;
  height: 16px;
  cursor: nesw-resize;
}
.handle-br {
  bottom: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
}

/* ============================================
   MOBILE MODE (≤ 768px)
============================================ */
.window-mobile {
  border-radius: 0 !important;
  border: none !important;
  box-shadow: none !important;
}

@media (max-width: 768px) {
  .resize-handle {
    display: none !important;
    pointer-events: none !important;
  }

  .window-content {
    padding: 16px;
  }
}
</style>
