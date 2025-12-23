# WorkmateOS Frontend/UI Architecture Guide

## Overview

The WorkmateOS frontend is a Vue 3 + TypeScript + Vite-based application using a **modular architecture** with a unique desktop-like window manager system. The application is organized into independent modules (CRM, Dashboard, etc.) that can be opened as floating windows within the main application.

---

## 1. Overall Directory Structure

```
ui/src/
├── main.ts                          # Entry point
├── App.vue                          # Root component
├── style.css                        # Global styles
│
├── router/
│   └── index.ts                     # Vue Router configuration
│
├── layouts/
│   ├── AppLayout.vue                # Main layout (topbar + dock + window host)
│   ├── app-manager/
│   │   ├── appRegistry.ts           # Central app registration
│   │   ├── useAppManager.ts         # Window manager logic
│   │   ├── WindowHost.vue           # Container for all windows
│   │   ├── WindowFrame.vue          # Individual window wrapper
│   │   └── index.ts                 # Exports
│   └── components/
│       ├── Topbar.vue               # Top navigation bar
│       ├── Dock.vue                 # Bottom app dock
│       └── index.ts                 # Exports
│
├── modules/
│   ├── crm/                         # CRM Module
│   │   ├── CrmApp.vue               # Module entry component
│   │   ├── pages/                   # Page components
│   │   │   ├── dashboard/
│   │   │   │   └── CrmDashboardPage.vue
│   │   │   ├── customer/
│   │   │   │   ├── CustomersListPage.vue
│   │   │   │   └── CustomerDetailPage.vue
│   │   │   ├── contacts/
│   │   │   │   ├── ContactsListPage.vue
│   │   │   │   └── ContactDetailPage.vue
│   │   │   └── index.ts             # Page exports
│   │   ├── components/
│   │   │   ├── customer/
│   │   │   │   ├── CustomerCard.vue
│   │   │   │   └── CustomerForm.vue
│   │   │   ├── contacts/
│   │   │   │   ├── ContactCard.vue
│   │   │   │   └── ContactForm.vue
│   │   │   ├── widgets/
│   │   │   │   ├── CrmKpiCustomers.vue
│   │   │   │   ├── CrmRecentActivity.vue
│   │   │   │   ├── CrmShortcuts.vue
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── composables/
│   │   │   ├── useCrmNavigation.ts   # Navigation state management
│   │   │   ├── useCrmStats.ts        # Statistics logic
│   │   │   └── useCrmActivity.ts     # Activity management
│   │   ├── services/
│   │   │   └── crm.service.ts        # API calls
│   │   └── types/
│   │       ├── customer.ts
│   │       ├── contact.ts
│   │       ├── activity.ts
│   │       └── stats.ts
│   │
│   └── dashboard/
│       ├── pages/
│       │   └── DashboardPage.vue
│       ├── components/
│       │   ├── WidgetRenderer.vue
│       │   └── widgets/
│       │       ├── StatsWidget.vue
│       │       ├── RemindersWidget.vue
│       │       ├── ShortcutsWidget.vue
│       │       ├── ActivityFeedWidget.vue
│       │       ├── NotificationsWidget.vue
│       │       ├── CalendarWidget.vue
│       │       ├── WeatherWidget.vue
│       │       ├── ChartWidget.vue
│       │       ├── SystemMonitorWidget.vue
│       │       └── index.ts
│       ├── services/
│       │   └── widgetRegistry.ts     # Widget registration
│       └── types/
│           └── widgetTypes.ts        # Type definitions
│
├── services/
│   ├── api/
│   │   └── client.ts                # Axios API client
│   └── assets.ts                    # Asset paths
│
├── composables/
│   ├── useDashboard.ts              # Global dashboard logic
│   ├── useEmployees.ts
│   ├── useProjects.ts
│   └── useInvocies.ts
│
├── styles/
│   ├── tokens.css                   # Design tokens (colors, spacing, etc)
│   ├── base.css                     # Global styles
│   └── components/
│       ├── button.css
│       └── kit-components.css
│
├── pages/                           # Global pages
│   ├── UnderConstruction.vue
│   └── Linktree.vue
│
└── assets/
    └── [images, fonts, etc]
```

