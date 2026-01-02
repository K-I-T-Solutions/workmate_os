"""add audit logs and soft delete for compliance

Revision ID: 8c8325d750e6
Revises: 8e3d5cbbbc47
Create Date: 2026-01-02 15:25:42.207617+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8c8325d750e6'
down_revision: Union[str, None] = '8e3d5cbbbc47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================================================
    # 1. Create audit_logs table for compliance (GoBD, HGB, AO)
    # ========================================================================
    op.create_table('audit_logs',
    sa.Column('entity_type', sa.String(length=50), nullable=False, comment='Typ der Entität (Invoice, Payment, Expense)'),
    sa.Column('entity_id', sa.Uuid(), nullable=False, comment='UUID der geänderten Entität'),
    sa.Column('action', sa.String(length=50), nullable=False, comment='Art der Änderung (create, update, delete, status_change)'),
    sa.Column('old_values', sa.JSON(), nullable=True, comment='Alte Werte als JSON (bei update/delete)'),
    sa.Column('new_values', sa.JSON(), nullable=True, comment='Neue Werte als JSON (bei create/update)'),
    sa.Column('user_id', sa.String(length=100), nullable=True, comment='User-ID des Benutzers (für zukünftige Integration)'),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Zeitstempel der Änderung'),
    sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP-Adresse (IPv4/IPv6) für zusätzliche Sicherheit'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.CheckConstraint("action IN ('create', 'update', 'delete', 'status_change')", name='check_audit_action_valid'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'], unique=False)
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)

    # ========================================================================
    # 2. Add deleted_at columns for soft-delete (GoBD compliance)
    # ========================================================================
    # Invoices
    op.add_column('invoices',
        sa.Column('deleted_at', sa.DateTime(), nullable=True,
                  comment='Zeitpunkt der Soft-Deletion (NULL = nicht gelöscht)'))
    op.create_index('ix_invoices_deleted_at', 'invoices', ['deleted_at'], unique=False)

    # Invoice Line Items
    op.add_column('invoice_line_items',
        sa.Column('deleted_at', sa.DateTime(), nullable=True,
                  comment='Zeitpunkt der Soft-Deletion (NULL = nicht gelöscht)'))
    op.create_index('ix_invoice_line_items_deleted_at', 'invoice_line_items', ['deleted_at'], unique=False)

    # Payments
    op.add_column('payments',
        sa.Column('deleted_at', sa.DateTime(), nullable=True,
                  comment='Zeitpunkt der Soft-Deletion (NULL = nicht gelöscht)'))
    op.create_index('ix_payments_deleted_at', 'payments', ['deleted_at'], unique=False)


def downgrade() -> None:
    # ========================================================================
    # 1. Remove deleted_at columns
    # ========================================================================
    op.drop_index('ix_payments_deleted_at', table_name='payments')
    op.drop_column('payments', 'deleted_at')

    op.drop_index('ix_invoice_line_items_deleted_at', table_name='invoice_line_items')
    op.drop_column('invoice_line_items', 'deleted_at')

    op.drop_index('ix_invoices_deleted_at', table_name='invoices')
    op.drop_column('invoices', 'deleted_at')

    # ========================================================================
    # 2. Remove audit_logs table
    # ========================================================================
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_table('audit_logs')