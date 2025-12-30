---
layout: default
title: Visual Guide
parent: Frontend
grand_parent: Wiki
nav_order: 4
---

# WorkmateOS Frontend Architecture - Visual Overview

## Application Structure Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                          main.ts (Entry Point)                  │
│                    Creates App + Pinia + Router                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        App.vue (Root)                           │
│                    Simple RouterView delegate                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Vue Router (router/index.ts)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Route: "/" → redirect to "/under-construction"          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Route: "/app" → AppLayout (Main Application)            │  │
│  │  Children:                                              │  │
│  │    - /dashboard → DashboardPage                         │  │
│  │    - /crm → CrmApp                                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Route: "/under-construction"                            │  │
│  │ Route: "/linktree"                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │        AppLayout.vue                 │
        │  (Main Container with 3 parts)       │
        └──────────────────────────────────────┘
                  │         │         │
        ┌─────────┴────┐    │    ┌────┴─────────┐
        ▼              ▼    ▼    ▼              ▼
    ┌────────┐   ┌───────────────┐   ┌────────┐
    │ Topbar │   │ WindowHost    │   │  Dock  │
    │(Fixed) │   │(App Windows)  │   │(Fixed) │
    └────────┘   └───────────────┘   └────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │WindowFrame│          │WindowFrame│
        │(CRM App) │          │(Projects)│
        └──────────┘          └──────────┘
             │                     │
             ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │ CrmApp   │          │ProjectsApp
        │(Module)  │          │(Module)  │
        └──────────┘          └──────────┘
```

---

## Module Internal Architecture (CRM Example)

```
┌───────────────────────────────────────────────────────────┐
│              CrmApp.vue (Module Entry)                    │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Uses: useCrmNavigation()                            │ │
│  │   - view: "dashboard" | "customers" | ...          │ │
│  │   - activeCustomerId, activeContactId              │ │
│  │   - Navigation functions: goCustomers, etc         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Conditional Rendering based on view state          │ │
│  │                                                     │ │
│  │ ┌────────────────────────────────────────────────┐ │ │
│  │ │ <CrmDashboardPage v-if="view === 'dashboard"" │ │ │
│  │ │   @openCustomers="goCustomers" />             │ │ │
│  │ ├────────────────────────────────────────────────┤ │ │
│  │ │ <CustomersListPage v-if="view === 'customers'" │ │ │
│  │ │   @openCustomer="goCustomerDetail" />         │ │ │
│  │ ├────────────────────────────────────────────────┤ │ │
│  │ │ <CustomerDetailPage v-if="view === ..."       │ │ │
│  │ │   :customerId="activeCustomerId" />           │ │ │
│  │ ├────────────────────────────────────────────────┤ │ │
│  │ │ <CustomerForm v-if="view === 'customer-create'"│ │ │
│  │ │   @saved="goCustomers" />                     │ │ │
│  │ └────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│     Pages Layer              │  │   Components Layer           │
├──────────────────────────────┤  ├──────────────────────────────┤
│ - CrmDashboardPage.vue       │  │ - CustomerCard.vue           │
│ - CustomersListPage.vue      │  │ - CustomerForm.vue           │
│ - CustomerDetailPage.vue     │  │ - ContactCard.vue            │
│ - ContactsListPage.vue       │  │ - ContactForm.vue            │
│ - ContactDetailPage.vue      │  │ - CrmKpiCustomers.vue        │
│                              │  │ - CrmRecentActivity.vue      │
│ (Emit events, no routing)   │  │ - CrmShortcuts.vue           │
└──────────────────────────────┘  └──────────────────────────────┘
        │                                 │
        └────────────────┬────────────────┘
                         ▼
        ┌────────────────────────────────┐
        │   Services/Composables Layer   │
        ├────────────────────────────────┤
        │ • crmService (HTTP calls)      │
        │ • useCrmNavigation (state)     │
        │ • useCrmStats (fetch + state)  │
        │ • useCrmActivity (fetch state) │
        └────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │     Types / Interfaces         │
        ├────────────────────────────────┤
        │ - Customer                     │
        │ - Contact                      │
        │ - CrmActivity                  │
        │ - CrmStats                     │
        └────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │    Shared API Client           │
        │  (services/api/client.ts)      │
        │  Axios instance with           │
        │  interceptors                  │
        └────────────────────────────────┘
