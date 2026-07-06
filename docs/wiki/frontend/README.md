---
layout: default
title: Frontend
parent: Wiki
nav_order: 4
has_children: true
---

# WorkmateOS Frontend — Dokumentation

**Stack:** Next.js 14 · TypeScript · Tailwind CSS 4 · Base UI  
**Verzeichnis:** `ui-v3/`  
**Letzte Aktualisierung:** Juli 2026

---

## Überblick

Das Frontend nutzt den Next.js 14 App Router und ist vollständig in TypeScript geschrieben. Die Authentifizierung läuft via Keycloak PKCE — kein Client-Secret im Browser. Permissions kommen vom Backend-Endpoint `/api/auth/me`.

---

## Verzeichnisstruktur

```
ui-v3/
├── app/                      # Next.js App Router
│   ├── (app)/                # Geschützte Seiten (Auth-required)
│   │   ├── layout.tsx        # App-Shell mit Sidebar
│   │   ├── dashboard/        # Dashboard
│   │   ├── crm/              # CRM (Kunden, Kontakte)
│   │   ├── invoices/         # Rechnungen
│   │   ├── projects/         # Projekte
│   │   ├── time-tracking/    # Zeiterfassung
│   │   ├── finance/          # Finanzen
│   │   ├── hr/               # HR (Urlaub, Training, Vergütung …)
│   │   ├── documents/        # Dokumente
│   │   ├── employees/        # Mitarbeiterverwaltung
│   │   ├── support/          # Support-Tickets
│   │   ├── knowledge/        # Knowledge Base
│   │   └── settings/         # Benutzereinstellungen
│   ├── login/                # Login-Seite
│   └── auth/callback/        # PKCE Callback-Handler
├── components/
│   ├── providers/
│   │   ├── auth-provider.tsx # AuthContext, Permissions, hasPermission()
│   │   └── theme-provider.tsx
│   ├── app-sidebar.tsx       # Navigation mit Permission-Guards
│   ├── ui/                   # Base UI Komponenten (Select, Combobox, Dialog …)
│   ├── time-tracking/        # Modul-spezifische Komponenten
│   ├── crm/
│   ├── hr/
│   └── …
├── lib/
│   ├── auth/
│   │   ├── pkce.ts           # PKCE Flow, Token-Refresh, Logout-URL
│   │   └── session.ts        # Token-Lesen aus localStorage, JWT-Decode
│   └── api-client.ts         # Axios-Instanz, Bearer-Interceptor
└── types/                    # TypeScript-Definitionen
```

---

## Auth-Flow

1. Nicht eingeloggt → Redirect zu Keycloak via PKCE (`/login`)
2. Keycloak gibt `code` zurück → `/auth/callback` tauscht gegen Tokens
3. Tokens in `localStorage` gespeichert (`access_token`, `id_token`, `refresh_token`)
4. `auth-provider.tsx` lädt beim App-Start Permissions via `GET /api/auth/me`
5. `hasPermission(perm)` prüft gegen geladene Liste

---

## Permissions im Frontend

```typescript
const { hasPermission } = useAuth()

// Sidebar-Eintrag
{ label: "CRM", href: "/crm", permission: "backoffice.crm.read" }

// Action-Button
{hasPermission("backoffice.crm.write") && (
  <Button>Neuer Kunde</Button>
)}
```

Wildcard-Matching:
- `"*"` → immer `true` (Admin)
- `"backoffice.*"` → alle `backoffice.X`-Permissions
- exakter String → exakter Treffer

---

## API-Client

`lib/api-client.ts` ist eine Axios-Instanz mit:
- `baseURL` = `NEXT_PUBLIC_API_BASE`
- Request-Interceptor: setzt `Authorization: Bearer <access_token>`
- Response-Interceptor: Bei 401 → Token-Refresh versuchen, danach Logout

---

## Neue Seite anlegen

1. `app/(app)/mein-modul/page.tsx` erstellen
2. Sidebar-Eintrag in `components/app-sidebar.tsx` ergänzen (mit `permission:`-Key)
3. API-Calls über `api-client.ts` abwickeln
4. Permission-Guards auf alle Buttons und Actions setzen

---

## Dokumentationsdateien

| Datei | Inhalt |
|-------|--------|
| `architecture.md` | Ausführliche Architektur-Beschreibung |
| `quick_reference.md` | Schnell-Referenz für häufige Patterns |
