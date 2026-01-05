---
layout: default
title: Architektur
parent: Frontend
grand_parent: Wiki
nav_order: 1
---

# WorkmateOS Frontend/UI Architektur-Leitfaden

## Überblick

Das WorkmateOS Frontend ist eine Vue 3 + TypeScript + Vite-basierte Anwendung, die eine **modulare Architektur** mit einem einzigartigen desktop-ähnlichen Fensterverwaltungssystem verwendet. Die Anwendung ist in unabhängige Module (CRM, Dashboard, etc.) organisiert, die als schwebende Fenster innerhalb der Hauptanwendung geöffnet werden können.

---

## 1. Gesamte Verzeichnisstruktur

```
ui/src/
├── main.ts                          # Einstiegspunkt
├── App.vue                          # Root-Komponente
├── style.css                        # Globale Styles
│
├── router/
│   └── index.ts                     # Vue Router Konfiguration
│
├── layouts/
│   ├── AppLayout.vue                # Haupt-Layout (Topbar + Dock + Window Host)
│   ├── app-manager/
│   │   ├── appRegistry.ts           # Zentrale App-Registrierung
│   │   ├── useAppManager.ts         # Fensterverwaltungslogik
│   │   ├── WindowHost.vue           # Container für alle Fenster
│   │   ├── WindowFrame.vue          # Individueller Fenster-Wrapper
│   │   └── index.ts                 # Exports
│   └── components/
│       ├── Topbar.vue               # Obere Navigationsleiste
│       ├── Dock.vue                 # Unteres App-Dock
│       └── index.ts                 # Exports
│
├── modules/
│   ├── crm/                         # CRM-Modul
│   │   ├── CrmApp.vue               # Modul-Einstiegskomponente
│   │   ├── pages/                   # Seiten-Komponenten
│   │   │   ├── dashboard/
│   │   │   │   └── CrmDashboardPage.vue
│   │   │   ├── customer/
│   │   │   │   ├── CustomersListPage.vue
│   │   │   │   └── CustomerDetailPage.vue
│   │   │   ├── contacts/
│   │   │   │   ├── ContactsListPage.vue
│   │   │   │   └── ContactDetailPage.vue
│   │   │   └── index.ts             # Seiten-Exports
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
│   │   │   ├── useCrmNavigation.ts   # Navigationszustandsverwaltung
│   │   │   ├── useCrmStats.ts        # Statistik-Logik
│   │   │   └── useCrmActivity.ts     # Aktivitätsverwaltung
│   │   ├── services/
│   │   │   └── crm.service.ts        # API-Aufrufe
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
│       │   └── widgetRegistry.ts     # Widget-Registrierung
│       └── types/
│           └── widgetTypes.ts        # Typ-Definitionen
│
├── services/
│   ├── api/
│   │   └── client.ts                # Axios API Client
│   └── assets.ts                    # Asset-Pfade
│
├── composables/
│   ├── useDashboard.ts              # Globale Dashboard-Logik
│   ├── useEmployees.ts
│   ├── useProjects.ts
│   └── useInvocies.ts
│
├── styles/
│   ├── tokens.css                   # Design-Tokens (Farben, Abstände, etc.)
│   ├── base.css                     # Globale Styles
│   └── components/
│       ├── button.css
│       └── kit-components.css
│
├── pages/                           # Globale Seiten
│   ├── UnderConstruction.vue
│   └── Linktree.vue
│
└── assets/
    └── [Bilder, Schriften, etc.]
```

---

## 2. Anwendungs-Bootstrap-Ablauf

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

**Wichtige Punkte:**
- Pinia wird für State Management initialisiert (aktuell minimal genutzt)
- Vue Router verwaltet globales Routing
- App.vue ist die Root-Komponente

### App.vue (Root-Komponente)
```vue
<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>
```

Einfache Root-Komponente, die an den Router delegiert.

---

## 3. Router-Konfiguration (router/index.ts)

Der Router verwendet zwei Hauptrouten:

```typescript
const routes = [
  // Standard-Weiterleitung
  { path: "/", redirect: "/under-construction" },

  // Haupt-App-Layout mit Modulen
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
        component: CrmApp,  // Modul-Einstiegspunkt
      }
    ],
  },

  // Öffentliche Routen
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

**Muster:** Child-Routen werden lazy-loaded, außer CrmApp, die direkt importiert wird.

---

## 4. Modul-System-Architektur

### Modul-Registrierung (appRegistry.ts)

Zentrale Registrierung für alle Module:

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
  // Weitere Apps hier...
];
```

**Wichtige Punkte:**
- Verwendet `markRaw()`, um Vue-Reaktivitäts-Overhead zu vermeiden
- Jede App hat eine `id`, `title`, `icon`, `component` und Standard-Fenstergröße
- Wird vom Fenstermanager zum Öffnen von Apps verwendet

### Fenstermanager (useAppManager.ts)

Reaktive Zustandsverwaltung für Fenster:

```typescript
export interface WindowApp {
  id: string;              // Eindeutige Fensterinstanz-ID
  appId: string;           // Referenz zur App-Registrierung
  title: string;
  component: Component;
  props?: Record<string, any>;
  x: number; y: number;    // Position
  width: number;
  height: number;
  z: number;               // Z-Index für Layering
}

export const appManager = {
  windows,          // Reaktives Array geöffneter Fenster
  activeWindow,     // Aktuell fokussiertes Fenster

  openWindow(appId),    // App öffnen
  closeWindow(id),      // Fenster schließen
  focusWindow(id),      // Fenster fokussieren (nach vorne bringen)
  startDragFor(id, e),  // Drag-Handler
  startResizeFor(id, e) // Resize-Handler
};
```

**Hauptfunktionen:**
- Mehrere Instanzen derselben App können geöffnet sein
- Fenster sind verschiebbar und in der Größe veränderbar
- Z-Index wird für richtiges Layering verwaltet
- Position/Größe auf Viewport begrenzt

---

## 5. Modul-Strukturmuster - CRM-Modul-Beispiel

### Modul-Einstiegspunkt (CrmApp.vue)

Fungiert als Router/Container für das Modul:

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
    <!-- Bedingte Darstellung basierend auf Ansichtszustand -->
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

    <!-- Weitere Ansichten... -->
  </div>
</template>
```

**Muster:**
- Modul hat internes Routing über Composable-basierten State
- Keine Vue Router Child-Routen (in sich geschlossen)
- Ansichtswechsel über bedingte Darstellung

### Navigations-Composable (useCrmNavigation.ts)

Interne Zustandsverwaltung für Modulansichten:

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

  // ... weitere Navigationsfunktionen

  return {
    view,
    activeCustomerId,
    activeContactId,
    goDashboard,
    goCustomers,
    // ... weitere Exports
  };
}
```

**Muster:**
- Pures Composable ohne Abhängigkeiten vom Vue Router
- Referenzen über Composable übergeben, nicht über Route-Parameter
- Im gesamten Modul für Navigation verwendet

### API-Service-Schicht (crm.service.ts)

Zentralisierte API-Aufrufe:

```typescript
import api from "@/services/api/client";

export const crmService = {
  // Kunden
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

  // Kontakte
  async getContacts(): Promise<Contact[]> {
    const { data } = await api.get("/api/backoffice/crm/contacts");
    return data;
  },

  // Aktivitäten
  async getLatestActivities(limit: number): Promise<CrmActivity[]> {
    const { data } = await api.get(`/api/backoffice/crm/activities/latest?limit=${limit}`);
    return data;
  },

  // Statistiken
  async getCrmStats(): Promise<CrmStats> {
    const { data } = await api.get("/api/backoffice/crm/stats");
    return data;
  }
};
```

**Muster:**
- Service-Objekt mit statischen Methoden
- Verwendet gemeinsamen Axios-Client
- Gibt Promise<T> für richtige Typisierung zurück
- Handhabt URL-Konstruktion und Parameter

### Datenabruf-Composable (useCrmStats.ts)