```

---

## Window Manager System

```
┌──────────────────────────────────────────────────────────────────┐
│                  useAppManager() Composable                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ State:                                                     │ │
│  │  - windows: WindowApp[]    (Reactive array)               │ │
│  │  - activeWindow: Ref<string|null>  (Currently focused)    │ │
│  │  - zCounter: number        (For layering)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ WindowApp Interface:                                       │ │
│  │  {                                                         │ │
│  │    id: string;              // Unique window instance     │ │
│  │    appId: string;           // Reference to apps registry │ │
│  │    title: string;                                         │ │
│  │    component: Component;                                  │ │
│  │    props?: Record<string, any>;                           │ │
│  │    x, y, width, height: number;  // Position/Size        │ │
│  │    z: number;               // Layer depth               │ │
│  │  }                                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Methods:                                                   │ │
│  │  • openWindow(appId)        → Opens/focuses app           │ │
│  │  • closeWindow(id)          → Closes window               │ │
│  │  • focusWindow(id)          → Brings to front             │ │
│  │  • startDragFor(id, e)      → Initiates drag              │ │
│  │  • startResizeFor(id, e)    → Initiates resize            │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │   appRegistry.ts               │
            │  (Central App Registration)    │
            ├────────────────────────────────┤
            │ const apps = [                 │
            │   {                            │
            │     id: "crm",                 │
            │     title: "CRM",              │
            │     icon: markRaw(icons.Users),│
            │     component: markRaw(CrmApp),│
            │     window: {                  │
            │       width: 1100,             │
            │       height: 700              │
            │     }                          │
            │   },                           │
            │   // More apps...              │
            │ ]                              │
            └────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │   WindowHost.vue               │
            │  (Renders all windows)         │
            └────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────┐
        ▼                                     ▼
┌─────────────────────┐              ┌─────────────────────┐
│  WindowFrame.vue    │              │  WindowFrame.vue    │
│  (CRM Instance)     │              │  (Project Instance) │
│                     │              │                     │
│ Titlebar (Draggable)│              │ Titlebar (Draggable)│
│ Content Area        │              │ Content Area        │
│ Resize Handle       │              │ Resize Handle       │
│ Close Button        │              │ Close Button        │
└─────────────────────┘              └─────────────────────┘
        │                                     │
        ▼                                     ▼
┌─────────────────────┐              ┌─────────────────────┐
│   CrmApp.vue        │              │  ProjectsApp.vue    │
│   (Active)          │              │   (Background)      │
└─────────────────────┘              └─────────────────────┘
```

---

## Data Flow: Fetch Data Pattern

```
Component (Page)
    │
    ├─ onMounted()
    │   └─→ Call composable.fetchData()
    │
    ▼
Composable (useCrmStats, etc)
    │
    ├─ loading = true
    ├─ error = null
    │
    ▼
Service (crmService)
    │
    ├─ Calls api.get("/api/...")
    │
    ▼
API Client (axios instance)
    │
    ├─ Request Interceptor (add JWT token)
    ├─ Makes HTTP request
    ├─ Response Interceptor (handle errors)
    │
    ▼
Backend API (e.g., FastAPI)
    │
    ▼
API Client (returns response)
    │
    ▼
Service (extracts data)
    │
    │ return data
    ▼
Composable
    │
    ├─ stats.value = data
    ├─ loading = false
    ├─ error = null
    │
    ▼
Component (Template)
    │
    ├─ v-if="loading" → Show spinner
    ├─ v-else-if="error" → Show error
    ├─ v-else → Show data (stats.value)
    │
    └─ UI Updates automatically (reactive)
