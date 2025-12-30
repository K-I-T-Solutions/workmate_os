---
layout: default
title: Analyse
parent: Finance DE
grand_parent: Finance
nav_order: 1
---

# WorkmateOS Finanz- & Rechnungsfunktionalität - Umfassende Übersicht

**Letzte Aktualisierung:** 23. Dezember 2025

## Zusammenfassung

Das WorkmateOS-System verfügt über ein gut strukturiertes **Finanz- & Rechnungsmodul** (Phase 2) mit umfassenden Funktionen zur Rechnungserstellung, Zahlungsverfolgung, Ausgabenverwaltung und Finanzberichterstattung. Die Implementierung umfasst Datenbankmodelle, API-Endpoints, PDF-Generierung und Planung für UI-Komponenten.

---

## 1. RECHNUNGSVERWALTUNG

### 1.1 Datenbankmodelle
**Standort:** `/backend/app/modules/backoffice/invoices/models.py`

#### Invoice-Modell (Rechnung)
- **Zweck:** Verwaltet Kundenrechnungen und Angebote
- **Hauptfelder:**
  - `invoice_number` (str, unique): Auto-generiert (RE-2025-0001, AN-2025-0001, etc.)
  - `total` (Decimal): Gesamtbetrag inkl. MwSt.
  - `subtotal` (Decimal): Betrag ohne MwSt.
  - `tax_amount` (Decimal): MwSt.-Betrag
  - `status` (str): draft, sent, paid, partial, overdue, cancelled
  - `document_type` (str): invoice, quote, credit_note, order_confirmation
  - `issued_date`, `due_date` (Date): Rechnungs- und Fälligkeitsdatum
  - `pdf_path` (str, optional): Pfad zur generierten PDF
  - `customer_id` (FK): Erforderliche Kundenreferenz
  - `project_id` (FK, optional): Zugehöriges Projekt
  - `notes`, `terms` (Text, optional): Interne Notizen und Zahlungsbedingungen

- **Hauptmethoden:**
  - `recalculate_totals()`: Berechnet Zwischensumme, Steuer und Gesamt aus Positionen neu
  - `update_status_from_payments()`: Aktualisiert Status automatisch basierend auf Zahlungsfortschritt
  - `is_overdue` (property): Boolean-Prüfung ob überfällig und unbezahlt
  - `paid_amount` (property): Summe aller Zahlungen
  - `outstanding_amount` (property): Verbleibender zu zahlender Betrag
  - `is_paid` (property): Boolean-Prüfung ob vollständig bezahlt
  - `days_until_due` (property): Verbleibende Tage (negativ = überfällig)
  - `payment_rate` (property): Bezahlter Prozentsatz (0-100)

- **Beziehungen:**
  - `customer` (many-to-one): CRM-Kunde
  - `project` (many-to-one, optional): Projekt
  - `line_items` (one-to-many): Rechnungspositionen (kaskadierendes Löschen)
  - `payments` (one-to-many): Zahlungseinträge (kaskadierendes Löschen)
  - `expenses` (one-to-many): Zugehörige Ausgaben (kaskadierendes Löschen)

- **Constraints:**
  - Alle Geldbeträge >= 0
  - Fälligkeitsdatum muss >= Rechnungsdatum sein
  - Status muss gültiger Enum-Wert sein
  - Rechnungsnummer ist eindeutig

#### InvoiceLineItem-Modell (Rechnungsposition)
- **Zweck:** Einzelne Positionen auf Rechnungen
- **Hauptfelder:**
  - `position` (int): Sortierreihenfolge auf der Rechnung
  - `description` (str): Service-/Produktbeschreibung
  - `quantity` (Decimal): Menge/Anzahl
  - `unit` (str): Maßeinheit (Stunden, Stück, m², etc.)
  - `unit_price` (Decimal): Preis pro Einheit (netto)
  - `tax_rate` (Decimal): MwSt.-Prozentsatz (0-100)
  - `discount_percent` (Decimal): Rabatt-Prozentsatz (0-100)
  - `invoice_id` (FK): Übergeordnete Rechnung

