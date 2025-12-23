"""add customer_number field to customers table

Revision ID: t4rkt11jnja2
Revises: 8521f00b62ae
Create Date: 2025-12-23 18:55:00.000000+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 't4rkt11jnja2'
down_revision: Union[str, None] = '8521f00b62ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Fügt customer_number Feld zur customers Tabelle hinzu.
    Format: KIT-CUS-000001 (mit 6-stelliger führender Null)
    """
    # Füge customer_number Spalte hinzu (nullable=True erstmal)
    op.add_column('customers', sa.Column(
        'customer_number',
        sa.String(length=50),
        nullable=True,
        comment='Eindeutige Kundennummer (KIT-CUS-000001)'
    ))

    # Generiere Kundennummern für existierende Kunden
    # Das passiert in Python/SQL, nicht durch Alembic direkt
    connection = op.get_bind()

    # Hole alle existierenden Kunden
    result = connection.execute(sa.text("SELECT id FROM customers ORDER BY created_at"))
    customer_ids = [row[0] for row in result]

    # Generiere und setze Kundennummern
    for index, customer_id in enumerate(customer_ids, start=1):
        customer_number = f"KIT-CUS-{index:06d}"
        connection.execute(
            sa.text("UPDATE customers SET customer_number = :number WHERE id = :id"),
            {"number": customer_number, "id": customer_id}
        )

    # Jetzt mache customer_number NOT NULL
    op.alter_column('customers', 'customer_number',
                   existing_type=sa.String(length=50),
                   nullable=False)

    # Füge UNIQUE Constraint hinzu
    op.create_unique_constraint('uq_customers_customer_number', 'customers', ['customer_number'])

    # Füge Index hinzu
    op.create_index('ix_customers_customer_number', 'customers', ['customer_number'])


def downgrade() -> None:
    """
    Entfernt customer_number Feld von customers Tabelle.
    """
    op.drop_index('ix_customers_customer_number', table_name='customers')
    op.drop_constraint('uq_customers_customer_number', 'customers', type_='unique')
    op.drop_column('customers', 'customer_number')
