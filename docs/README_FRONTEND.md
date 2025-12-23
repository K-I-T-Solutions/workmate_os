# WorkmateOS Frontend Documentation

Welcome to the WorkmateOS frontend documentation. This directory contains comprehensive guides for understanding and developing the Vue 3 + TypeScript frontend application.

## Documentation Files

### 1. **UI_ARCHITECTURE.md** - Complete Architecture Guide
The most comprehensive guide covering:
- Complete directory structure with explanations
- Application bootstrap flow (main.ts → App.vue → Router)
- Router configuration and routing patterns
- Module system architecture
- Window manager system for floating windows
- CRM module as a complete example
- API client setup with Axios
- Layout system (Topbar, Dock, WindowHost)
- State management with Pinia
- Styling system (Design tokens + Tailwind)
- Step-by-step guide to creating a new module
- Common patterns and best practices

**Use this when:** You need a deep understanding of how everything works together, or you're creating a new module from scratch.

### 2. **ARCHITECTURE_VISUAL.md** - Visual Diagrams
ASCII diagrams showing:
- Application structure hierarchy
- Module internal architecture
- Window manager system
- Data flow patterns
- Styling architecture
- Component communication patterns
- File creation checklist for new modules

**Use this when:** You want to visualize how components relate to each other.

### 3. **QUICK_REFERENCE.md** - Quick Lookup Guide
Fast reference for:
- File locations for common tasks
- Existing module structures (CRM, Dashboard)
- Code snippets for common tasks
- Important patterns (Service, Composable, Events)
- Environment variables
- Debugging tips
- Common errors and fixes

**Use this when:** You need to quickly find a file location or remember a pattern.

---

## Quick Start for Developers

### Understanding the Architecture (5 min read)

1. **Entry Point**: `main.ts` creates Vue app + Pinia + Router
2. **Root Component**: `App.vue` just renders RouterView
3. **Main Router**: Handles `/app` route → `AppLayout`
4. **AppLayout**: Contains Topbar + WindowHost + Dock
5. **Modules**: Self-contained apps (CRM, Dashboard, etc.) that open in windows

### How Modules Work (Unique Feature)

Unlike traditional web apps, WorkmateOS uses a **desktop-like window manager**:

```
Dock Item (e.g., "CRM") 
    ↓ Click to open
useAppManager.openWindow("crm")
    ↓ Looks up in appRegistry
CrmApp component
    ↓ Renders in WindowFrame
Module with internal routing (no Vue Router)
    ↓ Uses composable for navigation
Pages and components
```

**Key Insight**: Modules handle their own internal routing using composables, not Vue Router. This allows multiple instances of the same module to be open simultaneously.

### Module Structure Pattern

Every module follows this structure:

```
modules/crm/
├── CrmApp.vue                    # Entry point, uses useCrmNavigation()
├── types/customer.ts             # TypeScript interfaces
├── services/crm.service.ts        # API calls via axios
├── composables/useCrmNavigation.ts # Internal navigation state
├── pages/                         # Full-page components
│   ├── CustomersListPage.vue
│   └── CustomerDetailPage.vue
└── components/                    # Reusable components
    ├── CustomerCard.vue
    └── CustomerForm.vue
```

### The Data Flow

```
Component mounts
    ↓
Calls composable.fetch()
    ↓
Composable calls service.getData()
    ↓
Service calls api.get("/endpoint")
    ↓
Axios sends request with interceptors
    ↓
Backend API responds
    ↓
Service returns data to composable
    ↓
Composable updates reactive refs (stats.value = data)
    ↓
Component template re-renders (automatic with Vue reactivity)
```

---

## Key Technologies

| Technology | Purpose | Version |
|-----------|---------|---------|
| Vue 3 | UI framework | ^3.5.22 |
| TypeScript | Type safety | ~5.9.3 |
| Vite | Build tool | 7.1.14 (rolldown) |
| Tailwind CSS | Styling | ^4.1.16 |
| Vue Router | Global routing | ^4.6.3 |
| Pinia | State management | ^3.0.4 |
| Axios | HTTP client | ^1.13.2 |
| Lucide Vue | Icons | ^0.554.0 |

---

## Common Development Tasks

### Creating a New Module

See: **UI_ARCHITECTURE.md → Section 10: Creating a New Module**

Summary:
1. Create folder structure under `ui/src/modules/mymodule/`
2. Define types in `types/`
3. Create service in `services/`
4. Create composable in `composables/`
5. Create pages in `pages/`
6. Create module entry point `MyModuleApp.vue`
7. Register in `appRegistry.ts`
8. Add dock item in `Dock.vue`

### Adding an API Call

1. Add method to service (e.g., `crm.service.ts`)
2. Create composable that wraps it (e.g., `useCrmStats.ts`)
3. Use composable in component

Example:
```typescript
// Service
async getCustomers() { return api.get("/api/customers"); }

// Composable
const { data, loading, error, fetch } = useMyComposable();

// Component
onMounted(() => fetch());
<div v-if="loading">Loading...</div>
<div>{{ data }}</div>
```

### Styling Components

