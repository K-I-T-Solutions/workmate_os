---
layout: default
title: SevDesk Integration Test Workflow
parent: Setup
nav_order: 4
---

# SevDesk Integration - Test Workflow

## Workflow-Konzept

**Bidirektionale Synchronisation:**
- **Push → SevDesk:** Rechnungen von WorkmateOS zu SevDesk senden
- **Pull ← SevDesk:** Zahlungsinformationen von SevDesk holen

---

## 🧪 Test-Ablauf

### Phase 1: Initiale Konfiguration ✅

**Status:** Bereits erledigt
- SevDesk API Token konfiguriert
- Verbindung erfolgreich getestet
- Ergebnis: 3 Accounts, 2 Invoices, 1 Contact, 0 Transactions

---

### Phase 2: Invoice Push (WorkmateOS → SevDesk)

**Ziel:** Eine Rechnung aus WorkmateOS zu SevDesk übertragen

#### Schritt 1: Rechnung in WorkmateOS auswählen
1. Navigiere zu **Invoices** (Rechnungsmodul)
2. Wähle eine Rechnung mit Status "sent" oder "draft"
3. Öffne die Rechnung im Detail

**Erwartung:**
- "SevDesk" Button ist sichtbar oben rechts (neben "Bearbeiten")
- Button ist nur sichtbar wenn SevDesk konfiguriert ist

#### Schritt 2: Rechnung zu SevDesk pushen
1. Klicke auf **"SevDesk"** Button
2. System führt aus:
   - Prüft ob Rechnung bereits gesynct wurde (Duplicate Check)
   - Holt Customer aus WorkmateOS → mapped zu SevDesk Contact
   - Holt SevUser (contactPerson)
   - Erstellt Invoice in SevDesk mit Status "100" (Draft)
   - Speichert Mapping in `sevdesk_invoice_mappings` Tabelle

**Erwartung:**
- ✅ Grüne Success-Message: "Rechnung erfolgreich zu SevDesk synchronisiert"
- Nachricht verschwindet nach 5 Sekunden
- Invoice ID und SevDesk Invoice ID in der Message

**Backend-Log (zu prüfen):**
```
🔍 [Auth] Token algorithm: HS256, Key ID: None
🔑 [Auth] Validating HS256 token (Local Auth)
✅ [Auth] HS256 token validated successfully
📤 [SevDesk] Syncing invoice RE-2026-XXXX to SevDesk...
✅ [SevDesk] Invoice created with ID: 123456
```

#### Schritt 3: In SevDesk verifizieren
1. Gehe zu SevDesk Dashboard
2. Navigiere zu **Rechnungen**
3. Finde die neu erstellte Rechnung

**Erwartung:**
- Rechnung ist vorhanden mit allen Details
- Status: "Entwurf" (100)
- Customer-Daten korrekt übernommen
- Line Items korrekt

---

### Phase 3: Zahlung in SevDesk erfassen

**Ziel:** In SevDesk eine Zahlung für die Rechnung buchen

#### Schritt 1: Zahlung in SevDesk buchen
1. In SevDesk: Öffne die synchronisierte Rechnung
2. Klicke auf "Zahlung erfassen" oder "Als bezahlt markieren"
3. Gib Zahlungsbetrag ein (z.B. voller Betrag oder Teilbetrag)
4. Speichere die Zahlung

**Erwartung:**
- Rechnung in SevDesk zeigt `paidAmount > 0`
- Status ändert sich zu "Bezahlt" oder "Teilweise bezahlt"

---

### Phase 4: Payment Sync (SevDesk → WorkmateOS)

**Ziel:** Zahlungsinformationen von SevDesk nach WorkmateOS holen

#### Schritt 1: Payment Sync ausführen
1. Navigiere zu **Finance → Dashboard**
2. Suche die blaue **"SevDesk Zahlungssync"** Karte
3. Klicke auf **"Zahlungen synchronisieren"**

**System führt aus:**
- Holt alle Invoice Mappings aus der Datenbank
- Für jede gemappte Rechnung:
  - Fetched SevDesk Invoice mit `paidAmount`
  - Vergleicht mit WorkmateOS `invoice.paid_amount`
  - Wenn Differenz > €0.01:
    - Erstellt `Payment` Eintrag in WorkmateOS
    - Setzt `amount = Differenz`
    - Setzt `method = "bank_transfer"`
    - Setzt `reference = "SevDesk Sync - Invoice RE-XXX"`
  - Aktualisiert Invoice Status:
    - `paid_amount >= total_amount` → Status "paid"
    - `paid_amount > 0` → Status "partial"

**Erwartung:**
- ✅ Grüne Success-Message:
  ```
  Erfolgreich: 1 Zahlung(en) erstellt, 1 Rechnung(en) aktualisiert
  ```
- Dashboard KPIs aktualisieren sich:
  - "Offene Forderungen" verringert sich
  - "Gesamtumsatz" bleibt gleich
  - "Gewinn" erhöht sich

**Backend-Log (zu prüfen):**
```
📥 [SevDesk] Syncing payments for 1 mapped invoices...
💰 [SevDesk] Invoice RE-2026-XXXX: SevDesk paid €500.00, WorkmateOS paid €0.00
✅ [SevDesk] Created payment: €500.00
📝 [SevDesk] Updated invoice status to: paid
```

---

### Phase 5: Verifizierung in WorkmateOS

#### Schritt 1: Invoice Status prüfen
1. Gehe zu **Invoices**
2. Finde die synchronisierte Rechnung
3. Öffne im Detail

**Erwartung:**
- Status Badge zeigt "Bezahlt" (grün) oder "Teilbezahlt" (gelb)
- Im "Zahlungen" Abschnitt:
  - Neue Zahlung ist sichtbar
  - Betrag korrekt
  - Methode: "Überweisung"
  - Referenz: "SevDesk Sync - Invoice RE-XXX"
  - Datum: Heute

