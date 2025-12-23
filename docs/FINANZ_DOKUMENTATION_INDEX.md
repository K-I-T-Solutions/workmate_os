# Finanz- & Rechnungsmodul - Dokumentations-Index

Dieses Verzeichnis enthält die umfassende Dokumentation der WorkmateOS Finanz- und Rechnungsfunktionalität.

## Dokumentationsdateien

### 1. FINANZ_UND_RECHNUNGSERSTELLUNG_ANALYSE.md (603 Zeilen)
**Umfassende Detailanalyse**

Das detaillierteste Dokument mit:
- Komplette Rechnungsverwaltungs-Features und Modelle
- Ausgabenverwaltung & Finanz-Tracking
- Datenbankschema & Migrationen
- Integration mit anderen Modulen (CRM, Projekte, Dokumente)
- Aktueller Implementierungsstatus (vollständig vs. teilweise implementiert)
- API-Response-Beispiele
- Test-Ansatz
- Konfiguration & Firmendetails
- Dateistruktur-Zusammenfassung
- Empfohlene nächste Schritte
- Bekannte Einschränkungen
- Wichtige technische Entscheidungen

**Wann verwenden:** Lies dies, wenn du ein vollständiges Verständnis benötigst, was existiert, wie es funktioniert und was fehlt.

---

### 2. FINANZ_SCHNELLREFERENZ.md (184 Zeilen)
**Schnellnachschlage-Leitfaden**

Schnellreferenz für:
- Implementierungs-Checkliste (was ist fertig, was nicht)
- Wichtige API-Pfade
- Datenbank-Entity-Beziehungen
- Wichtige Zahlen & Formate
- Dateistandort-Tabelle
- Berechnete Eigenschaften-Referenz
- Berechnungsformeln
- Rechnungsstatus-Ablauf
- Fest kodierte Firmendetails
- Letzte Git-Änderungen
- Test-Standort
- Nächste Prioritäten

**Wann verwenden:** Schnellnachschlagen, Präsentationen, Erinnern an Pfade oder Konstanten.

---

### 3. FINANZ_CODE_ARCHITEKTUR.md (505 Zeilen)
**Technisches Architektur-Dokument**

Detaillierte technische Tiefenanalyse:
- Komplette Modulstruktur (Dateibaum mit Beschreibungen)
- Datenfluss-Diagramme (Erstellung, Zahlung, Filterung)
- Datenbankschema (CREATE TABLE-Anweisungen)
- Validierungsebenen (4-Ebenen-Validierungsfluss)
- Modell-Eigenschaften & Berechnete Felder
- API-Endpoint-Matrix (alle 22 Endpoints)
- Fehlerbehandlungs-Strategie
- Test-Strategie
- Performance-Überlegungen
- Sicherheits-Überlegungen
- Deployment-Hinweise

**Wann verwenden:** Bei der Entwicklung neuer Features, Optimierung oder beim Verstehen der technischen Architektur.

---

## Wichtige Statistiken

- **Gesamte Dokumentationszeilen:** 1.292
- **Generierte Dateien:** 3
- **Erstellungsdatum:** 22. Dezember 2025
- **Rechnungsmodul:** ~500 LOC Modelle + ~600 LOC Routes + ~200 LOC CRUD + ~100 LOC PDF
- **Finanzmodul:** ~60 LOC Modelle + ~160 LOC Routes + ~160 LOC CRUD
- **API-Endpoints:** 22 insgesamt (18 Rechnung, 6 Finanzen)
- **Datenbanktabellen:** 5 (invoices, invoice_line_items, payments, number_sequences, expenses)

---

## Schnellnavigation

### Wenn du möchtest...

**...verstehen was existiert**
→ Starte mit FINANZ_UND_RECHNUNGSERSTELLUNG_ANALYSE.md Abschnitt 5

**...schnell einen API-Endpoint nachschlagen**
→ Prüfe FINANZ_CODE_ARCHITEKTUR.md API-Endpoint-Matrix

**...herausfinden wo der Code liegt**
→ Siehe FINANZ_SCHNELLREFERENZ.md Dateistandort-Tabelle

**...das Datenmodell verstehen**
→ Lies FINANZ_CODE_ARCHITEKTUR.md Datenbankschema & FINANZ_UND_RECHNUNGSERSTELLUNG_ANALYSE.md Abschnitt 1

