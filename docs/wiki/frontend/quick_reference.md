---
layout: default
title: Quick Reference
parent: Frontend
grand_parent: Wiki
nav_order: 3
---

# WorkmateOS Frontend - Quick Reference Guide

## File Locations Quick Lookup

### Core Application Files
- **Entry Point**: `ui/src/main.ts`
- **Root Component**: `ui/src/App.vue`
- **Global Router**: `ui/src/router/index.ts`
- **Main Layout**: `ui/src/layouts/AppLayout.vue`

### Module System
- **App Registry** (add new modules here): `ui/src/layouts/app-manager/appRegistry.ts`
- **Window Manager**: `ui/src/layouts/app-manager/useAppManager.ts`
- **Window Container**: `ui/src/layouts/app-manager/WindowHost.vue`
- **Window Wrapper**: `ui/src/layouts/app-manager/WindowFrame.vue`

### Navigation Components
- **Topbar**: `ui/src/layouts/components/Topbar.vue`
- **Dock** (app launcher, add items here): `ui/src/layouts/components/Dock.vue`

### API & Services
- **API Client** (Axios setup): `ui/src/services/api/client.ts`
- **Assets**: `ui/src/services/assets.ts`

### Global Composables
- `ui/src/composables/useDashboard.ts`
- `ui/src/composables/useEmployees.ts`
- `ui/src/composables/useProjects.ts`

### Styling
- **Design Tokens**: `ui/src/styles/tokens.css` (CSS custom properties)
- **Base Styles**: `ui/src/styles/base.css` (Global styles + Tailwind)
- **Component Styles**: `ui/src/styles/components/button.css`

### Existing Modules

#### CRM Module
```
ui/src/modules/crm/
├── CrmApp.vue                      # Entry point
├── pages/
│   ├── dashboard/CrmDashboardPage.vue
│   ├── customer/CustomersListPage.vue
│   ├── customer/CustomerDetailPage.vue
│   ├── contacts/ContactsListPage.vue
│   ├── contacts/ContactDetailPage.vue
│   └── index.ts
├── components/
│   ├── customer/CustomerCard.vue
│   ├── customer/CustomerForm.vue
│   ├── contacts/ContactCard.vue
│   ├── contacts/ContactForm.vue
│   ├── widgets/CrmKpiCustomers.vue
│   ├── widgets/CrmRecentActivity.vue
│   ├── widgets/CrmShortcuts.vue
│   └── index.ts
├── composables/
│   ├── useCrmNavigation.ts         # Module internal routing
│   ├── useCrmStats.ts              # Stats loading state
│   └── useCrmActivity.ts           # Activity management
├── services/
│   └── crm.service.ts              # API calls
└── types/
    ├── customer.ts
    ├── contact.ts
    ├── activity.ts
    └── stats.ts
```

#### Dashboard Module
```
ui/src/modules/dashboard/
├── pages/DashboardPage.vue
├── components/
│   ├── WidgetRenderer.vue
│   ├── widgets/StatsWidget.vue
│   ├── widgets/RemindersWidget.vue
│   ├── widgets/ShortcutsWidget.vue
│   ├── widgets/ActivityFeedWidget.vue
│   └── ... more widgets
├── services/
│   └── widgetRegistry.ts           # Widget registration
└── types/
    └── widgetTypes.ts
```

---

## Common Tasks

### Task 1: Add a New Module

**Files to Create:**
1. `ui/src/modules/mymodule/MyModuleApp.vue` - Entry point
2. `ui/src/modules/mymodule/types/mymodule.ts` - Types
3. `ui/src/modules/mymodule/services/mymodule.service.ts` - API calls
4. `ui/src/modules/mymodule/composables/useMyModuleNav.ts` - Navigation
5. `ui/src/modules/mymodule/pages/MyPage.vue` - Pages
6. `ui/src/modules/mymodule/components/MyComponent.vue` - Components

**Files to Modify:**
1. `ui/src/layouts/app-manager/appRegistry.ts` - Add app to `apps` array
2. `ui/src/layouts/components/Dock.vue` - Add item to `dockItems` array
3. `ui/src/router/index.ts` (optional) - Add child route

---

### Task 2: Add API Endpoint to Service

**Location**: `ui/src/modules/crm/services/crm.service.ts`

```typescript
async getCustomers(): Promise<Customer[]> {
  const { data } = await api.get("/api/backoffice/crm/customers");
  return data;
}
```

---

### Task 3: Create Data Fetching Composable

**Location**: `ui/src/modules/crm/composables/useCrmStats.ts`

```typescript
import { ref } from "vue";
import { crmService } from "../services/crm.service";
import type { CrmStats } from "../types/stats";

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

  return { stats, loading, error, fetchStats };
}
```

---

### Task 4: Use Composable in Component

```vue
<script setup lang="ts">
import { onMounted } from "vue";
import { useCrmStats } from "../../composables/useCrmStats";

const { stats, loading, error, fetchStats } = useCrmStats();

onMounted(() => {
  fetchStats();
});
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error" class="text-red">{{ error }}</div>
    <div v-else>{{ stats }}</div>
  </div>
</template>
```

---

### Task 5: Add Navigation to Module

**In Module Entry** (`CrmApp.vue`):
```typescript
const { view, activeCustomerId, goCustomerDetail, goCustomers } = useCrmNavigation();
```

**In Child Component**:
```typescript
emit("openCustomer", id);
// Parent catches: @openCustomer="goCustomerDetail"
```

---

### Task 6: Style Component

**Using Tailwind (inline classes):**
```vue
<div class="px-4 py-2 bg-white/5 border border-white/10 rounded">
  <h2 class="text-lg font-semibold text-white">Title</h2>
</div>
```

