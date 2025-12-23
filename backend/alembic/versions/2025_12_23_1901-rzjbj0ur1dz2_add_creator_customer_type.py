"""add creator customer type

Revision ID: rzjbj0ur1dz2
Revises: t4rkt11jnja2
Create Date: 2025-12-23 19:01:00.000000+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'rzjbj0ur1dz2'
down_revision: Union[str, None] = 't4rkt11jnja2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Erstellt den CustomerType Check Constraint mit 'creator'.
    Erlaubte Werte: creator, individual, business, government
    """
    # Normalisiere existierende Werte
    connection = op.get_bind()

    # Konvertiere ungültige/alte Werte zu gültigen
    connection.execute(sa.text("UPDATE customers SET type = 'business' WHERE type NOT IN ('creator', 'individual', 'business', 'government') OR type IS NULL"))

    # Create check constraint
    op.create_check_constraint(
        'check_customer_type_valid',
        'customers',
        "type IN ('creator', 'individual', 'business', 'government')"
    )


def downgrade() -> None:
    """
    Entfernt den CustomerType Check Constraint.
    """
    # Drop constraint
    op.drop_constraint('check_customer_type_valid', 'customers', type_='check')
