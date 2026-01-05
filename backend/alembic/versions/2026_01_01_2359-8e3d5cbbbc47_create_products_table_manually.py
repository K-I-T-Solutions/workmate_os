"""create products table manually

Revision ID: 8e3d5cbbbc47
Revises: d13ce3a3941e
Create Date: 2026-01-01 23:59:26.239405+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e3d5cbbbc47'
down_revision: Union[str, None] = 'd13ce3a3941e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create products table"""
    op.create_table(
        'products',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, comment='Produktname/Dienstleistung'),
        sa.Column('description', sa.Text(), nullable=True, comment='Ausführliche Beschreibung'),
        sa.Column('short_description', sa.String(length=500), nullable=True, comment='Kurzbeschreibung für Rechnungen'),
        sa.Column('sku', sa.String(length=50), nullable=True, comment='SKU / Artikelnummer'),
        sa.Column('category', sa.Enum('private_customer', 'small_business', 'enterprise', 'hardware', 'software', 'consulting', 'support', 'development', 'other', name='productcategory'), nullable=False, comment='Produktkategorie'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Aktiv/Inaktiv'),
        sa.Column('is_service', sa.Boolean(), nullable=False, server_default='true', comment='Ist eine Dienstleistung (vs. Produkt)'),
        sa.Column('price_type', sa.Enum('hourly', 'fixed', 'monthly', 'project', 'per_unit', name='pricetype'), nullable=False, comment='Preistyp (Stundensatz, Pauschal, etc.)'),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00', comment='Preis pro Einheit (€)'),
        sa.Column('unit', sa.String(length=50), nullable=False, server_default='Stück', comment='Einheit (Stunde, Stück, Projekt, Monat, etc.)'),
        sa.Column('default_tax_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='19.00', comment='Standard-Steuersatz (%)'),
        sa.Column('min_quantity', sa.Numeric(precision=10, scale=2), nullable=True, comment='Mindestmenge'),
        sa.Column('max_quantity', sa.Numeric(precision=10, scale=2), nullable=True, comment='Maximalmenge'),
        sa.Column('internal_notes', sa.Text(), nullable=True, comment='Interne Notizen (nicht auf Rechnung)'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku')
    )

    # Create indexes
    op.create_index(op.f('ix_products_name'), 'products', ['name'])
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'])
    op.create_index(op.f('ix_products_category'), 'products', ['category'])
    op.create_index(op.f('ix_products_is_active'), 'products', ['is_active'])


def downgrade() -> None:
    """Drop products table"""
    op.drop_index(op.f('ix_products_is_active'), table_name='products')
    op.drop_index(op.f('ix_products_category'), table_name='products')
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_table('products')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS pricetype')
    op.execute('DROP TYPE IF EXISTS productcategory')