- **Hauptberechnungen:**
  - `subtotal`: Menge × Einzelpreis
  - `discount_amount`: Zwischensumme × (Rabatt-Prozent / 100)
  - `subtotal_after_discount`: Zwischensumme - Rabatt-Betrag
  - `tax_amount`: Zwischensumme_nach_Rabatt × (Steuersatz / 100)
  - `total`: Zwischensumme_nach_Rabatt + Steuer-Betrag

#### Payment-Modell (Zahlung)
- **Zweck:** Alle Zahlungseingänge für Rechnungen verfolgen
- **Hauptfelder:**
  - `amount` (Decimal): Zahlungsbetrag (> 0)
  - `payment_date` (Date): Wann die Zahlung eingegangen ist
  - `method` (str): cash, bank_transfer, credit_card, debit_card, paypal, sepa, other
  - `reference` (str, optional): Transaktions-ID oder Verwendungszweck
  - `note` (str, optional): Interne Notiz
  - `invoice_id` (FK): Zugehörige Rechnung

- **Trigger:**
  - Aktualisiert Rechnungsstatus automatisch nach create/update/delete via SQLAlchemy Events

#### NumberSequence-Modell (Nummernsequenz)
- **Zweck:** Verwaltet Rechnungsnummernsequenzen nach Dokumenttyp und Jahr
- **Felder:**
  - `doc_type` (str): Dokumenttyp (invoice, quote, credit_note, cancellation)
  - `year` (int): Jahr für Sequenz
  - `current_number` (int): Letzte ausgegebene Laufnummer
- **Format:** RE-2025-0001, AN-2025-0001, GS-2025-0001, ST-2025-0001
- **Features:** Atomarer Zähler mit FOR UPDATE Sperre für Nebenläufigkeitssicherheit

### 1.2 API-Endpoints

**Basispfad:** `/api/backoffice/invoices`

#### Liste & Filter
- `GET /` - Rechnungen mit Pagination und Filtern auflisten
  - Query-Parameter: `skip`, `limit`, `status`, `customer_id`, `project_id`, `date_from`, `date_to`
  - Gibt zurück: `InvoiceListResponse` mit Pagination-Metadaten

- `GET /statistics` - Rechnungsstatistiken
  - Gibt zurück: Gesamtzahl, Gesamtumsatz, offener Betrag, überfällige Anzahl, Anzahl nach Status

#### Einzelne Rechnungsoperationen
- `GET /{invoice_id}` - Einzelne Rechnung mit allen Beziehungen abrufen
- `GET /by-number/{invoice_number}` - Rechnung nach Rechnungsnummer abrufen
- `POST /` - Neue Rechnung erstellen (mit automatischer PDF-Generierungsoption)
- `PATCH /{invoice_id}` - Rechnung aktualisieren (nur Status, Notizen, Bedingungen)
- `PATCH /{invoice_id}/status` - Nur Status aktualisieren
- `POST /{invoice_id}/recalculate` - Summen aus Positionen neu berechnen
- `DELETE /{invoice_id}` - Rechnung löschen (kaskadierend: Positionen, Zahlungen, PDF)

#### PDF-Operationen
- `GET /{invoice_id}/pdf` - Rechnungs-PDF herunterladen (auto-generiert wenn fehlend)
- `POST /{invoice_id}/regenerate-pdf` - PDF neu generieren (z.B. nach Vorlagenänderung)

#### Bulk-Operationen
- `POST /bulk/status-update` - Status für mehrere Rechnungen aktualisieren
  - Gibt zurück: success_count, failed_count, failed_ids

#### Zahlungsverwaltung
- `POST /{invoice_id}/payments` - Zahlung hinzufügen (aktualisiert Rechnungsstatus automatisch)
- `GET /{invoice_id}/payments` - Zahlungen für Rechnung auflisten
- `GET /payments/{payment_id}` - Einzelne Zahlung abrufen
- `PATCH /payments/{payment_id}` - Zahlung aktualisieren
- `DELETE /payments/{payment_id}` - Zahlung löschen (aktualisiert Rechnungsstatus automatisch)

