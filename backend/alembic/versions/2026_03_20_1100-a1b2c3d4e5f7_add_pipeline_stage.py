"""add pipeline stage to customers

Revision ID: a1b2c3d4e5f7
Revises: f1a2b3c4d5e6
Create Date: 2026-03-20 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'customers',
        sa.Column(
            'pipeline_stage',
            sa.String(50),
            nullable=True,
            server_default='new_lead',
            comment='Pipeline-Stage: new_lead, qualified, proposal, negotiation, won, lost'
        )
    )
    op.create_index('ix_customers_pipeline_stage', 'customers', ['pipeline_stage'])


def downgrade() -> None:
    op.drop_index('ix_customers_pipeline_stage', table_name='customers')
    op.drop_column('customers', 'pipeline_stage')
