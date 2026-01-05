---
layout: default
title: Visual Guide
parent: Frontend
grand_parent: Wiki
nav_order: 4
---

# WorkmateOS Frontend-Architektur - Visuelle Übersicht

## Anwendungsstruktur-Hierarchie

```
┌─────────────────────────────────────────────────────────────────┐
│                     main.ts (Entry Point)                       │
│                   Erstellt App + Pinia + Router                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        App.vue (Root)                           │
│                 Einfacher RouterView-Delegat                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Vue Router (router/index.ts)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Route: "/" → umleiten zu "/under-construction"          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Route: "/app" → AppLayout (Hauptanwendung)              │  │
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
        │  (Hauptcontainer mit 3 Teilen)       │
        └──────────────────────────────────────┘
                  │         │         │
        ┌─────────┴────┐    │    ┌────┴─────────┐
        ▼              ▼    ▼    ▼              ▼
    ┌────────┐   ┌───────────────┐   ┌────────┐
    │ Topbar │   │ WindowHost    │   │  Dock  │
    │(Fixed) │   │(App-Fenster)  │   │(Fixed) │
    └────────┘   └───────────────┘   └────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │WindowFrame│          │WindowFrame│
        │(CRM-App) │          │(Projekte)│
        └──────────┘          └──────────┘
             │                     │
             ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │ CrmApp   │          │ProjectsApp
        │(Modul)   │          │(Modul)   │
        └──────────┘          └──────────┘
```

---

## Modulinterne Architektur (CRM-Beispiel)

```
┌───────────────────────────────────────────────────────────┐
│              CrmApp.vue (Modul-Entry)                     │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Verwendet: useCrmNavigation()                       │ │
│  │   - view: "dashboard" | "customers" | ...          │ │
│  │   - activeCustomerId, activeContactId              │ │
│  │   - Navigationsfunktionen: goCustomers, etc        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Bedingtes Rendering basierend auf view-State       │ │
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
│     Pages-Layer              │  │   Components-Layer           │
├──────────────────────────────┤  ├──────────────────────────────┤
│ - CrmDashboardPage.vue       │  │ - CustomerCard.vue           │
│ - CustomersListPage.vue      │  │ - CustomerForm.vue           │
│ - CustomerDetailPage.vue     │  │ - ContactCard.vue            │
│ - ContactsListPage.vue       │  │ - ContactForm.vue            │
│ - ContactDetailPage.vue      │  │ - CrmKpiCustomers.vue        │
│                              │  │ - CrmRecentActivity.vue      │
│ (Emit Events, kein Routing) │  │ - CrmShortcuts.vue           │
└──────────────────────────────┘  └──────────────────────────────┘
        │                                 │
        └────────────────┬────────────────┘
                         ▼
        ┌────────────────────────────────┐
        │   Services/Composables-Layer   │
        ├────────────────────────────────┤
        │ • crmService (HTTP-Aufrufe)    │
        │ • useCrmNavigation (State)     │
        │ • useCrmStats (fetch + State)  │
        │ • useCrmActivity (fetch State) │
        └────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │     Typen / Interfaces         │
        ├────────────────────────────────┤
        │ - Customer                     │
        │ - Contact                      │
        │ - CrmActivity                  │
        │ - CrmStats                     │
        └────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │    Gemeinsamer API-Client      │
        │  (services/api/client.ts)      │
        │  Axios-Instanz mit             │
        │  Interceptors                  │
        └────────────────────────────────┘
```

---

## Fensterverwaltungssystem

```
┌──────────────────────────────────────────────────────────────────┐
│                  useAppManager() Composable                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ State:                                                     │ │
│  │  - windows: WindowApp[]    (Reaktives Array)              │ │
│  │  - activeWindow: Ref<string|null>  (Aktuell fokussiert)   │ │
│  │  - zCounter: number        (Für Layering)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ WindowApp Interface:                                       │ │
│  │  {                                                         │ │
│  │    id: string;              // Eindeutige Fensterinstanz  │ │
│  │    appId: string;           // Referenz zur App-Registry  │ │
│  │    title: string;                                         │ │
│  │    component: Component;                                  │ │
│  │    props?: Record<string, any>;                           │ │
│  │    x, y, width, height: number;  // Position/Größe       │ │
│  │    z: number;               // Layer-Tiefe               │ │
│  │  }                                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Methoden:                                                  │ │
│  │  • openWindow(appId)        → Öffnet/fokussiert App       │ │
│  │  • closeWindow(id)          → Schließt Fenster            │ │
│  │  • focusWindow(id)          → Bringt in Vordergrund       │ │
│  │  • startDragFor(id, e)      → Initiiert Drag              │ │
│  │  • startResizeFor(id, e)    → Initiiert Resize            │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │   appRegistry.ts               │
            │  (Zentrale App-Registrierung)  │
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
            │   // Weitere Apps...           │
            │ ]                              │
            └────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │   WindowHost.vue               │
            │  (Rendert alle Fenster)        │
            └────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────┐
        ▼                                     ▼
┌─────────────────────┐              ┌─────────────────────┐
│  WindowFrame.vue    │              │  WindowFrame.vue    │
│  (CRM-Instanz)      │              │  (Projekt-Instanz)  │
│                     │              │                     │
│ Titelleiste (Ziehbar)│             │ Titelleiste (Ziehbar)│
│ Inhaltsbereich      │              │ Inhaltsbereich      │
│ Größenänderungs-    │              │ Größenänderungs-    │
│ Handle              │              │ Handle              │
│ Schließen-Button    │              │ Schließen-Button    │
└─────────────────────┘              └─────────────────────┘
        │                                     │
        ▼                                     ▼
┌─────────────────────┐              ┌─────────────────────┐
│   CrmApp.vue        │              │  ProjectsApp.vue    │
│   (Aktiv)           │              │   (Hintergrund)     │
└─────────────────────┘              └─────────────────────┘
```

