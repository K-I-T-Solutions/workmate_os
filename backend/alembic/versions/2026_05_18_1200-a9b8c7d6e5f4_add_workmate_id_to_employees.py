"""add workmate_id to employees

Revision ID: a9b8c7d6e5f4
Revises: c1d2e3f4a5b6
Create Date: 2026-05-18 12:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'a9b8c7d6e5f4'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('employees', sa.Column(
        'workmate_id', sa.String(),
        nullable=True,
        comment='WM-100 — plattformübergreifende ID'
    ))
    op.create_unique_constraint('uq_employees_workmate_id', 'employees', ['workmate_id'])
    op.create_index('ix_employees_workmate_id', 'employees', ['workmate_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_employees_workmate_id', table_name='employees')
    op.drop_constraint('uq_employees_workmate_id', 'employees', type_='unique')
    op.drop_column('employees', 'workmate_id')