---

## 2. Application Bootstrap Flow

### main.ts
```typescript
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import { router } from "./router/index.ts";

const pinia = createPinia();

createApp(App)
  .use(pinia)
  .use(router)
  .mount("#app");
```

**Key Points:**
- Pinia is initialized for state management (currently not heavily used)
- Vue Router manages global routing
- App.vue is the root component

### App.vue (Root Component)
```vue
<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>
```

Simple root that delegates to router.

---

## 3. Router Configuration (router/index.ts)

The router uses two main routes:

```typescript
const routes = [
  // Default redirect
  { path: "/", redirect: "/under-construction" },

  // Main app layout with modules
  {
    path: "/app",
    component: AppLayout,
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: () => import("@/modules/dashboard/pages/DashboardPage.vue"),
      },
      {
        path: "crm",
        name: "crm",
        component: CrmApp,  // Module entry point
      }
    ],
  },

  // Public routes
  {
    path: "/under-construction",
    component: () => import("@/pages/UnderConstruction.vue"),
  },
  {
    path: "/linktree",
    component: () => import("@/pages/Linktree.vue"),
  },
];
```

**Pattern:** Child routes are lazy-loaded, except CrmApp which is imported directly.

---

## 4. Module System Architecture

### Module Registration (appRegistry.ts)

Central registry for all modules:

```typescript
import { markRaw } from "vue";
import { icons } from "lucide-vue-next";
import CrmApp from "@/modules/crm/CrmApp.vue";

export const apps = [
  {
    id: "crm",
    title: "CRM",
    icons: markRaw(icons.Users),
    component: markRaw(CrmApp),
    window: {
      width: 1100,
      height: 700
    }
  },
  // More apps here...
];
```

**Key Points:**
- Uses `markRaw()` to prevent Vue reactivity overhead
- Each app has an `id`, `title`, `icon`, `component`, and default window size
- This is used by the window manager to open apps

### Window Manager (useAppManager.ts)

Reactive state management for windows:

```typescript
export interface WindowApp {
  id: string;              // Unique window instance ID
  appId: string;           // Reference to app registry
  title: string;
  component: Component;
  props?: Record<string, any>;
  x: number; y: number;    // Position
  width: number;
  height: number;
  z: number;               // Z-index for layering
}

export const appManager = {
  windows,          // Reactive array of open windows
  activeWindow,     // Currently focused window

  openWindow(appId),    // Open an app
  closeWindow(id),      // Close a window
  focusWindow(id),      // Focus a window (bring to front)
  startDragFor(id, e),  // Drag handler
  startResizeFor(id, e) // Resize handler
};
```

**Key Features:**
- Multiple instances of same app can be open
- Windows are draggable and resizable
- Z-index managed for proper layering
- Position/size constrained to viewport

---

## 5. Module Structure Pattern - CRM Module Example

### Module Entry Point (CrmApp.vue)

Acts as a router/container for the module:

```vue
<script setup lang="ts">
import { 
  CrmDashboardPage,
  CustomersListPage,
  CustomerDetailPage,
  ContactListPage,
  ContactDetailPage,
} from "./pages";
import { useCrmNavigation } from "./composables/useCrmNavigation";

const {
  view,
  activeCustomerId,
  activeContactId,
  goDashboard,
  goCustomers,
  goCustomerDetail,
  goContacts,
  goContactDetail,
  openCreateContact,
  openCreateCustomer
} = useCrmNavigation();
</script>

<template>
  <div class="crm-app h-full">
    <!-- Conditional rendering based on view state -->
    <CrmDashboardPage
      v-if="view === 'dashboard'"
      @openCustomers="goCustomers"
      @create-customer="openCreateCustomer"
      @create-contact="openCreateContact"
    />

    <CustomersListPage
      v-if="view === 'customers'"
      @openCustomer="goCustomerDetail"
      @openDashboard="goDashboard"
    />

    <!-- More views... -->
  </div>
</template>
```