**...sehen wie eine Rechnung erstellt wird (Code-Ablauf)**
→ Prüfe FINANZ_CODE_ARCHITEKTUR.md Datenfluss-Diagramm

**...die Validierung verstehen**
→ Siehe FINANZ_CODE_ARCHITEKTUR.md Validierungsebenen

**...nächste Features planen**
→ Lies FINANZ_UND_RECHNUNGSERSTELLUNG_ANALYSE.md Abschnitt 10 (Empfohlene nächste Schritte)

**...aktuelle Einschränkungen verstehen**
→ Prüfe FINANZ_UND_RECHNUNGSERSTELLUNG_ANALYSE.md Abschnitt 12

**...den Zahlungsablauf sehen**
→ Schau dir FINANZ_CODE_ARCHITEKTUR.md Datenfluss-Diagramm an

**...Performance-Optimierungen verstehen**
→ Siehe FINANZ_CODE_ARCHITEKTUR.md Performance-Überlegungen

---

## Implementierungsstatus Zusammenfassung

### Vollständig implementiert
- Rechnungserstellung mit Positionen
- Automatische Rechnungsnummerierung
- Zahlungsverfolgung & -erfassung
- Rechnungsstatus-Verwaltung mit Auto-Updates
- Professionelle PDF-Generierung
- Ausgabenverfolgung mit Kategorien
- Finanz-KPIs
- Vollständige REST API mit Pagination & Filtern
- Datenbank-Validierung & Constraints
- Unterstützung mehrerer Dokumenttypen

### Noch nicht implementiert
- Frontend-UI-Komponenten
- Payment-Gateway-Integration
- Erweiterte Finanzberichte
- Buchhaltungsfunktionen
- E-Mail-Benachrichtigungen
- Mahnwesen bei überfälligen Rechnungen
- Multi-Währungs-Unterstützung
- Änderungsprotokoll
- Eigene Vorlagen
- Batch-Operationen

---

## Dateistandorte (Schnellreferenz)

| Komponente | Pfad |
|-----------|------|
| Rechnungsmodelle | `backend/app/modules/backoffice/invoices/models.py` |
| Rechnungs-API-Endpoints | `backend/app/modules/backoffice/invoices/routes.py` |
| Rechnungs-Datenbankoperationen | `backend/app/modules/backoffice/invoices/crud.py` |
| Zahlungs-Datenbankoperationen | `backend/app/modules/backoffice/invoices/payments_crud.py` |
| PDF-Generierung | `backend/app/modules/backoffice/invoices/pdf_generator.py` |
| Ausgabenmodelle | `backend/app/modules/backoffice/finance/models.py` |
| Finanz-API-Endpoints | `backend/app/modules/backoffice/finance/router.py` |
| Finanz-Datenbankoperationen | `backend/app/modules/backoffice/finance/crud.py` |
| Validierungs-Schemas | `backend/app/modules/backoffice/{invoices,finance}/schemas.py` |
| Datenbank-Migrationen | `backend/alembic/versions/` (3 Dateien) |
| Integrationstests | `backend/tests/test_invoice.py` |
| Haupt-App-Router-Setup | `backend/app/main.py` (Zeilen 22-24, 100-102) |

---

## Datenbanktabellen

```
1. invoices
   - Haupt-Rechnungsdatensätze
   - Verfolgt: Nummer, Status, Summen, Daten, Kunde, Projekt
   - 11 indizierte Spalten

2. invoice_line_items
   - Einzelne Positionen pro Rechnung
   - Verfolgt: Beschreibung, Menge, Einheit, Preis, Steuer, Rabatt
   - Kaskadierendes Löschen mit Rechnung

3. payments
   - Zahlungseingänge für Rechnungen
   - Verfolgt: Betrag, Datum, Methode, Referenz
   - Löst Auto-Status-Update bei Rechnung aus

4. number_sequences
   - Verwaltet Rechnungsnummern-Generierung
   - Pro Dokumenttyp (invoice, quote, credit_note, etc.)
   - Pro Jahr (jährliches Reset)
   - Atomarer Zähler mit FOR UPDATE Sperre

5. expenses
   - Projektkosten und Ausgaben
   - Verfolgt: Kategorie, Betrag, Verrechenbar-Flag
   - Verknüpft mit Projekt und Rechnung
```

---

## API-Endpoints (Komplette Liste)

### Rechnungen (18 Endpoints)

**Liste & Statistiken:**
- GET /api/backoffice/invoices/ - Liste mit Filtern/Pagination
- GET /api/backoffice/invoices/statistics - KPIs abrufen

