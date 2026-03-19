"""add_email_intake

Revision ID: e9f4a6c7b8d9
Revises: d8e3f5c6b7a8
Create Date: 2026-03-19 12:00:00.000000+01:00

Erstellt Tabellen für das Email-Intake-Modul:
- email_contacts  – Absender-Kontakte (eindeutig per E-Mail)
- email_tickets   – Tickets aus dem E-Mail-Eingang
- api_keys        – Service-API-Keys für externe Integrationen (z. B. n8n)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e9f4a6c7b8d9"
down_revision: Union[str, None] = "d8e3f5c6b7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # email_contacts                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "email_contacts",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_email_contacts_email", "email_contacts", ["email"], unique=True)

    # ------------------------------------------------------------------ #
    # email_tickets                                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        "email_tickets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("from_email", sa.String(255), nullable=False),
        sa.Column("from_name", sa.String(255), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="email"),
        sa.Column("mailbox", sa.String(20), nullable=False),
        sa.Column("ticket_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column(
            "contact_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("email_contacts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("received_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_email_tickets_mailbox", "email_tickets", ["mailbox"])
    op.create_index("ix_email_tickets_status", "email_tickets", ["status"])
    op.create_index("ix_email_tickets_ticket_type", "email_tickets", ["ticket_type"])
    op.create_index("ix_email_tickets_contact_id", "email_tickets", ["contact_id"])
    op.create_index("ix_email_tickets_from_email", "email_tickets", ["from_email"])

    # ------------------------------------------------------------------ #
    # api_keys                                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "api_keys",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("scopes", sa.JSON, nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_api_keys_name", "api_keys", ["name"])


def downgrade() -> None:
    op.drop_index("ix_api_keys_name", "api_keys")
    op.drop_table("api_keys")

    op.drop_index("ix_email_tickets_from_email", "email_tickets")
    op.drop_index("ix_email_tickets_contact_id", "email_tickets")
    op.drop_index("ix_email_tickets_ticket_type", "email_tickets")
    op.drop_index("ix_email_tickets_status", "email_tickets")
    op.drop_index("ix_email_tickets_mailbox", "email_tickets")
    op.drop_table("email_tickets")

    op.drop_index("ix_email_contacts_email", "email_contacts")
    op.drop_table("email_contacts")
