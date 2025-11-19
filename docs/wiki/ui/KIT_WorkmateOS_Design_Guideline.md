# 🎨 K.I.T. Solutions – Design Guideline (WorkmateOS)

**Projekt:** WorkmateOS  
**Version:** 1.0  
**Designsystem:** K.I.T. Core UI  
**Autor:** Joshua Phu Kuhrau  
**Letzte Aktualisierung:** 02.11.2025

---

## 🧭 1. Grundprinzipien

**WorkmateOS** ist ein modulares, OS-ähnliches UI-System für interne Tools, Dashboards und Verwaltungssysteme.  
Das Design soll **technisch, ruhig und professionell** wirken – mit klaren Strukturen, hoher Lesbarkeit und einer wiedererkennbaren Markenästhetik.

### Designwerte
- **Klarheit:** Einfache, funktionale Oberflächen  
- **Konsistenz:** Einheitliche Abstände, Farben, Komponenten  
- **Balance:** Dezente Grundgestaltung mit kräftigem Akzent  
- **Modernität:** Sanfte Schatten, Glas-Effekte, minimalistische Icons  
- **Identität:** Sofort erkennbar als „K.I.T. Solutions“-Interface

---

## 🎨 2. Farbpalette

| Kategorie | Name | Hex-Code | Verwendung |
|------------|------|-----------|-------------|
| 🎛️ Hintergrund | `color.bg.primary` | `#232223` | Hauptoberfläche / Panels |
| 🟠 Akzent / Primary | `color.accent.primary` | `#ff9100` | Buttons, aktive Elemente |
| ⚪ Text hell | `color.text.primary` | `#ffffff` | Haupttext |
| ⚪ Text sekundär | `color.text.secondary` | `rgba(255,255,255,0.7)` | Labels, Hilfetext |
| ⚫ Linien / Rahmen | `color.border.light` | `rgba(255,255,255,0.1)` | Trennlinien, Container |
| 🌫️ Panel Overlay | `color.panel.glass` | `rgba(255,255,255,0.05)` | Glas- oder Blur-Effekt |

> 💡 **Tipp:** In Figma unter `kit/colors/` als Styles anlegen.

---

## 🔠 3. Typografie

| Kategorie | Schriftart | Gewicht | Verwendung |
|------------|-------------|----------|-------------|
| **Primary Font** | *Inter* oder *JetBrains Mono* | 400–600 | Standard / Body |
| **Headings** | *Inter SemiBold* | 600–700 | Überschriften |
| **Monospace (optional)** | *JetBrains Mono* | 400–500 | Technische Elemente |

### Typo-Skala

| Größe | Name | Verwendung |
|--------|-------|------------|
| 24px | `display` | große Titel |
| 18px | `heading` | Modul-Überschriften |
| 16px | `body` | Standardtext |
| 14px | `label` | Beschreibung, UI-Text |
| 12px | `caption` | Sekundärinfos |

---

## 🧱 4. Spacing & Layout

### Spacing-Skala

| Token | Wert | Verwendung |
|--------|------|-------------|
| `space.xs` | 4px | minimaler Abstand |
| `space.sm` | 8px | Standard Padding |
| `space.md` | 16px | Card-Inhalt, Layout-Padding |
| `space.lg` | 24px | Section-Abstand |
| `space.xl` | 32px | große Layout-Elemente |

### Grid-System
- 12-Spalten-Layout  
- Max. Breite: **1440px**  
- Gutter: **24px**  
- Margin: **32px**

---

## 🧩 5. Komponentenstruktur

Alle Komponenten folgen dem Namensschema:

```
kit/<Kategorie>/<Komponente>/<Variante>
```

### Basis-Komponenten

| Kategorie | Komponenten | Varianten |
|------------|--------------|------------|
| **Button** | Primary / Secondary / Ghost / Icon | `default`, `hover`, `disabled` |
| **Input** | Textfeld / Checkbox / Switch / Dropdown | `default`, `error`, `focused` |
| **Card / Panel** | Container, Info-Karten | `default`, `glass`, `highlight` |
| **Dock** | OS-Dock, App-Icons | `active`, `hover`, `inactive` |
| **Sidebar** | Navigation, Gruppen | `collapsed`, `expanded` |
| **Modal / Window** | OS-Fenster mit Titelleiste | `focused`, `unfocused` |
| **Toast** | Benachrichtigung | `info`, `success`, `warning`, `error` |
| **Widget** | Dashboard-Elemente | `tasks`, `status`, `calendar`, `metrics` |

> 🔧 In Figma als **Variants** mit Auto Layout aufbauen.

---

## 🪞 6. UI-Elemente & Effekte

### Rundungen
| Token | Wert |
|--------|------|
| `radius.sm` | 8px |
| `radius.md` | 12px |
| `radius.lg` | 16px |

### Schatten & Blur
| Token | Wert | Verwendung |
|--------|------|-------------|
| `shadow.soft` | 0 2px 8px rgba(0,0,0,0.2) | Panels, Modals |
| `blur.glass` | Background Blur 8–12px | Glasoberflächen |

---

## 🖥️ 7. OS-Layout-Vorgaben

### Grundstruktur

1. **Dock (unten):** Zentriert, 6–8 Icons, Glow bei aktivem Modul  
2. **Topbar (oben):** Uhrzeit, Profil, System-Icons  
3. **Sidebar (links):** Navigation zwischen Modulen  
4. **Main Window:** Dynamischer Inhaltsbereich mit Tabs oder Cards  
5. **Widgets-Bereich (rechts optional):** Systemstatus, Erinnerungen etc.

> 🧩 Für alle Layoutzonen `Auto Layout Frames` oder `Grids` verwenden.

---

## 🧭 8. Layer- & Page-Struktur in Figma

Empfohlene Struktur:

```
📁 K.I.T. WorkmateOS
│
├── 01_Foundations
│   ├── Colors
│   ├── Typography
│   ├── Effects
│   └── Spacing & Grid
│
├── 02_Components
│   ├── Buttons
│   ├── Inputs
│   ├── Panels
│   ├── Dock
│   ├── Sidebar
│   ├── Widgets
│   └── Modals
│
├── 03_Patterns
│   ├── OS Layout
│   ├── Dashboard View
│   ├── Reminder System
│   └── Settings View
│
└── 04_Assets
    ├── Icons
    ├── Logos
    └── Illustrations
```

---

## ⚡ 9. Interaktionsprinzipien

| Zustand | Beschreibung |
|----------|---------------|
| **Hover** | Leicht aufgehellte Akzentfarbe oder Glow |
| **Active** | Kräftiger Farbton + Schatten |
| **Focus** | Feine Linie in `#ff9100` |
| **Disabled** | 40% Deckkraft |
| **Transition** | 100–200 ms, `ease-in-out` |

---

## 🧠 10. Best Practices

✅ Verwende **Auto Layout** konsequent  
✅ Nutze **Variants** für Zustände  
✅ Halte alle Farben & Fonts als **Figma Styles**  
✅ Baue Komponenten **responsiv** (min/max width)  
✅ Kommentiere komplexe Frames mit Beschriftungen  
✅ Vermeide manuelle Positionierungen – arbeite mit Constraints  

---

> 🧡 **Ziel:**  
> Ein einheitliches, wartbares und OS-inspiriertes UI-System für WorkmateOS und zukünftige Tools im K.I.T. Solutions-Ökosystem.
