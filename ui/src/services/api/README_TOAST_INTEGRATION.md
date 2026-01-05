# Toast Notification Integration - TODO

## Aktueller Status

Das Error Handling im API Client ist **strukturiert vorbereitet**, aber nutzt aktuell nur **Console-Ausgaben** als Fallback.

### Was funktioniert bereits:

✅ **Backend** sendet strukturierte Error Messages:
```json
{
  "detail": {
    "error_code": "AUTH_1002",
    "message": "Ihr Sitzungstoken ist ungültig.",
    "hint": "Bitte melden Sie sich erneut an."
  }
}
```

✅ **Frontend** verarbeitet strukturierte Errors:
- Type Guards in `src/types/errors.ts`
- Error Extraction in `client.ts`
- Formatierte Console-Ausgabe

❌ **User sieht aktuell:** Nur Browser Console Logs

---

## Nächste Schritte: Toast Library Integration

### Empfohlene Library: vue-toastification

**Warum?**
- ✅ Lightweight (~10KB gzipped)
- ✅ Vue 3 kompatibel
- ✅ TypeScript Support
- ✅ Customizable
- ✅ Gut maintained

**Installation:**

```bash
cd ui
npm install vue-toastification@next
```

**Setup in `main.ts`:**

```typescript
import { createApp } from 'vue';
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const app = createApp(App);
app.use(Toast, {
  position: 'top-right',
  timeout: 5000,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false,
});
```

**Custom Styling (Tailwind):**

```css
/* src/assets/toast-custom.css */
.Vue-Toastification__toast--error {
  @apply bg-red-50 border border-red-200 text-red-900;
}

.Vue-Toastification__toast--error .Vue-Toastification__icon {
  @apply text-red-500;
}
```

---

### Integration in API Client

**Ersetze in `client.ts`:**

```typescript
// VORHER (aktuell):
function showUserNotification(errorDetail: ErrorDetail) {
  // Fallback: Strukturierte Console-Ausgabe
  console.group(`🔴 ${errorDetail.message}`);
  if (errorDetail.hint) {
    console.info(`💡 ${errorDetail.hint}`);
  }
  console.info(`🔢 Error Code: ${errorDetail.error_code}`);
  console.groupEnd();
}

// NACHHER (mit Toast):
import { useToast } from 'vue-toastification';

function showUserNotification(errorDetail: ErrorDetail) {
  const toast = useToast();

  // Erstelle Toast mit Message + Hint
  const content = errorDetail.hint
    ? `${errorDetail.message}\n\n💡 ${errorDetail.hint}`
    : errorDetail.message;

  toast.error(content, {
    timeout: 5000,
    icon: '⚠️',
  });

  // Behalte Console-Log für Debugging
  if (import.meta.env.DEV) {
    console.group(`🔴 ${errorDetail.message}`);
    if (errorDetail.hint) {
      console.info(`💡 ${errorDetail.hint}`);
    }
    console.info(`🔢 Error Code: ${errorDetail.error_code}`);
    console.groupEnd();
  }
}
```

---

### Erweiterte Integration (Optional)

**Custom Toast Component für bessere UX:**

```typescript
// src/components/ErrorToast.vue
<template>
  <div class="flex flex-col gap-2">
    <div class="font-semibold text-red-900">
      {{ error.message }}
    </div>
    <div v-if="error.hint" class="text-sm text-red-700 flex items-start gap-1">
      <span>💡</span>
      <span>{{ error.hint }}</span>
    </div>
    <div class="text-xs text-red-600 font-mono">
      Code: {{ error.error_code }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ErrorDetail } from '@/types/errors';

defineProps<{
  error: ErrorDetail;
}>();
</script>
```

**Verwendung:**

```typescript
import { h } from 'vue';
import ErrorToast from '@/components/ErrorToast.vue';

function showUserNotification(errorDetail: ErrorDetail) {
  const toast = useToast();

  toast.error({
    component: h(ErrorToast, { error: errorDetail }),
  }, {
    timeout: 5000,
  });
}
```

---

### Alternative Libraries

Wenn `vue-toastification` nicht passt:

1. **Naive UI** (Full Component Library)
   - Includes notification system
   - Heavy (~200KB), aber feature-complete

2. **@kyvg/vue3-notification**
   - Very lightweight
   - Simple API

3. **Custom Implementation**
   - Composable mit Pinia Store
   - Tailwind Transitions
   - Volle Kontrolle

---

## Testing nach Integration

**Testfälle:**

1. **Auth Errors (401)**
   ```typescript
   // Login mit falschen Credentials
   // Erwarte: Toast "E-Mail oder Passwort ist falsch"
   ```

2. **Invoice Errors (404)**
   ```typescript
   // Nicht existierende Rechnung öffnen
   // Erwarte: Toast "Rechnung 'XYZ' wurde nicht gefunden"
   ```

3. **Validation Errors (400)**
   ```typescript
   // Payment größer als Outstanding Amount
   // Erwarte: Toast mit Hint "Bitte reduzieren Sie den Zahlungsbetrag"
   ```

4. **Network Errors**
   ```typescript
   // Backend offline
   // Erwarte: Toast "Keine Verbindung zum Server"
   ```

5. **Legacy Errors**
   ```typescript
   // Alter API Endpoint ohne strukturierte Errors
   // Erwarte: Toast mit Legacy-Message
   ```

---

## Geschätzter Aufwand

| Task | Zeit |
|------|------|
| Library Installation | 5 min |
| Basic Setup in main.ts | 5 min |
| Integration in client.ts | 10 min |
| Custom Styling (Optional) | 10 min |
| Testing | 10 min |
| **Total** | **30-40 min** |

---

## Priorität

**MEDIUM** - Verbessert UX deutlich, aber System funktioniert auch ohne

**Wann implementieren?**
- Vor Production Deploy
- Wenn User Feedback kommt ("Sehe keine Fehlermeldungen")
- Nächster UI/UX Sprint

---

## Status Tracking

- [ ] vue-toastification installiert
- [ ] Toast Plugin in main.ts registriert
- [ ] showUserNotification() erweitert
- [ ] Custom Styling angepasst
- [ ] Error Scenarios getestet
- [ ] Dokumentation aktualisiert

---

**Erstellt:** 2026-01-05
**Autor:** Claude Code (Better Error Messages Quick Win)
