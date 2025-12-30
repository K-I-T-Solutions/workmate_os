---
layout: default
title: Index
parent: Frontend
grand_parent: Wiki
nav_order: 2
---

# Frontend Dokumentations-Index

Dieses Dokument dient als Index für die gesamte Frontend-Dokumentation von WorkmateOS.

## Dokumentationsdateien

Die gesamte Dokumentation befindet sich im `/docs/`-Verzeichnis:

### 1. README_FRONTEND.md (HIER STARTEN)
**Datei**: `/docs/README_FRONTEND.md`
**Größe**: ~10 KB
**Lesezeit**: 10-15 Minuten

Der Einstiegspunkt für die gesamte Frontend-Dokumentation. Enthält:
- Überblick über jede Dokumentationsdatei
- Schnellstart für Entwickler (5-Minuten-Version)
- Wie Module funktionieren (einzigartige Desktop-ähnliche Architektur)
- Modul-Strukturmuster
- Datenfluss-Erklärung
- Wichtige Technologien und Versionen
- Häufige Entwicklungsaufgaben
- Architektur-Highlights
- Debugging-Leitfaden
- Nächste Schritte

**Am besten für**: Orientierung, Verständnis der Gesamtarchitektur

---

### 2. UI_ARCHITECTURE.md (UMFASSENDER LEITFADEN)
**Datei**: `/docs/UI_ARCHITECTURE.md`
**Größe**: ~29 KB
**Lesezeit**: 30-45 Minuten

Vollständiger detaillierter Leitfaden mit:
- Vollständige Verzeichnisstruktur mit Pfaden und Erklärungen
- Anwendungs-Bootstrap-Ablauf (main.ts → App.vue → Router)
- Router-Konfiguration mit Beispielen
- Modul-System-Architektur im Detail
- Fensterverwaltungssystem mit Schnittstellen und Methoden
- CRM-Modul als vollständiges Praxisbeispiel
- Service-Layer-Muster (crm.service.ts)
- Navigations-Composables-Muster
- Datenabruf-Composables-Muster
- Seitenkomponenten-Muster
- Organisation von Typdefinitionen
- Komponenten-Barrel-Exports
- API-Client-Setup mit Axios
- Layout-System (Topbar, Dock, WindowHost, WindowFrame)
- State Management mit Pinia
- Styling-System (Design Tokens + Tailwind)
- Schritt-für-Schritt-Anleitung zum Erstellen neuer Module (10 Schritte)
- Häufige Muster und Best Practices
- Umgebungssetup
- Build und Ausführung
- Technologie-Stack-Übersicht

**Am besten für**: Tiefes Verständnis, Erstellen neuer Module, Referenzmaterial

---

### 3. ARCHITECTURE_VISUAL.md (DIAGRAMME)
**Datei**: `/docs/ARCHITECTURE_VISUAL.md`
**Größe**: ~25 KB
**Lesezeit**: 15-20 Minuten

ASCII-Art-Diagramme zeigen:
- Anwendungsstruktur-Hierarchie
- Modul-interne Architektur (CRM-Beispiel)
- Fensterverwaltungssystem-Ablauf
- Datenabruf-Ablauf
- Styling-Architektur
- Datentypen-Organisation
- Komponentenkommunikationsmuster
- Dateierstellungs-Checkliste

**Am besten für**: Visuelle Lerner, Verständnis von Beziehungen, Datenfluss-Visualisierung

---

### 4. QUICK_REFERENCE.md (NACHSCHLAGEWERK)
**Datei**: `/docs/QUICK_REFERENCE.md`
**Größe**: ~11 KB
**Lesezeit**: Variiert (Referenzmaterial)

Schnelles Nachschlagen für:
- Dateispeicherorte für häufige Aufgaben
- Bestehende Modulstrukturen (CRM, Dashboard)
- Code-Snippets für häufige Aufgaben:
  - Neues Modul hinzufügen
  - API-Endpunkt hinzufügen
  - Datenabruf-Composable erstellen
  - Composable in Komponente verwenden
  - Navigation hinzufügen
  - Komponenten stylen
  - Pinia Store erstellen
  - Typdefinitionen hinzufügen
- Wichtige Muster mit Code
- Umgebungsvariablen
- Anwendung ausführen
- Komponentenhierarchie-Karte
- Verfügbare Icons (lucide-vue-next)
- TypeScript-Pfad-Aliase
- Tailwind-Klassen-Schnellreferenz
- Debugging-Tipps
- Häufige Fehler und Lösungen
- Schnellbefehle

