"""Knowledge Base Models"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import String, Text, DateTime, Integer, Boolean, Index, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.settings.database import Base, generate_uuid


class KBCategory(Base):
    __tablename__ = "kb_categories"
    __table_args__ = (
        Index("ix_kb_categories_slug", "slug", unique=True),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50))  # lucide icon name
    color: Mapped[Optional[str]] = mapped_column(String(30))  # tailwind color
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    articles: Mapped[List["KBArticle"]] = relationship("KBArticle", back_populates="category", cascade="all, delete-orphan")


class KBArticle(Base):
    __tablename__ = "kb_articles"
    __table_args__ = (
        Index("ix_kb_articles_category_id", "category_id"),
        Index("ix_kb_articles_status", "status"),
        Index("ix_kb_articles_slug", "slug"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid)
    category_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("kb_categories.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    author_id: Mapped[Optional[str]] = mapped_column(String(100))
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    category: Mapped[Optional["KBCategory"]] = relationship("KBCategory", back_populates="articles")