- **Global tokens**: `src/styles/tokens.css` (CSS custom properties)
- **Tailwind classes**: Use directly in templates
- **Component scoped styles**: `<style scoped>` in Vue files

Example:
```vue
<div class="px-4 py-2 bg-white/5 border border-white/10">
  <h2 class="text-lg font-semibold">Title</h2>
</div>
```

---

## Architecture Highlights

### Window Manager
Unique feature allowing floating, draggable, resizable windows:
- `useAppManager()` - Composable managing window state
- `WindowHost.vue` - Container for all windows
- `WindowFrame.vue` - Individual window with titlebar/resize

### Service Layer
Clean separation of API concerns:
- `services/api/client.ts` - Shared Axios instance
- `modules/*/services/*.ts` - Module-specific API methods

### Composables
Vue 3 composables for state management:
- Navigation: `useCrmNavigation()` (internal routing)
- Data fetching: `useCrmStats()` (loading + error states)
- Global: `useDashboard()` (shared across app)

### Design System
Consistent styling through tokens:
- Colors, spacing, typography defined in CSS custom properties
- Tailwind for utility classes
- Component-specific styles in scoped `<style>` blocks

---

## Project Structure at a Glance

```
workmate_os/
├── ui/                          # Frontend (this is you!)
│   ├── src/
│   │   ├── main.ts              # Entry point
│   │   ├── App.vue              # Root component
│   │   ├── router/              # Vue Router
│   │   ├── layouts/             # Layout components + app manager
│   │   ├── modules/             # Feature modules (CRM, Dashboard, etc)
│   │   ├── services/            # API client and global services
│   │   ├── composables/         # Global composables
│   │   └── styles/              # Design system
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                     # FastAPI backend (not your concern)
└── docs/
    ├── UI_ARCHITECTURE.md       # This you're reading
    ├── ARCHITECTURE_VISUAL.md   # Diagrams
    └── QUICK_REFERENCE.md       # Quick lookup
```

---

## Important Files You'll Modify Frequently

| File | Purpose | When to Edit |
|------|---------|--------------|
| `appRegistry.ts` | Register new modules | Adding new module |
| `Dock.vue` | Add dock items | Adding new module |
| `router/index.ts` | Global routes | Adding new routes |
| `modules/*/services/*.ts` | API methods | New endpoints |
| `modules/*/types/*.ts` | Data types | New data structures |
| `modules/*/composables/*.ts` | State management | New state logic |
| `styles/tokens.css` | Design tokens | Updating design system |

---

## Important Concepts

### Modules are NOT Routed (Unique!)
Traditional: Route changes → Component loads
WorkmateOS: Dock item click → Window opens → Module internal state changes

This means:
- No URL changes when navigating within a module
- Multiple instances of same module can coexist
- Navigation is faster (no router involvement)
- BUT: Bookmark/URL doesn't reflect internal module state

### Composables > Vue Router Navigation
Instead of route params, modules use composables:
```typescript
// Old way (not used)
// useRoute().params.customerId

// New way
const { activeCustomerId } = useCrmNavigation();
```

### Service + Composable Pattern
Always use two-layer approach:
1. **Service**: Just HTTP calls, no state
2. **Composable**: Wraps service, manages loading/error state

This separation keeps concerns clean and reusable.

---

## Debugging Guide

### Check Network Requests
Browser DevTools → Network tab → Look for API calls
Verify:
- Correct URL endpoint
- Request headers (Content-Type)
- Response status (200, 404, 500, etc.)

### Check Component State
```vue
<pre>{{ someRef }}</pre>  <!-- Debug output -->
```

### Check Window Manager
Open browser console:
```javascript
// Check if windows are opening
import { useAppManager } from "@/layouts/app-manager/useAppManager";
const { windows } = useAppManager();
console.log(windows.value);
```

### TypeScript Errors
```bash
cd ui
vue-tsc --noEmit  # Check for type errors
```

---

## Next Steps

1. **Read**: Start with UI_ARCHITECTURE.md for complete understanding
2. **Explore**: Look at CRM module (`ui/src/modules/crm/`) as reference
3. **Create**: Build a small test module following patterns
4. **Refer**: Use QUICK_REFERENCE.md for fast lookups

---

## Testing the Setup

```bash
cd ui
pnpm install
pnpm run dev
# Visit http://localhost:5173
```

You should see:
- WorkmateOS topbar with logo and clock
- Window area in center
- Dock at bottom with app icons (CRM, Projects, etc.)

Click CRM icon to open a floating window with the CRM module.

---

## Getting Help

1. **Architecture questions**: See UI_ARCHITECTURE.md
2. **Code patterns**: Check QUICK_REFERENCE.md
3. **Visual understanding**: Review ARCHITECTURE_VISUAL.md
4. **Specific file locations**: Use QUICK_REFERENCE.md Quick Lookup

---

## Summary

WorkmateOS frontend is a **Vue 3 + TypeScript** application with a unique **desktop-like window manager** architecture. Modules are self-contained and opened as floating windows, each handling their own internal routing via composables rather than Vue Router. The app emphasizes clean separation of concerns: Services handle API calls, Composables manage state, Components render UI. All styling is done through a consistent design token system + Tailwind CSS.

Happy coding!

