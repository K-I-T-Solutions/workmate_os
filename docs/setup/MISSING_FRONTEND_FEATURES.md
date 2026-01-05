---
layout: default
title: Missing Frontend Features - Development Roadmap
parent: Setup
nav_order: 3
---

# Fehlende Frontend-Implementierungen

Analyse vom 2026-01-02: Backend-Features die noch nicht im Frontend implementiert sind.

## 🚨 KRITISCH - Wichtige Features

### 1. **SevDesk Integration** (Komplett fehlend)
**Backend:** Vollständig implementiert mit allen Endpoints
**Frontend:** Keine UI vorhanden

#### Fehlende Endpoints:
- `POST /api/backoffice/finance/sevdesk/config` - Token-Konfiguration
- `GET /api/backoffice/finance/sevdesk/config` - Config Status abrufen
- `DELETE /api/backoffice/finance/sevdesk/config` - Config deaktivieren
- `GET /api/backoffice/finance/sevdesk/test` - Verbindung testen
- `POST /api/backoffice/finance/sevdesk/sync/invoice` - Rechnung zu SevDesk pushen
- `POST /api/backoffice/finance/sevdesk/sync/payments` - Zahlungen von SevDesk pullen
- `POST /api/backoffice/finance/sevdesk/sync/bank-account` - Bankkonto mappen
- `POST /api/backoffice/finance/sevdesk/sync/transactions` - Transaktionen pullen
- `GET /api/backoffice/finance/sevdesk/sync/history` - Sync-Historie

#### Benötigte UI-Komponenten:
- [ ] SevDesk Settings Page (Token-Eingabe, Auto-Sync Toggle)
- [ ] Sync Buttons in Invoice-Detail (Push to SevDesk)
- [ ] Payment Sync Button in Finance Dashboard
- [ ] Sync History Viewer
- [ ] Connection Status Indicator

---

### 2. **Invoice Restore-Funktion** (Backend vorhanden, Frontend fehlt)
**Backend:** `POST /invoices/{id}/restore` implementiert
**Frontend:** Keine UI vorhanden

#### Was fehlt:
- [ ] "Restore" Button in gelöschten Invoices
- [ ] Gelöschte Invoices-View (mit deleted_at != NULL Filter)
- [ ] Restore-Confirmation Dialog
- [ ] Audit Log Entry nach Restore

---

### 3. **XRechnung Validierung** (Backend vorhanden, Frontend fehlt)
**Backend:** `POST /invoices/{id}/validate-xrechnung` implementiert
**Frontend:** Keine UI vorhanden

#### Was fehlt:
- [ ] "Validate XRechnung" Button in Invoice-Detail
- [ ] Validation Results Dialog mit:
  - XML Syntax Check
  - Structure Check (EN16931)
  - Business Rules Check
  - Fehler/Warnings Anzeige
- [ ] Validation Status Badge

---

### 4. **Retention Policy Management** (Backend vorhanden, Frontend fehlt)
**Backend:**
- `GET /invoices/retention/report` - Lösch-Report
- `POST /invoices/retention/cleanup` - Auto-Löschung

**Frontend:** Keine UI vorhanden

#### Was fehlt:
- [ ] Retention Policy Dashboard
- [ ] Report-Viewer (Invoices > 10 Jahre alt)
- [ ] Manual Cleanup Trigger Button
- [ ] Cleanup History/Logs

---

### 5. **GoBD Export** (Backend vorhanden, Frontend fehlt)
**Backend:** `GET /invoices/gobd-export` implementiert (CSV Download)
**Frontend:** Keine UI vorhanden

#### Was fehlt:
- [ ] "GoBD Export" Button im Invoice-Dashboard
- [ ] Date Range Selector
- [ ] Format Selection (derzeit nur CSV, später ZIP mit PDFs)
- [ ] Export History

---

## ⚠️ WICHTIG - Banking Features

### 6. **FinTS/HBCI Integration** (Backend vollständig, Frontend teilweise)
**Backend:** Vollständig implementiert
**Frontend:** Service vorhanden, aber keine UI

#### Fehlende UI-Komponenten:
- [ ] FinTS Connection Dialog
  - BLZ Eingabe
  - Login/PIN Eingabe
  - Bank-Auswahl
- [ ] FinTS Sync Button in BankAccountsPage
- [ ] Account Sync (alle Konten importieren)
- [ ] Transaction Sync (Transaktionen importieren)
- [ ] Balance Check Button

#### Backend Endpoints ohne Frontend:
- `POST /finance/fints/sync-transactions`
- `POST /finance/fints/sync-accounts`
- `POST /finance/fints/check-balance`

---

### 7. **PSD2/Open Banking** (Backend vollständig, Frontend teilweise)
**Backend:** Vollständig implementiert
**Frontend:** Service vorhanden (psd2Api), aber keine UI

#### Fehlende UI-Komponenten:
- [ ] PSD2 Consent Flow UI
- [ ] OAuth Redirect Handling
- [ ] Access Token Management
- [ ] Account Selection nach Consent
- [ ] Transaction Sync Controls

#### Backend Endpoints ohne Frontend:
- `POST /finance/psd2/consent/initiate`
- `POST /finance/psd2/consent/callback`
- `POST /finance/psd2/accounts/sync`
- `POST /finance/psd2/transactions/sync`