**Pattern:**
- Module has internal routing using composable-based state
- No Vue Router child routes (self-contained)
- View switching via conditional rendering

### Navigation Composable (useCrmNavigation.ts)

Internal state management for module views:

```typescript
export type CrmView =
  | "dashboard"
  | "customers"
  | "customer-detail"
  | "contacts"
  | "contact-detail"
  | "customer-create"
  | "contact-create";

export function useCrmNavigation() {
  const view = ref<CrmView>("dashboard");
  const activeCustomerId = ref<string | null>(null);
  const activeContactId = ref<string | null>(null);

  function goDashboard() {
    view.value = "dashboard";
    activeCustomerId.value = null;
    activeContactId.value = null;
  }

  function goCustomers() {
    view.value = "customers";
    activeCustomerId.value = null;
  }

  // ... more navigation functions

  return {
    view,
    activeCustomerId,
    activeContactId,
    goDashboard,
    goCustomers,
    // ... more exports
  };
}
```

**Pattern:**
- Pure composable with no dependencies on Vue Router
- References passed via composable, not route params
- Used throughout module for navigation

### API Service Layer (crm.service.ts)

Centralized API calls:

```typescript
import api from "@/services/api/client";

export const crmService = {
  // Customers
  async getCustomers(): Promise<Customer[]> {
    const { data } = await api.get("/api/backoffice/crm/customers");
    return data;
  },

  async getCustomer(id: string): Promise<Customer> {
    const { data } = await api.get(`/api/backoffice/crm/customers/${id}`);
    return data;
  },

  async createCustomer(payload: Partial<Customer>) {
    return api.post("/api/backoffice/crm/customers", payload);
  },

  // Contacts
  async getContacts(): Promise<Contact[]> {
    const { data } = await api.get("/api/backoffice/crm/contacts");
    return data;
  },

  // Activities
  async getLatestActivities(limit: number): Promise<CrmActivity[]> {
    const { data } = await api.get(`/api/backoffice/crm/activities/latest?limit=${limit}`);
    return data;
  },

  // Stats
  async getCrmStats(): Promise<CrmStats> {
    const { data } = await api.get("/api/backoffice/crm/stats");
    return data;
  }
};
```

**Pattern:**
- Service object with static methods
- Uses shared axios client
- Returns Promise<T> for proper typing
- Handles URL construction and parameters

### Data Fetching Composable (useCrmStats.ts)

Loading state + service integration:

```typescript
export function useCrmStats() {
  const stats = ref<CrmStats | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchStats() {
    loading.value = true;
    error.value = null;

    try {
      const data = await crmService.getCrmStats();
      stats.value = data;
    } catch (e: any) {
      error.value = e.message ?? "Failed to load stats";
    } finally {
      loading.value = false;
    }
  }

  return {
    stats,
    loading,
    error,
    fetchStats,
  };
}
```

**Pattern:**
- Wraps service calls
- Manages loading/error states
- Returns reactive ref + fetch function
- Used in components via `const { stats, loading } = useCrmStats()`

### Page Components (CustomersListPage.vue)

