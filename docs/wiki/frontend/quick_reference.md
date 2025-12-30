---
layout: default
title: Quick Reference
parent: Frontend
grand_parent: Wiki
nav_order: 3
---

# WorkmateOS Frontend - Schnellreferenz-Leitfaden

## Dateispeicherorte - Schnellsuche

### Kernanwendungsdateien
- **Entry Point**: `ui/src/main.ts`
- **Root-Komponente**: `ui/src/App.vue`
- **Globaler Router**: `ui/src/router/index.ts`
- **Main Layout**: `ui/src/layouts/AppLayout.vue`

### Modul-System
- **App Registry** (hier neue Module hinzufügen): `ui/src/layouts/app-manager/appRegistry.ts`
- **Window Manager**: `ui/src/layouts/app-manager/useAppManager.ts`
- **Window Container**: `ui/src/layouts/app-manager/WindowHost.vue`
- **Window Wrapper**: `ui/src/layouts/app-manager/WindowFrame.vue`

### Navigations-Komponenten
- **Topbar**: `ui/src/layouts/components/Topbar.vue`
- **Dock** (App-Launcher, hier Items hinzufügen): `ui/src/layouts/components/Dock.vue`

### API & Services
- **API-Client** (Axios-Setup): `ui/src/services/api/client.ts`
- **Assets**: `ui/src/services/assets.ts`

### Globale Composables
- `ui/src/composables/useDashboard.ts`
- `ui/src/composables/useEmployees.ts`
- `ui/src/composables/useProjects.ts`

### Styling
- **Design Tokens**: `ui/src/styles/tokens.css` (CSS Custom Properties)
- **Basis-Styles**: `ui/src/styles/base.css` (Globale Styles + Tailwind)
- **Komponenten-Styles**: `ui/src/styles/components/button.css`

### Bestehende Module

#### CRM-Modul
```
ui/src/modules/crm/
├── CrmApp.vue                      # Entry Point
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
│   ├── useCrmNavigation.ts         # Modulinternes Routing
│   ├── useCrmStats.ts              # Stats Loading State
│   └── useCrmActivity.ts           # Activity Management
├── services/
│   └── crm.service.ts              # API-Aufrufe
└── types/
    ├── customer.ts
    ├── contact.ts
    ├── activity.ts
    └── stats.ts
```

#### Dashboard-Modul
```
ui/src/modules/dashboard/
├── pages/DashboardPage.vue
├── components/
│   ├── WidgetRenderer.vue
│   ├── widgets/StatsWidget.vue
│   ├── widgets/RemindersWidget.vue
│   ├── widgets/ShortcutsWidget.vue
│   ├── widgets/ActivityFeedWidget.vue
│   └── ... weitere Widgets
├── services/
│   └── widgetRegistry.ts           # Widget-Registrierung
└── types/
    └── widgetTypes.ts
```

---

## Häufige Aufgaben

### Aufgabe 1: Neues Modul hinzufügen

**Zu erstellende Dateien:**
1. `ui/src/modules/mymodule/MyModuleApp.vue` - Entry Point
2. `ui/src/modules/mymodule/types/mymodule.ts` - Typen
3. `ui/src/modules/mymodule/services/mymodule.service.ts` - API-Aufrufe
4. `ui/src/modules/mymodule/composables/useMyModuleNav.ts` - Navigation
5. `ui/src/modules/mymodule/pages/MyPage.vue` - Seiten
6. `ui/src/modules/mymodule/components/MyComponent.vue` - Komponenten

**Zu modifizierende Dateien:**
1. `ui/src/layouts/app-manager/appRegistry.ts` - App zum `apps`-Array hinzufügen
2. `ui/src/layouts/components/Dock.vue` - Item zum `dockItems`-Array hinzufügen
3. `ui/src/router/index.ts` (optional) - Child-Route hinzufügen

---

### Aufgabe 2: API-Endpunkt zum Service hinzufügen

**Speicherort**: `ui/src/modules/crm/services/crm.service.ts`

```typescript
async getCustomers(): Promise<Customer[]> {
  const { data } = await api.get("/api/backoffice/crm/customers");
  return data;
}
```

---

### Aufgabe 3: Datenabruf-Composable erstellen

**Speicherort**: `ui/src/modules/crm/composables/useCrmStats.ts`

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

### Aufgabe 4: Composable in Komponente verwenden

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

### Aufgabe 5: Navigation zum Modul hinzufügen

**Im Modul-Entry** (`CrmApp.vue`):
```typescript
const { view, activeCustomerId, goCustomerDetail, goCustomers } = useCrmNavigation();
```

**In Child-Komponente**:
```typescript
emit("openCustomer", id);
// Parent fängt ab: @openCustomer="goCustomerDetail"
```

---

### Aufgabe 6: Komponente stylen

**Tailwind verwenden (Inline-Klassen):**
```vue
<div class="px-4 py-2 bg-white/5 border border-white/10 rounded">
  <h2 class="text-lg font-semibold text-white">Titel</h2>
</div>
```

