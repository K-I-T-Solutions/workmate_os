"""add_invoice_reminders

Revision ID: f1a2b3c4d5e6
Revises: e9f4a6c7b8d9
Create Date: 2026-03-20 10:00:00.000000+01:00

Mahnwesen: Tabelle invoice_reminders für Mahnstufen 1-3
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e9f4a6c7b8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invoice_reminders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("invoice_id", sa.UUID(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, comment="1=Erinnerung, 2=1.Mahnung, 3=2.Mahnung"),
        sa.Column("fee", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("pdf_path", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("level IN (1, 2, 3)", name="check_reminder_level_valid"),
        sa.CheckConstraint("fee >= 0", name="check_reminder_fee_positive"),
        sa.UniqueConstraint("invoice_id", "level", name="uq_invoice_reminder_level"),
    )
    op.create_index("ix_invoice_reminders_invoice_id", "invoice_reminders", ["invoice_id"])
    op.create_index("ix_invoice_reminders_level", "invoice_reminders", ["invoice_id", "level"])


def downgrade() -> None:
    op.drop_index("ix_invoice_reminders_level", table_name="invoice_reminders")
    op.drop_index("ix_invoice_reminders_invoice_id", table_name="invoice_reminders")
    op.drop_table("invoice_reminders")