```vue
<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-white">Kundenliste</h1>
      <button class="kit-btn-primary" @click="openCreateModal">
        + Neuer Kunde
      </button>
    </div>

    <!-- Search/Filter -->
    <input v-model="search" type="text" placeholder="Kunde suchen…" />

    <!-- Grid -->
    <div class="grid grid-cols-4 gap-2">
      <div
        v-for="c in pagedCustomers"
        :key="c.id"
        @click="openCustomer(c.id)"
      >
        {{ c.name }}
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between">
      <button :disabled="page === 1" @click="page--">← Zurück</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page === totalPages" @click="page++">Weiter →</button>
    </div>

    <CustomerForm v-if="showModal" @close="showModal = false" @saved="reload" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { crmService } from "../../services/crm.service";

const emit = defineEmits<{
  (e: "openCustomer", id: string): void;
  (e: "openDashboard"): void;
}>();

const customers = ref<Customer[]>([]);
const search = ref("");
const page = ref(1);
const pageSize = 8;

async function load() {
  customers.value = await crmService.getCustomers();
}

onMounted(load);

const filtered = computed(() =>
  customers.value.filter(c =>
    c.name.toLowerCase().includes(search.value.toLowerCase())
  )
);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filtered.value.length / pageSize))
);

const pagedCustomers = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filtered.value.slice(start, start + pageSize);
});

function openCustomer(id: string) {
  emit("openCustomer", id);
}
</script>
```

**Pattern:**
- Page emits events to parent (CrmApp.vue)
- Uses composables for logic
- Handles its own local state (search, pagination)
- Service calls in onMounted
- Computed for filtering/pagination

### Type Definitions (types/customer.ts)

```typescript
export interface Customer {
  id: string;
  customer_number: string | null;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  zip: string | null;
  city: string | null;
  country: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

**Pattern:**
- All module types in dedicated `types/` folder
- Exported interfaces, not classes
- Nullable fields marked with `| null`
- ISO date strings for dates

### Component Barrel Exports (components/index.ts)

```typescript
// Cards
export { default as ContactCard } from "./contacts/ContactCard.vue";
export { default as CustomerCard } from "./customer/CustomerCard.vue";

// Forms
export { default as ContactForm } from "./contacts/ContactForm.vue";
export { default as CustomerForm } from "./customer/CustomerForm.vue";

// Widgets
export * from "./widgets";
```

**Pattern:**
- All components exported from index
- Enables `import { CustomerForm } from "../../components"`

---

## 6. API Client Setup (services/api/client.ts)

Centralized Axios instance:

```typescript
import axios, { type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request Interceptor (JWT token would go here)
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Add JWT token
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor (Error Handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Global error handling (401, 403, 404, 500, etc)
    return Promise.reject(error);
  }
);

export default apiClient;
```

**Usage in Services:**
```typescript
const { data } = await api.get("/api/backoffice/crm/customers");
```

**Features:**
- Single instance shared across app
- Base URL from environment
- Ready for JWT interceptor
- Centralized error handling

---

## 7. Layout System (AppLayout.vue)

Main container with topbar, window host, and dock:

```vue
<template>
  <div class="w-screen h-screen overflow-hidden flex flex-col bg-bg-primary">
    <!-- Topbar -->
    <KitTopbar />

    <!-- Main Window Area -->
    <div class="flex flex-1 overflow-hidden">
      <WindowHost class="flex-1" />
    </div>

    <!-- Dock (Bottom) -->
    <KitDock />
  </div>
</template>
```

### Dock Component (Dock.vue)

Bottom navigation bar for opening apps:

```vue
<script setup lang="ts">
const dockItems = [
  { id: "crm", label: "CRM", icon: markRaw(Users) },
  { id: "projects", label: "Projects", icon: markRaw(Briefcase) },
  { id: "time", label: "Time", icon: markRaw(Timer) },
  // More items...
];

function openApp(appId: string) {
  openWindow(appId);
}

const isActive = (appId: string) => {
  const winId = activeWindow.value;
  return windows.some(w => w.id === winId && w.appId === appId);
};
</script>
```

**Features:**
- Uses lucide-vue-next icons (markRaw for performance)
- Integrates with useAppManager
- Shows active state when app window is open
- Responsive design (hidden on mobile)

### Window Host (WindowHost.vue)

Container for all floating windows:

```vue
<template>
  <div class="window-host">
    <WindowFrame
      v-for="w in windows"
      :key="w.id"
      :win="w"
    >
      <!-- App component rendered here -->
      <component :is="resolveComponent(w.appId)" v-bind="w.props" />
    </WindowFrame>
  </div>
