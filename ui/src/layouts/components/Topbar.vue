<template>
  <header
    class="wm-topbar fixed top-0 z-50 transition-all duration-300 ease-in-out w-full"
  >
    <!-- Inner Container - Zentriert mit max-width -->
    <div class="topbar-inner">
      <!-- Left Section -->
      <div class="topbar-section-left">
        <!-- Mobile Menu -->
        <button
          class="mobile-menu-btn"
          aria-label="Toggle Menu"
        >
          <Menu class="w-5 h-5" " />
          <X class="w-5 h-5"  />
        </button>

        <!-- Logo & Brand -->
        <div class="brand-container">
          <div class="logo-wrapper">
            <img
              v-if="logo"
              :src="logo"
              alt="WorkmateOS"
              class="logo-image"
              
            />
            <div v-else class="logo-fallback">
              W
            </div>
          </div>

          <span class="brand-name">
            WorkmateOS
          </span>
        </div>
      </div>

      <!-- Center Title -->
      <div v-if="title" class="topbar-title">
        {{ title }}
      </div>

      <!-- Right Section -->
      <div class="topbar-section-right">
        <!-- Time & Date -->
        <div class="time-display" :title="fullDate">
          <div class="time-container">
            <svg class="time-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="time-text">{{ time }}</span>
          </div>
          <span class="date-text">{{ shortDate }}</span>
        </div>

        <!-- Profile Button -->
        <button class="profile-btn" @click="toggleProfileMenu">
          <UserIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { Menu, X, User as UserIcon } from "lucide-vue-next";
import { WorkmateAssets } from "@/services/assets";


interface Props {
  title?: string;
}

defineProps<Props>();

const logo = ref<string | null>(WorkmateAssets.workmateFavicon);



// Time & Date
const time = ref("");
const shortDate = ref("");
const fullDate = ref("");

const updateClock = () => {
  const now = new Date();
  time.value = now.toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });
  shortDate.value = now.toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
  });
  fullDate.value = now.toLocaleDateString("de-DE", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

let clockInterval: any = null;
onMounted(() => {
  updateClock();
  clockInterval = setInterval(updateClock, 60000);
});
onUnmounted(() => clearInterval(clockInterval));

const toggleProfileMenu = () => console.log("TODO: Profile menu");
</script>

<style scoped>
/* Topbar Container */
.wm-topbar {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-light);
  height: var(--os-topbar-height);
}

/* Inner Container - Zentriert mit Padding */
.topbar-inner {
  max-width: 1920px;
  margin: 0 auto;
  height: 100%;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

/* Left Section */
.topbar-section-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-shrink: 0;
}

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
  padding: 0.5rem;
  border-radius: 0.5rem;
  color: var(--color-text-secondary);
  transition: all 200ms;
}

.mobile-menu-btn:hover {
  color: var(--color-accent-primary);
  background: rgba(255, 255, 255, 0.05);
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* Brand Container */
.brand-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Logo Wrapper */
.logo-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  opacity: 0.9;
  transition: opacity 200ms;
}

.logo-image:hover {
  opacity: 1;
}

.logo-fallback {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
  background: rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.15);
  color: var(--color-accent-primary);
  font-size: 0.875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Brand Name */
.brand-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  letter-spacing: -0.01em;
  transition: color 200ms;
}

.brand-container:hover .brand-name {
  color: var(--color-text-primary);
}

/* Center Title */
.topbar-title {
  flex: 1;
  text-align: center;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

/* Right Section */
.topbar-section-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-shrink: 0;
}

/* Time Display */
.time-display {
  display: none;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--color-border-light);
  border-radius: 0.625rem;
  cursor: default;
  transition: all 200ms;
}

.time-display:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--color-accent-primary);
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
  flex-shrink: 0;
}

.time-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}

.date-text {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  padding-left: 0.75rem;
  border-left: 1px solid var(--color-border-light);
}

/* Profile Button */
.profile-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-light);
  background: rgba(255, 255, 255, 0.03);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 200ms;
}

.profile-btn:hover {
  border-color: var(--color-accent-primary);
  background: rgba(var(--color-accent-primary-rgb, 99, 102, 241), 0.1);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.profile-btn:active {
  transform: translateY(0);
}

/* Responsive */
@media (max-width: 1200px) {
  .topbar-inner {
    padding: 0 1.5rem;
  }
}

@media (max-width: 768px) {
  .topbar-inner {
    padding: 0 1rem;
    gap: 1rem;
  }

  .brand-name {
    display: none;
  }

  .topbar-title {
    font-size: 0.9375rem;
  }
}

@media (max-width: 640px) {
  .time-display {
    display: none;
  }
}

/* Dark Mode Enhancements */
@media (prefers-color-scheme: dark) {
  .wm-topbar {
    background: rgba(0, 0, 0, 0.3);
  }

  .time-display {
    background: rgba(255, 255, 255, 0.02);
  }

  .profile-btn {
    background: rgba(255, 255, 255, 0.02);
  }
}
</style>