### 1.3 Schemas & Validierung

**Standort:** `/backend/app/modules/backoffice/invoices/schemas.py`

- `InvoiceStatus` Enum: draft, sent, paid, partial, overdue, cancelled
- `PaymentMethod` Enum: cash, bank_transfer, credit_card, debit_card, paypal, sepa, other
- `DocumentType` Enum: invoice, quote, credit_note, order_confirmation

**Request/Response-Schemas:**
- `InvoiceCreate`: Zum Erstellen von Rechnungen (erfordert min. 1 Position)
- `InvoiceUpdate`: Für partielle Updates
- `InvoiceResponse`: Vollständige Rechnungsantwort mit berechneten Feldern
- `InvoiceListResponse`: Paginierte Liste mit Seiten-/Seitenanzahl-Berechnungen
- `InvoiceStatisticsResponse`: KPI-Daten
- `PaymentCreate`, `PaymentUpdate`, `PaymentResponse`: Zahlungsoperationen
- `InvoiceLineItemCreate`, `InvoiceLineItemResponse`: Positionsoperationen
- `BulkStatusUpdate`, `BulkUpdateResponse`: Bulk-Operationen
- `InvoiceFilterParams`: Query-Parameter-Validierung

**Validierungen:**
- Decimal-Konvertierung für Geldbeträge
- Datumsvalidierung (due_date >= issued_date)
- Status-Enum-Validierung
- Mindestens 1 Position bei Erstellung erforderlich

### 1.4 CRUD-Operationen

**Standort:** `/backend/app/modules/backoffice/invoices/crud.py`

**Erstellen:**
- Automatische oder manuelle Rechnungsnummern-Generierung
- Validiert, dass Kunde existiert
- Validiert, dass Projekt existiert (falls angegeben)
- Erstellt Positionen mit automatischer Positionierung
- Berechnet Summen automatisch neu
- Optionale synchrone PDF-Generierung
- Registriert PDF als Dokument

**Lesen:**
- Rechnungen mit optionalen Filtern abrufen (Status, Kunde, Projekt, Datumsbereich)
- Zählung mit denselben Filtern
- Einzelne Rechnung mit allen Beziehungen Eager-geladen abrufen
- Rechnung nach Nummer abrufen

**Aktualisieren:**
- Nur Status, Notizen, Bedingungen aktualisieren
- Neuen Status validieren
- Summen aus Positionen neu berechnen

**Löschen:**
- Kaskadierendes Löschen von Positionen und Zahlungen
- PDF-Datei aus Dateisystem löschen

**Statistiken:**
- Gesamtzahl
- Gesamtumsatz (nur bezahlte Rechnungen)
- Offener Betrag (unbezahlt + teilbezahlt)
- Anzahl überfälliger, Entwurfs-, gesendeter, bezahlter, stornierter Rechnungen

### 1.5 PDF-Generierung

**Standort:** `/backend/app/modules/backoffice/invoices/pdf_generator.py`

**Features:**
- Dokumenttyp-Vorlagen (invoice, quote, credit_note, order_confirmation)
- Eigene Farben pro Dokumenttyp
- Firmenbranding (K.I.T. Solutions)
- Wasserzeichen-Unterstützung (Firmenlogo)
- SEPA QR-Code-Generierung für Zahlungen
- Deutsche Zahlenformatierung (1.234,50 €)
- Positionstabelle mit Berechnungen
- Bankdetails (IBAN, BIC)
- AGB
- Professionelles Rechnungslayout

**Dateinamen:** `KIT-RE-{sequenz}.pdf`
**Speicherort:** `/root/workmate_os_uploads/invoices/`

---

## 2. AUSGABENVERWALTUNG & FINANZ-TRACKING

### 2.1 Datenbankmodelle

**Standort:** `/backend/app/modules/backoffice/finance/models.py`

