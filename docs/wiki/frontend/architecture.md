---
layout: default
title: Architektur
parent: Frontend
grand_parent: Wiki
nav_order: 1
---

# WorkmateOS Frontend Architektur

**Stack:** Next.js 15 · TypeScript · Tailwind CSS · NextAuth.js

---

## Überblick

Das WorkmateOS Frontend (UI v3) ist eine Next.js App-Router-Anwendung mit serverseitigem Rendering und Keycloak-Authentifizierung via NextAuth.js. Die Anwendung ist in Module (CRM, HR, Invoices, etc.) unterteilt, die jeweils eigene Routen unter `app/(app)/` haben.

---

## Verzeichnisstruktur

```
ui-v3/
├── app/
│   ├── (app)/               # Geschützte Routen (Auth-Guard via Layout)
│   │   ├── dashboard/
│   │   ├── crm/
│   │   │   ├── customers/
│   │   │   │   ├── page.tsx         # Kundenliste
│   │   │   │   ├── [id]/page.tsx    # Kundendetail
│   │   │   │   ├── [id]/edit/page.tsx
│   │   │   │   └── new/page.tsx
│   │   │   ├── contacts/
│   │   │   └── pipeline/
│   │   ├── invoices/
│   │   ├── projects/
│   │   ├── hr/
│   │   ├── support/
│   │   ├── documents/
│   │   ├── finance/
│   │   ├── time/
│   │   ├── knowledge/
│   │   ├── admin/
│   │   └── settings/
│   ├── auth/
│   │   └── callback/        # NextAuth Keycloak Callback
│   ├── login/
│   ├── layout.tsx
│   └── page.tsx             # Redirect → /dashboard
├── components/              # Wiederverwendbare UI-Komponenten
├── lib/                     # API-Client, Auth-Helpers
├── public/
└── next.config.ts
```

---

## Authentifizierung

Auth läuft über **NextAuth.js** mit Keycloak als OIDC-Provider (PKCE-Flow).

- Alle Routen unter `app/(app)/` sind durch ein Server-Layout geschützt
- Token wird serverseitig geprüft, kein Client-seitiger Token-State
- Keycloak-Realm: `kit` auf `login.kit-it-koblenz.de`

---

## API-Kommunikation

Ein zentraler API-Client (`lib/api.ts`) kommuniziert mit dem FastAPI-Backend. Alle Requests werden mit dem Keycloak-JWT authentifiziert.

```ts
// Beispiel
const customers = await apiClient.get('/crm/customers')
```

---

## Routing-Konventionen

| Muster | Bedeutung |
|:--|:--|
| `app/(app)/[modul]/page.tsx` | Listenansicht |
| `app/(app)/[modul]/[id]/page.tsx` | Detailansicht |
| `app/(app)/[modul]/[id]/edit/page.tsx` | Bearbeitungsformular |
| `app/(app)/[modul]/new/page.tsx` | Neues Objekt anlegen |

---

## Theme-System

4 Farbvarianten via CSS-Custom-Properties (umschaltbar in `/settings`):

- `kit-blue` (Standard)
- `kit-dark`
- `kit-warm`
- `kit-contrast`

---

## Design Guidelines

→ [Design Guidelines](./design/guidelines.md)

---

**Stand:** Juni 2026 · UI v3 · WorkmateOS v3.0
