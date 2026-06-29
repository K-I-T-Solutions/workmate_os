"""drop hr_employee_documents table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b9
Create Date: 2026-06-29 18:00:00.000000

"""
from alembic import op

revision = 'd4e5f6a7b8c9'
down_revision = 'b2c3d4e5f6a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('hr_employee_documents')


def downgrade() -> None:
    pass