#### Expense-Modell (Ausgabe)
- **Zweck:** Projektkosten und Ausgaben verfolgen
- **Hauptfelder:**
  - `title` (str): Ausgabenname
  - `category` (str enum): travel, material, software, hardware, consulting, marketing, office, training, other
  - `amount` (Decimal): Ausgabenbetrag (> 0)
  - `description` (str): Detaillierte Beschreibung
  - `receipt_path` (str, optional): Pfad zu Beleg/Dokument
  - `note` (str, optional): Zusätzliche Notizen
  - `is_billable` (bool): Kann dem Kunden berechnet werden
  - `project_id` (FK, optional): Zugehöriges Projekt
  - `invoice_id` (FK, optional): Falls bereits abgerechnet

- **Hauptmethoden:**
  - `is_invoiced` (property): Boolean-Prüfung ob Rechnung zugewiesen ist

- **Beziehungen:**
  - `project` (many-to-one, optional): Projekt
  - `invoice` (many-to-one, optional): Rechnung falls abgerechnet

- **Constraints:**
  - Betrag muss > 0 sein

### 2.2 API-Endpoints

**Basispfad:** `/api/backoffice/finance`

#### Ausgaben-CRUD
- `POST /expenses` - Ausgabe erstellen
- `GET /expenses` - Ausgaben mit Filtern und Pagination auflisten
  - Query-Parameter: `title`, `category`, `project_id`, `invoice_id`, `from_date`, `to_date`, `limit`, `offset`
- `GET /expenses/{expense_id}` - Einzelne Ausgabe abrufen
- `PATCH /expenses/{expense_id}` - Ausgabe aktualisieren
- `DELETE /expenses/{expense_id}` - Ausgabe löschen

#### Finanz-KPIs
- `GET /kpis/expenses` - Ausgaben-KPIs abrufen
  - Query-Parameter: `title`, `category`, `project_id`, `from_date`, `to_date`
  - Gibt zurück: Gesamtausgaben, Aufschlüsselung nach Kategorie

### 2.3 Schemas & Validierung

**Standort:** `/backend/app/modules/backoffice/finance/schemas.py`

- `ExpenseCreate`: Zum Erstellen von Ausgaben
- `ExpenseUpdate`: Für partielle Updates (alle Felder optional)
- `ExpenseRead`: Vollständige Ausgabenantwort
- `ExpenseListResponse`: Paginierte Liste
- `ExpenseKpiRequest`: Optionale KPI-Request-Parameter
- `ExpenseKpiResponse`: Gesamt und Aufschlüsselung nach Kategorie

**Validierungen:**
- Betrag muss > 0 sein
- Kategorie muss gültiger Enum sein

### 2.4 CRUD-Operationen

**Standort:** `/backend/app/modules/backoffice/finance/crud.py` (benannt service.py)

**Erstellen:**
- Erstellt Ausgabe mit allen Feldern
- Kategorie-Enum-Handhabung

**Lesen:**
- Liste mit Titel-, Kategorie-, Projekt-, Rechnungs- und Datumsbereichsfiltern
- Pagination-Unterstützung (Limit, Offset)
- Gibt Gesamtzahl mit Einträgen zurück

**Aktualisieren:**
- Partielle Updates (exclude_unset=True)
- Kategorie-Enum-Handhabung
- Alle Felder außer ID optional

**Löschen:**
- Hartes Löschen (v0.1)

**KPIs:**
- Berechnet Gesamtausgabenbetrag
- Gruppiert nach Kategorie mit Summe pro Kategorie
- Unterstützt dieselben Filter wie Liste (Titel, Kategorie, Projekt, Datumsbereich)

---

## 3. DATENBANKSCHEMA-MIGRATION

**Standort:** `/backend/alembic/versions/`

**Migrationsdateien:**
1. `2025_10_24_1224-0c0b8f566bc5_fix_invoice_expense_relationship.py`
   - Stellt Rechnung-Ausgaben-Beziehung her

