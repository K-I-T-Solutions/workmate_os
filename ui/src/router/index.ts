import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";
import CrmApp from "@/modules/crm/CrmApp.vue";

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
          import("@/modules/dashboard/pages/DashboardPage.vue"),
      },
      {
        path: "crm",
        name: "crm",
        component: CrmApp,
      }
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
