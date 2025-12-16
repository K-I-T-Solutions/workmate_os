import { reactive, ref } from "vue";
import { apps } from "./appRegistry"; // ⬅️ wichtig

export interface WindowApp {
  id: string;
  appId: string;
  title: string;
  component: any;
  props?: Record<string, any>;
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

/* -----------------------------
   Viewport Helpers
------------------------------ */
function getViewport() {
  return {
    vw: window.innerWidth,
    vh: window.innerHeight,
  };
}

function constrainWindow(win: WindowApp) {
  const { vw, vh } = getViewport();

  win.width = Math.max(MIN_WIDTH, Math.min(win.width, vw));
  win.height = Math.max(MIN_HEIGHT, Math.min(win.height, vh));

  win.x = Math.max(0, Math.min(win.x, vw - win.width));
  win.y = Math.max(0, Math.min(win.y, vh - win.height));
}

/* -----------------------------
   App Manager
------------------------------ */
export const appManager = {
  windows,
  activeWindow,

  openWindow(appId: string) {
    const app = apps.find(a => a.id === appId);
    if (!app) return;

    const existing = windows.find(w => w.appId === appId);
    if (existing) {
      appManager.focusWindow(existing.id);
      return existing.id;
    }

    const { vw, vh } = getViewport();

    const width = app.window?.width ?? 960;
    const height = app.window?.height ?? 620;

    const id = crypto.randomUUID();

    const win: WindowApp = {
      id,
      appId: app.id,
      title: app.title,
      component: app.component,
      props: {},
      width,
      height,
      x: (vw - width) / 2,
      y: (vh - height) / 2,
      z: ++zCounter,
    };

    constrainWindow(win);
    windows.push(win);
    activeWindow.value = id;

    return id;
  },

  closeWindow(id: string) {
    const i = windows.findIndex(w => w.id === id);
    if (i !== -1) windows.splice(i, 1);
  },

  focusWindow(id: string) {
    const win = windows.find(w => w.id === id);
    if (!win) return;
    win.z = ++zCounter;
    activeWindow.value = id;
  },

  startDragFor(id: string, e: MouseEvent) {
    const win = windows.find(w => w.id === id);
    if (!win) return;

    const startX = e.clientX;
    const startY = e.clientY;
    const initialX = win.x;
    const initialY = win.y;

    function move(ev: MouseEvent) {
      win.x = initialX + (ev.clientX - startX);
      win.y = initialY + (ev.clientY - startY);
    }

    function stop() {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
      constrainWindow(win);
    }

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
  },

  startResizeFor(id: string, e: MouseEvent) {
    const win = windows.find(w => w.id === id);
    if (!win) return;

    const startX = e.clientX;
    const startY = e.clientY;
    const initialW = win.width;
    const initialH = win.height;

    function move(ev: MouseEvent) {
      win.width = Math.max(
        MIN_WIDTH,
        initialW + (ev.clientX - startX)
      );
      win.height = Math.max(
        MIN_HEIGHT,
        initialH + (ev.clientY - startY)
      );
    }

    function stop() {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
      constrainWindow(win);
    }

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
  },
};

export function useAppManager() {
  return appManager;
}
