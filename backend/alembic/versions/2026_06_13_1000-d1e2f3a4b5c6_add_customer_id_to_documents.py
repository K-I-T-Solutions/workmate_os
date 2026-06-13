"""add customer_id to documents

Revision ID: d1e2f3a4b5c6
Revises: a9b8c7d6e5f4
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'd1e2f3a4b5c6'
down_revision = 'a9b8c7d6e5f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('documents', sa.Column(
        'customer_id',
        UUID(as_uuid=True),
        sa.ForeignKey('customers.id', ondelete='SET NULL'),
        nullable=True,
        comment='Optional link to a CRM customer',
    ))
    op.create_index('ix_documents_customer_id', 'documents', ['customer_id'])


def downgrade() -> None:
    op.drop_index('ix_documents_customer_id', table_name='documents')
    op.drop_column('documents', 'customer_id')
