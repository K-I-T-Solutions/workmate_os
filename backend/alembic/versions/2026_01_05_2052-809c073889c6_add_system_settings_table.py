"""add_system_settings_table

Revision ID: 809c073889c6
Revises: 3831958a8e57
Create Date: 2026-01-05 20:52:00.961885+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '809c073889c6'
down_revision: Union[str, None] = '3831958a8e57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Uuid(), nullable=False),

        # Company Information
        sa.Column('company_name', sa.String(length=200), nullable=False, server_default='WorkmateOS'),
        sa.Column('company_legal', sa.String(length=50), server_default=''),
        sa.Column('tax_number', sa.String(length=50), server_default=''),
        sa.Column('registration_number', sa.String(length=50), server_default=''),
        sa.Column('address_street', sa.String(length=200), server_default=''),
        sa.Column('address_zip', sa.String(length=10), server_default=''),
        sa.Column('address_city', sa.String(length=100), server_default=''),
        sa.Column('address_country', sa.String(length=100), server_default='Deutschland'),
        sa.Column('company_email', sa.String(length=100), server_default=''),
        sa.Column('company_phone', sa.String(length=50), server_default=''),
        sa.Column('company_website', sa.String(length=200), server_default=''),

        # Localization
        sa.Column('default_timezone', sa.String(length=50), nullable=False, server_default='Europe/Berlin'),
        sa.Column('default_language', sa.String(length=10), nullable=False, server_default='de'),
        sa.Column('default_currency', sa.String(length=10), nullable=False, server_default='EUR'),
        sa.Column('date_format', sa.String(length=20), nullable=False, server_default='DD.MM.YYYY'),

        # Working Hours
        sa.Column('working_hours_per_day', sa.Integer(), nullable=False, server_default='8'),
        sa.Column('working_days_per_week', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('vacation_days_per_year', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('weekend_saturday', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('weekend_sunday', sa.Boolean(), nullable=False, server_default='true'),

        # System Configuration
        sa.Column('maintenance_mode', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('allow_registration', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('require_email_verification', sa.Boolean(), nullable=False, server_default='true'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),

        sa.PrimaryKeyConstraint('id')
    )

    # Insert initial default settings (Singleton pattern)
    op.execute("""
        INSERT INTO system_settings (id, company_name)
        VALUES (gen_random_uuid(), 'WorkmateOS')
    """)


def downgrade() -> None:
    op.drop_table('system_settings')