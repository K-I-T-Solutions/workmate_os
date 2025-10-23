"""
WorkmateOS - Seed Initial Data
Erstellt Default Roles, Departments und Admin User
"""
import sys
from datetime import date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.modules.employees.models import Department, Role, Employee


def seed_database():
    """Seed initial data"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # ==========================================
        # 1. CREATE DEFAULT ROLES
        # ==========================================
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
                ]
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
                    "reports.*"
                ]
            },
            {
                "name": "Manager",
                "description": "Department Manager",
                "permissions_json": [
                    "employees.view",
                    "hr.view",
                    "hr.approve",
                    "reports.view"
                ]
            },
            {
                "name": "Employee",
                "description": "Standard employee access",
                "permissions_json": [
                    "hr.view_own",
                    "hr.request",
                    "documents.view_own"
                ]
            }
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
        
        # ==========================================
        # 2. CREATE DEFAULT DEPARTMENTS
        # ==========================================
        print("\n🏢 Creating default departments...")
        
        departments_data = [
            {
                "name": "Management",
                "code": "MGMT",
                "description": "Executive Management & Strategy"
            },
            {
                "name": "IT & Development",
                "code": "IT",
                "description": "Software Development & IT Services"
            },
            {
                "name": "Finance",
                "code": "FIN",
                "description": "Accounting & Financial Management"
            },
            {
                "name": "Operations",
                "code": "OPS",
                "description": "Business Operations & Support"
            }
        ]
        
        departments = {}
        for dept_data in departments_data:
            existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
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
        
        # ==========================================
        # 3. CREATE ADMIN USER (Joshua Phu Kuhrau)
        # ==========================================
        print("\n👤 Creating admin user...")
        
        admin_email = "joshua@kit-it-koblenz.de"
        existing_admin = db.query(Employee).filter(Employee.email == admin_email).first()
        
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
                hire_date=date(2020, 1, 1),  # Anpassen an tatsächliches Gründungsdatum
                status="active",
                timezone="Europe/Berlin",
                language="de",
                theme="catppuccin-frappe",
                notifications_enabled=True,
                bio="Founder & CEO of K.I.T. Solutions - Fachinformatiker für Systemintegration"
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Set as department manager
            departments["MGMT"].manager_id = admin_user.id
            db.commit()
            
            print(f"  ✓ Created admin user: {admin_user.first_name} {admin_user.last_name}")
            print(f"    Email: {admin_user.email}")
            print(f"    Employee Code: {admin_user.employee_code}")
            print(f"    Role: CEO")
            print(f"    Department: Management")
        else:
            print(f"  ⊙ Admin user already exists: {existing_admin.email}")
        
        print("\n✅ Database seeding completed successfully!")
        print("\n" + "="*60)
        print("🎉 WORKMATE OS - READY TO USE!")
        print("="*60)
        print(f"\n👤 Admin Account:")
        print(f"   Email: {admin_email}")
        print(f"   Code:  KIT-0001")
        print(f"   Role:  CEO")
        print("\n📝 Next steps:")
        print("   1. Configure Keycloak integration")
        print("   2. Create API endpoints")
        print("   3. Build frontend components")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌱 WORKMATE OS - DATABASE SEEDING")
    print("="*60)
    seed_database()