**Am besten für**: Schnelles Nachschlagen, Muster merken, Dateispeicherorte finden

---

## Empfohlene Lesereihenfolge

### Für neue Entwickler (Erstmalig)
1. README_FRONTEND.md (10-15 Min.)
2. ARCHITECTURE_VISUAL.md (15-20 Min.) - Überspringen, wenn kein visueller Lerntyp
3. UI_ARCHITECTURE.md (30-45 Min.) - Fokus auf Abschnitte 1-5

**Gesamt: ~1 Stunde** um sich mit der Architektur vertraut zu machen

### Zum Erstellen eines neuen Moduls
1. QUICK_REFERENCE.md → Aufgabe 1: Neues Modul hinzufügen
2. UI_ARCHITECTURE.md → Abschnitt 10: Neues Modul erstellen
3. Referenz CRM-Modul: `ui/src/modules/crm/`

**Gesamt: 30-45 Minuten**

### Für tägliche Entwicklung
QUICK_REFERENCE.md als Referenzmaterial geöffnet halten

---

## Schnellnavigation nach Aufgabe

### "Ich möchte die Gesamtarchitektur verstehen"
→ README_FRONTEND.md

### "Ich möchte ein neues Modul erstellen"
→ UI_ARCHITECTURE.md (Abschnitt 10) + QUICK_REFERENCE.md (Aufgabe 1)

### "Ich möchte einen neuen API-Endpunkt hinzufügen"
→ QUICK_REFERENCE.md (Aufgabe 2)

### "Ich möchte verstehen, wie Daten fließen"
→ ARCHITECTURE_VISUAL.md + README_FRONTEND.md (Datenfluss-Abschnitt)

### "Ich muss einen Dateispeicherort finden"
→ QUICK_REFERENCE.md (Dateispeicherorte-Schnellsuche)

### "Ich bekomme einen Fehler"
→ QUICK_REFERENCE.md (Häufige Fehler & Lösungen)

### "Ich möchte die Modul-Navigation verstehen"
→ UI_ARCHITECTURE.md (Abschnitt 5: Modul-Strukturmuster)

### "Ich möchte Styling zu einer Komponente hinzufügen"
→ README_FRONTEND.md (Komponenten stylen) oder QUICK_REFERENCE.md (Aufgabe 6)

### "Ich muss Pinia für globalen State verwenden"
→ QUICK_REFERENCE.md (Aufgabe 7)

### "Ich möchte den Window Manager verstehen"
→ UI_ARCHITECTURE.md (Abschnitt 4: Modul-System-Architektur) + ARCHITECTURE_VISUAL.md (Fensterverwaltungssystem)

---

## Wichtige Konzepte zum Verstehen

Diese werden in der Dokumentation im Detail erklärt:

1. **Window Manager**: Desktop-ähnliche schwebende Fenster (nicht traditionelles Routing)
2. **Module**: In sich geschlossene Apps mit interner Routing (kein Vue Router)
3. **Service Layer**: Behandelt API-Aufrufe (crm.service.ts)
4. **Composables**: Verwalten State und wrappen Services (useCrmStats.ts)
5. **Design Tokens**: CSS Custom Properties für konsistentes Styling
6. **App Registry**: Zentrale Stelle zur Registrierung aller Module
7. **Type Safety**: Durchgängige starke TypeScript-Nutzung

---

## Dateispeicherorte - Schnellreferenz

**Kerndateien**:
- Entry: `ui/src/main.ts`
- Root: `ui/src/App.vue`
- Router: `ui/src/router/index.ts`
- Layout: `ui/src/layouts/AppLayout.vue`

**Modul-System**:
- Registry: `ui/src/layouts/app-manager/appRegistry.ts`
- Window Manager: `ui/src/layouts/app-manager/useAppManager.ts`
- Dock: `ui/src/layouts/components/Dock.vue`

**API**:
- Client: `ui/src/services/api/client.ts`

**Styles**:
- Tokens: `ui/src/styles/tokens.css`
- Base: `ui/src/styles/base.css`

**Beispiel-Modul (CRM)**:
- Entry: `ui/src/modules/crm/CrmApp.vue`
- Service: `ui/src/modules/crm/services/crm.service.ts`
- Navigation: `ui/src/modules/crm/composables/useCrmNavigation.ts`

