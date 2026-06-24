// src/layouts/app-manager/useAppManager.ts
import { router } from "@/router";
import { reactive, ref } from "vue";

export interface WindowApp {
  id: string;
  appId: string;
  title: string;
  routePath: string;
  x: number;
  y: number;
  width: number;
  height: number;
  z: number;
}

const windows = reactive<WindowApp[]>([]);
const activeWindow = ref<string | null>(null);

let zCounter = 10;

const MIN_WIDTH = 480;
const MIN_HEIGHT = 320;
const VIEWPORT_MAX_RATIO = 0.9;
const WINDOW_MARGIN = 16;

function getViewport() {
  if (typeof window === "undefined") {
    return { vw: 1920, vh: 1080 };
  }
  return { vw: window.innerWidth, vh: window.innerHeight };
}

function constrainWindow(win: WindowApp) {
  const { vw, vh } = getViewport();

  const maxWidth = vw * VIEWPORT_MAX_RATIO;
  const maxHeight = vh * VIEWPORT_MAX_RATIO;

  if (win.width > maxWidth) {
    win.width = Math.max(MIN_WIDTH, maxWidth);
  }
  if (win.height > maxHeight) {
    win.height = Math.max(MIN_HEIGHT, maxHeight);
  }

  if (win.x < WINDOW_MARGIN) win.x = WINDOW_MARGIN;
  if (win.y < WINDOW_MARGIN) win.y = WINDOW_MARGIN;

  if (win.x + win.width > vw - WINDOW_MARGIN) {
    win.x = vw - WINDOW_MARGIN - win.width;
  }
  if (win.y + win.height > vh - WINDOW_MARGIN) {
    win.y = vh - WINDOW_MARGIN - win.height;
  }
}

function constrainAllWindows() {
  windows.forEach((w) => constrainWindow(w));
}

if (typeof window !== "undefined") {
  window.addEventListener("resize", () => {
    constrainAllWindows();
  });
}

const appManager = {
  windows,
  activeWindow,

  openWindow(appId: string, title: string, routePath: string) {
    const existing = windows.find((w) => w.appId === appId);
    if (existing) {
      existing.routePath = routePath;
      appManager.focusWindow(existing.id);
      router.push(routePath);
      return existing.id;
    }

    const { vw, vh } = getViewport();
    const defaultWidth = Math.min(960, vw * VIEWPORT_MAX_RATIO);
    const defaultHeight = Math.min(620, vh * VIEWPORT_MAX_RATIO);

    const id = crypto.randomUUID();
    const win: WindowApp = {
      id,
      appId,
      title,
      routePath,
      width: defaultWidth,
      height: defaultHeight,
      x: (vw - defaultWidth) / 2,
      y: (vh - defaultHeight) / 2,
      z: ++zCounter,
    };

    constrainWindow(win);
    windows.push(win);
    activeWindow.value = id;

    router.push(routePath);
    return id;
  },

  closeWindow(id: string) {
    const idx = windows.findIndex((w) => w.id === id);
    if (idx !== -1) {
      windows.splice(idx, 1);
      if (activeWindow.value === id) {
        activeWindow.value = windows.length
          ? windows[windows.length - 1].id
          : null;
      }
    }
  },

  focusWindow(id: string) {
    const win = windows.find((w) => w.id === id);
    if (!win) return;
    win.z = ++zCounter;
    activeWindow.value = id;
  },

  startDragFor(id: string, e: MouseEvent) {
    const win = windows.find((w) => w.id === id);
    if (!win) return;

    const startX = e.clientX;
    const startY = e.clientY;
    const initialX = win.x;
    const initialY = win.y;

    function move(ev: MouseEvent) {
      const { vw, vh } = getViewport();

      const dx = ev.clientX - startX;
      const dy = ev.clientY - startY;

      let nextX = initialX + dx;
      let nextY = initialY + dy;

      if (nextX < WINDOW_MARGIN) nextX = WINDOW_MARGIN;
      if (nextY < WINDOW_MARGIN) nextY = WINDOW_MARGIN;

      if (nextX + win.width > vw - WINDOW_MARGIN) {
        nextX = vw - WINDOW_MARGIN - win.width;
      }
      if (nextY + win.height > vh - WINDOW_MARGIN) {
        nextY = vh - WINDOW_MARGIN - win.height;
      }

      win.x = nextX;
      win.y = nextY;
    }

    function stop() {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
      constrainWindow(win);
    }

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
  },

  startResizeFor(id: string, e: MouseEvent, direction: string) {
    const win = windows.find((w) => w.id === id);
    if (!win) return;

    const startX = e.clientX;
    const startY = e.clientY;

    const startW = win.width;
    const startH = win.height;
    const startLeft = win.x;
    const startTop = win.y;

    function move(ev: MouseEvent) {
      const dx = ev.clientX - startX;
      const dy = ev.clientY - startY;

      let nextW = startW;
      let nextH = startH;
      let nextX = startLeft;
      let nextY = startTop;

      switch (direction) {
        case "right":
          nextW = Math.max(MIN_WIDTH, startW + dx);
          break;
        case "left":
          nextW = Math.max(MIN_WIDTH, startW - dx);
          nextX = startLeft + dx;
          break;
        case "bottom":
          nextH = Math.max(MIN_HEIGHT, startH + dy);
          break;
        case "top":
          nextH = Math.max(MIN_HEIGHT, startH - dy);
          nextY = startTop + dy;
          break;
        case "bottom-right":
          nextW = Math.max(MIN_WIDTH, startW + dx);
          nextH = Math.max(MIN_HEIGHT, startH + dy);
          break;
        case "bottom-left":
          nextW = Math.max(MIN_WIDTH, startW - dx);
          nextH = Math.max(MIN_HEIGHT, startH + dy);
          nextX = startLeft + dx;
          break;
        case "top-right":
          nextW = Math.max(MIN_WIDTH, startW + dx);
          nextH = Math.max(MIN_HEIGHT, startH - dy);
          nextY = startTop + dy;
          break;
        case "top-left":
          nextW = Math.max(MIN_WIDTH, startW - dx);
          nextH = Math.max(MIN_HEIGHT, startH - dy);
          nextX = startLeft + dx;
          nextY = startTop + dy;
          break;
      }

      win.width = nextW;
      win.height = nextH;
      win.x = nextX;
      win.y = nextY;

      constrainWindow(win);
    }

    function stop() {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
    }

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
  },
};

export function useAppManager() {
  return appManager;
}
