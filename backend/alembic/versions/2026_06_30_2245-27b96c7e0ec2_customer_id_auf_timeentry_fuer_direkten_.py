"""customer_id auf TimeEntry fuer direkten Kundenbezug ohne Projekt

Revision ID: 27b96c7e0ec2
Revises: e5f6a7b8c9d0
Create Date: 2026-06-30 22:45:08.186207+02:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '27b96c7e0ec2'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'time_entries',
        sa.Column(
            'customer_id',
            sa.Uuid(),
            nullable=True,
            comment='Direkter Kundenbezug — auch ohne Projekt (z.B. Support-Einsatz)',
        ),
    )
    op.create_index(
        op.f('ix_time_entries_customer_id'),
        'time_entries',
        ['customer_id'],
        unique=False,
    )
    op.create_foreign_key(
        'fk_time_entries_customer_id_customers',
        'time_entries',
        'customers',
        ['customer_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_time_entries_customer_id_customers',
        'time_entries',
        type_='foreignkey',
    )
    op.drop_index(op.f('ix_time_entries_customer_id'), table_name='time_entries')
    op.drop_column('time_entries', 'customer_id')
