<template>
  <aside class="os-sidebar fixed left-0 top-0 h-full flex flex-col py-4 px-3 z-40">
    <!-- Logo / Header -->
    <div class="flex items-center gap-2 mb-6 px-2">
      <img :src="logo" alt="WorkmateOS" class="w-8 h-8 opacity-90" />
      <span class="text-text-secondary text-sm font-semibold">WorkmateOS</span>
    </div>

    <!-- Navigation Items -->
    <nav class="flex flex-col gap-1">
      <button
        v-for="item in navItems"
        :key="item.label"
        @click="navigate(item.to)"
        class="flex items-center gap-3 px-3 py-2 rounded-md text-left transition-all duration-150 hover:bg-[rgba(255,255,255,0.06)] hover:text-white"
        :class="{ 'bg-[rgba(255,255,255,0.1)] text-white': isActive(item.to) }"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span class="text-sm">{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import { Users, Briefcase, Timer, Receipt, Wallet, MessageSquare } from "lucide-vue-next";
import { WorkmateAssets } from "../../services/assets";

const router = useRouter();
const route = useRoute();

const logo = WorkmateAssets.workmateWhite;

const navigate = (to: string) => {
  router.push(to);
};

const isActive = (path: string) => route.path.startsWith(path);

const navItems = [
  { label: "CRM", icon: Users, to: "/backoffice/crm" },
  { label: "Projects", icon: Briefcase, to: "/backoffice/projects" },
  { label: "Time Tracking", icon: Timer, to: "/backoffice/time-tracking" },
  { label: "Invoices", icon: Receipt, to: "/backoffice/invoices" },
  { label: "Finance", icon: Wallet, to: "/backoffice/finance" },
  { label: "Notes", icon: MessageSquare, to: "/backoffice/chat" }
];
</script>

<style scoped>
.os-sidebar {
  background: rgba(255, 255, 255, 0.03);
  border-right: 1px solid var(--color-border-light);
  backdrop-filter: blur(12px);
}
</style>
