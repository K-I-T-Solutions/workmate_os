"""add_invoice_number_unique_constraint

Revision ID: 3831958a8e57
Revises: a1b2c3d4e5f6
Create Date: 2026-01-04 16:38:53.073505+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3831958a8e57'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ersetzt den UNIQUE Index durch eine explizite UNIQUE Constraint.

    Dies verhindert Race Conditions und Duplikate auf DB-Ebene.
    Eine Constraint ist expliziter als ein Index und dokumentiert die Business-Regel besser.

    Der alte Index wird entfernt, die Constraint erstellt automatisch einen neuen Index.
    """
    # Entferne den alten UNIQUE Index (falls vorhanden)
    # Der wird durch SQLAlchemy unique=True automatisch erstellt
    op.execute("""
        DROP INDEX IF EXISTS ix_invoices_invoice_number;
    """)

    # Füge explizite UNIQUE Constraint hinzu (erstellt automatisch einen Index)
    op.create_unique_constraint(
        'uq_invoices_invoice_number',
        'invoices',
        ['invoice_number']
    )


def downgrade() -> None:
    """
    Entfernt die UNIQUE Constraint und stellt den alten Index wieder her.
    """
    # Entferne die UNIQUE Constraint
    op.drop_constraint('uq_invoices_invoice_number', 'invoices', type_='unique')

    # Stelle den alten UNIQUE Index wieder her
    op.create_index(
        'ix_invoices_invoice_number',
        'invoices',
        ['invoice_number'],
        unique=True
    )