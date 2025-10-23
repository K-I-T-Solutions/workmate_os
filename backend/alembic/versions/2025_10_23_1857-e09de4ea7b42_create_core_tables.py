"""Create core tables

Revision ID: e09de4ea7b42
Revises:
Create Date: 2025-10-23 18:57:40.119120+02:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e09de4ea7b42'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create roles table first (no dependencies)
    op.create_table('roles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('keycloak_id', sa.String(), nullable=True, comment='Linked Keycloak role ID'),
        sa.Column('permissions_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="List of permissions, e.g. ['hr.view', 'finance.edit']"),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Step 2: Create departments WITHOUT manager_id FK (circular dependency)
    op.create_table('departments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=True, comment='Short code, e.g. HR, FIN, IT'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('manager_id', sa.UUID(), nullable=True),  # FK added later
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Step 3: Create employees table
    op.create_table('employees',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('employee_code', sa.String(), nullable=False, comment='KIT-0001 etc.'),
        sa.Column('uuid_keycloak', sa.String(), nullable=True, comment='Linked Keycloak user ID'),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True, comment='male, female, diverse, other'),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('nationality', sa.String(), nullable=True),
        sa.Column('photo_url', sa.String(), nullable=True, comment='/uploads/avatars/...'),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('address_street', sa.String(), nullable=True),
        sa.Column('address_zip', sa.String(), nullable=True),
        sa.Column('address_city', sa.String(), nullable=True),
        sa.Column('address_country', sa.String(), nullable=True),
        sa.Column('department_id', sa.UUID(), nullable=True),
        sa.Column('role_id', sa.UUID(), nullable=True),
        sa.Column('reports_to', sa.UUID(), nullable=True, comment='Supervisor'),
        sa.Column('employment_type', sa.String(), nullable=True, comment='fulltime, parttime, intern, external'),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, comment='active, inactive, on_leave'),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=True),
        sa.Column('matrix_username', sa.String(), nullable=True, comment='@user:intern.phudevelopement.xyz'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['reports_to'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('employee_code')
    )
    
    # Step 4: Add the circular FK from departments to employees
    op.create_foreign_key(
        'fk_departments_manager_id_employees',
        'departments', 'employees',
        ['manager_id'], ['id']
    )
    
    # Step 5: Create remaining tables (depend on employees)
    op.create_table('dashboards',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('widgets_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('layout_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('last_accessed', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True, comment='pdf, image, doc, etc.'),
        sa.Column('category', sa.String(), nullable=True, comment='e.g. Krankmeldung, Vertrag, Rechnung'),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('linked_module', sa.String(), nullable=True, comment='Origin module e.g. HR, Finance'),
        sa.Column('uploaded_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('checksum', sa.String(), nullable=True),
        sa.Column('is_confidential', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('infra_services',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True, comment='database, auth, mail, chat, storage, external_api'),
        sa.Column('connection_url', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('last_sync', sa.TIMESTAMP(), nullable=True),
        sa.Column('managed_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['managed_by'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('reminders',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True, comment='low, medium, high, critical'),
        sa.Column('linked_entity_type', sa.String(), nullable=True, comment='Target type, e.g. Document, Ticket'),
        sa.Column('linked_entity_id', sa.UUID(), nullable=True),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, comment='open, done, overdue'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('notified', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop in reverse order
    op.drop_table('reminders')
    op.drop_table('infra_services')
    op.drop_table('documents')
    op.drop_table('dashboards')
    
    # Drop the circular FK first
    op.drop_constraint('fk_departments_manager_id_employees', 'departments', type_='foreignkey')
    
    op.drop_table('employees')
    op.drop_table('departments')
    op.drop_table('roles')