2. `2025_10_24_1331-452a56fe4f4d_add_invoices_and_payments_tables.py`
   - Erstellt invoices, invoice_line_items, payments Tabellen
   - Erstellt Indizes für Filterung und Lookups

3. `2025_11_19_1707-c87120e6a54d_add_document_type_to_invoices.py`
   - Fügt document_type Spalte zur invoices Tabelle hinzu

**Hauptindizes:**
- `ix_invoices_customer_id`: Schnelle Kunden-Lookups
- `ix_invoices_project_id`: Schnelle Projekt-Lookups
- `ix_invoices_status`: Schnelle Status-Filterung
- `ix_invoices_issued_date`, `ix_invoices_due_date`: Datumsfilterung
- `ix_invoices_invoice_number`: Nummern-Lookups
- `ix_invoice_line_items_invoice_id`, `ix_invoice_line_items_position`: Positions-Sortierung
- `ix_payments_invoice_id`, `ix_payments_payment_date`, `ix_payments_method`: Zahlungs-Lookups
- `ix_expenses_*`: Ähnliche Indizes für Ausgabenfilterung

---

## 4. INTEGRATION MIT ANDEREN MODULEN

### 4.1 CRM-Integration
- Rechnungen benötigen einen Kunden (CRM-Modul)
- Kunde hat back_populates-Beziehung zu Rechnungen
- Customer.invoices greift auf alle ihre Rechnungen zu

### 4.2 Projekt-Integration
- Rechnungen können optional mit Projekten verknüpft werden
- Ausgaben können optional mit Projekten verknüpft werden
- Projekte verfolgen zugehörige Rechnungen und Ausgaben

### 4.3 Dokumentenverwaltung
- Rechnungs-PDFs werden als Dokumente registriert
- Dokument-Kategorie: "Rechnungen"
- Verknüpftes Modul: "invoices"
- Mit Metadaten für Suche/Organisation gespeichert

### 4.4 Zeiterfassungs-Integration
- Zukünftiges Potenzial: Zeiteinträge mit Rechnungspositionen verknüpfen
- Aktuell: Manuelle Eingabe von Stunden/Leistungen auf Rechnungen

---

## 5. AKTUELLER STAND & IMPLEMENTIERUNGSGRAD

### Vollständig implementiert
- **Rechnungserstellung & -verwaltung**
  - Vollständige CRUD-Operationen
  - Automatische Nummernvergabe mit jährlichem Sequenz-Reset
  - Unterstützung mehrerer Dokumenttypen
  - PDF-Generierung mit Branding

- **Zahlungsabwicklung**
  - Zahlungseingänge erfassen
  - Zahlungsmethoden verfolgen
  - Auto-Update des Rechnungsstatus basierend auf Zahlungen
  - Teilzahlungsunterstützung

- **Finanzberichterstattung**
  - Rechnungsstatistiken (Anzahlen, Summen, Offene Posten)
  - Ausgaben-KPIs (Summen nach Kategorie)
  - Status-basierte Berichterstattung
  - Datumsbereichsfilterung

- **Ausgabenverfolgung**
  - Ausgabenerstellung und -verwaltung
  - Kategoriebasierte Organisation
  - Verrechenbar-Flag für Kundenabrechnung
  - Beleg-/Dokumentanhang-Unterstützung

- **Validierung & Integrität**
  - Ordentliche Constraints auf Datenbankebene
  - Pydantic-Schema-Validierung
  - Beziehungsvalidierung (Kunde/Projekt existiert)
  - Eindeutige Rechnungsnummern-Durchsetzung

- **PDF-Generierung**
  - Professionelle Rechnungsvorlagen
  - Multi-Dokumenttyp-Unterstützung
  - QR-Code für SEPA-Zahlungen
  - Wasserzeichen-Unterstützung
  - Deutsche Formatierung

### Teilweise implementiert / Geplant
- **UI-Komponenten**
  - Keine aktuellen UI-Komponenten in `/ui/src/modules/`
  - Nur CRM- und Dashboard-Module haben UI
  - Rechnungs-/Finanz-UI muss entwickelt werden