**Design Tokens verwenden (CSS):**
```vue
<div class="my-custom-card">
  <h2>Titel</h2>
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

### Aufgabe 7: Globalen Pinia Store registrieren

**Store erstellen**: `ui/src/stores/authStore.ts`
```typescript
import { defineStore } from "pinia";
import { ref } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);

  return { user };
});
```

**In Komponente verwenden**:
```typescript
import { useAuthStore } from "@/stores/authStore";

const authStore = useAuthStore();
console.log(authStore.user);
```

---

### Aufgabe 8: Typdefinition hinzufügen

**Speicherort**: `ui/src/modules/crm/types/customer.ts`

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

## Wichtige Muster

### Service-Muster
```typescript
// services/crm.service.ts
export const crmService = {
  async getCustomers() { ... },
  async getCustomer(id) { ... },
  async createCustomer(payload) { ... },
};
```

### Composable-Muster
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

### Komponenten-Event-Muster
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

### Modul-Navigations-Muster
```typescript
// In CrmApp.vue
const { view, activeId, goList, goDetail } = useCrmNavigation();

// In CustomersListPage.vue
emit("openCustomer", id);

// In CrmApp.vue
@openCustomer="goDetail"
```

---

## Umgebungsvariablen

### .env (ui/.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

### Zugriff im Code
```typescript
import.meta.env.VITE_API_BASE_URL
```

---

## Anwendung ausführen

```bash
# Abhängigkeiten installieren
cd ui
pnpm install

# Entwicklungsserver (Hot Reload)
pnpm run dev
# Zugriff unter: http://localhost:5173

# Für Produktion bauen
pnpm run build

# Produktions-Build in der Vorschau anzeigen
pnpm run preview
```

---

## Komponentenhierarchie - Schnellübersicht

```
main.ts
  └─ App.vue
      └─ Router
          ├─ /app → AppLayout
          │    ├─ Topbar
          │    ├─ WindowHost
          │    │   └─ WindowFrame (mehrere Instanzen)
          │    │       └─ CrmApp, ProjectsApp, etc (Module)
          │    └─ Dock
          │
          ├─ /under-construction
          └─ /linktree
```

---

## Pinia Store Speicherorte (aktuell leer)

Um globalen State zu erstellen, füge Stores hinzu zu:
```
ui/src/stores/
├── authStore.ts
├── userStore.ts
├── appStore.ts
└── ... etc
```

Zugriff mit:
```typescript
import { useAuthStore } from "@/stores/authStore";
const authStore = useAuthStore();
```

---

## Verfügbare Icons (lucide-vue-next)

Verwendet in Dock und gesamter UI:
```typescript
import { Users, Briefcase, Timer, Receipt, Wallet, MessageSquare } from "lucide-vue-next";
```

Siehe: https://lucide.dev/

---

## TypeScript-Pfad-Aliase

```
@ → ui/src/
```

Beispiel-Imports:
```typescript
import CrmApp from "@/modules/crm/CrmApp.vue";
import { crmService } from "@/modules/crm/services/crm.service";
import type { Customer } from "@/modules/crm/types/customer";
import { useAppManager } from "@/layouts/app-manager/useAppManager";
import api from "@/services/api/client";
```

---

## Tailwind-Klassen - Schnellreferenz

**Farben:**
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

## Debugging-Tipps

### API-Antworten prüfen
```typescript
const { data } = await api.get("/api/endpoint");
console.log(data);
```

### Komponenten-State prüfen
```vue
<script setup>
const myRef = ref("value");
</script>

<template>
  <!-- Debug-Ausgabe -->
  <pre>{{ myRef }}</pre>
</template>
```

### Router-State prüfen
```typescript
import { useRouter, useRoute } from "vue-router";
const router = useRouter();
const route = useRoute();
console.log(route.path, route.params);
```

### Window Manager State prüfen
```typescript
import { useAppManager } from "@/layouts/app-manager/useAppManager";
const { windows, activeWindow } = useAppManager();
console.log(windows.value, activeWindow.value);
```

---

## Häufige Fehler & Lösungen

### "Cannot find module '@/modules/...'"
- Pfad in Import-Anweisung prüfen
- `@`-Alias korrekt verwenden
- Prüfen, ob Datei existiert

### "Type '...' is not assignable to type '...'"
- Typdefinitionen in `types/`-Ordner prüfen
- Sicherstellen, dass API-Antwort zum Interface passt

### "composable not defined"
- Von korrektem Pfad importieren: `from "../../composables/useXxx"`
- Sicherstellen, dass `useXxx` exportiert ist

### API-Aufrufe geben undefined zurück
- API-Basis-URL in `.env` prüfen
- Verifizieren, dass API-Endpunkt-Pfad zum Backend passt
- Loading-State prüfen, bevor auf Daten zugegriffen wird

---

## Schnellbefehle

```bash
# Abhängigkeiten installieren
pnpm install

# Dev-Server starten
pnpm run dev

# Build
pnpm run build

# Code formatieren (falls prettier konfiguriert)
pnpm run format

# Typen prüfen
vue-tsc --noEmit
```