</template>
```

### Window Frame (WindowFrame.vue)

Individual window wrapper with titlebar, resize handle:

```vue
<template>
  <div class="window-frame" :style="frameStyleString" @mousedown="focus">
    <!-- Titlebar (draggable) -->
    <div class="window-titlebar" @mousedown.stop="startDrag">
      <span>{{ win.title }}</span>
      <button @click.stop="close">✕</button>
    </div>

    <!-- Content -->
    <div class="window-content">
      <slot />
    </div>

    <!-- Resize handle -->
    <div class="resize-handle" @mousedown.stop="startResize" />
  </div>
</template>
```

**Features:**
- Positioned absolutely with dynamic x, y, width, height
- Draggable titlebar
- Resizable via corner handle
- Close button
- Focus on click (z-index management)

---

## 8. State Management (Pinia)

Currently Pinia is set up but **minimally used**. The app relies on:
- **Composables** for local state (useCrmNavigation, useCrmStats, etc)
- **Service layer** for API calls
- **Reactive refs** for component state

**When to add a Pinia store:**
- Global app state (user, auth, theme)
- Shared state across multiple modules
- Complex state transitions

---

## 9. Styling System

### Design Tokens (styles/tokens.css)

CSS custom properties for consistency:

```css
:root {
  /* Colors */
  --color-bg-primary: #232223;
  --color-accent-primary: #ff9100;
  --color-text-primary: #ffffff;
  --color-text-secondary: rgba(255, 255, 255, 0.7);
  --color-border-light: rgba(255, 255, 255, 0.1);

  /* Typography */
  --font-primary: "Fira Sans", sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Layout */
  --os-dock-height: 80px;
  --os-topbar-height: 48px;
}
```

### Tailwind CSS

Uses Tailwind v4 with `@tailwindcss/vite` plugin:

```vue
<div class="px-6 py-4 bg-white/5 border border-white/10 rounded-lg">
  <h2 class="text-lg font-semibold text-white">Title</h2>
</div>
```

**Classes used throughout:**
- `bg-bg-primary`, `bg-bg-secondary`
- `text-white`, `text-white/70`
- `border-white/10`
- Grid layouts: `grid grid-cols-4 gap-2`
- Flex: `flex items-center justify-between`

### Component Styles (styles/components/)

```css
/* button.css */
.kit-btn-primary {
  @apply px-4 py-2 bg-accent-primary rounded hover:opacity-80;
}

.kit-btn-accent {
  @apply px-4 py-2 bg-white/10 rounded hover:bg-white/20;
}

.kit-input {
  @apply px-3 py-2 bg-white/5 border border-white/10 rounded;
}

.kit-label {
  @apply block text-sm font-medium text-white/70 mb-1;
}
```

---

## 10. Creating a New Module - Step by Step

### Step 1: Create Module Structure

```
ui/src/modules/mymodule/
├── MyModuleApp.vue           # Entry point
├── pages/
│   ├── MyPage.vue
│   └── index.ts
├── components/
│   ├── MyComponent.vue
│   └── index.ts
├── composables/
│   └── useMyModuleNav.ts
├── services/
│   └── mymodule.service.ts
└── types/
    └── mymodule.ts
```

### Step 2: Create Type Definitions (types/mymodule.ts)

```typescript
export interface MyResource {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}
```

### Step 3: Create Service Layer (services/mymodule.service.ts)

```typescript
import api from "@/services/api/client";
import type { MyResource } from "../types/mymodule";