- **Payment-Gateway-Integration**
  - Keine echte Zahlungsabwicklung (Stripe, PayPal, etc.)
  - Nur manuelle Zahlungseingabe
  - Zukunft: Webhook-Integration für Auto-Abgleich

- **Erweiterte Finanzberichte**
  - Keine GuV-Rechnungen
  - Keine Steuerberichte
  - Keine Cashflow-Prognosen
  - Keine Profitabilitätsanalyse nach Projekt

- **Buchhaltungsfunktionen**
  - Keine doppelte Buchführung
  - Keine Journal-Einträge
  - Kein Hauptbuch/Kontenplan
  - Keine Abschreibungsverfolgung

- **Multi-Währungs-Unterstützung**
  - Aktuell nur deutsche Formatierung
  - Kein Währungsfeld auf Rechnungen
  - Geht von EUR aus

---

## 6. API-RESPONSE-BEISPIELE

### Rechnung erstellen (200+ Zeilen Beispiel in Testdatei)
```json
{
  "invoice_number": "RE-2025-0001",
  "issued_date": "2025-12-22",
  "due_date": "2026-01-05",
  "customer_id": "uuid...",
  "project_id": "uuid...",
  "status": "draft",
  "total": 2145.50,
  "subtotal": 1800.00,
  "tax_amount": 342.00,
  "line_items": [
    {
      "position": 1,
      "description": "IT-Support",
      "quantity": 2,
      "unit": "Stunden",
      "unit_price": 85.00,
      "tax_rate": 19.0,
      "discount_percent": 0.0,
      "subtotal": 170.00,
      "tax_amount": 32.30,
      "total": 202.30
    }
  ],
  "payments": [],
  "paid_amount": 0,
  "outstanding_amount": 2145.50,
  "is_paid": false,
  "is_overdue": false
}
```

### Rechnungsstatistiken
```json
{
  "total_count": 42,
  "total_revenue": 150000.00,
  "outstanding_amount": 25000.00,
  "overdue_count": 3,
  "draft_count": 5,
  "sent_count": 12,
  "paid_count": 20,
  "cancelled_count": 2
}
```

---

## 7. TESTS

**Standort:** `/backend/tests/test_invoice.py`

- Integrationstestskript gegen Live-API
- Testet Rechnungserstellung mit Positionen
- Testet PDF-Generierung
- Testet Zahlungsablauf
- Manueller Test-Ansatz (nicht pytest)

---

## 8. KONFIGURATION & KONSTANTEN

### PDF-Generator-Konstanten
- **Firma:** K.I.T. Solutions
- **Inhaber:** Joshua Phu Kuhrau
- **Adresse:** Dietzstr. 1, 56073 Koblenz, Germany
- **E-Mail:** info@kit-it-koblenz.de
- **Website:** https://kit-it-koblenz.de
- **Telefon:** Tel. 0162 / 2654262
- **Bank:** DE94100110012706471170 (N26 Bank AG)

### Dokumenttyp-Konfigurationen
| Typ | Titel | Farbe | Standard-Bedingungen |
|------|-------|-------|----------------|
| invoice | RECHNUNG | #ff9100 | 14 Tage |
| quote | ANGEBOT | #008cff | 14 Tage gültig |
| credit_note | GUTSCHRIFT | #5dcc5d | Verrechnung mit offenen Posten |
| order_confirmation | AUFTRAGSBESTÄTIGUNG | #9933ff | Bitte prüfen |

---

## 9. DATEISTRUKTUR-ZUSAMMENFASSUNG

