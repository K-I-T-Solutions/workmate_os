"""add_xml_paths_to_invoices

Revision ID: a8b3f3dda2c6
Revises: 8c8325d750e6
Create Date: 2026-01-02 17:03:29.456873+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8b3f3dda2c6'
down_revision: Union[str, None] = '8c8325d750e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add XML paths for E-Rechnung (XRechnung/ZUGFeRD)
    op.add_column('invoices', sa.Column('xml_path', sa.Text(), nullable=True, comment='Pfad zur XRechnung-XML-Datei'))
    op.add_column('invoices', sa.Column('zugferd_path', sa.Text(), nullable=True, comment='Pfad zum ZUGFeRD-PDF (Hybrid mit eingebetteter XML)'))


def downgrade() -> None:
    # Remove XML paths
    op.drop_column('invoices', 'zugferd_path')
    op.drop_column('invoices', 'xml_path')