export const mymoduleService = {
  async getResources(): Promise<MyResource[]> {
    const { data } = await api.get("/api/mymodule/resources");
    return data;
  },

  async getResource(id: string): Promise<MyResource> {
    const { data } = await api.get(`/api/mymodule/resources/${id}`);
    return data;
  },

  async createResource(payload: Partial<MyResource>) {
    return api.post("/api/mymodule/resources", payload);
  },
};
```

### Step 4: Create Navigation Composable (composables/useMyModuleNav.ts)

```typescript
import { ref } from "vue";

export type MyModuleView = "list" | "detail" | "create";

export function useMyModuleNav() {
  const view = ref<MyModuleView>("list");
  const activeResourceId = ref<string | null>(null);

  function goList() {
    view.value = "list";
    activeResourceId.value = null;
  }

  function goDetail(resourceId: string) {
    activeResourceId.value = resourceId;
    view.value = "detail";
  }

  function goCreate() {
    view.value = "create";
    activeResourceId.value = null;
  }

  return {
    view,
    activeResourceId,
    goList,
    goDetail,
    goCreate,
  };
}
```

### Step 5: Create Pages

```vue
<!-- pages/ResourceListPage.vue -->
<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <h1 class="text-2xl font-semibold text-white">Resources</h1>
    
    <button class="kit-btn-primary" @click="openCreate">
      + New Resource
    </button>

    <div class="grid grid-cols-4 gap-2">
      <div
        v-for="r in resources"
        :key="r.id"
        @click="openDetail(r.id)"
        class="p-3 bg-white/5 rounded border border-white/10"
      >
        {{ r.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { mymoduleService } from "../../services/mymodule.service";

const emit = defineEmits<{
  (e: "openDetail", id: string): void;
  (e: "openCreate"): void;
}>();

const resources = ref([]);

onMounted(async () => {
  resources.value = await mymoduleService.getResources();
});

function openDetail(id: string) {
  emit("openDetail", id);
}

function openCreate() {
  emit("openCreate");
}
</script>
```

### Step 6: Create Module Entry Point (MyModuleApp.vue)

```vue
<script setup lang="ts">
import { ResourceListPage } from "./pages";
import { useMyModuleNav } from "./composables/useMyModuleNav";

const { view, activeResourceId, goList, goDetail, goCreate } = useMyModuleNav();
</script>

<template>
  <div class="mymodule-app h-full">
    <ResourceListPage
      v-if="view === 'list'"
      @openDetail="goDetail"
      @openCreate="goCreate"
    />
  </div>
</template>
```

### Step 7: Register Module (layouts/app-manager/appRegistry.ts)

```typescript
import MyModuleApp from "@/modules/mymodule/MyModuleApp.vue";

export const apps = [
  {
    id: "crm",
    title: "CRM",
    icons: markRaw(icons.Users),
    component: markRaw(CrmApp),
    window: { width: 1100, height: 700 }
  },
  {
    id: "mymodule",
    title: "My Module",
    icons: markRaw(icons.Package),
    component: markRaw(MyModuleApp),
    window: { width: 900, height: 600 }
  },
];
```

### Step 8: Add Dock Item (layouts/components/Dock.vue)

```typescript
const dockItems = [
  { id: "crm", label: "CRM", icon: markRaw(Users) },
  { id: "mymodule", label: "Module", icon: markRaw(Package) }, // Add here
  { id: "projects", label: "Projects", icon: markRaw(Briefcase) },
];
```

### Step 9 (Optional): Add Route (router/index.ts)

For landing page or standalone route:

```typescript
{
  path: "/app",
  component: AppLayout,
  children: [
    {
      path: "mymodule",
      name: "mymodule",
      component: () => import("@/modules/mymodule/MyModuleApp.vue"),
    },
  ],
}
```

---

## 11. Common Patterns & Best Practices

### Pattern: Service + Composable

**Service handles HTTP:**
```typescript
// crm.service.ts
async getCustomers(): Promise<Customer[]> {
  const { data } = await api.get("/api/crm/customers");
  return data;
}
```

**Composable handles state + error:**
```typescript
// useCrmStats.ts
export function useCrmStats() {
  const stats = ref<CrmStats | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchStats() {
    loading.value = true;
    try {
      stats.value = await crmService.getCrmStats();
    } catch (e) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  return { stats, loading, error, fetchStats };
}
```

**Component uses composable:**
```vue
<script setup>
const { stats, loading, error, fetchStats } = useCrmStats();
onMounted(fetchStats);
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error" class="text-red">{{ error }}</div>
  <div v-else>{{ stats }}</div>
</template>
```

### Pattern: Module Navigation

**Module entry uses local state, not router:**
```typescript
const { view, activeId, goList, goDetail } = useModuleNav();
```

**Parent component conditionally renders:**
```vue
<ListPage v-if="view === 'list'" @openDetail="goDetail" />
<DetailPage v-if="view === 'detail'" :id="activeId" @back="goList" />
```

**Events propagate up:**
```typescript
const emit = defineEmits<{
  (e: "openCustomer", id: string): void;
  (e: "back"): void;
}>();
```

### Pattern: Reactive Forms

**Simple v-model binding:**
```vue
<input v-model="form.name" class="kit-input" />
<input v-model="form.email" type="email" class="kit-input" />

<script setup>
const form = ref({ name: "", email: "" });
</script>
```

**Submit via service:**
```typescript
async function save() {
  loading.value = true;
  try {
    await crmService.createCustomer(form.value);
    emit("saved");
  } finally {
    loading.value = false;
  }
}
```

### Pattern: Pagination

```typescript
const page = ref(1);
const pageSize = 10;

const filtered = computed(() =>
  items.value.filter(i => i.name.includes(search.value))
);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filtered.value.length / pageSize))
);