Ladezustand + Service-Integration:

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
      error.value = e.message ?? "Fehler beim Laden der Statistiken";
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

**Muster:**
- Wrapping von Service-Aufrufen
- Verwaltet Lade-/Fehlerzustände
- Gibt reaktive Ref + Fetch-Funktion zurück
- In Komponenten verwendet via `const { stats, loading } = useCrmStats()`

### Seiten-Komponenten (CustomersListPage.vue)

```vue
<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-white">Kundenliste</h1>
      <button class="kit-btn-primary" @click="openCreateModal">
        + Neuer Kunde
      </button>
    </div>

    <!-- Suche/Filter -->
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

**Muster:**
- Seite emit Events zur übergeordneten Komponente (CrmApp.vue)
- Verwendet Composables für Logik
- Handhabt eigenen lokalen Zustand (Suche, Pagination)
- Service-Aufrufe in onMounted
- Computed für Filterung/Pagination

### Typ-Definitionen (types/customer.ts)

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

**Muster:**
- Alle Modul-Typen in dediziertem `types/`-Ordner
- Exportierte Interfaces, keine Klassen
- Nullable Felder mit `| null` gekennzeichnet
- ISO-Datums-Strings für Daten

### Komponenten-Barrel-Exports (components/index.ts)

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

**Muster:**
- Alle Komponenten aus Index exportiert
- Ermöglicht `import { CustomerForm } from "../../components"`

---

## 6. API-Client-Setup (services/api/client.ts)

Zentralisierte Axios-Instanz:

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

// Request Interceptor (JWT Token würde hier hinzugefügt)
apiClient.interceptors.request.use(
  (config) => {
    // TODO: JWT Token hinzufügen
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor (Fehlerbehandlung)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Globale Fehlerbehandlung (401, 403, 404, 500, etc)
    return Promise.reject(error);
  }
);

export default apiClient;
```

**Verwendung in Services:**
```typescript
const { data } = await api.get("/api/backoffice/crm/customers");
```

**Funktionen:**
- Einzelne Instanz wird app-weit geteilt
- Base-URL aus Umgebungsvariablen
- Bereit für JWT-Interceptor
- Zentralisierte Fehlerbehandlung

---

## 7. Layout-System (AppLayout.vue)

Haupt-Container mit Topbar, Window Host und Dock:

```vue
<template>
  <div class="w-screen h-screen overflow-hidden flex flex-col bg-bg-primary">
    <!-- Topbar -->
    <KitTopbar />

    <!-- Haupt-Fensterbereich -->
    <div class="flex flex-1 overflow-hidden">
      <WindowHost class="flex-1" />
    </div>

    <!-- Dock (Unten) -->
    <KitDock />
  </div>
</template>
```

### Dock-Komponente (Dock.vue)

Untere Navigationsleiste zum Öffnen von Apps:

```vue
<script setup lang="ts">
const dockItems = [
  { id: "crm", label: "CRM", icon: markRaw(Users) },
  { id: "projects", label: "Projects", icon: markRaw(Briefcase) },
  { id: "time", label: "Time", icon: markRaw(Timer) },
  // Weitere Items...
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

**Funktionen:**
- Verwendet lucide-vue-next Icons (markRaw für Performance)
- Integriert mit useAppManager
- Zeigt aktiven Zustand, wenn App-Fenster geöffnet ist
- Responsive Design (versteckt auf Mobilgeräten)

### Window Host (WindowHost.vue)

Container für alle schwebenden Fenster:

```vue
<template>
  <div class="window-host">
    <WindowFrame
      v-for="w in windows"
      :key="w.id"
      :win="w"
    >
      <!-- App-Komponente wird hier gerendert -->
      <component :is="resolveComponent(w.appId)" v-bind="w.props" />
    </WindowFrame>
  </div>
