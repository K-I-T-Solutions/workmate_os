"""db cleanup: drop chat_messages, create products + ticket_events

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-29 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Leichen droppen
    op.drop_table('chat_messages')

    # products erstellen
    op.create_table(
        'products',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('sku', sa.String(100), nullable=True, unique=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_service', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('price_type', sa.String(50), nullable=False, server_default='fixed'),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('unit', sa.String(50), nullable=False, server_default='Stk.'),
        sa.Column('default_tax_rate', sa.Numeric(5, 2), nullable=False, server_default='19.00'),
        sa.Column('min_quantity', sa.Numeric(10, 2), nullable=True),
        sa.Column('max_quantity', sa.Numeric(10, 2), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # ticket_events erstellen
    op.create_table(
        'ticket_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('ticket_id', UUID(as_uuid=True), sa.ForeignKey('support_tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('actor_id', sa.String(100), nullable=True),
        sa.Column('old_value', JSONB, nullable=True),
        sa.Column('new_value', JSONB, nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_ticket_events_ticket_id', 'ticket_events', ['ticket_id'])
    op.create_index('ix_ticket_events_created_at', 'ticket_events', ['created_at'])


def downgrade() -> None:
    op.drop_table('ticket_events')
    op.drop_table('products')
