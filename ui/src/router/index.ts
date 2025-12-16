import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";

const routes = [
  { path: "/", redirect: "/under-construction" },

  {
    path: "/app",
    component: AppLayout,
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: () =>
          import("@/modules/dashboard/DashboardApp.vue"),
      },
      {
        path: "crm",
        name: "crm",
        component: () =>
          import("@/modules/crm/CrmApp.vue"),
      },
      {
        path: "finance",
        name: "finance",
        component: () =>
          import("@/modules/finance/FinanceApp.vue"),
      },
    ],
  },

  // Public
  {
    path: "/under-construction",
    component: () => import("@/pages/UnderConstruction.vue"),
  },
  {
    path: "/linktree",
    component: () => import("@/pages/Linktree.vue"),
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
