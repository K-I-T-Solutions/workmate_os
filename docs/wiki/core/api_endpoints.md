# 🧩 Core API Endpoints (Entwurf)

| Endpoint | Methode | Beschreibung |
|-----------|----------|---------------|
| `/api/employees` | GET / POST / PUT / DELETE | CRUD für Mitarbeiter |
| `/api/departments` | GET / POST | Abteilungsverwaltung |
| `/api/roles` | GET / POST | Rollen und Berechtigungen |
| `/api/documents` | GET / POST / DELETE | Dokumente hochladen und verwalten |
| `/api/reminders` | GET / POST / PATCH | Erinnerungen und Aufgaben |
| `/api/dashboard` | GET | Zusammenfassung für eingeloggte Nutzer |
| `/api/infra` | GET / PATCH | Überwachung externer Systeme |

> ⚙️ Alle Endpunkte sind mit Keycloak abgesichert (`bearer token`),  
> Rückgaben erfolgen im JSON-Format.
