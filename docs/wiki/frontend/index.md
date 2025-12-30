# Frontend Documentation Index

This document serves as an index to all frontend documentation for WorkmateOS.

## Documentation Files

All documentation is located in `/docs/` directory:

### 1. README_FRONTEND.md (START HERE)
**File**: `/docs/README_FRONTEND.md`
**Size**: ~10 KB
**Read Time**: 10-15 minutes

The entry point for all frontend documentation. Contains:
- Overview of what's in each documentation file
- Quick start for developers (5 min version)
- How modules work (unique desktop-like architecture)
- Module structure pattern
- Data flow explanation
- Key technologies and versions
- Common development tasks
- Architecture highlights
- Debugging guide
- Next steps

**Best for**: Getting oriented, understanding overall architecture

---

### 2. UI_ARCHITECTURE.md (COMPREHENSIVE GUIDE)
**File**: `/docs/UI_ARCHITECTURE.md`
**Size**: ~29 KB
**Read Time**: 30-45 minutes

Complete in-depth guide covering:
- Complete directory structure with full paths and explanations
- Application bootstrap flow (main.ts → App.vue → Router)
- Router configuration with examples
- Module system architecture in detail
- Window manager system with interfaces and methods
- CRM module as complete real-world example
- Service layer pattern (crm.service.ts)
- Navigation composables pattern
- Data fetching composables pattern
- Page components pattern
- Type definitions organization
- Component barrel exports
- API client setup with Axios
- Layout system (Topbar, Dock, WindowHost, WindowFrame)
- State management with Pinia
- Styling system (Design tokens + Tailwind)
- Step-by-step guide to creating new module (10 steps)
- Common patterns and best practices
- Environment setup
- Building and running
- Technology stack summary

**Best for**: Deep understanding, creating new modules, reference material

---

### 3. ARCHITECTURE_VISUAL.md (DIAGRAMS)
**File**: `/docs/ARCHITECTURE_VISUAL.md`
**Size**: ~25 KB
**Read Time**: 15-20 minutes

ASCII art diagrams showing:
- Application structure hierarchy
- Module internal architecture (CRM example)
- Window manager system flow
- Data fetching flow
- Styling architecture
- Data types organization
- Component communication pattern
- File creation checklist

**Best for**: Visual learners, understanding relationships, seeing data flow

---

### 4. QUICK_REFERENCE.md (LOOKUP GUIDE)
**File**: `/docs/QUICK_REFERENCE.md`
**Size**: ~11 KB
**Read Time**: Varies (reference material)

Quick lookup for:
- File locations for common tasks
- Existing module structures (CRM, Dashboard)
- Common task code snippets:
  - Adding new module
  - Adding API endpoint
  - Creating data fetching composable
  - Using composable in component
  - Adding navigation
  - Styling components
  - Creating Pinia store
  - Adding type definitions
- Important patterns with code
- Environment variables
- Running the application
- Component hierarchy map
- Available icons (lucide-vue-next)
- TypeScript path aliases
- Tailwind classes quick reference
- Debugging tips
- Common errors and fixes
- Quick commands

**Best for**: Fast lookups, remembering patterns, finding file locations

---

## Recommended Reading Order

### For New Developers (First Time)
1. README_FRONTEND.md (10-15 min)
2. ARCHITECTURE_VISUAL.md (15-20 min) - Skip if not a visual learner
3. UI_ARCHITECTURE.md (30-45 min) - Focus on sections 1-5

**Total: ~1 hour** to get comfortable with the architecture

### For Creating a New Module
1. QUICK_REFERENCE.md → Task 1: Add a New Module
2. UI_ARCHITECTURE.md → Section 10: Creating a New Module
3. Reference CRM module: `ui/src/modules/crm/`

**Total: 30-45 minutes**

### For Daily Development
Keep QUICK_REFERENCE.md open as reference material

---

## Quick Navigation by Task

### "I want to understand the overall architecture"
→ README_FRONTEND.md

### "I want to create a new module"
→ UI_ARCHITECTURE.md (Section 10) + QUICK_REFERENCE.md (Task 1)

### "I want to add a new API endpoint"
→ QUICK_REFERENCE.md (Task 2)

### "I want to understand how data flows"
→ ARCHITECTURE_VISUAL.md + README_FRONTEND.md (Data Flow section)

### "I need to find a file location"
→ QUICK_REFERENCE.md (File Locations Quick Lookup)

### "I'm getting an error"
→ QUICK_REFERENCE.md (Common Errors & Fixes)

### "I want to understand module navigation"
→ UI_ARCHITECTURE.md (Section 5: Module Structure Pattern)

### "I want to add styling to a component"
→ README_FRONTEND.md (Styling Components) or QUICK_REFERENCE.md (Task 6)

