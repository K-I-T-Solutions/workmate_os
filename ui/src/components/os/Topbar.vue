<template>
  <header class="os-topbar fixed top-0 left-0 w-full z-50 flex items-center justify-between px-4">
    <!-- Left Section -->
    <div class="flex items-center gap-3">
      <img :src="logo" alt="WorkmateOS" class="w-6 h-6 opacity-90" />
      <span class="text-sm font-semibold text-text-secondary">WorkmateOS</span>
    </div>

    <!-- Center Section (Optional: Dynamic Title) -->
    <div class="text-text-secondary text-sm" v-if="title">
      {{ title }}
    </div>

    <!-- Right Section -->
    <div class="flex items-center gap-4">
      <!-- Time -->
      <span class="text-sm text-white font-medium">{{ time }}</span>

      <!-- Profile Icon -->
      <div
        class="w-8 h-8 rounded-full bg-[rgba(255,255,255,0.1)] flex items-center justify-center border border-[rgba(255,255,255,0.15)] text-white cursor-pointer hover:border-accent-primary transition"
      >
        <component :is="UserIcon" class="w-4 h-4" />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { WorkmateAssets } from "../../services/assets";
import { User as UserIcon } from "lucide-vue-next";

interface Props {
  title?: string;
}

const props = defineProps<Props>();

const logo = WorkmateAssets.workmateWhite;

// Clock
const time = ref("");
const updateClock = () => {
  const now = new Date();
  time.value = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

onMounted(() => {
  updateClock();
  setInterval(updateClock, 60000);
});
</script>

<style scoped>
.os-topbar {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border-light);
}
</style>
