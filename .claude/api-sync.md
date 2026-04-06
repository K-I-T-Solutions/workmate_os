---
name: api-sync
description: >
  Synchronisiert das OpenAPI-Schema vom FastAPI-Backend mit dem Vue-Frontend.
  Invoke wenn: neue Backend-Endpoints gebaut wurden, Pydantic-Schemas geändert
  wurden, TypeScript-Typen veraltet sind, oder nach jedem backend-builder Einsatz.
  Exportiert /openapi.json → assets/openapi.yaml, generiert ui/src/types/openapi.ts
  via openapi-typescript, prüft TypeScript-Kompatibilität.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

## Kontext

WorkmateOS nutzt FastAPI mit automatischer OpenAPI-Schema-Generierung.
Das Frontend (Vue 3 + TypeScript) importiert Typen aus `ui/src/types/openapi.ts`.
Diese Datei wird via `openapi-typescript` aus dem Schema generiert — NICHT manuell geschrieben.

**Immer nach Backend-Änderungen (neue Modelle, Schemas, Routen) diesen Agent ausführen.**

---

## Dein Workflow

### Schritt 1: Backend läuft?

```bash
curl -s http://localhost:8000/health | head -5
```

Wenn kein Backend läuft → User auffordern: `make dev-up` zuerst.

### Schritt 2: Schema exportieren

```bash
curl -s http://localhost:8000/openapi.json \
  | python3 -c "import sys,json,yaml; yaml.dump(json.load(sys.stdin), sys.stdout, allow_unicode=True, sort_keys=False)" \
  > assets/openapi.yaml
```

Prüfe ob die Datei Inhalt hat:
```bash
wc -l assets/openapi.yaml
head -5 assets/openapi.yaml
```

Erwarteter Anfang:
```yaml
openapi: 3.1.0
info:
  title: Workmate OS
  version: ...
```

Falls `python3 -c ... yaml` nicht verfügbar (kein pyyaml):
```bash
curl -s http://localhost:8000/openapi.json > assets/openapi.json
# Dann openapi-typescript direkt auf JSON aufrufen (unterstützt beides)
```

### Schritt 3: TypeScript-Typen generieren

```bash
cd ui && pnpm run api:generate
```

Das Script (in `package.json` definiert) läuft:
```
openapi-typescript ../assets/openapi.yaml -o src/types/openapi.ts
```

Oder direkt:
```bash
cd ui && npx openapi-typescript ../assets/openapi.yaml -o src/types/openapi.ts
```

### Schritt 4: Generierte Typen prüfen

```bash
head -30 ui/src/types/openapi.ts
grep -c "export" ui/src/types/openapi.ts
```

Erwartete Struktur:
```typescript
export interface paths { ... }
export interface components {
  schemas: {
    CustomerRead: { ... }
    InvoiceCreate: { ... }
    // ...alle Pydantic-Schemas
  }
}
```

### Schritt 5: TypeScript-Check

```bash
cd ui && pnpm build
```

Alle Fehler beheben bevor fertig gemeldet wird (siehe unten).

---

## Typen im Frontend verwenden

Nach dem Sync importieren alle Components und Composables so:

```typescript
import type { components } from '@/types/openapi'

// Schema-Typen
type Customer    = components['schemas']['CustomerRead']
type Invoice     = components['schemas']['InvoiceRead']
type InvoiceItem = components['schemas']['InvoiceItemCreate']

// Nie manuell Interface nachbauen wenn der Typ existiert!
```

Verfügbare Schema-Namen prüfen:
```bash
grep "^\s\{2,4\}[A-Z]" ui/src/types/openapi.ts | head -40
```

---

## Fehlerbehandlung

### TypeScript-Fehler nach Sync

**Problem:** Altes Component nutzt gelöschtes Feld.
```
Property 'old_field' does not exist on type 'CustomerRead'
```

**Fix:** Component lesen, auf neuen Feldnamen umstellen. Nie den generierten Typ anpassen.

**Problem:** Typ hat `undefined` wo `string` erwartet wird.
```
Type 'string | undefined' is not assignable to type 'string'
```

**Fix:** Optional Chaining oder Nullish Coalescing ergänzen:
```typescript
const name = customer.name ?? ''
const city  = customer.address?.city
```

### Schema-Export schlägt fehl

```bash
# Backend nicht erreichbar?
curl -v http://localhost:8000/health

# Container läuft?
docker ps | grep backend

# Logs prüfen
make dev-logs
```

### openapi-typescript Fehler

```bash
# Version prüfen
cd ui && npx openapi-typescript --version

# Direkt mit JSON (falls YAML-Problem)
cd ui && npx openapi-typescript ../assets/openapi.json -o src/types/openapi.ts
```

---

## Änderungen an package.json prüfen

Falls `api:generate` Script noch nicht in `ui/package.json` steht, hinzufügen:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview",
    "api:generate": "openapi-typescript ../assets/openapi.yaml -o src/types/openapi.ts"
  }
}
```

---

## Makefile-Targets (Referenz)

```bash
make openapi-export   # Nur Schema exportieren
make openapi-codegen  # Nur Typen generieren (Schema muss existieren)
make openapi-sync     # Beides in einem Schritt
```

---

## Was du NICHT tust

- Keine manuellen Änderungen an `ui/src/types/openapi.ts` — wird überschrieben
- Kein manuelles Nachbauen von Pydantic-Schemas als TypeScript-Interface
- Kein Schema-Export wenn Backend nicht läuft — Datei wird leer/korrupt
- Kein `assets/openapi.yaml` manuell editieren — kommt vom Backend
- Keine `any`-Casts als Fix für Typ-Fehler nach Sync
