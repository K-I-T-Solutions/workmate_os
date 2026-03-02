"""
WorkmateOS - Initial Database Seeder (v2)
-----------------------------------------
Erstellt Default Roles, Departments, Admin User & Demo CRM-Daten.
Wiederholbares, sicheres Setup für neue Installationen.
"""


from datetime import date
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

from app.core.settings.database import SessionLocal, engine, Base
from app.modules.employees.models import Department, Role, Employee
from app.modules.backoffice.crm.models import Customer, Contact, CustomerType, CustomerStatus
from app.modules.backoffice.projects.models import Project, ProjectStatus, ProjectPriority
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
                    "description": "Full system access",
                    "permissions_json": [
                        "system.*",
                        "employees.*",
                        "hr.*",
                        "finance.*",
                        "backoffice.*",
                        "support.*"
                    ],
                },
                {
                    "name": "CEO",
                    "description": "Chief Executive Officer - Full business access",
                    "permissions_json": [
                        "employees.view",
                        "employees.edit",
                        "hr.*",
                        "finance.*",
                        "backoffice.*",
                        "reports.*",
                    ],
                },
                {
                    "name": "Manager",
                    "description": "Department Manager",
                    "permissions_json": [
                        "employees.view",
                        "hr.view",
                        "hr.approve",
                        "reports.view",
                    ],
                },
                {
                    "name": "Employee",
                    "description": "Standard employee access",
                    "permissions_json": [
                        "hr.view_own",
                        "hr.request",
                        "documents.view_own",
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
                    roles[role_data["name"]] = existing
                    print(f"  ⊙ Role already exists: {role_data['name']}")

            db.commit()

            # ----------------------------------
            # 2. Default Departments
            # ----------------------------------
            print("\n🏢 Creating default departments...")

            departments_data = [
                {
                    "name": "Management",
                    "code": "MGMT",
                    "description": "Executive Management & Strategy",
                },
                {
                    "name": "IT & Development",
                    "code": "IT",
                    "description": "Software Development & IT Services",
                },
                {
                    "name": "Finance",
                    "code": "FIN",
                    "description": "Accounting & Financial Management",
                },
                {
                    "name": "Operations",
                    "code": "OPS",
                    "description": "Business Operations & Support",
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
                    department_id=departments["MGMT"].id,
                    role_id=roles["CEO"].id,
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
            # 6. Streamerforge (freiwillige Begleitung)
            # ----------------------------------
            print("\n🎮 Creating Streamerforge data...")

            sf_email = "kontakt@streamerforge.net"
            existing_sf = db.query(Customer).filter(Customer.email == sf_email).first()

            if not existing_sf:
                sf_customer = Customer(
                    customer_number="KIT-CUS-000006",
                    name="Streamerforge",
                    type=CustomerType.CREATOR.value,
                    status=CustomerStatus.ACTIVE.value,
                    email=sf_email,
                    website="https://streamerforge.net",
                    notes=(
                        "Streaming & Event-Tech Projekt. "
                        "Joshua begleitet als Techniker auf freiwilliger Basis. "
                        "Infrastruktur: Hetzner infra-1 (188.245.146.122), "
                        "Traefik + mailcow + kroma + docs."
                    ),
                )
                db.add(sf_customer)
                db.commit()
                db.refresh(sf_customer)
                print(f"  ✓ Created customer: {sf_customer.name}")
            else:
                sf_customer = existing_sf
                print(f"  ⊙ Customer already exists: {existing_sf.email}")

            # Projekt
            existing_sf_proj = (
                db.query(Project)
                .filter(Project.title == "Streamerforge Infrastruktur")
                .first()
            )

            if not existing_sf_proj:
                sf_project = Project(
                    customer_id=sf_customer.id,
                    department_id=departments["IT"].id,
                    project_manager_id=admin_user.id,
                    title="Streamerforge Infrastruktur",
                    project_number="PRJ-2026-001",
                    status=ProjectStatus.ACTIVE.value,
                    priority=ProjectPriority.MEDIUM.value,
                    start_date=date(2026, 2, 27),
                    description=(
                        "Aufbau und Dokumentation der gesamten Streamerforge-Infrastruktur. "
                        "Ansible-Playbook für lückenlose Reproduktion. "
                        "Dienste: Traefik, mailcow, kroma, docs."
                    ),
                    notes="Freiwillige Begleitung durch K.I.T. — kein Vertrag.",
                )
                db.add(sf_project)
                db.commit()
                db.refresh(sf_project)
                print(f"  ✓ Created project: {sf_project.title}")
            else:
                sf_project = existing_sf_proj
                print(f"  ⊙ Project already exists: {existing_sf_proj.title}")

            # TimeEntries aus Tätigkeitsnachweis
            sf_entries = [
                {
                    "start_time": datetime(2026, 2, 27, 20, 0),
                    "end_time":   datetime(2026, 2, 28,  2, 0),
                    "duration_minutes": 360,
                    "task_type": "deployment",
                    "note": "Kroma deployed, Mail-Server deployed, Debugging",
                    "billable": False,
                },
                {
                    "start_time": datetime(2026, 3, 1, 14, 30),
                    "end_time":   datetime(2026, 3, 1, 14, 45),
                    "duration_minutes": 15,
                    "task_type": "deployment",
                    "note": "Deploy-Docs Container, Dokumentation",
                    "billable": False,
                },
            ]

            for entry_data in sf_entries:
                existing_entry = (
                    db.query(TimeEntry)
                    .filter(
                        TimeEntry.project_id == sf_project.id,
                        TimeEntry.start_time == entry_data["start_time"],
                    )
                    .first()
                )
                if not existing_entry:
                    entry = TimeEntry(
                        project_id=sf_project.id,
                        employee_id=admin_user.id,
                        **entry_data,
                    )
                    db.add(entry)
                    print(f"  ⏺ Added time entry: {entry_data['note'][:50]} ({entry_data['duration_minutes']}min)")
                else:
                    print(f"  ⊙ Time entry already exists: {entry_data['start_time']}")

            db.commit()
            print("  ✓ Streamerforge data complete.")

            # ----------------------------------
            # DONE
            # ----------------------------------
            print("\n✅ Database seeding completed successfully!")
            print("\n" + "=" * 60)
            print("🎉 WORKMATE OS - READY TO USE!")
            print("=" * 60)
            print(f"\n👤 Admin Account:\n   Email: {admin_email}\n   Code:  KIT-0001\n   Role:  CEO")
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
