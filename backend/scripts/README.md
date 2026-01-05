# WorkmateOS Scripts

Dieses Verzeichnis enthält Utility-Scripts für WorkmateOS.

## generate_demo_data.py

Generiert realistische Demo-Daten für Entwicklung und Testing.

### Features

- ✅ **Kunden (Customers):** 3 Demo-Kunden mit unterschiedlichen Typen (Business, Creator)
- ✅ **Kontakte (Contacts):** 6 Ansprechpartner für die Kunden
- ✅ **CRM Aktivitäten:** 20 realistische Aktivitäten (Calls, Meetings, Emails, etc.)
- ✅ **Projekte:** 3 Projekte mit Budget und Hourly Rate
- ✅ **Zeiterfassung:** 30 Time Entries über verschiedene Projekte

### Usage

```bash
# Im Container ausführen
docker exec workmate_backend python scripts/generate_demo_data.py

# Oder lokal (falls Backend läuft)
cd backend
python scripts/generate_demo_data.py
```

### Generierte Demo-Kunden

1. **TechStart GmbH** (KIT-CUS-000003)
   - Startup im Bereich Cloud-Infrastruktur
   - 3 Kontakte: CTO, Geschäftsführerin, DevOps Engineer
   - Projekt: Cloud Migration & Infrastruktur

2. **Müller Handwerk e.K.** (KIT-CUS-000004)
   - Traditioneller Handwerksbetrieb
   - 2 Kontakte: Geschäftsführer, Bürokauffrau
   - Projekt: Digitalisierung Handwerksbetrieb

3. **Sarah Schmidt** (KIT-CUS-000005)
   - Content Creator (YouTube, Twitch)
   - 1 Kontakt: Sarah Schmidt (Primary)
   - Projekt: Creator IT-Setup

### Idempotenz

Das Script ist idempotent - es kann mehrfach ausgeführt werden ohne Duplikate zu erstellen:
- Prüft vor dem Erstellen ob Kunden bereits existieren (anhand Name)
- Prüft vor dem Erstellen ob Kontakte bereits existieren (anhand Email)
- Überspringt bereits vorhandene Projekte (anhand Titel)

### Datenanpassung

Die Demo-Daten können in `/backend/scripts/generate_demo_data.py` angepasst werden:

```python
DEMO_CUSTOMERS = [...]
DEMO_CONTACTS = {...}
DEMO_ACTIVITIES_TEMPLATES = [...]
DEMO_PROJECTS = [...]
```

### Zeitstempel

- Kunden: Zufällig zwischen 30-90 Tagen in der Vergangenheit
- Kontakte: Zufällig zwischen 10-60 Tagen in der Vergangenheit
- Aktivitäten: Zufällig zwischen 1-60 Tagen in der Vergangenheit
- Zeiterfassung: Zufällig in den letzten 30 Tagen

### Dependencies

- SQLAlchemy
- App Models (CRM, Projects, Time Tracking, Employees)
- Database Session

---

## import_kit_products.py

Importiert K.I.T. Solutions Produktkatalog.

### Usage

```bash
docker exec workmate_backend python scripts/import_kit_products.py
```

Erstellt 10 Produkte in den Kategorien:
- Privatkunden (PC-Service, WLAN, Smart-Home, Creator-IT, Backup)
- Kleine Unternehmen (IT-Beratung, NAS/Server, Cloud, Creator-Workflows)
- Support (Wartung & Monitoring)

---

## migrate_invoice_pdfs_to_storage.py

Migriert Invoice PDFs zu einem neuen Storage-System.

### Usage

```bash
docker exec workmate_backend python scripts/migrate_invoice_pdfs_to_storage.py
```

Verschiebt PDF-Dateien und aktualisiert Datenbank-Pfade.

---

## Best Practices

1. **Backup erstellen** vor dem Ausführen von Scripts
2. **Development-Umgebung** nutzen für Tests
3. **Logs prüfen** nach Ausführung
4. **Idempotenz** beachten - Scripts können mehrfach laufen

## Neue Scripts erstellen

Template für neue Scripts:

```python
#!/usr/bin/env python3
"""
Script Description

Usage:
    python scripts/your_script.py
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.settings.database import SessionLocal

def main():
    db = SessionLocal()
    try:
        # Your logic here
        print("✅ Success!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
```
