import { createRouter, createWebHistory } from "vue-router";
import UnderConstruction from "../pages/UnderConstruction.vue";
import Linktree from "../pages/Linktree.vue";
import MainPage from "../pages/MainPage.vue";
import CustomersPage from "../pages/backoffice/crm/CustomersPage.vue";
import CustomerDetailPage from "../pages/backoffice/crm/CustomerDetailPage.vue";

const routes = [
  { path: "/", redirect: "/under-construction" },
  { path: "/under-construction", component: UnderConstruction },
  { path: "/linktree", component: Linktree },
  { path: "/main", component: MainPage },
  { path: "/backoffice/crm/", name: "crm", component: CustomersPage },
  {
    path: "/backoffice/crm/customer/:customerId",
    name: "customer-detail",
    component: CustomerDetailPage,
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