```
backend/
├── alembic/versions/
│   ├── 2025_10_24_1224-..._fix_invoice_expense_relationship.py
│   ├── 2025_10_24_1331-..._add_invoices_and_payments_tables.py
│   └── 2025_11_19_1707-..._add_document_type_to_invoices.py
│
└── app/modules/backoffice/
    ├── invoices/
    │   ├── __init__.py
    │   ├── models.py (Invoice, InvoiceLineItem, Payment, NumberSequence)
    │   ├── schemas.py (Pydantic-Modelle)
    │   ├── routes.py (FastAPI-Endpoints)
    │   ├── crud.py (Datenbankoperationen)
    │   ├── payments_crud.py (Zahlungsoperationen)
    │   ├── pdf_generator.py (PDF-Generierung)
    │   └── templates/ (leer, für zukünftige Vorlagen)
    │
    └── finance/
        ├── __init__.py
        ├── models.py (Expense)
        ├── schemas.py (Pydantic-Modelle)
        ├── router.py (FastAPI-Endpoints)
        ├── crud.py (service.py - Datenbankoperationen)
        └── service.py (identisch mit crud.py)

tests/
└── test_invoice.py (Integrationstestskript)
```

---

## 10. EMPFOHLENE NÄCHSTE SCHRITTE

### Priorität 1: UI-Implementierung
- Rechnungslistenseite mit Filtern und Pagination erstellen
- Rechnungsdetail-/Bearbeitungsseite erstellen
- Rechnungserstellungsformular mit Positionen erstellen
- Zahlungseingabeformular erstellen
- Rechnungsstatus-Verwaltungs-UI hinzufügen
- PDF-Download-Button hinzufügen

### Priorität 2: Payment-Integration
- Stripe oder PayPal integrieren
- Zahlungs-Webhooks für Auto-Abgleich hinzufügen
- Zahlungsstatus-Updates hinzufügen
- Zahlungshistorie-Visualisierung hinzufügen

### Priorität 3: Erweiterte Berichterstattung
- GuV-Rechnung erstellen
- Steuerbericht-Generierung hinzufügen
- Cashflow-Prognose hinzufügen
- Profitabilität nach Projekt hinzufügen
- Export zu Buchhaltungssoftware (ELSTER, Datev-Format)

### Priorität 4: Buchhaltungsfunktionen
- Kontenplan implementieren
- Journal-Einträge für manuelle Buchführung hinzufügen
- Hauptbuch-Ansichten hinzufügen
- Probebilanz-Berichte hinzufügen
- Abschreibungsverfolgung hinzufügen

### Priorität 5: Finanzanalyse
- Finanz-Dashboards hinzufügen
- Trend-Analyse hinzufügen
- Kundenprofitabilität hinzufügen
- Projektprofitabilität hinzufügen
- Prognosemodelle hinzufügen

---

## 11. WICHTIGE TECHNISCHE ENTSCHEIDUNGEN

1. **Automatische Rechnungsnummerierung:** Jährliche Sequenz pro Dokumenttyp mit atomarem Zähler mit FOR UPDATE Sperre
2. **Status-Verwaltung:** Auto-aktualisiert via SQLAlchemy Events wenn Zahlungen hinzugefügt/entfernt werden
3. **Kaskadier-Beziehungen:** Rechnung löschen kaskadiert zu Positionen, Zahlungen und Ausgaben
4. **PDF-Generierung:** ReportLab für professionelle Vorlagen, optionale Background-Task-Generierung
5. **Validierung:** Zwei-Ebenen-Validierung (Schema + Datenbank-Constraints)
6. **Pagination:** Limit auf max. 500 Einträge pro Anfrage zur Vermeidung von Speicherproblemen
7. **Decimal-Arithmetik:** Verwendet Decimal-Typ durchgehend für finanzielle Genauigkeit

---

## 12. BEKANNTE EINSCHRÄNKUNGEN

1. Noch keine UI-Komponenten (nur Backend)
2. Keine echte Payment-Processor-Integration (nur manuelle Eingabe)
3. Einzelne Währung (EUR angenommen)
4. Nur deutsche Sprache für PDF-Ausgabe
5. Kein Änderungsprotokoll für Rechnungsänderungen
6. Keine Rechnungsvorlagen (verwendet festes Layout)
7. Kein E-Mail-Benachrichtigungssystem
8. Keine Mahnungen bei überfälligen Rechnungen
9. Keine Verzugszinsen-/Zinsberechnung
10. Kein Mahnwesen-Management