#### Schritt 2: Dashboard prüfen
1. Gehe zu **Finance → Dashboard**
2. Prüfe KPIs

**Erwartung:**
- "Offene Forderungen" reduziert um Zahlungsbetrag
- "Überfällige Forderungen" unverändert (oder reduziert wenn Invoice überfällig war)

---

### Phase 6: Sync History prüfen

#### Schritt 1: Historie anzeigen
1. Gehe zu **Finance → SevDesk**
2. Scrolle nach unten zu "Synchronisations-Historie"

**Erwartung:**
- Mindestens 2 Einträge sichtbar:
  1. **Invoice Sync** (Push to SevDesk)
     - Typ: "Rechnung"
     - Richtung: "Push → SevDesk"
     - Status: "Erfolgreich" (grün)
     - Verarbeitet: 1, Erfolgreich: 1, Fehlgeschlagen: 0

  2. **Payment Sync** (Pull from SevDesk)
     - Typ: "Zahlung"
     - Richtung: "Pull ← SevDesk"
     - Status: "Erfolgreich" (grün)
     - Verarbeitet: 1, Erfolgreich: 1, Fehlgeschlagen: 0

---

## 🔄 Wiederholbare Test-Szenarien

### Szenario A: Teilzahlung
1. Rechnung zu SevDesk pushen (€1000)
2. In SevDesk €400 als bezahlt markieren
3. Payment Sync ausführen
4. **Erwartung:** Status "Teilbezahlt", Payment €400 erstellt
5. In SevDesk weitere €600 bezahlen
6. Payment Sync erneut ausführen
7. **Erwartung:** Status "Bezahlt", zweiter Payment €600 erstellt

### Szenario B: Mehrere Rechnungen
1. 3 Rechnungen zu SevDesk pushen
2. 2 davon in SevDesk als bezahlt markieren
3. Payment Sync ausführen
4. **Erwartung:**
   - "2 Zahlung(en) erstellt, 2 Rechnung(en) aktualisiert"
   - 2 Rechnungen haben Status "Bezahlt"
   - 1 Rechnung bleibt "Versendet"

### Szenario C: Duplicate Prevention
1. Rechnung zu SevDesk pushen
2. **Versuche dieselbe Rechnung nochmals zu pushen**
3. **Erwartung:**
   - ⚠️ Warnung: "Rechnung bereits synchronisiert"
   - Keine doppelte Rechnung in SevDesk

---

## 📊 Test-Checkliste

### Initial Setup
- [x] SevDesk API Token konfiguriert
- [x] Verbindungstest erfolgreich
- [x] Config gespeichert in DB

### Invoice Sync (Push)
- [ ] SevDesk Button sichtbar in Invoice Detail
- [ ] Invoice erfolgreich zu SevDesk gepusht
- [ ] Mapping in DB gespeichert
- [ ] Rechnung in SevDesk vorhanden
- [ ] Customer-Daten korrekt
- [ ] Line Items korrekt
- [ ] Duplicate Check funktioniert

### Payment Sync (Pull)
- [ ] Sync Button sichtbar im Dashboard
- [ ] Zahlung in SevDesk erfasst
- [ ] Payment Sync erfolgreich
- [ ] Payment in WorkmateOS erstellt
- [ ] Invoice Status aktualisiert
- [ ] Dashboard KPIs aktualisiert

### Sync History
- [ ] Invoice Sync in Historie
- [ ] Payment Sync in Historie
- [ ] Status-Badges korrekt
- [ ] Record Counts korrekt

---

## 🐛 Bekannte Probleme & Lösungen

### Problem: "Missing credentials"
**Ursache:** JWT Token nicht oder falsch im localStorage
**Lösung:** Neu einloggen

### Problem: "Token verification failed"
**Ursache:** Token-Format nicht erkannt (HS256 vs RS256)
**Lösung:** Backend unterstützt jetzt beide

### Problem: "Employee object has no attribute 'name'"
**Ursache:** Falsches Employee Model Attribute
**Lösung:** Korrigiert zu `first_name` / `last_name`

### Problem: Sync Button nicht sichtbar
**Ursache:** Config nicht geladen beim Seitenaufruf
**Lösung:** `fetchConfig()` in `onMounted()` hinzugefügt

---

## 📝 Nächste Features (Optional)

1. **Auto-Sync Timer**
   - Alle X Minuten automatisch Payment Sync
   - Konfigurierbar in Settings

2. **Bank Account Sync**
   - WorkmateOS Bank Accounts → SevDesk CheckAccounts
   - Mapping für spätere Transaction Sync

3. **Transaction Sync**
   - SevDesk Vouchers → WorkmateOS BankTransactions
   - Automatisches Matching mit Invoices

4. **Conflict Resolution**
   - Was tun wenn Beträge nicht übereinstimmen?
   - Manual Override Funktion

5. **Bulk Operations**
   - Mehrere Invoices auf einmal pushen
   - "Alle nicht gesyncten Invoices pushen" Button

---

## 🎯 Erfolgs-Kriterien

✅ **Integration erfolgreich wenn:**
1. Rechnungen können fehlerfrei zu SevDesk gepusht werden
2. Zahlungen werden korrekt von SevDesk geholt
3. Invoice Status aktualisiert sich automatisch
4. Dashboard zeigt korrekte Finanz-Übersicht
5. Sync History protokolliert alle Operationen
6. Keine Duplicate-Einträge entstehen
7. Error Handling funktioniert (z.B. ungültiger Token)

---

## 📅 Test-Datum: 2026-01-03
**Durchgeführt von:** Claude Code Assistant
**Status:** Bereit für manuellen Test
