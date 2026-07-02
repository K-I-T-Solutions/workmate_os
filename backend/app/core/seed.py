"""
WorkmateOS - Initial Database Seeder (v2)
-----------------------------------------
Erstellt Default Roles, Departments, Admin User & Demo CRM-Daten.
Wiederholbares, sicheres Setup für neue Installationen.
"""


from datetime import date
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal, engine, Base
from app.modules.employees.models import Department, Role, Employee
from app.modules.backoffice.crm.models import Customer, Contact
from app.modules.backoffice.projects.models import Project
from app.modules.backoffice.time_tracking.models import TimeEntry
from datetime import datetime, timedelta
import random

# ==========================================
#  Helper: Context-Managed DB Session
# ==========================================
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
#  Seeder Logic
# ==========================================
def seed_database():
    """Seed initial WorkmateOS data."""
    print("\n" + "=" * 60)
    print("🌱 WORKMATE OS - DATABASE SEEDING")
    print("=" * 60)

    # Ensure tables exist (for first startup)
    Base.metadata.create_all(bind=engine)

    with get_db() as db:
        try:
            print("🌿 Starting database seeding...")

            # ----------------------------------
            # 1. Default Roles
            # ----------------------------------
            print("\n📋 Creating default roles...")

            roles_data = [
                {
                    "name": "Admin",
                    "description": "Vollzugriff – Systemadministration",
                    "permissions_json": ["*"],
                },
                {
                    "name": "Geschäftsführung",
                    "description": "COO/CEO – Operative Gesamtverantwortung",
                    "permissions_json": [
                        "employees.*", "hr.*", "backoffice.*",
                        "documents.*", "reminders.*", "support.*",
                        "kb.*", "dashboards.*", "admin.read",
                    ],
                },
                {
                    "name": "CTO",
                    "description": "Technische Leitung – Infrastruktur, WorkmateOS, DevOps",
                    "permissions_json": [
                        "employees.read", "hr.view",
                        "backoffice.projects.*", "backoffice.time_tracking.*",
                        "backoffice.crm.read", "backoffice.products.read",
                        "backoffice.invoices.read", "backoffice.finance.read",
                        "documents.*", "support.*", "kb.*", "reminders.*", "dashboards.read",
                    ],
                },
                {
                    "name": "CFO",
                    "description": "Finanzleitung – Rechnungen, Finanzen, Controlling",
                    "permissions_json": [
                        "employees.read", "hr.view",
                        "backoffice.finance.*", "backoffice.invoices.*",
                        "backoffice.crm.read", "backoffice.projects.read",
                        "backoffice.time_tracking.view", "backoffice.products.read",
                        "documents.read", "reminders.*", "dashboards.read",
                    ],
                },
                {
                    "name": "Head of Events",
                    "description": "Eventvertrieb, Kundenbeziehungen, Projektleitung Events",
                    "permissions_json": [
                        "hr.view",
                        "backoffice.crm.*", "backoffice.projects.*",
                        "backoffice.time_tracking.write",
                        "backoffice.invoices.read", "backoffice.products.read",
                        "documents.read", "reminders.*", "support.view", "dashboards.read",
                    ],
                },
                {
                    "name": "Mitarbeiter",
                    "description": "Standard-Mitarbeiterzugang – Zeiterfassung, HR-Ansicht, Dokumente",
                    "permissions_json": [
                        "hr.view",
                        "backoffice.time_tracking.write",
                        "documents.read", "reminders.*", "dashboards.read",
                    ],
                },
                {
                    "name": "Marketing",
                    "description": "Marketing & Kommunikation – CRM lesend, Content",
                    "permissions_json": [
                        "hr.view",
                        "backoffice.crm.read",
                        "documents.read", "reminders.read", "dashboards.read",
                    ],
                },
            ]

            roles = {}
            for role_data in roles_data:
                existing = db.query(Role).filter(Role.name == role_data["name"]).first()
                if not existing:
                    role = Role(**role_data)
                    db.add(role)
                    db.flush()
                    roles[role_data["name"]] = role
                    print(f"  ✓ Created role: {role_data['name']}")
                else:
                    # Permissions immer aktualisieren (nicht nur beim Erstellen)
                    existing.permissions_json = role_data["permissions_json"]
                    existing.description = role_data["description"]
                    roles[role_data["name"]] = existing
                    print(f"  ↺ Updated role: {role_data['name']}")

            db.commit()

            # ----------------------------------
            # 2. Default Departments
            # ----------------------------------
            print("\n🏢 Creating default departments...")

            departments_data = [
                {
                    "name": "Geschäftsführung",
                    "code": "GF",
                    "description": "CEO & COO – Strategie, Operations, Gesamtverantwortung",
                },
                {
                    "name": "Technology & Software",
                    "code": "TECH",
                    "description": "Infrastruktur, DevOps, WorkmateOS, Custom Software",
                },
                {
                    "name": "Finance & Administration",
                    "code": "FIN",
                    "description": "Buchhaltung, Rechnungswesen, Controlling, Verträge",
                },
                {
                    "name": "Events & Live Technology",
                    "code": "EVT",
                    "description": "Eventvertrieb, Kundenbeziehungen, Streaming, Hybrid-Setups",
                },
                {
                    "name": "Facility & Produktion",
                    "code": "FAC",
                    "description": "Aufbau, Materialverwaltung, Transport, Standort-Instandhaltung",
                },
                {
                    "name": "Marketing & Kommunikation",
                    "code": "MKT",
                    "description": "Social Media, Content, Website-Pflege, lokale Sichtbarkeit",
                },
            ]

            departments = {}
            for dept_data in departments_data:
                existing = (
                    db.query(Department).filter(Department.code == dept_data["code"]).first()
                )
                if not existing:
                    dept = Department(**dept_data)
                    db.add(dept)
                    db.flush()
                    departments[dept_data["code"]] = dept
                    print(f"  ✓ Created department: {dept_data['name']}")
                else:
                    departments[dept_data["code"]] = existing
                    print(f"  ⊙ Department already exists: {dept_data['name']}")

            db.commit()

            # ----------------------------------
            # 3. Admin User (Joshua Phu Kuhrau)
            # ----------------------------------
            print("\n👤 Creating admin user...")

            admin_email = "joshua@kit-it-koblenz.de"
            existing_admin = (
                db.query(Employee).filter(Employee.email == admin_email).first()
            )

            if not existing_admin:
                admin_user = Employee(
                    employee_code="KIT-0001",
                    first_name="Joshua Phu",
                    last_name="Kuhrau",
                    gender="male",
                    birth_date=date(1995, 11, 22),
                    nationality="German",
                    email=admin_email,
                    phone="0162-2654262",
                    address_street="Dietzstr. 1",
                    address_zip="56073",
                    address_city="Koblenz",
                    address_country="Germany",
                    department_id=departments["GF"].id,
                    role_id=roles["Admin"].id,
                    employment_type="fulltime",
                    hire_date=date(2020, 1, 1),
                    status="active",
                    timezone="Europe/Berlin",
                    language="de",
                    theme="catppuccin-frappe",
                    notifications_enabled=True,
                    bio="Founder & CEO of K.I.T. Solutions - Fachinformatiker für Systemintegration",
                )

                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)

                # Set as department manager
                departments["MGMT"].manager_id = admin_user.id
                db.commit()

                print(f"  ✓ Created admin user: {admin_user.first_name} {admin_user.last_name}")
            else:
                admin_user = existing_admin  # WICHTIGER FIX
                print(f"  ⊙ Admin user already exists: {existing_admin.email}")

            # ----------------------------------
            # 4. Demo CRM-Daten
            # ----------------------------------
            print("\n🧩 Creating demo CRM data...")

            print("\n🧩 Creating demo CRM data...")

            demo_customer_email = "kontakt@demo-kunde.de"
            existing_customer = (
                db.query(Customer).filter(Customer.email == demo_customer_email).first()
            )

            if not existing_customer:
                demo_customer = Customer(
                    name="K.I.T. Solutions Demo Kunde",
                    type="Company",
                    email=demo_customer_email,
                    phone="0261-1234567",
                    street="Rheinstraße 10",
                    zip_code="56068",
                    city="Koblenz",
                    country="Germany",
                    notes="Demo-Kunde für Tests und API-Dokumentation."
                )

                db.add(demo_customer)
                db.commit()
                db.refresh(demo_customer)

                contact = Contact(
                    customer_id=demo_customer.id,
                    firstname="Max",
                    lastname="Muster",
                    email="max@demo-kunde.de",
                    phone="0151-999999",
                    position="IT-Beauftragter",
                )
                db.add(contact)
                db.commit()

                print(f"  ✓ Created demo customer & contact: {demo_customer.name}")
            else:
                demo_customer = existing_customer  # 🧩 WICHTIGER FIX
                print(f"  ⊙ Demo customer already exists: {existing_customer.email}")


            # ----------------------------------
            # 5. Demo Projects & Time Entries
            # ----------------------------------
            print("\n📁 Creating demo projects...")

            projects_data = [
                {
                    "title": "IT-Support Vertragskunde",
                    "description": "Regelmäßige Wartung und Support für K.I.T. Solutions Demo Kunde.",
                    "status": "active",
                    "customer_id": demo_customer.id,
                    "department_id": departments["IT"].id,
                    "start_date": datetime(2025, 10, 1),
                    "end_date": datetime(2025, 12, 31),
                },
                {
                    "title": "Netzwerk-Audit & Sicherheit",
                    "description": "Projekt zur Analyse und Optimierung der Netzwerksicherheit.",
                    "status": "in_progress",
                    "customer_id": demo_customer.id,
                    "department_id": departments["IT"].id,
                    "start_date": datetime(2025, 10, 5),
                    "end_date": datetime(2025, 11, 30),
                },
            ]

            projects = []
            for proj_data in projects_data:
                existing = (
                    db.query(Project)
                    .filter(Project.title == proj_data["title"])
                    .first()
                )
                if not existing:
                    project = Project(**proj_data)
                    db.add(project)
                    db.flush()
                    projects.append(project)
                    print(f"  ✓ Created project: {project.title}")
                else:
                    projects.append(existing)
                    print(f"  ⊙ Project already exists: {existing.title}")

            db.commit()

            # ==========================================
            # 5. CREATE DEMO TIME ENTRIES
            # ==========================================
            print("\n⏱️ Creating demo time entries...")

            time_entries = []
            for project in projects:
                for i in range(3):
                    start_time = datetime(2025, 10, 20, 9 + i, 0)
                    end_time = start_time + timedelta(hours=random.randint(1, 3))
                    note = f"Wartung / Tätigkeit Nr. {i+1} für {project.title}"

                    entry = TimeEntry(
                        project_id=project.id,
                        employee_id=admin_user.id,
                        start_time=start_time,
                        end_time=end_time,
                        note=note,
                    )
                    db.add(entry)
                    db.flush()
                    time_entries.append(entry)
                    print(f"  ⏺ Added time entry {i+1}h for project '{project.title}'")

            db.commit()
            print(f"  ✓ {len(time_entries)} time entries created successfully.")

            # ----------------------------------
            # DONE
            # ----------------------------------
            print("\n✅ Database seeding completed successfully!")
            print("\n" + "=" * 60)
            print("🎉 WORKMATE OS - READY TO USE!")
            print("=" * 60)
            print(f"\n👤 Admin Account:\n   Email: {admin_email}\n   Code:  KIT-0001\n   Role:  Admin")
            print("\n🧩 Demo CRM:\n   Customer: K.I.T. Solutions Demo Kunde\n   Contact: Max Muster")
            print("\n📝 Next steps:\n   1. Configure Keycloak integration\n   2. Create API endpoints\n   3. Build frontend components")
            print("=" * 60 + "\n")

        except SQLAlchemyError as e:
            print(f"\n❌ SQLAlchemy Error during seeding: {e}")
            db.rollback()
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            db.rollback()
            raise


if __name__ == "__main__":
    seed_database()
