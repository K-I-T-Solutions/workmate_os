<template>
  <header
    class="wm-topbar fixed top-0 z-50 w-full transition-all duration-300 ease-in-out"
  >
    <div class="topbar-inner">
      <!-- LEFT -->
      <div class="topbar-section-left">
        <!-- Mobile Menu Button -->
        <button
          class="mobile-menu-btn"
          aria-label="Toggle menu"
          aria-controls="app-sidebar"
          :aria-expanded="isMenuOpen"
          @click="toggleMenu"
        >
          <Menu v-if="!isMenuOpen" class="w-5 h-5" />
          <X v-else class="w-5 h-5" />
        </button>

        <!-- Brand -->
        <div class="brand-container">
          <div class="logo-wrapper">
            <img
              v-if="logo"
              :src="logo"
              alt="WorkmateOS"
              class="logo-image"
            />
            <div v-else class="logo-fallback">W</div>
          </div>

          <span class="brand-name">WorkmateOS</span>
        </div>
      </div>

      <!-- CENTER -->
      <div v-if="title" class="topbar-title">
        {{ title }}
      </div>

      <!-- RIGHT -->
      <div class="topbar-section-right">
        <!-- Time -->
        <div class="time-display" :title="fullDate">
          <div class="time-container">
            <Clock class="time-icon" />
            <span class="time-text">{{ time }}</span>
          </div>
          <span class="date-text">{{ shortDate }}</span>
        </div>

        <!-- Profile -->
        <button
          class="profile-btn"
          aria-label="Open profile menu"
          @click="toggleProfileMenu"
        >
          <UserIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import {
  Menu,
  X,
  Clock,
  User as UserIcon,
} from "lucide-vue-next";
import { WorkmateAssets } from "@/services/assets";

/* Props */
interface Props {
  title?: string;
}
defineProps<Props>();

/* Emits (optional, future-proof) */
const emit = defineEmits<{
  (e: "toggle-menu", open: boolean): void;
}>();

/* State */
const isMenuOpen = ref(false);
const logo = ref<string | null>(WorkmateAssets.workmateFavicon);

/* Actions */
function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value;
  emit("toggle-menu", isMenuOpen.value);
}

function toggleProfileMenu() {
  console.log("TODO: Profile menu");
}

/* Clock */
const time = ref("");
const shortDate = ref("");
const fullDate = ref("");

function updateClock() {
  const now = new Date();

  time.value = now.toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });

  shortDate.value = now.toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
  });

  fullDate.value = now.toLocaleDateString("de-DE", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

let clockInterval: number | undefined;

onMounted(() => {
  updateClock();
  clockInterval = window.setInterval(updateClock, 60000);
});

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval);
});
</script>

<style scoped>
/* Container */
.wm-topbar {
  height: var(--os-topbar-height);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid var(--color-border-light);
}

/* Inner */
.topbar-inner {
  max-width: 1920px;
  height: 100%;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

/* Sections */
.topbar-section-left,
.topbar-section-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

/* Mobile Menu */
.mobile-menu-btn {
  display: none;
  padding: 0.5rem;
  border-radius: 0.5rem;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }
}

/* Brand */
.brand-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-wrapper {
  width: 2rem;
  height: 2rem;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-fallback {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
  background: rgba(var(--color-accent-primary-rgb), 0.15);
  color: var(--color-accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

/* Title */
.topbar-title {
  flex: 1;
  text-align: center;
  font-weight: 600;
}

/* Time */
.time-display {
  display: none;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 0.625rem;
  border: 1px solid var(--color-border-light);
}

@media (min-width: 640px) {
  .time-display {
    display: flex;
  }
}

.time-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.time-icon {
  width: 1rem;
  height: 1rem;
  color: var(--color-accent-primary);
}

/* Profile */
.profile-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-light);
}
</style>