const pagedItems = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filtered.value.slice(start, start + pageSize);
});
```

### Pattern: Modal/Form Modal

```vue
<div v-if="showModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
  <div class="bg-bg-secondary rounded-xl p-6">
    <h2>{{ isEdit ? "Edit" : "Create" }}</h2>
    
    <form @submit.prevent="save">
      <input v-model="form.name" />
      <button type="submit">Save</button>
      <button @click="close">Cancel</button>
    </form>
  </div>
</div>
```

---

## 12. Key Files to Modify When Adding a Module

1. **layouts/app-manager/appRegistry.ts** - Register app
2. **layouts/components/Dock.vue** - Add dock item
3. **router/index.ts** (optional) - Add route
4. Create module folder under `modules/`

---

## 13. Environment Setup

### .env
```
VITE_API_BASE_URL=http://localhost:8000
```

### vite.config.ts
```typescript
export default defineConfig({
  plugins: [tailwindcss(), vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
});
```

---

## 14. Building & Running

```bash
# Install dependencies
pnpm install

# Development
pnpm run dev

# Build
pnpm run build

# Preview
pnpm run preview
```

---

## 15. Technology Stack

- **Vue 3** - Framework
- **Vite** - Build tool (with rolldown-vite)
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Styling
- **Vue Router 4** - Global routing
- **Pinia 3** - State management (set up, minimally used)
- **Axios** - HTTP client
- **Lucide Vue Next** - Icons

---

## Summary

The WorkmateOS frontend uses a **modular window-based architecture** where:

1. **Modules are self-contained** with their own pages, components, services, types
2. **Composables manage local state** (navigation, data fetching)
3. **Services handle API calls** (no HTTP logic in components)
4. **Types keep everything type-safe**
5. **Window manager** allows floating windows with drag/resize
6. **Design tokens + Tailwind** provide consistent styling
7. **No complex routing** - modules use internal view switching

To add a new module: Create the folder structure → Define types → Create service → Create composables → Create pages → Create module entry point → Register in appRegistry → Add dock item.