**Einzelne Rechnung:**
- GET /api/backoffice/invoices/{id} - Nach ID abrufen
- GET /api/backoffice/invoices/by-number/{num} - Nach Nummer abrufen
- POST /api/backoffice/invoices/ - Neue erstellen
- PATCH /api/backoffice/invoices/{id} - Aktualisieren
- PATCH /api/backoffice/invoices/{id}/status - Nur Status aktualisieren
- POST /api/backoffice/invoices/{id}/recalculate - Summen neu berechnen
- DELETE /api/backoffice/invoices/{id} - Löschen

**PDF-Operationen:**
- GET /api/backoffice/invoices/{id}/pdf - PDF herunterladen
- POST /api/backoffice/invoices/{id}/regenerate-pdf - PDF neu generieren

**Bulk-Operationen:**
- POST /api/backoffice/invoices/bulk/status-update - Bulk-Status-Update

**Zahlungen (6 Endpoints):**
- POST /api/backoffice/invoices/{id}/payments - Zahlung erstellen
- GET /api/backoffice/invoices/{id}/payments - Zahlungen auflisten
- GET /api/backoffice/invoices/payments/{id} - Zahlung abrufen
- PATCH /api/backoffice/invoices/payments/{id} - Zahlung aktualisieren
- DELETE /api/backoffice/invoices/payments/{id} - Zahlung löschen

### Finanzen (6 Endpoints)

**Ausgaben:**
- POST /api/backoffice/finance/expenses - Erstellen
- GET /api/backoffice/finance/expenses - Liste mit Filtern
- GET /api/backoffice/finance/expenses/{id} - Einzelne abrufen
- PATCH /api/backoffice/finance/expenses/{id} - Aktualisieren
- DELETE /api/backoffice/finance/expenses/{id} - Löschen

**KPIs:**
- GET /api/backoffice/finance/kpis/expenses - Ausgabensummen nach Kategorie

---

## Wichtige Modelle & Ihre Eigenschaften

### Invoice (Rechnung)
```
Datenbankfelder:
- invoice_number (str, unique)
- customer_id (FK, erforderlich)
- project_id (FK, optional)
- total, subtotal, tax_amount (Decimal)
- status (enum: draft/sent/paid/partial/overdue/cancelled)
- document_type (enum: invoice/quote/credit_note/order_confirmation)
- issued_date, due_date (Date, optional)
- pdf_path (str, optional)

Berechnete Eigenschaften:
- paid_amount (Summe der Zahlungen)
- outstanding_amount (total - paid)
- is_paid (bool)
- is_overdue (bool)
- payment_rate (0-100%)
- days_until_due (int, kann negativ sein)

Methoden:
- recalculate_totals() - Neu berechnen aus Positionen
- update_status_from_payments() - Auto-Update Status
```

### InvoiceLineItem (Rechnungsposition)
```
Datenbankfelder:
- position (int, Sortierreihenfolge)
- description (str)
- quantity, unit_price (Decimal)
- unit (str)
- tax_rate, discount_percent (Decimal)

Berechnete Eigenschaften:
- subtotal = quantity * unit_price
- discount_amount = subtotal * (discount_percent / 100)
- subtotal_after_discount = subtotal - discount_amount
- tax_amount = subtotal_after_discount * (tax_rate / 100)
- total = subtotal_after_discount + tax_amount
```

### Payment (Zahlung)
```
Datenbankfelder:
- amount (Decimal, > 0)
- payment_date (Date)
- method (enum: cash/bank_transfer/credit_card/etc.)
- reference (str, optional - Transaktions-ID)
- note (str, optional)
- invoice_id (FK, erforderlich)

Trigger:
- Auto-Update des Rechnungsstatus bei create/update/delete via SQLAlchemy Events
```

### Expense (Ausgabe)
```
Datenbankfelder:
- title (str)
- category (enum: travel/material/software/hardware/consulting/marketing/office/training/other)
- amount (Decimal, > 0)
- description (str)
- receipt_path (str, optional)
- note (str, optional)
- is_billable (bool)
- project_id (FK, optional)
- invoice_id (FK, optional)

Berechnete Eigenschaften:
- is_invoiced (bool) - wenn invoice_id gesetzt ist
```

---

## Wichtige Konstanten & Konfigurationen