---

### 8. **Auto-Reconciliation** (Backend vorhanden, Frontend fehlt)
**Backend:**
- `POST /bank-transactions/{id}/auto-reconcile` - Single Transaction
- `POST /bank-transactions/auto-reconcile-all` - Alle Transaktionen
- `GET /bank-transactions/{id}/suggestions` - Vorschläge

**Frontend:** Keine UI vorhanden

#### Was fehlt:
- [ ] "Auto-Reconcile" Button bei einzelner Transaktion
- [ ] "Auto-Reconcile All" Button in BankTransactionsPage
- [ ] Reconciliation Suggestions Panel mit:
  - Confidence Score Anzeige
  - Invoice-Match Details
  - Accept/Reject Buttons
- [ ] Reconciliation Status Filter

---

### 9. **Manual Reconciliation** (Backend vorhanden, Frontend fehlt)
**Backend:**
- `POST /bank-transactions/{id}/reconcile`
- `POST /bank-transactions/{id}/unreconcile`

**Frontend:** Keine UI vorhanden

#### Was fehlt:
- [ ] Reconcile Dialog:
  - Payment/Invoice Auswahl
  - Expense Auswahl
  - Notes Eingabe
- [ ] Unreconcile Button
- [ ] Reconciled Transactions Badge/Filter

---

## 📊 NICE-TO-HAVE - Erweiterte Features

### 10. **Bulk Operations** (Backend vorhanden, Frontend fehlt)
**Backend:** `POST /invoices/bulk/status-update`
**Frontend:** Keine Multi-Select UI

#### Was fehlt:
- [ ] Multi-Select Checkboxen in Invoice List
- [ ] Bulk Actions Toolbar
- [ ] Bulk Status Update Dialog

---

### 11. **Invoice Recalculate** (Backend vorhanden, Frontend fehlt)
**Backend:** `POST /invoices/{id}/recalculate`
**Frontend:** Kein Button vorhanden

#### Was fehlt:
- [ ] "Recalculate Totals" Button in Invoice-Edit
- [ ] Auto-Recalculate beim Line Item Edit

---

### 12. **PDF Regeneration** (Backend vorhanden, Frontend fehlt)
**Backend:** `POST /invoices/{id}/regenerate-pdf`
**Frontend:** Keine UI

#### Was fehlt:
- [ ] "Regenerate PDF" Button in Invoice-Detail
- [ ] Regenerate mit Template-Auswahl

---

## 📈 STATISTIKEN

### Implementierungsstand:

**Invoices Module:**
- Backend Endpoints: ~25
- Frontend implementiert: ~15
- **Fehlend: ~10 Endpoints (40%)**

**Finance/Banking Module:**
- Backend Endpoints: ~30
- Frontend implementiert: ~8
- **Fehlend: ~22 Endpoints (73%)**

**SevDesk Integration:**
- Backend Endpoints: 9
- Frontend implementiert: 0
- **Fehlend: 9 Endpoints (100%)**

---

## 🎯 PRIORISIERUNG

### Phase 1 - KRITISCH (Sofort):
1. **SevDesk Integration UI** (komplett fehlend, aber Backend fertig)
   - Config Page
   - Sync Buttons
   - History Viewer

2. **Auto-Reconciliation UI** (wichtig für Banking-Workflow)
   - Auto-Reconcile Buttons
   - Suggestions Panel

3. **Invoice Restore UI** (GoBD Compliance-relevant)

### Phase 2 - WICHTIG (Diese Woche):
4. **XRechnung Validation UI**
5. **FinTS Integration UI**
6. **Manual Reconciliation UI**
7. **GoBD Export UI**

### Phase 3 - NICE-TO-HAVE (Nächste Woche):
8. **PSD2 Integration UI**
9. **Retention Policy Management UI**
10. **Bulk Operations UI**
11. **PDF Regeneration UI**

---

## 💡 EMPFEHLUNGEN

### Architektur:
1. **SevDesk Service erstellen:** `ui/src/modules/finance/services/sevdesk.service.ts`
2. **SevDesk Composable:** `ui/src/modules/finance/composables/useSevDesk.ts`
3. **Settings Page erweitern:** SevDesk-Tab in FinanceApp Settings
4. **Reconciliation Composable:** `ui/src/modules/finance/composables/useReconciliation.ts`

### UI-Patterns:
- **Config Pages:** Modal statt Full Page (schnellerer Zugriff)
- **Sync Buttons:** Loading State + Toast Notifications
- **Suggestions Panel:** Slide-over Panel mit Accept/Reject
- **History Viewer:** Table mit Filter + Export

### Testing:
- Alle neuen Services mit Vitest testen
- E2E Tests für kritische Flows (SevDesk Sync, Reconciliation)
- API Mock Data für Development

---

## 📝 NÄCHSTE SCHRITTE

1. **SevDesk Integration implementieren** (höchste Priorität)
   - Service + Composable
   - Settings UI
   - Sync Buttons in Invoice Detail
   - Payment Sync Dashboard

2. **Banking Auto-Reconciliation** (zweit-höchste Priorität)
   - Reconciliation Composable
   - Auto-Reconcile Buttons
   - Suggestions Panel

3. **Compliance Features vervollständigen**
   - Invoice Restore UI
   - XRechnung Validation UI
   - GoBD Export UI
