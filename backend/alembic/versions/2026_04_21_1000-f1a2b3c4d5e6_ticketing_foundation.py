"""ticketing foundation: type, channel, soft delete, sla, event log

Revision ID: f1a2b3c4d5e6
Revises: e8aae60dde48
Create Date: 2026-04-21 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'f1a2b3c4d5e6'
down_revision = 'e8aae60dde48'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Neue Spalten in support_tickets ---
    op.add_column('support_tickets', sa.Column('type', sa.String(50), nullable=False, server_default='support'))
    op.add_column('support_tickets', sa.Column('channel', sa.String(50), nullable=False, server_default='manual'))
    op.add_column('support_tickets', sa.Column('sla_deadline', sa.DateTime(), nullable=True))
    op.add_column('support_tickets', sa.Column('sla_breached', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('support_tickets', sa.Column('deleted_at', sa.DateTime(), nullable=True))

    op.create_index('ix_tickets_type', 'support_tickets', ['type'])
    op.create_index('ix_tickets_deleted_at', 'support_tickets', ['deleted_at'])

    # --- ticket_events Tabelle ---
    op.create_table(
        'ticket_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('ticket_id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('actor_id', sa.String(100), nullable=True),
        sa.Column('old_value', JSONB(), nullable=True),
        sa.Column('new_value', JSONB(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ticket_events_ticket_id', 'ticket_events', ['ticket_id'])
    op.create_index('ix_ticket_events_created_at', 'ticket_events', ['created_at'])


def downgrade() -> None:
    op.drop_table('ticket_events')
    op.drop_index('ix_tickets_deleted_at', 'support_tickets')
    op.drop_index('ix_tickets_type', 'support_tickets')
    op.drop_column('support_tickets', 'deleted_at')
    op.drop_column('support_tickets', 'sla_breached')
    op.drop_column('support_tickets', 'sla_deadline')
    op.drop_column('support_tickets', 'channel')
    op.drop_column('support_tickets', 'type')