```

---

## Styling Architecture

```
┌─────────────────────────────────────────────────┐
│           Design Tokens (tokens.css)            │
│  ┌──────────────────────────────────────────┐  │
│  │ CSS Custom Properties:                   │  │
│  │  --color-bg-primary: #232223             │  │
│  │  --color-accent-primary: #ff9100         │  │
│  │  --color-text-primary: #ffffff           │  │
│  │  --space-md: 16px                        │  │
│  │  --os-dock-height: 80px                  │  │
│  │  ... etc ...                             │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        ▼                            ▼
┌──────────────────┐        ┌──────────────────┐
│  Tailwind CSS    │        │  Component CSS   │
│  (base.css)      │        │  (button.css)    │
├──────────────────┤        ├──────────────────┤
│ @layer base      │        │ .kit-btn-primary │
│ @layer components│        │ .kit-input       │
│ @layer utilities │        │ .kit-label       │
│                  │        │ ... etc ...      │
│ Tailwind classes │        │                  │
│ px-4, py-2, etc  │        │ Scoped in .vue   │
└──────────────────┘        └──────────────────┘
        │                            │
        └─────────────┬──────────────┘
                      ▼
        ┌──────────────────────────┐
        │   Component Styling      │
        │   (Template + <style>)   │
        │                          │
        │ <div class="px-4 py-2    │
        │   bg-white/5 ...">       │
        │                          │
        │ <style scoped>           │
        │   .window-frame { ... }  │
        │ </style>                 │
        └──────────────────────────┘
```

---

## Data Types Organization

```
Module Root: src/modules/crm/

types/
├── customer.ts
│   └─ export interface Customer { ... }
├── contact.ts
│   └─ export interface Contact { ... }
├── activity.ts
│   └─ export interface CrmActivity { ... }
│   └─ export interface CreateCrmActivity { ... }
└── stats.ts
    └─ export interface CrmStats { ... }

services/
└── crm.service.ts
    └─ export const crmService = {
         async getCustomers(): Promise<Customer[]> { ... }
         async getContact(id): Promise<Contact> { ... }
         async getCrmStats(): Promise<CrmStats> { ... }
       }

composables/
├── useCrmNavigation.ts
│   └─ Navigation state (view, activeId)
├── useCrmStats.ts
│   └─ Data fetching + loading state
└── useCrmActivity.ts
    └─ Activity management

pages/
├── CustomersListPage.vue
├── CustomerDetailPage.vue
├── ContactsListPage.vue
├── ContactDetailPage.vue
└── CrmDashboardPage.vue

components/
├── customer/
│   ├── CustomerCard.vue
│   └── CustomerForm.vue
├── contacts/
│   ├── ContactCard.vue
│   └── ContactForm.vue
└── widgets/
    ├── CrmKpiCustomers.vue
    ├── CrmRecentActivity.vue
    └── CrmShortcuts.vue
```

---

## Component Communication Pattern

```
┌─────────────────────────────┐
│      CrmApp.vue             │
│   (Parent/Router)           │
│                             │
│ const { view,              │
│         activeCustomerId,  │
│         goCustomerDetail   │
│       } = useCrmNavigation()│
└─────────────────────────────┘
        │
        ├─ Event: @openCustomer
        │           ↓
        │  Calls: goCustomerDetail(id)
        │           ↓
        │  Updates: activeCustomerId = id
        │           ↓
        │  Updates: view = "customer-detail"
        │
        ▼
┌─────────────────────────────┐
│ CustomersListPage.vue       │
│                             │
│ emit("openCustomer", id)    │
│                             │
│ @openCustomer="             │
│   goCustomerDetail"         │
└─────────────────────────────┘
        │
        ├─ Props: none
        │         (state passed via composable)
        ├─ Emits: openCustomer(id), openDashboard()
        └─ State: search, page (local)
                  customers (from service)
                  loading (from composable)

Props Down → Events Up → Composables for Shared State
```

---

## Adding a New Module: File Creation Checklist

```
✓ Step 1: Create Directory Structure
  └─ ui/src/modules/mymodule/

✓ Step 2: Create Type Definitions
  └─ types/mymodule.ts
     export interface MyResource { ... }

✓ Step 3: Create Service Layer
  └─ services/mymodule.service.ts
     export const mymoduleService = { ... }

✓ Step 4: Create Navigation Composable
  └─ composables/useMyModuleNav.ts
     export function useMyModuleNav() { ... }

✓ Step 5: Create Pages
  └─ pages/MyPage.vue
     pages/index.ts

✓ Step 6: Create Components
  └─ components/MyComponent.vue
     components/index.ts

✓ Step 7: Create Module Entry Point
  └─ MyModuleApp.vue
     (Uses useMyModuleNav, conditionally renders pages)

✓ Step 8: Register Module
  └─ layouts/app-manager/appRegistry.ts
     Add to apps[] array

✓ Step 9: Add Dock Item
  └─ layouts/components/Dock.vue
     Add to dockItems[] array

✓ Step 10 (Optional): Add Route
  └─ router/index.ts
     Add child route under /app
```