Siehe QUICK_REFERENCE.md für vollständige Dateiauflistung.

---

## Technologie-Stack

- Vue 3 (^3.5.22)
- TypeScript (~5.9.3)
- Vite 7.1.14 (mit rolldown)
- Tailwind CSS 4
- Vue Router 4
- Pinia 3
- Axios ^1.13.2
- Lucide Vue ^0.554.0

---

## Erste Schritte - Befehle

```bash
# Abhängigkeiten installieren
cd ui
pnpm install

# Entwicklungsserver starten
pnpm run dev
# Besuche http://localhost:5173

# Für Produktion bauen
pnpm run build

# TypeScript-Fehler prüfen
vue-tsc --noEmit
```

---

## Wie diese Dokumentation zu verwenden ist

1. **Finde deine Dokumentationsdatei** in der obigen Liste
2. **Lies die empfohlenen Abschnitte** basierend auf deiner Aufgabe
3. **Referenziere QUICK_REFERENCE.md** für Code-Snippets und Muster
4. **Schau dir das CRM-Modul an** (`ui/src/modules/crm/`) für Praxisbeispiele
5. **Nutze ARCHITECTURE_VISUAL.md** zur Visualisierung von Konzepten

---

## Struktur jeder Dokumentationsdatei

### README_FRONTEND.md
- Orientierung und Überblick
- Schnelle Konzepte
- Architektur-Highlights
- Häufige Aufgaben
- Hilfe bekommen

### UI_ARCHITECTURE.md
- Vollständige Referenz
- Code-Beispiele
- Schritt-für-Schritt-Anleitungen
- Best Practices
- Erklärte Muster

### ARCHITECTURE_VISUAL.md
- ASCII-Diagramme
- Datenflüsse
- Komponentenhierarchien
- Systembeziehungen
- Dateierstellungs-Checkliste

### QUICK_REFERENCE.md
- Dateispeicherorte
- Code-Snippets
- Schnelle Muster
- Befehle
- Debugging-Tipps

---

## Dokumentationsqualität

Gesamte Dokumentation:
- 4 umfassende Leitfäden
- ~2.600 Zeilen Inhalt
- 75+ Code-Beispiele
- 20+ Diagramme
- Vollständige Abdeckung von:
  - Architektur
  - Modul-Erstellung
  - API-Integration
  - Styling
  - Debugging
  - Häufige Muster
  - Bestehende Beispiele

---

## Zur Dokumentation beitragen

Falls du Probleme findest oder die Dokumentation verbessern möchtest:
1. Prüfe aktuelle Dateien in `/docs/`
2. Aktualisiere relevante Datei
3. Halte Code-Beispiele aktuell
4. Füge Diagramme für komplexe Konzepte hinzu
5. Wahre Konsistenz mit anderen Dateien

---

## Schnelle Checkliste für Entwickler

Nach dem Lesen der Dokumentation solltest du verstehen:

- [ ] Wie main.ts die App bootet
- [ ] Warum wir Window Manager statt Routing verwenden
- [ ] Wie Module in appRegistry registriert werden
- [ ] Service → Composable → Component Muster
- [ ] Wann types/, services/, composables/, pages/, components/ zu verwenden sind
- [ ] Wie man ein neues Modul von Grund auf erstellt
- [ ] Wo neue API-Endpunkte hinzugefügt werden
- [ ] Wie Design Tokens funktionieren
- [ ] Wie man Komponenten stylt
- [ ] Wie man häufige Probleme debuggt

---

## Brauchst du Hilfe?

1. **"Ich verstehe X nicht"** → Prüfe README_FRONTEND.md Überblick
2. **"Wie mache ich X?"** → Prüfe QUICK_REFERENCE.md
3. **"Wo ist X?"** → Prüfe QUICK_REFERENCE.md Dateispeicherorte
4. **"Zeig mir ein Beispiel"** → Schau dir ui/src/modules/crm/ oder Code-Beispiele in UI_ARCHITECTURE.md an
5. **"Ich bekomme Fehler X"** → Prüfe QUICK_REFERENCE.md Häufige Fehler

---

**Letzte Aktualisierung**: 23. Dezember 2025
**Dokumentationsversion**: 1.0
**Frontend-Framework**: Vue 3
**Status**: Vollständig und einsatzbereit
