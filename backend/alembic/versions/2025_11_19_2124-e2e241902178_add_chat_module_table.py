"""add chat_module table

Revision ID: e2e241902178
Revises: c87120e6a54d
Create Date: 2025-11-19 21:24:57.407744+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision: str = 'e2e241902178'
down_revision: Union[str, None] = 'c87120e6a54d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),

        sa.Column("message", sa.Text, nullable=False, comment="Nachrichteninhalt"),
        sa.Column("is_system_message", sa.Boolean, nullable=False, server_default="false", comment="System-Nachricht"),
        sa.Column("message_type", sa.String(length=50), nullable=False, server_default="text"),
        sa.Column("attachment_path", sa.Text, nullable=True, comment="Pfad zu Datei-Anhang"),

        sa.Column("project_id", sa.Uuid, sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Uuid, sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reply_to_id", sa.Uuid, sa.ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True),
    )

    # Indexes
    op.create_index("ix_chat_messages_project_id", "chat_messages", ["project_id"])
    op.create_index("ix_chat_messages_author_id", "chat_messages", ["author_id"])
    op.create_index("ix_chat_messages_created_at", "chat_messages", ["created_at"])
    op.create_index("ix_chat_messages_reply_to_id", "chat_messages", ["reply_to_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_messages_reply_to_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_author_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_project_id", table_name="chat_messages")

    op.drop_table("chat_messages")
