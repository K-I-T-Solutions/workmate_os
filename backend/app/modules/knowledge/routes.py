"""Knowledge Base API Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.settings.database import get_db
from app.core.auth.roles import require_permissions, get_current_user
from . import crud, schemas

router = APIRouter(prefix="/api/kb", tags=["Knowledge Base"])


# ── Categories ──

@router.get("/categories", response_model=list[schemas.KBCategoryResponse])
@require_permissions(["kb.view", "kb.*", "*"])
def list_categories(db: Session = Depends(get_db), user=Depends(get_current_user)):
    cats = crud.get_categories(db)
    result = []
    for c in cats:
        data = schemas.KBCategoryResponse.model_validate(c)
        data.article_count = crud.get_article_count(db, c.id)
        result.append(data)
    return result


@router.post("/categories", response_model=schemas.KBCategoryResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["kb.write", "kb.*", "*"])
def create_category(data: schemas.KBCategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_category(db, data)


@router.put("/categories/{cat_id}", response_model=schemas.KBCategoryResponse)
@require_permissions(["kb.write", "kb.*", "*"])
def update_category(cat_id: UUID, data: schemas.KBCategoryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.update_category(db, cat_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")
    return obj


@router.delete("/categories/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["kb.write", "kb.*", "*"])
def delete_category(cat_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.delete_category(db, cat_id):
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")


# ── Articles ──

@router.get("/articles", response_model=schemas.KBArticleListResponse)
@require_permissions(["kb.view", "kb.*", "*"])
def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items, total = crud.get_articles(db, skip=skip, limit=limit, category_id=category_id, status=status, search=search)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/articles/{article_id}", response_model=schemas.KBArticleDetailResponse)
@require_permissions(["kb.view", "kb.*", "*"])
def get_article(article_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get_article(db, article_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    crud.increment_views(db, article_id)
    return obj


@router.post("/articles", response_model=schemas.KBArticleDetailResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["kb.write", "kb.*", "*"])
def create_article(data: schemas.KBArticleCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_article(db, data, author_id=user.get("id"))


@router.put("/articles/{article_id}", response_model=schemas.KBArticleDetailResponse)
@require_permissions(["kb.write", "kb.*", "*"])
def update_article(article_id: UUID, data: schemas.KBArticleUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.update_article(db, article_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    return obj


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["kb.write", "kb.*", "*"])
def delete_article(article_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.delete_article(db, article_id):
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")


@router.post("/articles/{article_id}/vote")
@require_permissions(["kb.view", "kb.*", "*"])
def vote_article(
    article_id: UUID,
    helpful: bool = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not crud.get_article(db, article_id):
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    crud.vote_helpful(db, article_id, helpful)
    return {"ok": True}
