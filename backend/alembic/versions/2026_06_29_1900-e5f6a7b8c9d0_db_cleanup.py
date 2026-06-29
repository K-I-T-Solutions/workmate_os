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
    conn = op.get_bind()

    # chat_messages droppen (nur wenn noch vorhanden)
    conn.execute(sa.text("DROP TABLE IF EXISTS chat_messages CASCADE"))

    # products erstellen (idempotent)
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS products (
            id UUID PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            short_description VARCHAR(500),
            sku VARCHAR(100) UNIQUE,
            category VARCHAR(50) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_service BOOLEAN NOT NULL DEFAULT TRUE,
            price_type VARCHAR(50) NOT NULL DEFAULT 'fixed',
            unit_price NUMERIC(10,2) NOT NULL DEFAULT 0.00,
            unit VARCHAR(50) NOT NULL DEFAULT 'Stk.',
            default_tax_rate NUMERIC(5,2) NOT NULL DEFAULT 19.00,
            min_quantity NUMERIC(10,2),
            max_quantity NUMERIC(10,2),
            internal_notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))

    # ticket_events erstellen (idempotent)
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS ticket_events (
            id UUID PRIMARY KEY,
            ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            actor_id VARCHAR(100),
            old_value JSONB,
            new_value JSONB,
            comment TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_ticket_events_ticket_id ON ticket_events(ticket_id)
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_ticket_events_created_at ON ticket_events(created_at)
    """))


def downgrade() -> None:
    op.drop_table('ticket_events')
    op.drop_table('products')
