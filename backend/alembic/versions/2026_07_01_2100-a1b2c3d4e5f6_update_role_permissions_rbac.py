"""Update role permissions to match new RBAC schema

Revision ID: a1b2c3d4e5f6
Revises: 27b96c7e0ec2
Create Date: 2026-07-01 21:00:00.000000

"""
import json
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '27b96c7e0ec2'
branch_labels = None
depends_on = None

ROLE_PERMISSIONS = {
    "Admin": ["*"],
    "CEO": [
        "employees.read", "employees.write",
        "hr.*", "backoffice.*",
        "documents.read", "documents.write",
        "reminders.read", "reminders.write", "reminders.delete",
        "support.view", "kb.view", "dashboards.read", "admin.read",
    ],
    "Manager": [
        "employees.read",
        "hr.view", "hr.approve",
        "backoffice.time_tracking.view",
        "backoffice.projects.read",
        "backoffice.crm.read",
        "support.view", "documents.read",
        "reminders.read", "reminders.write", "reminders.delete",
        "kb.view", "dashboards.read",
    ],
    "Employee": [
        "hr.view_own", "hr.request",
        "backoffice.time_tracking.write",
        "documents.read",
        "reminders.read", "reminders.write", "reminders.delete",
        "dashboards.read",
    ],
}


def upgrade() -> None:
    conn = op.get_bind()
    for name, perms in ROLE_PERMISSIONS.items():
        conn.execute(
            sa.text("UPDATE roles SET permissions_json = :perms::jsonb WHERE name = :name"),
            {"perms": json.dumps(perms), "name": name},
        )


def downgrade() -> None:
    # Alte Permissions nicht rekonstruierbar
    pass
