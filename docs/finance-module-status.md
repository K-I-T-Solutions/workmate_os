# Finance & Buchhaltung — Modul-Bestandsaufnahme

> Stand: April 2026 | WorkmateOS v4.0.0

---

## Gesamtbewertung

| Bereich | Reifegrad |
|---------|-----------|
| Rechnungssystem | 85% |
| Ausgaben-Management | 90% |
| Bankintegration | 60% |
| Zahlungsabgleich | 75% |
| E-Invoicing | 30% |
| Buchhaltungslogik | 20% |
| Steuer & Compliance | 50% |
| Reporting | 40% |

**Fazit:** Solides Rechnungssystem für Agenturen/Freiberufler. Keine vollständige Buchhaltungslösung für deutsches KMU.

---

## Was funktioniert

### Rechnungen (`backoffice/invoices/`)

- Erstellung mit automatischen Nummernkreisen (`RE-2025-0001`, `AN-`, `GS-`, `AB-`)
- Dokumenttypen: Rechnung, Angebot, Gutschrift, Auftragsbestätigung
- Positionen mit Menge, Preis, MwSt-Satz (19%/7%/0%), Rabatt
- Automatische Summenberechnung inkl. Steuer
- Status-Workflow: `draft → sent → paid / partial / overdue / cancelled`
- Soft-Delete (GoBD-konform)
- PDF-Generierung via ReportLab
- XRechnung-XML (EN16931) Generator vorhanden
- Zahlungserfassung mit Methode, Referenz, Datum
- Automatisches `outstanding_amount` / `payment_rate` Tracking
- Mahnwesen: 3-stufig, Modell + Endpunkte vorhanden
- Bulk-Status-Update
- GoBD-Export (ZIP mit CSV)
- DATEV-EXTF Export (SKR03: 8400/8300/8100)
- Audit-Trail (`AuditLog` Tabelle mit old/new JSON)

### Ausgaben (`backoffice/finance/` — Expenses)

- CRUD vollständig
- 9 Kategorien (Travel, Material, Software, Hardware, Consulting, Marketing, Office, Training, Other)
- Projekt- und Rechnungszuordnung
- KPIs nach Kategorie und Zeitraum

### Bankkonten & Transaktionen

- Bankkonten CRUD (Girokonto, Sparkonto, Kreditkarte, Kasse)
- Transaktionen CRUD mit Typ (Einnahme/Ausgabe/Überweisung/Gebühr/Zinsen)
- CSV-Import: N26, Sparkasse, Volksbank, Deutsche Bank — automatische Format-Erkennung
- n8n-Webhook (`POST /n8n/import-transactions`)
- Duplikat-Erkennung via Referenz
- Automatischer Kontostand-Update

### Zahlungsabgleich (Reconciliation)

- Automatischer Abgleich via Confidence-Score (0–100%)
  1. Rechnungsnummer im Verwendungszweck
  2. Betragsabgleich (±1 EUR Toleranz)
  3. Auto-Match ab 90%
- Manueller Abgleich, Rückgängig-Funktion
- Vorschläge für UI

### Frontend

- Finance-Dashboard mit KPIs (Revenue, Profit, Expenses)
- Bankkonten-Verwaltung
- Transaktionsliste + Reconciliation-UI
- Audit-Log-Seite
- Rechnungs-Dashboard, Liste, Detail, Formular
- Ausgaben-Dashboard, Liste, Formular

---

## Was fehlt

### Kritisch

| Feature | Warum nötig |
|---------|-------------|
| **Doppelte Buchführung** (Soll/Haben) | Pflicht für bilanzierende Unternehmen |
| **Kontenrahmen SKR03/SKR04** mit Automatikkonten | Korrekte Buchungssätze |
| **GuV & Bilanz** | Jahresabschluss, Steuererklärung |
| **Eingangsrechnungen** (Supplier Invoices) | Vorsteuer verbuchen |
| **Vorsteuer-Management** | Umsatzsteuervoranmeldung |
| **Mahnprozess-Automation** | Automatisches Versenden nach Fälligkeit |
| **ZUGFeRD PDF-Embedding** | `zugferd_path` Feld existiert, Generator fehlt |
| **FinTS/HBCI** | Direkter Kontoauszugs-Download (Modelle vorhanden, Implementierung fehlt) |
| **Elster-Integration** | UStVA automatisch generieren |

### Wichtig

- Multi-Currency (aktuell nur EUR)
- Wiederkehrende Rechnungen (Subscriptions)
- Automatische Zahlungserinnerungen per E-Mail
- Buchungsregeln (Kategorisierung nach Regeln)
- Kostenstellenrechnung
- Projektkalkulation (Ist vs. Budget)
- Stripe-Integration (Schemas vorhanden, Implementierung unvollständig)

### Nice-to-Have

- Mobile Quittungs-Erfassung
- Forecasting / Cashflow-Planung
- HR-Gehalts-Buchungen
- Multi-Tenant

---

## Bekannte Lücken im Code

| Datei | Problem |
|-------|---------|
| `invoices/routes.py` | ZUGFeRD: `zugferd_path` Feld in Models, kein Generator implementiert |
| `finance/` | FinTS: `FinTsCredentials` Schema vorhanden, keine Kommunikations-Implementierung |
| `finance/` | Stripe: Config-Modell + Schemas vorhanden, Routes fehlen weitgehend |
| `datev_export.py` | Nur Ausgangsrechnungen, keine Eingangsrechnungen / Buchungsjournal |
| Kein Modul | Keine `SupplierInvoice` / `Eingangsrechnung` Tabelle |
| Kein Modul | Kein `Account` / `JournalEntry` für doppelte Buchführung |

---

## Empfehlung Phase 5

Für eine vollständige Buchhaltungslösung (deutsches KMU) in Phase 5 priorisieren:

1. **FinTS-Integration** — automatischer Kontoauszugs-Import (python-fints Library)
2. **Eingangsrechnungen** — Supplier Invoice Modul mit Vorsteuer
3. **Elster UStVA** — Monatliche Voranmeldung (python-elster oder eric Library)
4. **ZUGFeRD PDF** — facturx Library korrekt einbinden
5. **Mahnprozess-Automation** — Cron-Job + E-Mail-Versand bei Fälligkeit
6. **GuV-Report** — auf Basis der vorhandenen Buchungen

Alternativ: SevDesk als vollständige Buchhaltungslösung beibehalten und WorkmateOS als reines Rechnungssystem positionieren (SevDesk-Integration bereits vorhanden).
