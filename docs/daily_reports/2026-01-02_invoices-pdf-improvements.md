---
layout: default
title: Invoices PDF-Generator & Frontend Verbesserungen
parent: Daily Reports
nav_order: 5
---

# Daily Report - 02. Januar 2026

## Invoices Modul - PDF-Generator & Frontend Verbesserungen

### PDF-Generator komplett überarbeitet

#### Design & Typografie
- ✅ **Roboto Font** statt Helvetica implementiert
  - TrueType Fonts heruntergeladen und registriert
  - Alle Varianten: Regular, Bold, Italic, BoldItalic
  - Fonts im Verzeichnis: `backend/app/assets/fonts/`
- ✅ **Fettschrift** für wichtige Elemente:
  - Rechnungsnummer und Datum im Header
  - Position, Menge und Gesamt in der Positionstabelle
  - Kontaktname bei "Bei Rückfragen"
- ✅ **Zentrierung** aller Tabellenspalten außer Beschreibung
- ✅ Rückfragen-Text vereinfacht (nur Name, ohne "K.I.T. Solutions")

#### Intelligente Pagination
- ✅ **Automatischer Table-Split** bei zu vielen Positionen
  - Tabelle wird intelligent bei der richtigen Zeile umgebrochen
  - Header wird auf jeder Seite automatisch wiederholt (`repeatRows=1`)
  - Funktioniert mit beliebig vielen Positionen (getestet mit 3 und 10 Positionen)
- ✅ **Fortsetzungshinweise** zwischen Seiten
  - "Fortsetzung auf Seite 2 →" am Ende von Seite 1 (in Accent-Farbe, kursiv)
  - "← Fortsetzung von Seite 1" am Anfang von Seite 2 (in Accent-Farbe, kursiv)
- ✅ **Seitenzahlen** im Footer
  - Format: "Seite X von Y"
  - Zentriert unter dem 3-Spalten-Footer
  - Automatische Berechnung der Gesamtseitenzahl vor der Generierung
  - In grau für dezente Darstellung
- ✅ **Keine Überlappungen** mehr
  - Terms/Rückfragen werden automatisch auf neue Seite verschoben wenn nötig
  - Footer-Collision-Detection mit Sicherheitsabstand (10mm)
  - Alle Elemente haben genug Platz

#### Technische Details
- Neue `draw_footer()` Funktion mit optionalen `page_num` und `total_pages` Parametern
- Two-Pass-Logik: Seitenzahl wird vor der Generierung berechnet
  - Simulation der Tabellen-Höhe und Split-Positionen
  - Simulation der Terms/Rückfragen-Position
  - Berechnung ob neue Seite benötigt wird
- `table.split()` für intelligentes Aufteilen großer Tabellen
- Page-Counter wird bei jedem `showPage()` inkrementiert
- Paragraph-Styles für gemischte Font-Weights in Tabellenzellen

### Storage Abstraction Layer

- ✅ **Storage Factory** implementiert (`backend/app/core/storage/factory.py`)
  - Zentrale Funktion `get_storage()` für flexible Backend-Auswahl
  - Konfiguration über Environment Variable `STORAGE_BACKEND`
- ✅ **WebDAV Storage Adapter** (`backend/app/core/storage/nextcloud.py`)
  - Unterstützung für Nextcloud/WebDAV
  - Upload, Download, Delete, Exists Operationen
  - Konfiguration über `NEXTCLOUD_*` Environment Variables
- ✅ **Local Filesystem Storage Adapter** (`backend/app/core/storage/local.py`)
  - Fallback für lokale Entwicklung
  - Speicherung in `backend/app/storage/invoices/`
- ✅ **Invoice PDF Storage Migration**
  - Alte PDFs werden jetzt im konfigurierten Storage gespeichert
  - Migration-Script: `backend/scripts/migrate_invoice_pdfs_to_storage.py`

### Products Module (Artikel/Dienstleistungen)

- ✅ **CRUD Operations** für Products
  - `backend/app/modules/backoffice/products/crud.py`
  - `backend/app/modules/backoffice/products/routes.py`
  - `backend/app/modules/backoffice/products/schemas.py`
  - `backend/app/modules/backoffice/products/models.py`
- ✅ **Database Migrations**
  - `backend/alembic/versions/2026_01_01_2356-d13ce3a3941e_add_products_table.py`
  - `backend/alembic/versions/2026_01_01_2359-8e3d5cbbbc47_create_products_table_manually.py`
