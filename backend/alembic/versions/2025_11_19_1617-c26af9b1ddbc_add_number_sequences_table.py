"""add number_sequences table

Revision ID: c26af9b1ddbc
Revises: d188e9469e64
Create Date: 2025-11-19 16:17:44.609022+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c26af9b1ddbc'
down_revision: Union[str, None] = 'd188e9469e64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "number_sequences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("current_number", sa.Integer(), nullable=False, server_default="0"),

        sa.UniqueConstraint("doc_type", "year", name="uq_number_sequence_type_year")
    )

    op.create_index(
        "ix_number_sequences_doc_type_year",
        "number_sequences",
        ["doc_type", "year"],
        unique=False
    )

def downgrade() -> None:
    op.drop_index("ix_number_sequences_doc_type_year", table_name="number_sequences")
    op.drop_table("number_sequences")
