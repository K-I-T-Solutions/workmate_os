# WorkmateOS Finanz- & Rechnungserstellung - Schnellreferenz

## Aktueller Implementierungsstatus

### Vollständig implementierte Features
- [x] Rechnungserstellung mit Positionen
- [x] Automatische Rechnungsnummerierung (RE-2025-0001 Format)
- [x] Zahlungsverfolgung & -erfassung
- [x] Rechnungsstatus-Verwaltung (draft, sent, paid, partial, overdue, cancelled)
- [x] Auto-Status-Updates bei Zahlungseingängen
- [x] Professionelle PDF-Generierung mit SEPA QR-Codes
- [x] Ausgabenverfolgung mit Kategorien
- [x] Finanz-KPIs (Summen, Aufschlüsselung nach Kategorien)
- [x] Vollständige REST API mit Pagination & Filtern
- [x] Datenbank-Validierung & Constraints
- [x] Kunden- & Projekt-Integration
- [x] Mehrere Dokumenttypen (invoice, quote, credit_note, order_confirmation)
- [x] Zahlungsmethoden-Tracking (cash, bank_transfer, credit_card, etc.)
- [x] Decimal-Arithmetik für finanzielle Genauigkeit

### Noch nicht implementiert
- [ ] Frontend-UI-Komponenten
- [ ] Payment-Gateway-Integration (Stripe, PayPal)
- [ ] Erweiterte Finanzberichte (GuV, Steuer, Cashflow)
- [ ] Buchhaltungsfunktionen (Hauptbuch, Journal, Kontenplan)
- [ ] E-Mail-Benachrichtigungen
- [ ] Mahnwesen bei überfälligen Rechnungen
- [ ] Multi-Währungs-Unterstützung
- [ ] Rechnungs-Änderungsprotokoll
- [ ] Eigene Rechnungsvorlagen
- [ ] Batch-Rechnungsoperationen

---

## Wichtige API-Pfade

### Rechnungen
```
GET    /api/backoffice/invoices/
POST   /api/backoffice/invoices/
GET    /api/backoffice/invoices/statistics
GET    /api/backoffice/invoices/{invoice_id}
GET    /api/backoffice/invoices/{invoice_id}/pdf
PATCH  /api/backoffice/invoices/{invoice_id}
DELETE /api/backoffice/invoices/{invoice_id}
POST   /api/backoffice/invoices/{invoice_id}/payments
```

### Finanzen
```
GET    /api/backoffice/finance/expenses
POST   /api/backoffice/finance/expenses
GET    /api/backoffice/finance/kpis/expenses
```

---

## Datenbank-Modelle (Entity-Beziehungen)

```
Kunde ─────────→ Rechnung ──────────→ Rechnungsposition
                      ↓
                    Zahlung

Projekt ───→ Rechnung
        ↓
      Ausgabe ──→ Rechnung (optional)
```

---

## Wichtige Zahlen & Formate

- **Rechnungsnummern-Format:** `PREFIX-JAHR-LAUFNUMMER` (z.B. `RE-2025-0001`)
- **Präfixe nach Typ:**
  - RE = Rechnung (Invoice)
  - AN = Angebot (Quote)
  - GS = Gutschrift (Credit Note)
  - ST = Stornierung (Cancellation)
- **MwSt. Standard:** 19%
- **Pagination Max:** 500 Einträge pro Anfrage
- **Unterstützte Zahlungsmethoden:** 7 (cash, bank_transfer, credit_card, debit_card, paypal, sepa, other)

---

## Dateistandorte

| Komponente | Pfad |
|-----------|------|
| Rechnungsmodelle | `backend/app/modules/backoffice/invoices/models.py` |
| Rechnungs-API | `backend/app/modules/backoffice/invoices/routes.py` |
| Rechnungs-CRUD | `backend/app/modules/backoffice/invoices/crud.py` |
| Zahlungs-CRUD | `backend/app/modules/backoffice/invoices/payments_crud.py` |
| PDF-Generator | `backend/app/modules/backoffice/invoices/pdf_generator.py` |
| Finanzmodelle | `backend/app/modules/backoffice/finance/models.py` |
| Finanz-API | `backend/app/modules/backoffice/finance/router.py` |
| Finanz-CRUD | `backend/app/modules/backoffice/finance/crud.py` |
| Schemas | `backend/app/modules/backoffice/{invoices,finance}/schemas.py` |
| Migrationen | `backend/alembic/versions/*` (3 Migrationsdateien) |

---

## Rechnungs-Objekt-Eigenschaften (Berechnet)

```python
rechnung.paid_amount          # Summe aller Zahlungen
rechnung.outstanding_amount   # Total - paid_amount
rechnung.is_paid             # Boolean: outstanding_amount == 0
rechnung.is_overdue          # Boolean: heute > due_date und nicht bezahlt
rechnung.payment_rate        # Bezahlter Prozentsatz (0-100)
rechnung.days_until_due      # Verbleibende Tage (-N wenn überfällig)
```

---

## Positionsberechnungen

```
zwischensumme          = menge × einzelpreis
rabatt_betrag          = zwischensumme × (rabatt_prozent / 100)
zwischensumme_nach_rabatt = zwischensumme - rabatt_betrag
steuer_betrag          = zwischensumme_nach_rabatt × (steuer_satz / 100)
positions_gesamt       = zwischensumme_nach_rabatt + steuer_betrag
```

---

## Rechnungsstatus-Ablauf

```
ENTWURF → VERSENDET → { BEZAHLT | TEILBEZAHLT | ÜBERFÄLLIG } | STORNIERT
```

Status wird **automatisch aktualisiert** wenn:
- Zahlung erstellt: kann BEZAHLT oder TEILBEZAHLT werden
- Zahlung aktualisiert: Status neu berechnet
- Zahlung gelöscht: Status neu berechnet

---

## Firmendetails (Fest kodiert im PDF)

- **Name:** K.I.T. Solutions
- **Inhaber:** Joshua Phu Kuhrau
- **Adresse:** Dietzstr. 1, 56073 Koblenz, Germany
- **E-Mail:** info@kit-it-koblenz.de
- **Telefon:** Tel. 0162 / 2654262
- **Website:** https://kit-it-koblenz.de
- **IBAN:** DE94100110012706471170
- **BIC:** NTSBDEB1XX

---

## Letzte Änderungen (aus Git-Commits)

1. **2025-10-24**: Erstes Rechnungs- & Zahlungsmodul mit PDF-Generierung
2. **2025-11-19**: document_type Feld hinzugefügt (Multi-Dokument-Unterstützung)
3. **2025-12-16**: Erweitert mit Finanzmodul & Ausgabenverfolgung
4. **2025-12-19**: Nextcloud-Speicher-Integration für Dokumente

---

## Tests

**Testdatei:** `backend/tests/test_invoice.py`

Manueller Integrationstest gegen Live-API. Testet:
- Rechnungserstellung mit Positionen
- PDF-Generierung & Download
- Zahlungsablauf
- Status-Updates

Ausführen mit: `python tests/test_invoice.py`

---

## Nächste Prioritäten

1. **UI-Modul** - Vue.3/Vite-Komponenten für Rechnungs-/Finanzverwaltung erstellen
2. **Payment-Gateway** - Stripe/PayPal-Integration mit Webhooks
3. **Erweiterte Berichte** - GuV, Steuer, Cashflow, Profitabilitäts-Analyse
4. **Buchhaltung** - Kontenplan, Journal-Einträge, Hauptbuch-Ansichten
5. **Finanzanalyse** - Dashboards, Trend-Analyse, Forecasting
