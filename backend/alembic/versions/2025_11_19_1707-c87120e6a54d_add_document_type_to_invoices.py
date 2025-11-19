"""add document_type to invoices

Revision ID: c87120e6a54d
Revises: c26af9b1ddbc
Create Date: 2025-11-19 17:07:21.139258+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c87120e6a54d'
down_revision: Union[str, None] = 'c26af9b1ddbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column(
            "document_type",
            sa.String(length=50),
            nullable=False,
            server_default="invoice",
        ),
    )


def downgrade() -> None:
    op.drop_column("invoices", "document_type")