- ✅ **Frontend Integration**
  - Product-Select Component: `ui/src/modules/invoices/components/ProductSelect.vue`
  - useProducts Composable: `ui/src/modules/invoices/composables/useProducts.ts`
  - Product Types: `ui/src/modules/invoices/types/product.ts`
- ✅ **Import Script**
  - K.I.T. Products Import: `backend/scripts/import_kit_products.py`

### Frontend - Invoice Detail Verbesserungen

- ✅ **Card-basiertes Layout** für Positionen (`ui/src/modules/invoices/pages/InvoiceDetailPage.vue`)
  - Ersetzt die gequetschte 8-Spalten-Tabelle
  - Jede Position ist jetzt eine Card mit besserem Spacing
  - Prominente Anzeige von Beschreibung und Gesamtpreis
  - Details (Menge, Einzelpreis, Rabatt, MwSt) in flexibler Bottom-Row mit Badges
  - Positionsnummer in rundem Badge mit blauem Gradient
  - Hover-Effekte für bessere Interaktivität

### Dateien geändert

**Backend:**
- `backend/app/modules/backoffice/invoices/pdf_generator.py` (komplett überarbeitet, 764 Zeilen)
  - Neue `draw_footer()` Funktion mit Seitenzahlen
  - Table-Split-Logik
  - Two-Pass Seitenzahl-Berechnung
  - Fortsetzungshinweise
  - Roboto Font Integration
- `backend/app/modules/backoffice/invoices/crud.py` (angepasst für Storage)
- `backend/app/modules/backoffice/invoices/routes.py` (angepasst für Storage)
- `backend/app/modules/backoffice/invoices/schemas.py` (erweitert)
- `backend/app/core/settings/config.py` (Storage-Konfiguration)
- `backend/app/main.py` (Products-Routes registriert)
- **Neue Dateien:**
  - `backend/app/assets/fonts/Roboto-*.ttf` (4 Font-Dateien, ~2MB total)
  - `backend/app/core/storage/` (komplettes Package)
  - `backend/app/modules/backoffice/products/` (komplettes Module)
  - `backend/scripts/` (Migration & Import Scripts)

**Frontend:**
- `ui/src/modules/invoices/pages/InvoiceDetailPage.vue` (Positionen-Sektion redesigned)
- `ui/src/modules/invoices/pages/InvoiceFormPage.vue` (Product-Select integriert)
- `ui/src/modules/invoices/components/index.ts` (ProductSelect exportiert)
- `ui/src/modules/invoices/composables/index.ts` (useProducts exportiert)
- `ui/src/modules/invoices/types/index.ts` (Product-Types exportiert)
- **Neue Dateien:**
  - `ui/src/modules/invoices/components/ProductSelect.vue`
  - `ui/src/modules/invoices/composables/useProducts.ts`
  - `ui/src/modules/invoices/types/product.ts`

### Ergebnis

Das PDF-System ist jetzt **production-ready** und kann Rechnungen/Angebote mit beliebig vielen Positionen professionell darstellen. Die Pagination funktioniert automatisch und intelligent, ohne dass Inhalte mit dem Footer überlappen oder abgeschnitten werden.

**Features im Detail:**
- ✅ Roboto Font (professionell und modern)
- ✅ Fettschrift für wichtige Daten
- ✅ Zentrierung und optimiertes Layout
- ✅ Intelligente Pagination mit Table-Split
- ✅ Fortsetzungshinweise zwischen Seiten
- ✅ Seitenzahlen "Seite X von Y"
- ✅ Keine Footer-Überlappungen
- ✅ Funktioniert mit 3, 10, 50+ Positionen
- ✅ Storage Abstraction für flexible Speicherung
- ✅ Products Module für Artikelverwaltung

**Testing:**
- ✅ PDF mit 3 Positionen: 2 Seiten (Positionen + Terms/Rückfragen auf Seite 2)
- ✅ PDF mit 10 Positionen: 2 Seiten (Split bei Position 3/4, Summen + Terms auf Seite 2)
- ✅ Seitenzahlen korrekt berechnet und angezeigt
- ✅ Fortsetzungshinweise sichtbar
- ✅ Keine Überlappungen

---

**Git Commit:** `a7a290a`
**Branch:** `dev`
**Zeit:** ~3 Stunden
**Status:** ✅ Abgeschlossen, getestet und gepusht
