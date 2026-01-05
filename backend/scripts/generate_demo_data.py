#!/usr/bin/env python3
"""
WorkmateOS - Demo Data Generator

Generiert realistische Testdaten für:
- Kunden (Customers)
- Kontakte (Contacts)
- CRM Aktivitäten (Activities)
- Projekte (Projects)
- Zeiterfassung (Time Entries)
- Rechnungen (Invoices)

Usage:
    python scripts/generate_demo_data.py
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, date
from decimal import Decimal
from uuid import uuid4
import random

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.settings.database import SessionLocal
from app.modules.backoffice.crm import models as crm_models, crud as crm_crud, schemas as crm_schemas
from app.modules.backoffice.projects import models as project_models
from app.modules.backoffice.invoices import models as invoice_models
from app.modules.backoffice.time_tracking import models as time_models
from app.modules.employees.models import Employee


# ============================================================================
# DEMO DATA DEFINITIONS
# ============================================================================

DEMO_CUSTOMERS = [
    {
        "name": "TechStart GmbH",
        "email": "info@techstart-demo.de",
        "phone": "+49 261 98765432",
        "type": "business",
        "status": "active",
        "website": "https://techstart-demo.de",
        "street": "Innovationsweg 15",
        "city": "Koblenz",
        "zip_code": "56068",
        "country": "Deutschland",
        "tax_id": "DE987654321",
        "notes": "Startup im Bereich Cloud-Infrastruktur. Sehr technikaffin.",
    },
    {
        "name": "Müller Handwerk e.K.",
        "email": "kontakt@mueller-handwerk.de",
        "phone": "+49 261 55544433",
        "type": "business",
        "status": "active",
        "website": None,
        "street": "Meisterstraße 8",
        "city": "Koblenz",
        "zip_code": "56072",
        "country": "Deutschland",
        "tax_id": "DE112233445",
        "notes": "Traditioneller Handwerksbetrieb. Braucht Unterstützung bei Digitalisierung.",
    },
    {
        "name": "Sarah Schmidt",
        "email": "sarah.schmidt@creator-demo.de",
        "phone": "+49 175 1234567",
        "type": "creator",
        "status": "active",
        "website": "https://sarahschmidt.tv",
        "street": "Rheinufer 23",
        "city": "Koblenz",
        "zip_code": "56068",
        "country": "Deutschland",
        "tax_id": None,
        "notes": "Content Creator (YouTube, Twitch). Braucht Creator-IT-Lösungen.",
    },
]

DEMO_CONTACTS = {
    "TechStart GmbH": [
        {
            "firstname": "Martin",
            "lastname": "Weber",
            "email": "m.weber@techstart-demo.de",
            "phone": "+49 261 98765433",
            "position": "CTO",
            "department": "IT",
            "is_primary": True,
            "notes": "Hauptansprechpartner für technische Fragen",
        },
        {
            "firstname": "Julia",
            "lastname": "Schneider",
            "email": "j.schneider@techstart-demo.de",
            "phone": "+49 261 98765434",
            "position": "Geschäftsführerin",
            "department": "Management",
            "is_primary": False,
            "notes": "Entscheidungsträgerin für Budgets",
        },
        {
            "firstname": "Tom",
            "lastname": "Fischer",
            "email": "t.fischer@techstart-demo.de",
            "phone": "+49 261 98765435",
            "position": "DevOps Engineer",
            "department": "IT",
            "is_primary": False,
            "notes": "Technischer Kontakt für Infrastruktur",
        },
    ],
    "Müller Handwerk e.K.": [
        {
            "firstname": "Klaus",
            "lastname": "Müller",
            "email": "k.mueller@mueller-handwerk.de",
            "phone": "+49 261 55544434",
            "position": "Geschäftsführer",
            "department": None,
            "is_primary": True,
            "notes": "Inhaber und Meister",
        },
        {
            "firstname": "Anna",
            "lastname": "Müller",
            "email": "a.mueller@mueller-handwerk.de",
            "phone": "+49 261 55544435",
            "position": "Bürokauffrau",
            "department": "Verwaltung",
            "is_primary": False,
            "notes": "Zuständig für Rechnungen und Verwaltung",
        },
    ],
    "Sarah Schmidt": [
        {
            "firstname": "Sarah",
            "lastname": "Schmidt",
            "email": "sarah.schmidt@creator-demo.de",
            "phone": "+49 175 1234567",
            "position": "Content Creator",
            "department": None,
            "is_primary": True,
            "notes": "Direkter Kontakt für alle Anfragen",
        },
    ],
}

ACTIVITY_TYPES = [
    "call", "email", "meeting", "note", "task", "quote_sent",
    "contract_signed", "support_request", "follow_up"
]

DEMO_ACTIVITIES_TEMPLATES = [
    {
        "type": "call",
        "description": "Erstgespräch zur IT-Infrastruktur: Telefonisches Kennenlernen. Kunde hat Interesse an Cloud-Migration geäußert.",
    },
    {
        "type": "meeting",
        "description": "Vor-Ort Termin: Netzwerk-Analyse - Besichtigung der aktuellen IT-Infrastruktur. Potentiale identifiziert.",
    },
    {
        "type": "email",
        "description": "Angebot für IT-Beratung versendet - Angebot AN-2026-XXX per Email versendet. Rückmeldung bis Ende der Woche erwartet.",
    },
    {
        "type": "quote_sent",
        "description": "Angebot: Smart Home Installation - Detailliertes Angebot für Smart Home Lösung erstellt und versendet.",
    },
    {
        "type": "contract_signed",
        "description": "Vertrag unterschrieben: Wartungsvertrag für 12 Monate unterschrieben. Startdatum: nächsten Monat.",
    },
    {
        "type": "call",
        "description": "Nachfrage zum Support-Ticket - Kunde meldet sich bezüglich langsamer Server-Performance. Ticket erstellt.",
    },
    {
        "type": "meeting",
        "description": "Projektabschluss-Meeting - Finale Abnahme des Projekts. Kunde sehr zufrieden. Potential für Folgeauftrag.",
    },
    {
        "type": "email",
        "description": "Follow-Up nach Projekt-Abschluss - Feedback-Email versendet. Kunde antwortet mit positiver Bewertung.",
    },
    {
        "type": "task",
        "description": "Drucker-Problem gemeldet - Netzwerkdrucker wird nicht erkannt. Remote-Support durchgeführt.",
    },
    {
        "type": "note",
        "description": "Geburtstag notiert - Kunde hat morgen Geburtstag. Kurze Gratulations-Email senden.",
    },
]

DEMO_PROJECTS = [
    {
        "title": "Cloud Migration & Infrastruktur",
        "description": "Migration der On-Premise Infrastruktur zu AWS. Inklusive Setup von CI/CD Pipelines.",
        "status": "active",
        "priority": "high",
        "budget": Decimal("15000.00"),
        "hourly_rate": Decimal("95.00"),
    },
    {
        "title": "Digitalisierung Handwerksbetrieb",
        "description": "Implementierung von digitaler Zeiterfassung, Rechnungssoftware und Website.",
        "status": "planning",
        "priority": "medium",
        "budget": Decimal("8000.00"),
        "hourly_rate": Decimal("75.00"),
    },
    {
        "title": "Creator IT-Setup",
        "description": "Aufbau eines professionellen Creator-Studios mit Backup-Lösungen.",
        "status": "active",
        "priority": "medium",
        "budget": Decimal("5000.00"),
        "hourly_rate": Decimal("85.00"),
    },
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def random_date_in_range(start_days_ago: int, end_days_ago: int = 0) -> datetime:
    """Generiert ein zufälliges Datum in der Vergangenheit."""
    days_ago = random.randint(end_days_ago, start_days_ago)
    return datetime.now() - timedelta(days=days_ago)


def get_random_employee(db: Session) -> Employee | None:
    """Holt einen zufälligen Employee."""
    employees = db.query(Employee).limit(10).all()
    return random.choice(employees) if employees else None


# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def create_demo_customers(db: Session) -> dict:
    """Erstellt Demo-Kunden und gibt Mapping zurück."""
    print("\n📦 Erstelle Demo-Kunden...")

    # Hole existierende Kunden
    existing = db.query(crm_models.Customer).all()
    customer_map = {c.name: c for c in existing}

    created_count = 0
    for customer_data in DEMO_CUSTOMERS:
        if customer_data["name"] in customer_map:
            print(f"  ⏭️  {customer_data['name']} existiert bereits")
            continue

        # Verwende CRUD-Funktion für automatische customer_number Generierung
        customer_schema = crm_schemas.CustomerCreate(**customer_data)
        customer = crm_crud.create_customer(db, customer_schema)

        # Update timestamps für realistische Demo-Daten
        customer.created_at = random_date_in_range(90, 30)
        db.commit()
        db.refresh(customer)

        customer_map[customer.name] = customer
        created_count += 1
        print(f"  ✅ {customer.name} ({customer.customer_number}) erstellt")

    # Commit is already done in create_customer
    print(f"📊 {created_count} neue Kunden erstellt")
    return customer_map


def create_demo_contacts(db: Session, customer_map: dict) -> int:
    """Erstellt Demo-Kontakte für Kunden."""
    print("\n👥 Erstelle Demo-Kontakte...")

    created_count = 0
    for customer_name, contacts in DEMO_CONTACTS.items():
        customer = customer_map.get(customer_name)
        if not customer:
            print(f"  ⚠️ Kunde '{customer_name}' nicht gefunden")
            continue

        for contact_data in contacts:
            # Prüfe ob Kontakt bereits existiert
            existing = db.query(crm_models.Contact).filter(
                crm_models.Contact.customer_id == customer.id,
                crm_models.Contact.email == contact_data["email"]
            ).first()

            if existing:
                print(f"  ⏭️  {contact_data['firstname']} {contact_data['lastname']} existiert bereits")
                continue

            contact = crm_models.Contact(
                id=uuid4(),
                customer_id=customer.id,
                **contact_data,
                created_at=random_date_in_range(60, 10),
                updated_at=datetime.now(),
            )
            db.add(contact)
            created_count += 1
            print(f"  ✅ {contact.firstname} {contact.lastname} @ {customer_name}")

    db.commit()
    print(f"📊 {created_count} neue Kontakte erstellt")
    return created_count


def create_demo_activities(db: Session, customer_map: dict, count: int = 15) -> int:
    """Erstellt Demo CRM-Aktivitäten."""
    print(f"\n📝 Erstelle {count} Demo-Aktivitäten...")

    customers = list(customer_map.values())
    if not customers:
        print("  ⚠️ Keine Kunden gefunden")
        return 0

    created_count = 0
    for i in range(count):
        customer = random.choice(customers)

        # Hole Kontakte für diesen Kunden
        contacts = db.query(crm_models.Contact).filter(
            crm_models.Contact.customer_id == customer.id
        ).all()

        contact = random.choice(contacts) if contacts else None
        template = random.choice(DEMO_ACTIVITIES_TEMPLATES)

        activity = crm_models.Activity(
            id=uuid4(),
            customer_id=customer.id,
            contact_id=contact.id if contact else None,
            type=template["type"],
            description=template["description"],
            occurred_at=random_date_in_range(60, 1),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(activity)
        created_count += 1

        if (i + 1) % 5 == 0:
            print(f"  ✅ {i + 1}/{count} Aktivitäten erstellt...")

    db.commit()
    print(f"📊 {created_count} neue Aktivitäten erstellt")
    return created_count


def create_demo_projects(db: Session, customer_map: dict) -> dict:
    """Erstellt Demo-Projekte."""
    print("\n🚀 Erstelle Demo-Projekte...")

    customers = list(customer_map.values())
    if len(customers) < len(DEMO_PROJECTS):
        print(f"  ⚠️ Nur {len(customers)} Kunden, aber {len(DEMO_PROJECTS)} Projekte")

    project_map = {}
    created_count = 0

    for i, project_data in enumerate(DEMO_PROJECTS):
        if i >= len(customers):
            break

        customer = customers[i]
        employee = get_random_employee(db)

        # Prüfe ob Projekt bereits existiert
        existing = db.query(project_models.Project).filter(
            project_models.Project.title == project_data["title"]
        ).first()

        if existing:
            print(f"  ⏭️  {project_data['title']} existiert bereits")
            project_map[project_data["title"]] = existing
            continue

        start_date = date.today() - timedelta(days=random.randint(10, 60))

        project = project_models.Project(
            id=uuid4(),
            customer_id=customer.id,
            project_manager_id=employee.id if employee else None,
            start_date=start_date,
            deadline=start_date + timedelta(days=random.randint(30, 90)),
            **project_data,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(project)
        project_map[project.title] = project
        created_count += 1
        print(f"  ✅ {project.title} für {customer.name}")

    db.commit()
    print(f"📊 {created_count} neue Projekte erstellt")
    return project_map


def create_demo_time_entries(db: Session, project_map: dict, count: int = 20) -> int:
    """Erstellt Demo-Zeiterfassungen."""
    print(f"\n⏱️  Erstelle {count} Demo-Zeiterfassungen...")

    projects = list(project_map.values())
    if not projects:
        print("  ⚠️ Keine Projekte gefunden")
        return 0

    employees = db.query(Employee).limit(5).all()
    if not employees:
        print("  ⚠️ Keine Employees gefunden")
        return 0

    created_count = 0
    for i in range(count):
        project = random.choice(projects)
        employee = random.choice(employees)

        # Zufällige Zeit zwischen 1-8 Stunden
        duration_hours = random.uniform(1.0, 8.0)
        duration_minutes = int(duration_hours * 60)

        # Zufälliger Tag in den letzten 30 Tagen
        entry_date = date.today() - timedelta(days=random.randint(1, 30))
        start_time = datetime.combine(entry_date, datetime.min.time()) + timedelta(hours=random.randint(8, 12))
        end_time = start_time + timedelta(minutes=duration_minutes)

        billable = random.choice([True, True, True, False])  # 75% billable

        tasks = [
            "Projektplanung und Analyse",
            "Entwicklung und Implementierung",
            "Testing und Quality Assurance",
            "Dokumentation",
            "Meeting mit Kunde",
            "Code Review",
            "Deployment und Monitoring",
            "Support und Bugfixing",
        ]

        time_entry = time_models.TimeEntry(
            id=uuid4(),
            employee_id=employee.id,
            project_id=project.id,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            billable=billable,
            hourly_rate=project.hourly_rate if billable else None,
            note=random.choice(tasks),
            task_type=random.choice(["development", "meeting", "documentation", "support"]),
            is_approved=random.choice([True, False]),
            is_invoiced=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(time_entry)
        created_count += 1

        if (i + 1) % 5 == 0:
            print(f"  ✅ {i + 1}/{count} Time Entries erstellt...")

    db.commit()
    print(f"📊 {created_count} neue Zeiterfassungen erstellt")
    return created_count


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Hauptfunktion zum Generieren der Demo-Daten."""
    print("=" * 60)
    print("🎨 WorkmateOS Demo Data Generator")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. Kunden erstellen
        customer_map = create_demo_customers(db)

        # 2. Kontakte erstellen
        create_demo_contacts(db, customer_map)

        # 3. CRM Aktivitäten erstellen
        create_demo_activities(db, customer_map, count=20)

        # 4. Projekte erstellen
        project_map = create_demo_projects(db, customer_map)

        # 5. Zeiterfassungen erstellen
        create_demo_time_entries(db, project_map, count=30)

        print("\n" + "=" * 60)
        print("✅ Demo-Daten erfolgreich generiert!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Fehler beim Generieren der Demo-Daten:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
