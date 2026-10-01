"""cleanup remaining schema drift (dead columns, products enums, ticket_events tz)

Verifiziert vor Anwendung:
- expenses.title, payments.stripe_payment_intent_id, invoice_line_items.deleted_at:
  0 Zeilen mit Daten -> gefahrlos droppbar (Modelle referenzieren sie nicht mehr)
- products: Tabelle ist komplett leer -> Enum-Konvertierung + SKU-Laengenaenderung
  ohne Datenrisiko
- ticket_events: 0 Zeilen -> TIMESTAMPTZ auf TIMESTAMP (Projekt-Konvention: naive
  DateTime ueberall) ohne Datenverlust

Revision ID: b7c8d9e0f1a2
Revises: 9a1b2c3d4e5f
Create Date: 2026-07-27 19:30:00.000000+02:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = '9a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Tote Spalten entfernen (verifiziert: keine Daten vorhanden) ---
    op.drop_column('expenses', 'title')

    op.drop_constraint('uq_payments_stripe_payment_intent_id', 'payments', type_='unique')
    op.drop_column('payments', 'stripe_payment_intent_id')

    op.drop_column('invoice_line_items', 'deleted_at')

    # --- products: DB an Modell angleichen (Tabelle ist leer) ---
    op.drop_constraint('products_sku_key', 'products', type_='unique')
    op.alter_column('products', 'sku', existing_type=sa.VARCHAR(length=100), type_=sa.String(length=50))
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    op.create_index('ix_products_is_active', 'products', ['is_active'], unique=False)

    productcategory = sa.Enum(
        'private_customer', 'small_business', 'enterprise', 'hardware', 'software',
        'consulting', 'support', 'development', 'other',
        name='productcategory',
    )
    productcategory.create(op.get_bind(), checkfirst=True)
    op.execute(
        "ALTER TABLE products ALTER COLUMN category TYPE productcategory "
        "USING category::productcategory"
    )
    op.create_index('ix_products_category', 'products', ['category'], unique=False)

    pricetype = sa.Enum('hourly', 'fixed', 'monthly', 'project', 'per_unit', name='pricetype')
    pricetype.create(op.get_bind(), checkfirst=True)
    op.execute("ALTER TABLE products ALTER COLUMN price_type DROP DEFAULT")
    op.execute(
        "ALTER TABLE products ALTER COLUMN price_type TYPE pricetype "
        "USING price_type::pricetype"
    )

    # --- ticket_events: TIMESTAMPTZ -> TIMESTAMP (Projekt-Konvention: naive DateTime) ---
    op.execute(
        "ALTER TABLE ticket_events ALTER COLUMN created_at TYPE TIMESTAMP "
        "USING created_at AT TIME ZONE 'UTC'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE ticket_events ALTER COLUMN created_at TYPE TIMESTAMPTZ "
        "USING created_at AT TIME ZONE 'UTC'"
    )

    op.execute("ALTER TABLE products ALTER COLUMN price_type TYPE VARCHAR(50) USING price_type::text")
    op.execute("ALTER TABLE products ALTER COLUMN price_type SET DEFAULT 'fixed'")
    sa.Enum(name='pricetype').drop(op.get_bind(), checkfirst=True)

    op.drop_index('ix_products_category', table_name='products')
    op.execute("ALTER TABLE products ALTER COLUMN category TYPE VARCHAR(50) USING category::text")
    sa.Enum(name='productcategory').drop(op.get_bind(), checkfirst=True)

    op.drop_index('ix_products_is_active', table_name='products')
    op.drop_index('ix_products_sku', table_name='products')
    op.alter_column('products', 'sku', existing_type=sa.String(length=50), type_=sa.VARCHAR(length=100))
    op.create_unique_constraint('products_sku_key', 'products', ['sku'])

    op.add_column('invoice_line_items', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))

    op.add_column('payments', sa.Column('stripe_payment_intent_id', sa.VARCHAR(length=100), nullable=True))
    op.create_unique_constraint('uq_payments_stripe_payment_intent_id', 'payments', ['stripe_payment_intent_id'])

    op.add_column('expenses', sa.Column('title', sa.VARCHAR(length=50), nullable=False, server_default=''))