</template>
```

### Window Frame (WindowFrame.vue)

Individueller Fenster-Wrapper mit Titelleiste, Resize-Handle:

```vue
<template>
  <div class="window-frame" :style="frameStyleString" @mousedown="focus">
    <!-- Titelleiste (verschiebbar) -->
    <div class="window-titlebar" @mousedown.stop="startDrag">
      <span>{{ win.title }}</span>
      <button @click.stop="close">✕</button>
    </div>

    <!-- Inhalt -->
    <div class="window-content">
      <slot />
    </div>

    <!-- Resize-Handle -->
    <div class="resize-handle" @mousedown.stop="startResize" />
  </div>
</template>
```

**Funktionen:**
- Absolut positioniert mit dynamischem x, y, width, height
- Verschiebbare Titelleiste
- Größenänderbar über Eckengriff
- Schließen-Button
- Fokus bei Klick (Z-Index-Verwaltung)

---

## 8. State Management (Pinia)

Aktuell ist Pinia eingerichtet, aber **minimal genutzt**. Die App setzt auf:
- **Composables** für lokalen Zustand (useCrmNavigation, useCrmStats, etc.)
- **Service-Schicht** für API-Aufrufe
- **Reaktive Refs** für Komponentenzustand

**Wann einen Pinia Store hinzufügen:**
- Globaler App-Zustand (User, Auth, Theme)
- Geteilter Zustand über mehrere Module
- Komplexe Zustandsübergänge

---

## 9. Styling-System

### Design-Tokens (styles/tokens.css)

CSS Custom Properties für Konsistenz:

```css
:root {
  /* Farben */
  --color-bg-primary: #232223;
  --color-accent-primary: #ff9100;
  --color-text-primary: #ffffff;
  --color-text-secondary: rgba(255, 255, 255, 0.7);
  --color-border-light: rgba(255, 255, 255, 0.1);

  /* Typografie */
  --font-primary: "Fira Sans", sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  /* Abstände */
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

Verwendet Tailwind v4 mit `@tailwindcss/vite` Plugin:

```vue
<div class="px-6 py-4 bg-white/5 border border-white/10 rounded-lg">
  <h2 class="text-lg font-semibold text-white">Titel</h2>
</div>
```

**Verwendete Klassen:**
- `bg-bg-primary`, `bg-bg-secondary`
- `text-white`, `text-white/70`
- `border-white/10`
- Grid-Layouts: `grid grid-cols-4 gap-2`
- Flex: `flex items-center justify-between`

### Komponenten-Styles (styles/components/)

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

## 10. Neues Modul erstellen - Schritt für Schritt

### Schritt 1: Modul-Struktur erstellen

```
ui/src/modules/mymodule/
├── MyModuleApp.vue           # Einstiegspunkt
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

### Schritt 2: Typ-Definitionen erstellen (types/mymodule.ts)

```typescript
export interface MyResource {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}
```

### Schritt 3: Service-Schicht erstellen (services/mymodule.service.ts)

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

### Schritt 4: Navigations-Composable erstellen (composables/useMyModuleNav.ts)

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

### Schritt 5: Seiten erstellen

```vue
<!-- pages/ResourceListPage.vue -->
<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <h1 class="text-2xl font-semibold text-white">Ressourcen</h1>

    <button class="kit-btn-primary" @click="openCreate">
      + Neue Ressource
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

### Schritt 6: Modul-Einstiegspunkt erstellen (MyModuleApp.vue)

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

### Schritt 7: Modul registrieren (layouts/app-manager/appRegistry.ts)

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
    title: "Mein Modul",
    icons: markRaw(icons.Package),
    component: markRaw(MyModuleApp),
    window: { width: 900, height: 600 }
  },
];
```

### Schritt 8: Dock-Item hinzufügen (layouts/components/Dock.vue)

```typescript
const dockItems = [
  { id: "crm", label: "CRM", icon: markRaw(Users) },
  { id: "mymodule", label: "Modul", icon: markRaw(Package) }, // Hier hinzufügen
  { id: "projects", label: "Projects", icon: markRaw(Briefcase) },
];
```

### Schritt 9 (Optional): Route hinzufügen (router/index.ts)

Für Landing-Page oder eigenständige Route:

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

## 11. Häufige Muster & Best Practices

### Muster: Service + Composable

**Service handhabt HTTP:**
```typescript
// crm.service.ts
async getCustomers(): Promise<Customer[]> {
  const { data } = await api.get("/api/crm/customers");
  return data;
}
```

**Composable handhabt Zustand + Fehler:**
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

**Komponente verwendet Composable:**
```vue
<script setup>
const { stats, loading, error, fetchStats } = useCrmStats();
onMounted(fetchStats);
</script>

