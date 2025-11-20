<template>
  <div
    class="os-dock fixed bottom-0 left-0 w-full flex items-center justify-center gap-6 py-2 z-50"
  >
    <div
      v-for="item in dockItems"
      :key="item.label"
      @click="navigate(item.to)"
      class="flex flex-col items-center justify-center cursor-pointer transition-all duration-200"
    >
      <div
        class="p-3 rounded-xl bg-[rgba(255,255,255,0.06)] backdrop-blur-md border border-[rgba(255,255,255,0.1)] hover:border-accent-primary hover:scale-110 shadow-soft"
      >
        <component :is="item.icon" class="w-6 h-6 text-white" />
      </div>
      <span class="text-[12px] text-text-secondary mt-1">{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import {
  Briefcase,
  Users,
  Timer,
  Receipt,
  Wallet,
  MessageSquare,
} from "lucide-vue-next";

const router = useRouter();

const navigate = (to: string) => {
  router.push(to);
};

const dockItems = [
  { label: "CRM", icon: Users, to: "/backoffice/crm" },
  { label: "Projects", icon: Briefcase, to: "/backoffice/projects" },
  { label: "Time", icon: Timer, to: "/backoffice/time-tracking" },
  { label: "Invoices", icon: Receipt, to: "/backoffice/invoices" },
  { label: "Finance", icon: Wallet, to: "/backoffice/finance" },
  { label: "Notes", icon: MessageSquare, to: "/backoffice/chat" },
];
</script>

<style scoped>
.os-dock {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--color-border-light);
}
</style>
