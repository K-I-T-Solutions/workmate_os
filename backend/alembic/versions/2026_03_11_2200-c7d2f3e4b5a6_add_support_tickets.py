"""add_support_tickets

Revision ID: c7d2f3e4b5a6
Revises: b9f1e4c8a2d3
Create Date: 2026-03-11 22:00:00.000000+01:00

Erstellt support_tickets und support_ticket_comments Tabellen.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c7d2f3e4b5a6'
down_revision: Union[str, None] = 'b9f1e4c8a2d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'support_tickets',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('ticket_number', sa.String(20), unique=True, nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(50), server_default='open'),
        sa.Column('priority', sa.String(50), server_default='medium'),
        sa.Column('category', sa.String(50), server_default='general'),
        sa.Column('customer_id', sa.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('assignee_id', sa.String(100)),
        sa.Column('reporter_id', sa.String(100)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('closed_at', sa.DateTime),
    )
    op.create_index('ix_tickets_status', 'support_tickets', ['status'])
    op.create_index('ix_tickets_priority', 'support_tickets', ['priority'])
    op.create_index('ix_tickets_assignee_id', 'support_tickets', ['assignee_id'])
    op.create_index('ix_tickets_customer_id', 'support_tickets', ['customer_id'])
    op.create_index('ix_tickets_number', 'support_tickets', ['ticket_number'])

    op.create_table(
        'support_ticket_comments',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('ticket_id', sa.UUID(as_uuid=True), sa.ForeignKey('support_tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', sa.String(100)),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('is_internal', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_ticket_comments_ticket_id', 'support_ticket_comments', ['ticket_id'])


def downgrade() -> None:
    op.drop_index('ix_ticket_comments_ticket_id', 'support_ticket_comments')
    op.drop_table('support_ticket_comments')
    op.drop_index('ix_tickets_number', 'support_tickets')
    op.drop_index('ix_tickets_customer_id', 'support_tickets')
    op.drop_index('ix_tickets_assignee_id', 'support_tickets')
    op.drop_index('ix_tickets_priority', 'support_tickets')
    op.drop_index('ix_tickets_status', 'support_tickets')
    op.drop_table('support_tickets')
