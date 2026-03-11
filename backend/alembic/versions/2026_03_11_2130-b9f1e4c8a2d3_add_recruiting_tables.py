"""add_recruiting_tables

Revision ID: b9f1e4c8a2d3
Revises: a3f8c12d9e01
Create Date: 2026-03-11 21:30:00.000000+01:00

Erstellt hr_job_postings und hr_applications Tabellen.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b9f1e4c8a2d3'
down_revision: Union[str, None] = 'a3f8c12d9e01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'hr_job_postings',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('requirements', sa.Text),
        sa.Column('location', sa.String(200)),
        sa.Column('remote', sa.Boolean, default=False),
        sa.Column('employment_type', sa.String(50)),
        sa.Column('salary_min', sa.Numeric(10, 2)),
        sa.Column('salary_max', sa.Numeric(10, 2)),
        sa.Column('department_id', sa.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('published_at', sa.DateTime),
        sa.Column('deadline', sa.Date),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_job_postings_status', 'hr_job_postings', ['status'])
    op.create_index('ix_job_postings_department_id', 'hr_job_postings', ['department_id'])

    op.create_table(
        'hr_applications',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_posting_id', sa.UUID(as_uuid=True), sa.ForeignKey('hr_job_postings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(200), nullable=False),
        sa.Column('phone', sa.String(50)),
        sa.Column('cover_letter', sa.Text),
        sa.Column('cv_url', sa.String(500)),
        sa.Column('linkedin_url', sa.String(500)),
        sa.Column('status', sa.String(50), server_default='received'),
        sa.Column('notes', sa.Text),
        sa.Column('interview_date', sa.DateTime),
        sa.Column('rating', sa.Integer),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_applications_job_posting_id', 'hr_applications', ['job_posting_id'])
    op.create_index('ix_applications_status', 'hr_applications', ['status'])
    op.create_index('ix_applications_email', 'hr_applications', ['email'])


def downgrade() -> None:
    op.drop_index('ix_applications_email', 'hr_applications')
    op.drop_index('ix_applications_status', 'hr_applications')
    op.drop_index('ix_applications_job_posting_id', 'hr_applications')
    op.drop_table('hr_applications')
    op.drop_index('ix_job_postings_department_id', 'hr_job_postings')
    op.drop_index('ix_job_postings_status', 'hr_job_postings')
    op.drop_table('hr_job_postings')
