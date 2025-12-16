// src/layouts/app-manager/useAppManager.ts
import { reactive, ref } from "vue";

export interface WindowApp {
  id: string;          // Fenster-ID (Instanz!)
  appId: string;       // App-Typ (crm, finance, …)
  title: string;
  component: any;      // 🔥 WICHTIG
  props?: Record<string, any>; // optionaler State
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

const appManager = {
  windows,
  activeWindow,

  openWindow(appId: string, title: string, component: any, props?: Record<string, any>) {
  const id = crypto.randomUUID();

  windows.push({
    id,
    appId,
    title,
    component,
    props,
    x: 120,
    y: 80,
    width: 960,
    height: 620,
    z: ++zCounter,
  });

  activeWindow.value = id;
  return id;
},
  closeWindow(id: string) {
    const i = windows.findIndex((w) => w.id === id);
    if (i !== -1) windows.splice(i, 1);
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
      win.x = initialX + (ev.clientX - startX);
      win.y = initialY + (ev.clientY - startY);
    }

    function stop() {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
    }

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
  },

  /** Resize vom Bottom-Right-Handle aus */
  startResizeFor(id: string, e: MouseEvent) {
    const win = windows.find((w) => w.id === id);
    if (!win) return;

    const startX = e.clientX;
    const startY = e.clientY;
    const initialW = win.width;
    const initialH = win.height;

    function move(ev: MouseEvent) {
      const nextW = initialW + (ev.clientX - startX);
      const nextH = initialH + (ev.clientY - startY);

      win.width = Math.max(MIN_WIDTH, nextW);
      win.height = Math.max(MIN_HEIGHT, nextH);
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
