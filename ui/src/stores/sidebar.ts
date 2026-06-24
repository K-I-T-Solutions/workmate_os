import { defineStore } from "pinia";

export const useSidebarStore = defineStore("sidebar", {
  state: () => ({
    isOpen: false,
    isHovered: false,
  }),
  actions: {
    toggle() {},
    open() {},
    close() {},
    setHovered() {},
  },
});