**Using Design Tokens (CSS):**
```vue
<div class="my-custom-card">
  <h2>Title</h2>
</div>

<style scoped>
.my-custom-card {
  padding: var(--space-md);
  background: var(--color-panel-glass);
  border-radius: var(--radius-md);
}
</style>
```

---

### Task 7: Register Global Pinia Store

**Create Store**: `ui/src/stores/authStore.ts`
```typescript
import { defineStore } from "pinia";
import { ref } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  
  return { user };
});
```

**Use in Component**:
```typescript
import { useAuthStore } from "@/stores/authStore";

const authStore = useAuthStore();
console.log(authStore.user);
```

---

### Task 8: Add Type Definition

**Location**: `ui/src/modules/crm/types/customer.ts`

```typescript
export interface Customer {
  id: string;
  name: string;
  email: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

---

## Important Patterns

### Service Pattern
```typescript
// services/crm.service.ts
export const crmService = {
  async getCustomers() { ... },
  async getCustomer(id) { ... },
  async createCustomer(payload) { ... },
};
```

### Composable Pattern
```typescript
// composables/useCrmStats.ts
export function useCrmStats() {
  const data = ref(null);
  const loading = ref(false);
  const error = ref(null);
  
  async function fetch() { ... }
  
  return { data, loading, error, fetch };
}
```

### Component Event Pattern
```vue
<script setup>
const emit = defineEmits<{
  (e: "openCustomer", id: string): void;
  (e: "back"): void;
}>();

function handleClick(id: string) {
  emit("openCustomer", id);
}
</script>
```

### Module Navigation Pattern
```typescript
// In CrmApp.vue
const { view, activeId, goList, goDetail } = useCrmNavigation();

// In CustomersListPage.vue
emit("openCustomer", id);

// In CrmApp.vue
@openCustomer="goDetail"
```

---

## Environment Variables

### .env (ui/.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

### Access in Code
```typescript
import.meta.env.VITE_API_BASE_URL
```

---

## Running the Application

```bash
# Install dependencies
cd ui
pnpm install

# Development server (hot reload)
pnpm run dev
# Access at: http://localhost:5173

# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

---

## Component Hierarchy Quick Map

```
main.ts
  └─ App.vue
      └─ Router
          ├─ /app → AppLayout
          │    ├─ Topbar
          │    ├─ WindowHost
          │    │   └─ WindowFrame (multiple instances)
          │    │       └─ CrmApp, ProjectsApp, etc (modules)
          │    └─ Dock
          │
          ├─ /under-construction
          └─ /linktree
```

---

## Pinia Store Locations (Currently Empty)

To create global state, add stores to:
```
ui/src/stores/
├── authStore.ts
├── userStore.ts
├── appStore.ts
└── ... etc
```

Access with:
```typescript
import { useAuthStore } from "@/stores/authStore";
const authStore = useAuthStore();
```

---

## Available Icons (lucide-vue-next)

Used in Dock and throughout UI:
```typescript
import { Users, Briefcase, Timer, Receipt, Wallet, MessageSquare } from "lucide-vue-next";
```

See: https://lucide.dev/

---

## TypeScript Path Aliases

```
@ → ui/src/
```

Example imports:
```typescript
import CrmApp from "@/modules/crm/CrmApp.vue";
import { crmService } from "@/modules/crm/services/crm.service";
import type { Customer } from "@/modules/crm/types/customer";
import { useAppManager } from "@/layouts/app-manager/useAppManager";
import api from "@/services/api/client";
```

---

## Tailwind Classes Quick Reference

**Colors:**
- `bg-bg-primary`, `bg-bg-secondary`
- `text-white`, `text-white/70`, `text-white/50`
- `border-white/10`
- `hover:bg-white/10`

**Layout:**
- `flex flex-col`, `flex items-center justify-between`
- `grid grid-cols-4 gap-2`
- `w-full h-full`

**Spacing:**
- `px-4 py-2`, `p-6`
- `gap-4`, `space-y-4`

**Styling:**
- `rounded`, `rounded-xl`
- `border`
- `shadow-soft`
- `overflow-hidden`, `overflow-auto`

**Responsive:**
- `md:`, `lg:`, `xl:`

---

## Debugging Tips

### Check API Responses
```typescript
const { data } = await api.get("/api/endpoint");
console.log(data);
```

### Check Component State
```vue
<script setup>
const myRef = ref("value");
</script>

<template>
  <!-- Debug output -->
  <pre>{{ myRef }}</pre>
</template>
```

### Check Router State
```typescript
import { useRouter, useRoute } from "vue-router";
const router = useRouter();
const route = useRoute();
console.log(route.path, route.params);
```

### Check Window Manager State
```typescript
import { useAppManager } from "@/layouts/app-manager/useAppManager";
const { windows, activeWindow } = useAppManager();
console.log(windows.value, activeWindow.value);
```

---

## Common Errors & Fixes

### "Cannot find module '@/modules/...'"
- Check path in import statement
- Use `@` alias correctly
- Verify file exists

### "Type '...' is not assignable to type '...'"
- Check type definitions in `types/` folder
- Ensure API response matches interface

### "composable not defined"
- Import from correct path: `from "../../composables/useXxx"`
- Make sure `useXxx` is exported

### API calls returning undefined
- Check API base URL in `.env`
- Verify API endpoint path matches backend
- Check loading state before accessing data

---

## Quick Commands

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm run dev

# Build
pnpm run build

# Format code (if prettier configured)
pnpm run format

# Check types
vue-tsc --noEmit
```

