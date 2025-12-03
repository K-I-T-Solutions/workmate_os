import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";

const routes = [
  { path: "/", redirect: "/under-construction" },

  {
    path: "/app",
    component: AppLayout,
    children: [
      // Dashboard
      {
        path: "dashboard",
        name: "dashboard",
        component: () => import("@/modules/dashboard/pages/DashboardPage.vue"),
      },

      // CRM
      {
        path: "crm",
        children: [
          {
            path: "",
            name: "crm-root",
            component: () =>
              import("@/modules/crm/pages/CustomersListPage.vue"),
          },
          {
            path: "customers",
            name: "crm-customers",
            component: () =>
              import("@/modules/crm/pages/CustomersListPage.vue"),
          },
          {
            path: "customers/:customerId",
            name: "crm-customer-detail",
            component: () =>
              import("@/modules/crm/pages/CustomerDetailPage.vue"),
          },
          {
            path: "customers/:customerId/contacts",
            name: "crm-contacts",
            component: () =>
              import("@/modules/crm/pages/ContactsListPage.vue"),
          },
          {
            path: "customers/:customerId/contacts/:contactId",
            name: "crm-contact-detail",
            component: () =>
              import("@/modules/crm/pages/ContactDetailPage.vue"),
          },
        ],
      },
    ],
  },

  // Public Pages
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