<template>
  <div v-if="loading">Lädt...</div>
  <div v-else-if="error" class="text-red">{{ error }}</div>
  <div v-else>{{ stats }}</div>
</template>
```

### Muster: Modul-Navigation

**Modul-Eintrag verwendet lokalen Zustand, nicht Router:**
```typescript
const { view, activeId, goList, goDetail } = useModuleNav();
```

**Übergeordnete Komponente rendert bedingt:**
```vue
<ListPage v-if="view === 'list'" @openDetail="goDetail" />
<DetailPage v-if="view === 'detail'" :id="activeId" @back="goList" />
```

**Events propagieren nach oben:**
```typescript
const emit = defineEmits<{
  (e: "openCustomer", id: string): void;
  (e: "back"): void;
}>();
```

### Muster: Reaktive Formulare

**Einfaches v-model Binding:**
```vue
<input v-model="form.name" class="kit-input" />
<input v-model="form.email" type="email" class="kit-input" />

<script setup>
const form = ref({ name: "", email: "" });
</script>
```

**Submit über Service:**
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

### Muster: Pagination

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

### Muster: Modal/Formular-Modal

```vue
<div v-if="showModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
  <div class="bg-bg-secondary rounded-xl p-6">
    <h2>{{ isEdit ? "Bearbeiten" : "Erstellen" }}</h2>

    <form @submit.prevent="save">
      <input v-model="form.name" />
      <button type="submit">Speichern</button>
      <button @click="close">Abbrechen</button>
    </form>
  </div>
</div>
```

---

## 12. Wichtige Dateien zum Ändern beim Hinzufügen eines Moduls

1. **layouts/app-manager/appRegistry.ts** - App registrieren
2. **layouts/components/Dock.vue** - Dock-Item hinzufügen
3. **router/index.ts** (optional) - Route hinzufügen
4. Modul-Ordner unter `modules/` erstellen

---

## 13. Umgebungs-Setup

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

## 14. Build & Ausführung

```bash
# Dependencies installieren
pnpm install

# Entwicklung
pnpm run dev

# Build
pnpm run build

# Vorschau
pnpm run preview
```

---

## 15. Technologie-Stack

- **Vue 3** - Framework
- **Vite** - Build-Tool (mit rolldown-vite)
- **TypeScript** - Typ-Sicherheit
- **Tailwind CSS 4** - Styling
- **Vue Router 4** - Globales Routing
- **Pinia 3** - State Management (eingerichtet, minimal genutzt)
- **Axios** - HTTP-Client
- **Lucide Vue Next** - Icons

---

## Zusammenfassung

Das WorkmateOS Frontend verwendet eine **modulare fensterbasierte Architektur**, bei der:

1. **Module eigenständig sind** mit eigenen Pages, Components, Services, Types
2. **Composables lokalen Zustand verwalten** (Navigation, Datenabruf)
3. **Services API-Aufrufe handhaben** (keine HTTP-Logik in Komponenten)
4. **Types alles typsicher halten**
5. **Fenstermanager** schwebende Fenster mit Drag/Resize ermöglicht
6. **Design-Tokens + Tailwind** konsistentes Styling bieten
7. **Kein komplexes Routing** - Module verwenden interne Ansichtswechsel

Um ein neues Modul hinzuzufügen: Ordnerstruktur erstellen → Typen definieren → Service erstellen → Composables erstellen → Seiten erstellen → Modul-Einstiegspunkt erstellen → In appRegistry registrieren → Dock-Item hinzufügen.
