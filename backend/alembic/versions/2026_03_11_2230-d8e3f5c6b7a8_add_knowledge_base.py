"""add_knowledge_base

Revision ID: d8e3f5c6b7a8
Revises: c7d2f3e4b5a6
Create Date: 2026-03-11 22:30:00.000000+01:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd8e3f5c6b7a8'
down_revision: Union[str, None] = 'c7d2f3e4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'kb_categories',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('icon', sa.String(50)),
        sa.Column('color', sa.String(30)),
        sa.Column('order', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_kb_categories_slug', 'kb_categories', ['slug'], unique=True)

    op.create_table(
        'kb_articles',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', sa.String(36)),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('slug', sa.String(300), nullable=False),
        sa.Column('content', sa.Text, server_default=''),
        sa.Column('excerpt', sa.Text),
        sa.Column('tags', sa.JSON),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('author_id', sa.String(100)),
        sa.Column('view_count', sa.Integer, server_default='0'),
        sa.Column('helpful_count', sa.Integer, server_default='0'),
        sa.Column('not_helpful_count', sa.Integer, server_default='0'),
        sa.Column('pinned', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime),
    )
    op.create_index('ix_kb_articles_category_id', 'kb_articles', ['category_id'])
    op.create_index('ix_kb_articles_status', 'kb_articles', ['status'])
    op.create_index('ix_kb_articles_slug', 'kb_articles', ['slug'])


def downgrade() -> None:
    op.drop_index('ix_kb_articles_slug', 'kb_articles')
    op.drop_index('ix_kb_articles_status', 'kb_articles')
    op.drop_index('ix_kb_articles_category_id', 'kb_articles')
    op.drop_table('kb_articles')
    op.drop_index('ix_kb_categories_slug', 'kb_categories')
    op.drop_table('kb_categories')
