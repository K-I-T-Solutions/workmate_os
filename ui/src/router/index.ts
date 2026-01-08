import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";
import CrmApp from "@/modules/crm/CrmApp.vue";
import HRApp from "@/modules/hr/HRApp.vue";
import LoginPage from "@/pages/LoginPage.vue";
import { useAuth } from "@/composables/useAuth";

const routes = [
  // Redirect root to app
  { path: "/", redirect: "/app" },

  // Login Page (Public)
  {
    path: "/login",
    name: "login",
    component: LoginPage,
    meta: { requiresAuth: false },
  },

  // Auth Callback (Public)
  {
    path: "/auth/callback",
    name: "auth-callback",
    component: () => import("@/pages/AuthCallbackPage.vue"),
    meta: { requiresAuth: false },
  },

  // Main App (Protected)
  {
    path: "/app",
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/app/dashboard",
      },
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
      },
      {
        path: "hr",
        name: "hr",
        component: HRApp,
      }
    ],
  },

  // Public Pages
  {
    path: "/under-construction",
    component: () => import("@/pages/UnderConstruction.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/linktree",
    component: () => import("@/pages/Linktree.vue"),
    meta: { requiresAuth: false },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Auth Guard
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, initializeAuth, fetchCurrentUser } = useAuth();

  // Initialize auth from localStorage
  if (!isAuthenticated.value) {
    initializeAuth();
  }

  // Check if route requires auth
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false);

  if (requiresAuth) {
    if (!isAuthenticated.value) {
      // Not authenticated, redirect to login
      next({ name: 'login', query: { redirect: to.fullPath } });
    } else {
      // Authenticated, verify token is still valid
      // (Only check on route change, not every navigation)
      if (from.path === '/login') {
        await fetchCurrentUser();
      }
      next();
    }
  } else {
    // Public route
    if (to.name === 'login' && isAuthenticated.value) {
      // Already logged in, redirect to app
      next({ path: '/app' });
    } else {
      next();
    }
  }
});
