"""Knowledge Base CRUD"""
import re
from datetime import datetime
from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from .models import KBCategory, KBArticle
from .schemas import KBCategoryCreate, KBCategoryUpdate, KBArticleCreate, KBArticleUpdate


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[äöüß]', lambda m: {'ä':'ae','ö':'oe','ü':'ue','ß':'ss'}[m.group()], text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def _unique_article_slug(db: Session, base: str) -> str:
    slug = _slugify(base)
    existing = db.query(KBArticle).filter(KBArticle.slug.like(f"{slug}%")).count()
    return slug if existing == 0 else f"{slug}-{existing + 1}"


# ── Categories ──

def get_categories(db: Session) -> List[KBCategory]:
    return db.query(KBCategory).order_by(KBCategory.order, KBCategory.name).all()


def get_category(db: Session, cat_id: UUID) -> Optional[KBCategory]:
    return db.query(KBCategory).filter(KBCategory.id == cat_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[KBCategory]:
    return db.query(KBCategory).filter(KBCategory.slug == slug).first()


def create_category(db: Session, data: KBCategoryCreate) -> KBCategory:
    obj = KBCategory(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_category(db: Session, cat_id: UUID, data: KBCategoryUpdate) -> Optional[KBCategory]:
    obj = get_category(db, cat_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_category(db: Session, cat_id: UUID) -> bool:
    obj = get_category(db, cat_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def get_article_count(db: Session, cat_id: UUID) -> int:
    return db.query(func.count(KBArticle.id)).filter(
        KBArticle.category_id == str(cat_id), KBArticle.status == "published"
    ).scalar() or 0


# ── Articles ──

def get_articles(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    category_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    pinned_first: bool = True,
) -> Tuple[List[KBArticle], int]:
    query = db.query(KBArticle)
    if category_id:
        query = query.filter(KBArticle.category_id == category_id)
    if status:
        query = query.filter(KBArticle.status == status)
    if search:
        query = query.filter(
            or_(KBArticle.title.ilike(f"%{search}%"), KBArticle.content.ilike(f"%{search}%"))
        )
    total = query.count()
    if pinned_first:
        query = query.order_by(KBArticle.pinned.desc(), KBArticle.updated_at.desc())
    else:
        query = query.order_by(KBArticle.updated_at.desc())
    return query.offset(skip).limit(limit).all(), total


def get_article(db: Session, article_id: UUID) -> Optional[KBArticle]:
    return db.query(KBArticle).filter(KBArticle.id == article_id).first()


def get_article_by_slug(db: Session, slug: str) -> Optional[KBArticle]:
    return db.query(KBArticle).filter(KBArticle.slug == slug).first()


def create_article(db: Session, data: KBArticleCreate, author_id: Optional[str] = None) -> KBArticle:
    payload = data.model_dump()
    payload["slug"] = _unique_article_slug(db, data.title)
    if data.status == "published":
        payload["published_at"] = datetime.utcnow()
    obj = KBArticle(**payload, author_id=author_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_article(db: Session, article_id: UUID, data: KBArticleUpdate) -> Optional[KBArticle]:
    obj = get_article(db, article_id)
    if not obj:
        return None
    changes = data.model_dump(exclude_unset=True)
    if changes.get("status") == "published" and not obj.published_at:
        changes["published_at"] = datetime.utcnow()
    for k, v in changes.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_article(db: Session, article_id: UUID) -> bool:
    obj = get_article(db, article_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def increment_views(db: Session, article_id: UUID) -> None:
    db.query(KBArticle).filter(KBArticle.id == article_id).update(
        {KBArticle.view_count: KBArticle.view_count + 1}
    )
    db.commit()


def vote_helpful(db: Session, article_id: UUID, helpful: bool) -> None:
    if helpful:
        db.query(KBArticle).filter(KBArticle.id == article_id).update(
            {KBArticle.helpful_count: KBArticle.helpful_count + 1}
        )
    else:
        db.query(KBArticle).filter(KBArticle.id == article_id).update(
            {KBArticle.not_helpful_count: KBArticle.not_helpful_count + 1}
        )
    db.commit()
