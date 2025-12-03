// src/widgets/widgetTypes.ts

import type { Component } from "vue";

/**
 * Widget-Kategorien für bessere Organisation
 */
export type WidgetCategory =
  | "dashboard" // Allgemeine Dashboard-Widgets
  | "activity" // Aktivitäts-bezogene Widgets
  | "stats" // Statistik-Widgets
  | "actions" // Action-Widgets (Shortcuts)
  | "monitoring" // Monitoring & System
  | "communication" // Chat, Notifications
  | "custom"; // Benutzerdefiniert

/**
 * Widget-Größe im Grid (6-Spalten-System)
 */
export interface WidgetSize {
  w: number; // Breite (1-6)
  h: number; // Höhe in Grid-Einheiten
}

/**
 * Widget-Position im Grid
 */
export interface WidgetPosition {
  x: number; // Spalte (0-5)
  y: number; // Reihe (0-N)
  w: number; // Breite
  h: number; // Höhe
}

/**
 * Widget-Definition für Registry
 */
export interface WidgetDefinition {
  key: string;
  name: string;
  category: WidgetCategory;
  icon?: string;
  description?: string;
  component: () => Promise<Component>;
  defaultSize: WidgetSize;
  minSize?: WidgetSize;
  maxSize?: WidgetSize;
  resizable?: boolean;
  configurable?: boolean;
}

/**
 * Widget-Instanz-Konfiguration
 */
export interface WidgetConfig {
  enabled: boolean;
  data?: any;
  settings?: Record<string, any>;
}

/**
 * Dashboard-Layout-Konfiguration
 */
export interface DashboardLayout {
  [widgetKey: string]: WidgetPosition;
}

/**
 * Vollständige Widget-Konfiguration
 */
export interface DashboardWidgets {
  [widgetKey: string]: WidgetConfig;
}