### Rechnungsnummern-Format
- Muster: `PREFIX-YEAR-SEQNUM`
- Beispiel: `RE-2025-0001`
- Präfixe:
  - RE = Rechnung (Invoice)
  - AN = Angebot (Quote)
  - GS = Gutschrift (Credit Note)
  - ST = Stornierung (Cancellation)

### Dokumenttypen
- invoice: Titel "RECHNUNG", Farbe #ff9100
- quote: Titel "ANGEBOT", Farbe #008cff
- credit_note: Titel "GUTSCHRIFT", Farbe #5dcc5d
- order_confirmation: Titel "AUFTRAGSBESTÄTIGUNG", Farbe #9933ff

### Zahlungsmethoden
- cash (Bargeld)
- bank_transfer (Überweisung)
- credit_card (Kreditkarte)
- debit_card (EC-Karte)
- paypal
- sepa
- other (Sonstige)

### Ausgabenkategorien
- travel (Reise)
- material (Material)
- software
- hardware
- consulting (Beratung)
- marketing
- office (Büro)
- training (Schulung)
- other (Sonstige)

### Firmendetails (Fest kodiert)
- **Name:** K.I.T. Solutions
- **Inhaber:** Joshua Phu Kuhrau
- **Adresse:** Dietzstr. 1, 56073 Koblenz, Germany
- **E-Mail:** info@kit-it-koblenz.de
- **Telefon:** Tel. 0162 / 2654262
- **Website:** https://kit-it-koblenz.de
- **IBAN:** DE94100110012706471170
- **BIC:** NTSBDEB1XX
- **Bank:** N26 Bank AG

---

## Entwicklungsverlauf

**2025-10-24:** Erste Implementierung
- Rechnungsmodul mit vollständigem CRUD erstellt
- Zahlungsverfolgung implementiert
- PDF-Generierung mit ReportLab hinzugefügt
- Nummernsequenz-System erstellt

**2025-11-19:** Multi-Dokument-Unterstützung
- document_type Feld hinzugefügt
- PDF-Vorlagen für Angebote, Gutschriften, etc. erweitert

**2025-12-16:** Finanzmodul-Erweiterung
- Ausgaben/Finanz-Tracking hinzugefügt
- Ausgaben-KPIs implementiert
- Beziehungen zwischen Rechnungen und Ausgaben verbessert

**2025-12-19:** Dokumentenverwaltungs-Integration
- Nextcloud-Speicher integriert
- Dokumentenhandling verbessert

**2025-12-22:** Dokumentation
- Umfassende Dokumentation erstellt
- Architektur-Analyse
- Schnellreferenz-Leitfäden

---

## Wie navigiere ich durch diese Dokumentation

1. **Erstes Mal?** → Lies FINANZ_UND_RECHNUNGSERSTELLUNG_ANALYSE.md Abschnitte 1-3
2. **Brauchst du schnelle Fakten?** → Prüfe FINANZ_SCHNELLREFERENZ.md
3. **Features implementieren?** → Nutze FINANZ_CODE_ARCHITEKTUR.md
4. **Musst du wissen was fehlt?** → Siehe FINANZ_UND_RECHNUNGSERSTELLUNG_ANALYSE.md Abschnitte 5 & 10
5. **Debugging-Probleme?** → Prüfe FINANZ_CODE_ARCHITEKTUR.md Fehlerbehandlung & Validierungsebenen
6. **Deployment?** → Lies FINANZ_CODE_ARCHITEKTUR.md Deployment-Hinweise

---

## Deine Änderungen testen

### Integrationstests
```bash
cd backend/tests
python test_invoice.py
```

### Manuelle API-Tests
Nutze curl oder Postman gegen:
- `https://api.workmate.intern.phudevelopement.xyz/api/backoffice/invoices/`

### Datenbank-Validierung
Prüfe angewandte Migrationen:
```bash
alembic history
```

---

## Kontakt & Support

Für Fragen zum Finanzmodul:
1. Prüfe die relevante Dokumentationsdatei
2. Schaue dir die Code-Kommentare in den Implementierungsdateien an
3. Sieh dir test_invoice.py für Verwendungsbeispiele an
4. Prüfe letzte Git-Commits für Änderungen

---

## Lizenz & Vertraulichkeit

Diese Dokumentation und der Code sind Eigentum von K.I.T. Solutions.

Erstellt: 22. Dezember 2025
Letzte Aktualisierung: 23. Dezember 2025
Version: 1.0 (Deutsche Übersetzung)
