"""add_banking_tables

Revision ID: c2b2fce85638
Revises: a8b3f3dda2c6
Create Date: 2026-01-02 17:17:42.165833+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2b2fce85638'
down_revision: Union[str, None] = 'a8b3f3dda2c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create bank_accounts table
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('account_name', sa.String(length=100), nullable=False, comment='Bezeichnung des Kontos (z.B. \'Geschäftskonto\')'),
        sa.Column('account_type', sa.String(length=50), server_default='checking', nullable=False, comment='Kontotyp: checking, savings, credit, cash'),
        sa.Column('iban', sa.String(length=34), nullable=True, comment='Internationale Bankkontonummer'),
        sa.Column('bic', sa.String(length=11), nullable=True, comment='Bank Identifier Code (SWIFT)'),
        sa.Column('bank_name', sa.String(length=100), nullable=True, comment='Name der Bank'),
        sa.Column('account_holder', sa.String(length=100), nullable=True, comment='Kontoinhaber'),
        sa.Column('balance', sa.Numeric(precision=12, scale=2), server_default='0.00', nullable=False, comment='Aktueller Kontostand'),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False, comment='Konto ist aktiv?'),
        sa.Column('note', sa.Text(), nullable=True, comment='Notizen zum Konto'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_bank_accounts')),
        sa.UniqueConstraint('iban', name=op.f('uq_bank_accounts_iban')),
        sa.CheckConstraint("account_type IN ('checking', 'savings', 'credit', 'cash')", name='check_account_type_valid')
    )
    op.create_index(op.f('ix_bank_accounts_iban'), 'bank_accounts', ['iban'], unique=False)
    op.create_index(op.f('ix_bank_accounts_is_active'), 'bank_accounts', ['is_active'], unique=False)

    # Create bank_transactions table
    op.create_table(
        'bank_transactions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False, comment='Zugehöriges Bankkonto'),
        sa.Column('matched_payment_id', sa.UUID(), nullable=True, comment='Zugeordnete Zahlung (Payment aus Invoices)'),
        sa.Column('matched_expense_id', sa.UUID(), nullable=True, comment='Zugeordnete Ausgabe'),
        sa.Column('transaction_date', sa.Date(), nullable=False, comment='Buchungsdatum'),
        sa.Column('value_date', sa.Date(), nullable=True, comment='Wertstellungsdatum'),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False, comment='Betrag (positiv=Eingang, negativ=Ausgang)'),
        sa.Column('transaction_type', sa.String(length=50), nullable=False, comment='Typ: income, expense, transfer, fee, interest'),
        sa.Column('counterparty_name', sa.String(length=255), nullable=True, comment='Name des Zahlungspartners'),
        sa.Column('counterparty_iban', sa.String(length=34), nullable=True, comment='IBAN des Zahlungspartners'),
        sa.Column('purpose', sa.Text(), nullable=True, comment='Verwendungszweck'),
        sa.Column('reference', sa.String(length=255), nullable=True, comment='Eindeutige Transaktions-ID der Bank'),
        sa.Column('reconciliation_status', sa.String(length=50), server_default='unmatched', nullable=False, comment='Status des Zahlungsabgleichs'),
        sa.Column('reconciliation_note', sa.Text(), nullable=True, comment='Notizen zum Abgleich'),
        sa.Column('reconciled_at', sa.DateTime(), nullable=True, comment='Zeitpunkt des Abgleichs'),
        sa.Column('reconciled_by', sa.String(length=100), nullable=True, comment='Benutzer der den Abgleich durchgeführt hat'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['bank_accounts.id'], name=op.f('fk_bank_transactions_account_id_bank_accounts'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['matched_payment_id'], ['payments.id'], name=op.f('fk_bank_transactions_matched_payment_id_payments'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['matched_expense_id'], ['expenses.id'], name=op.f('fk_bank_transactions_matched_expense_id_expenses'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_bank_transactions')),
        sa.UniqueConstraint('reference', name=op.f('uq_bank_transactions_reference')),
        sa.CheckConstraint("transaction_type IN ('income', 'expense', 'transfer', 'fee', 'interest')", name='check_transaction_type_valid'),
        sa.CheckConstraint("reconciliation_status IN ('unmatched', 'matched', 'confirmed', 'ignored')", name='check_reconciliation_status_valid')
    )
    op.create_index(op.f('ix_bank_transactions_account_id'), 'bank_transactions', ['account_id'], unique=False)
    op.create_index(op.f('ix_bank_transactions_transaction_date'), 'bank_transactions', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_bank_transactions_reconciliation_status'), 'bank_transactions', ['reconciliation_status'], unique=False)
    op.create_index(op.f('ix_bank_transactions_reference'), 'bank_transactions', ['reference'], unique=False)


def downgrade() -> None:
    # Drop bank_transactions table
    op.drop_index(op.f('ix_bank_transactions_reference'), table_name='bank_transactions')
    op.drop_index(op.f('ix_bank_transactions_reconciliation_status'), table_name='bank_transactions')
    op.drop_index(op.f('ix_bank_transactions_transaction_date'), table_name='bank_transactions')
    op.drop_index(op.f('ix_bank_transactions_account_id'), table_name='bank_transactions')
    op.drop_table('bank_transactions')

    # Drop bank_accounts table
    op.drop_index(op.f('ix_bank_accounts_is_active'), table_name='bank_accounts')
    op.drop_index(op.f('ix_bank_accounts_iban'), table_name='bank_accounts')
    op.drop_table('bank_accounts')