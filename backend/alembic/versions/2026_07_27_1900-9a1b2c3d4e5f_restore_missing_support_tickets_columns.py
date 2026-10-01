"""restore missing support_tickets columns (schema drift fix)

Die Spalten type/channel/sla_deadline/sla_breached/deleted_at wurden von
Migration f1a2b3c4d5e6 (ticketing_foundation) erzeugt, fehlten aber
tatsaechlich in der DB (Schema-Drift). Diese Migration holt exakt das
nach, was f1a2b3c4d5e6 urspruenglich vorsah - keine weiteren Aenderungen.

Revision ID: 9a1b2c3d4e5f
Revises: d7f3a1b8e2c4
Create Date: 2026-07-27 19:00:00.000000+02:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9a1b2c3d4e5f'
down_revision: Union[str, None] = 'd7f3a1b8e2c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS type VARCHAR(50) NOT NULL DEFAULT 'support'"))
    conn.execute(sa.text("ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS channel VARCHAR(50) NOT NULL DEFAULT 'manual'"))
    conn.execute(sa.text("ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP"))
    conn.execute(sa.text("ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS sla_breached BOOLEAN NOT NULL DEFAULT false"))
    conn.execute(sa.text("ALTER TABLE support_tickets ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP"))

    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_tickets_type ON support_tickets (type)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_tickets_deleted_at ON support_tickets (deleted_at)"))


def downgrade() -> None:
    op.drop_index('ix_tickets_deleted_at', table_name='support_tickets')
    op.drop_index('ix_tickets_type', table_name='support_tickets')
    op.drop_column('support_tickets', 'deleted_at')
    op.drop_column('support_tickets', 'sla_breached')
    op.drop_column('support_tickets', 'sla_deadline')
    op.drop_column('support_tickets', 'channel')
    op.drop_column('support_tickets', 'type')
