<template>
  <header class="wm-topbar">
    <div class="topbar-inner">

      <!-- LEFT -->
      <div class="topbar-left">
        <div class="brand-container">
          <div class="logo-wrapper">
            <img
              v-if="logo"
              :src="logo"
              class="logo-image"
              @error="handleLogoError"
            />
            <div v-else class="logo-fallback">W</div>
          </div>

          <span class="brand-name">WorkmateOS</span>
        </div>
      </div>

      <!-- CENTER TITLE (always centered, never shifts) -->
      <div class="topbar-title">
        {{ title }}
      </div>

      <!-- RIGHT -->
      <div class="topbar-right">
        <div class="time-display" :title="fullDate">
            <svg class="time-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>

            <div class="time-stack">
              <span class="time-text">{{ time }}</span>
              <span class="date-text">{{ shortDate }}</span>
            </div>
          </div>

        <button class="profile-btn" @click="toggleProfileMenu">
          <UserIcon class="w-4 h-4" />
        </button>
      </div>

    </div>
  </header>
</template>


<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { User as UserIcon } from "lucide-vue-next";
import { WorkmateAssets } from "@/services/assets";

interface Props {
  title?: string;
}
defineProps<Props>();

const logo = ref<string | null>(WorkmateAssets.workmateFavicon);
const handleLogoError = () => (logo.value = null);

const time = ref("");
const shortDate = ref("");
const fullDate = ref("");

const updateClock = () => {
  const now = new Date();
  time.value = now.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
  shortDate.value = now.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" });
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
/* ----------------------------------------------
   TOPBAR ROOT
---------------------------------------------- */
.wm-topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;

  height: var(--os-topbar-height);

  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  display: flex;
  align-items: center;
  z-index: 99;
}

/* ----------------------------------------------
   FLEX REGION (Left – Center – Right)
---------------------------------------------- */
.topbar-inner {
  width: 100%;
  height: 100%;
  display: flex;

  /* verhindert jegliches Umbruch-Chaos */
  align-items: center;
  justify-content: space-between;

  padding: 0 1.25rem;
  position: relative;
  overflow: hidden;
}

/* ----------------------------------------------
   LEFT SECTION
---------------------------------------------- */
.topbar-left {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

/* Brand */
.brand-container {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.logo-wrapper {
  width: 28px;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
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
  background: rgba(255, 145, 0, 0.15);
  color: var(--color-accent-primary);
  font-weight: 700;
  display: flex;
  justify-content: center;
  align-items: center;
}

.brand-name {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
}

/* ----------------------------------------------
   CENTER TITLE (always perfectly centered)
---------------------------------------------- */
.topbar-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);

  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;

  pointer-events: none; /* verhindert Klickblockade */
}

/* ----------------------------------------------
   RIGHT SECTION
---------------------------------------------- */
.topbar-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Profile button */
.profile-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 0.6rem;

  border: 1px solid rgba(255,255,255,0.075);
  background: rgba(255,255,255,0.05);

  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  transition: 0.2s;
}
.profile-btn:hover {
  background: rgba(255,145,0,0.15);
  border-color: var(--color-accent-primary);
}

/* ----------------------------------------------
   TIME DISPLAY
---------------------------------------------- */
/* CLOCK CONTAINER */
.time-display {
  display: flex;
  align-items: center;
  gap: 0.6rem;

  padding: 0.4rem 0.9rem;
  border-radius: 0.65rem;

  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);

  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);

  white-space: nowrap;
}

/* Icon kleiner & ruhiger */
.time-icon {
  width: 1rem;
  height: 1rem;
  opacity: 0.85;
  color: var(--color-accent-primary);
}

/* STACKED TIME + DATE */
.time-stack {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.1;
}


/* Zeit fokussiert */
.time-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}
.date-text::before {
  content: "";
  display: block;
  width: 12px;
  height: 1px;
  margin: 2px 0 4px;
  background: rgba(255,145,0,0.35);
  border-radius: 2px
}
/* Datum dezent */
.date-text {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

/* Mobile: Clock ausblenden */
@media (max-width: 900px) {
  .time-display {
    display: none;
  }
}

/* Clock hides cleanly on smaller screens */
@media (max-width: 900px) {
  .time-display {
    display: none;
  }
}

/* ----------------------------------------------
   MOBILE RESPONSIVE
---------------------------------------------- */
@media (max-width: 768px) {
  .brand-name {
    display: none;
  }

  .topbar-inner {
    padding: 0 0.75rem;
  }
}

@media (max-width: 480px) {
  .profile-btn {
    width: 1.8rem;
    height: 1.8rem;
  }
}
</style>