### "I need to use Pinia for global state"
→ QUICK_REFERENCE.md (Task 7)

### "I want to understand the window manager"
→ UI_ARCHITECTURE.md (Section 4: Module System Architecture) + ARCHITECTURE_VISUAL.md (Window Manager System)

---

## Key Concepts to Understand

These are explained in detail in the documentation:

1. **Window Manager**: Desktop-like floating windows (not traditional routing)
2. **Modules**: Self-contained apps with internal routing (no Vue Router)
3. **Service Layer**: Handles API calls (crm.service.ts)
4. **Composables**: Manage state and wrap services (useCrmStats.ts)
5. **Design Tokens**: CSS custom properties for consistent styling
6. **App Registry**: Central place to register all modules
7. **Type Safety**: Strong TypeScript usage throughout

---

## File Locations Quick Reference

**Core Files**:
- Entry: `ui/src/main.ts`
- Root: `ui/src/App.vue`
- Router: `ui/src/router/index.ts`
- Layout: `ui/src/layouts/AppLayout.vue`

**Module System**:
- Registry: `ui/src/layouts/app-manager/appRegistry.ts`
- Window Manager: `ui/src/layouts/app-manager/useAppManager.ts`
- Dock: `ui/src/layouts/components/Dock.vue`

**API**:
- Client: `ui/src/services/api/client.ts`

**Styles**:
- Tokens: `ui/src/styles/tokens.css`
- Base: `ui/src/styles/base.css`

**Example Module (CRM)**:
- Entry: `ui/src/modules/crm/CrmApp.vue`
- Service: `ui/src/modules/crm/services/crm.service.ts`
- Navigation: `ui/src/modules/crm/composables/useCrmNavigation.ts`

See QUICK_REFERENCE.md for complete file listing.

---

## Technology Stack

- Vue 3 (^3.5.22)
- TypeScript (~5.9.3)
- Vite 7.1.14 (with rolldown)
- Tailwind CSS 4
- Vue Router 4
- Pinia 3
- Axios ^1.13.2
- Lucide Vue ^0.554.0

---

## Getting Started Commands

```bash
# Install dependencies
cd ui
pnpm install

# Start development server
pnpm run dev
# Visit http://localhost:5173

# Build for production
pnpm run build

# Check TypeScript errors
vue-tsc --noEmit
```

---

## How to Use This Documentation

1. **Find your documentation file** in the list above
2. **Read the recommended sections** based on your task
3. **Reference QUICK_REFERENCE.md** for code snippets and patterns
4. **Look at CRM module** (`ui/src/modules/crm/`) for real-world examples
5. **Use ARCHITECTURE_VISUAL.md** to visualize concepts

---

## Structure of Each Documentation File

### README_FRONTEND.md
- Orientation and overview
- Quick concepts
- Architecture highlights
- Common tasks
- Getting help

### UI_ARCHITECTURE.md
- Complete reference
- Code examples
- Step-by-step guides
- Best practices
- Patterns explained

### ARCHITECTURE_VISUAL.md
- ASCII diagrams
- Data flows
- Component hierarchies
- System relationships
- File creation checklist

### QUICK_REFERENCE.md
- File locations
- Code snippets
- Quick patterns
- Commands
- Debugging tips

---

## Documentation Quality

Total documentation:
- 4 comprehensive guides
- ~2,600 lines of content
- 75+ code examples
- 20+ diagrams
- Complete coverage of:
  - Architecture
  - Module creation
  - API integration
  - Styling
  - Debugging
  - Common patterns
  - Existing examples

---

## Contributing to Documentation

If you find issues or want to improve documentation:
1. Check current files in `/docs/`
2. Update relevant file
3. Keep code examples current
4. Add diagrams for complex concepts
5. Maintain consistency with other files

---

## Quick Checklist for Developers

After reading documentation, you should understand:

- [ ] How main.ts boots the app
- [ ] Why we use window manager instead of routing
- [ ] How modules are registered in appRegistry
- [ ] Service → Composable → Component pattern
- [ ] When to use types/, services/, composables/, pages/, components/
- [ ] How to create a new module from scratch
- [ ] Where to add new API endpoints
- [ ] How design tokens work
- [ ] How to style components
- [ ] How to debug common issues

---

## Need Help?

1. **"I don't understand X"** → Check README_FRONTEND.md overview
2. **"How do I do X?"** → Check QUICK_REFERENCE.md
3. **"Where is X?"** → Check QUICK_REFERENCE.md File Locations
4. **"Show me an example"** → Look at ui/src/modules/crm/ or code examples in UI_ARCHITECTURE.md
5. **"I'm getting error X"** → Check QUICK_REFERENCE.md Common Errors

---

**Last Updated**: December 23, 2025
**Documentation Version**: 1.0
**Frontend Framework**: Vue 3
**Status**: Complete and Ready to Use

