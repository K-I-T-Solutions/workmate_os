"""K.I.T. Rollenkonzept – Rollen neu strukturieren

Revision ID: d7f3a1b8e2c4
Revises: cc4e9f2b8d31
Create Date: 2026-07-02 09:00:00.000000

"""
import json
from alembic import op
import sqlalchemy as sa

revision = 'd7f3a1b8e2c4'
down_revision = 'cc4e9f2b8d31'
branch_labels = None
depends_on = None

# Bestehende Rollen umbenennen + neue Permissions
UPDATES = [
    # CEO → Geschäftsführung
    {
        "old_name": "CEO",
        "new_name": "Geschäftsführung",
        "description": "COO/CEO – Operative Gesamtverantwortung",
        "permissions": [
            "employees.*", "hr.*", "backoffice.*",
            "documents.*", "reminders.*", "support.*",
            "kb.*", "dashboards.*", "admin.read",
        ],
    },
    # Manager → Head of Events
    {
        "old_name": "Manager",
        "new_name": "Head of Events",
        "description": "Eventvertrieb, Kundenbeziehungen, Projektleitung Events",
        "permissions": [
            "hr.view",
            "backoffice.crm.*", "backoffice.projects.*",
            "backoffice.time_tracking.write",
            "backoffice.invoices.read", "backoffice.products.read",
            "documents.read", "reminders.*", "support.view", "dashboards.read",
        ],
    },
    # Employee → Mitarbeiter
    {
        "old_name": "Employee",
        "new_name": "Mitarbeiter",
        "description": "Standard-Mitarbeiterzugang – Zeiterfassung, HR-Ansicht, Dokumente",
        "permissions": [
            "hr.view",
            "backoffice.time_tracking.write",
            "documents.read", "reminders.*", "dashboards.read",
        ],
    },
    # Admin bleibt
    {
        "old_name": "Admin",
        "new_name": "Admin",
        "description": "Vollzugriff – Systemadministration",
        "permissions": ["*"],
    },
]

# Neue Rollen einfügen
INSERTS = [
    {
        "name": "CTO",
        "description": "Technische Leitung – Infrastruktur, WorkmateOS, DevOps",
        "permissions": [
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
        "permissions": [
            "employees.read", "hr.view",
            "backoffice.finance.*", "backoffice.invoices.*",
            "backoffice.crm.read", "backoffice.projects.read",
            "backoffice.time_tracking.view", "backoffice.products.read",
            "documents.read", "reminders.*", "dashboards.read",
        ],
    },
    {
        "name": "Marketing",
        "description": "Marketing & Kommunikation – CRM lesend, Content",
        "permissions": [
            "hr.view",
            "backoffice.crm.read",
            "documents.read", "reminders.read", "dashboards.read",
        ],
    },
]


def upgrade() -> None:
    conn = op.get_bind()

    # Bestehende Rollen aktualisieren
    for r in UPDATES:
        conn.execute(
            sa.text("""
                UPDATE roles
                SET name = :new_name,
                    description = :desc,
                    permissions_json = CAST(:perms AS jsonb)
                WHERE name = :old_name
            """),
            {
                "new_name": r["new_name"],
                "desc": r["description"],
                "perms": json.dumps(r["permissions"]),
                "old_name": r["old_name"],
            },
        )

    # Neue Rollen einfügen (falls noch nicht vorhanden)
    for r in INSERTS:
        conn.execute(
            sa.text("""
                INSERT INTO roles (id, name, description, permissions_json)
                VALUES (gen_random_uuid(), :name, :desc, CAST(:perms AS jsonb))
                ON CONFLICT (name) DO UPDATE
                SET description = EXCLUDED.description,
                    permissions_json = EXCLUDED.permissions_json
            """),
            {
                "name": r["name"],
                "desc": r["description"],
                "perms": json.dumps(r["permissions"]),
            },
        )


def downgrade() -> None:
    pass