---

## Datenfluss: Datenabruf-Muster

```
Komponente (Page)
    │
    ├─ onMounted()
    │   └─→ Ruft composable.fetchData() auf
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
    ├─ Ruft api.get("/api/...") auf
    │
    ▼
API-Client (Axios-Instanz)
    │
    ├─ Request-Interceptor (JWT-Token hinzufügen)
    ├─ HTTP-Request durchführen
    ├─ Response-Interceptor (Fehler behandeln)
    │
    ▼
Backend-API (z.B. FastAPI)
    │
    ▼
API-Client (gibt Antwort zurück)
    │
    ▼
Service (extrahiert Daten)
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
Komponente (Template)
    │
    ├─ v-if="loading" → Spinner anzeigen
    ├─ v-else-if="error" → Fehler anzeigen
    ├─ v-else → Daten anzeigen (stats.value)
    │
    └─ UI aktualisiert sich automatisch (reaktiv)
```

---

## Styling-Architektur

```
┌─────────────────────────────────────────────────┐
│        Design Tokens (tokens.css)               │
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
│  Tailwind CSS    │        │  Komponenten-CSS │
│  (base.css)      │        │  (button.css)    │
├──────────────────┤        ├──────────────────┤
│ @layer base      │        │ .kit-btn-primary │
│ @layer components│        │ .kit-input       │
│ @layer utilities │        │ .kit-label       │
│                  │        │ ... etc ...      │
│ Tailwind-Klassen │        │                  │
│ px-4, py-2, etc  │        │ Scoped in .vue   │
└──────────────────┘        └──────────────────┘
        │                            │
        └─────────────┬──────────────┘
                      ▼
        ┌──────────────────────────┐
        │   Komponenten-Styling    │
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

## Datentypen-Organisation

```
Modul-Root: src/modules/crm/

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
│   └─ Navigations-State (view, activeId)
├── useCrmStats.ts
│   └─ Datenabruf + Loading-State
└── useCrmActivity.ts
    └─ Activity-Management

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

## Komponentenkommunikations-Muster

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
        │  Ruft auf: goCustomerDetail(id)
        │           ↓
        │  Aktualisiert: activeCustomerId = id
        │           ↓
        │  Aktualisiert: view = "customer-detail"
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
        ├─ Props: keine
        │         (State über Composable übergeben)
        ├─ Emits: openCustomer(id), openDashboard()
        └─ State: search, page (lokal)
                  customers (vom Service)
                  loading (vom Composable)

Props nach unten → Events nach oben → Composables für gemeinsamen State
```

---

## Neues Modul hinzufügen: Dateierstellungs-Checkliste

```
✓ Schritt 1: Verzeichnisstruktur erstellen
  └─ ui/src/modules/mymodule/

✓ Schritt 2: Typdefinitionen erstellen
  └─ types/mymodule.ts
     export interface MyResource { ... }

✓ Schritt 3: Service-Layer erstellen
  └─ services/mymodule.service.ts
     export const mymoduleService = { ... }

✓ Schritt 4: Navigations-Composable erstellen
  └─ composables/useMyModuleNav.ts
     export function useMyModuleNav() { ... }

✓ Schritt 5: Pages erstellen
  └─ pages/MyPage.vue
     pages/index.ts

✓ Schritt 6: Komponenten erstellen
  └─ components/MyComponent.vue
     components/index.ts

✓ Schritt 7: Modul-Entry-Point erstellen
  └─ MyModuleApp.vue
     (Verwendet useMyModuleNav, rendert Pages bedingt)

✓ Schritt 8: Modul registrieren
  └─ layouts/app-manager/appRegistry.ts
     Zum apps[]-Array hinzufügen

✓ Schritt 9: Dock-Item hinzufügen
  └─ layouts/components/Dock.vue
     Zum dockItems[]-Array hinzufügen

✓ Schritt 10 (Optional): Route hinzufügen
  └─ router/index.ts
     Child-Route unter /app hinzufügen
```
