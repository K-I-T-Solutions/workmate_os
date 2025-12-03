import { ref, watch } from "vue";
import { defineStore } from "pinia";

export const useSidebarStore = defineStore("sidebar", () => {
  // Load from localStorage or default to FALSE (collapsed)
  const isOpen = ref(localStorage.getItem("sidebar-open") === "true");
  const isHovered = ref(false);

  // Save to localStorage when changed
  watch(isOpen, (value) => {
    localStorage.setItem("sidebar-open", value.toString());
  });

  function toggle() {
    isOpen.value = !isOpen.value;
  }

  function open() {
    isOpen.value = true;
  }

  function close() {
    isOpen.value = false;
  }

  function setHovered(value: boolean) {
    isHovered.value = value;
  }

  return {
    isOpen,
    isHovered,
    toggle,
    open,
    close,
    setHovered,
  };
});
