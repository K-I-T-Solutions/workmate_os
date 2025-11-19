# 📦 Core Entities

Das Core-System besteht aus folgenden zentralen Entitäten:

| Entity | Beschreibung |
|---------|---------------|
| `Employee` | Enthält alle persönlichen, organisatorischen und systemischen Informationen eines Mitarbeiters. |
| `Department` | Gruppiert Mitarbeiter und definiert Verantwortlichkeiten. |
| `Role` | Regelt Zugriffsrechte und Berechtigungen, synchronisiert mit Keycloak. |
| `Document` | Zentrale Dateiablage mit Typisierung und Metadaten. |
| `Reminder` | Modulübergreifende Erinnerungslogik (Tasks, Fristen, Notifications). |
| `Dashboard` | Individuelle Übersicht eines Mitarbeiters (Widgets, Layout, Themen). |
| `InfraService` | Verwaltung externer Systeme (DB, Auth, Mail, Chat etc.). |

### 📘 Entity Details
👉 Siehe das ER-Modell unter:  
[📄 Core ERM (DBML)](./core_erm.md)
