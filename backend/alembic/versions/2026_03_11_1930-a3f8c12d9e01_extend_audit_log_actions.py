"""extend_audit_log_actions

Revision ID: a3f8c12d9e01
Revises: 1c40c9b9cff5
Create Date: 2026-03-11 19:30:00.000000+01:00

Erweitert den CHECK-Constraint auf audit_logs.action um:
- CRM/Kommunikation: call, email, message, note
- Support (Phase 4): ticket_created, ticket_updated, ticket_closed
- Auth: login, logout
- Dokumente: upload
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f8c12d9e01'
down_revision: Union[str, None] = '1c40c9b9cff5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_CONSTRAINT = (
    "action IN ("
    "'create', 'update', 'delete', 'status_change',"
    "'call', 'email', 'message', 'note',"
    "'ticket_created', 'ticket_updated', 'ticket_closed',"
    "'login', 'logout',"
    "'upload'"
    ")"
)

OLD_CONSTRAINT = (
    "action IN ('create', 'update', 'delete', 'status_change')"
)


def upgrade() -> None:
    op.drop_constraint('check_audit_action_valid', 'audit_logs', type_='check')
    op.create_check_constraint('check_audit_action_valid', 'audit_logs', NEW_CONSTRAINT)


def downgrade() -> None:
    op.drop_constraint('check_audit_action_valid', 'audit_logs', type_='check')
    op.create_check_constraint('check_audit_action_valid', 'audit_logs', OLD_CONSTRAINT)
