# app/modules/backoffice/products/crud.py
"""
Products & Services CRUD Operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import uuid

from fastapi import HTTPException

from app.modules.backoffice.products import models, schemas


# ============================================================================
# READ OPERATIONS
# ============================================================================

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_service: Optional[bool] = None,
    search: Optional[str] = None,
) -> List[models.Product]:
    """
    Holt Products mit Pagination und Filtern.
    """
    query = db.query(models.Product)

    # Filter anwenden
    if category:
        query = query.filter(models.Product.category == category)
    if is_active is not None:
        query = query.filter(models.Product.is_active == is_active)
    if is_service is not None:
        query = query.filter(models.Product.is_service == is_service)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Product.name.ilike(search_pattern)) |
            (models.Product.description.ilike(search_pattern)) |
            (models.Product.sku.ilike(search_pattern))
        )

    # Sortierung und Pagination
    query = query.order_by(models.Product.name.asc())
    query = query.offset(skip).limit(limit)

    return query.all()


def count_products(
    db: Session,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_service: Optional[bool] = None,
    search: Optional[str] = None,
) -> int:
    """Zählt Products mit optionalen Filtern."""
    query = db.query(func.count(models.Product.id))

    if category:
        query = query.filter(models.Product.category == category)
    if is_active is not None:
        query = query.filter(models.Product.is_active == is_active)
    if is_service is not None:
        query = query.filter(models.Product.is_service == is_service)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Product.name.ilike(search_pattern)) |
            (models.Product.description.ilike(search_pattern)) |
            (models.Product.sku.ilike(search_pattern))
        )

    return query.scalar()


def get_product(db: Session, product_id: uuid.UUID) -> Optional[models.Product]:
    """Holt ein einzelnes Product."""
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[models.Product]:
    """Holt Product nach SKU."""
    return db.query(models.Product).filter(models.Product.sku == sku).first()


# ============================================================================
# CREATE OPERATIONS
# ============================================================================

def create_product(
    db: Session,
    data: schemas.ProductCreate,
) -> models.Product:
    """Erstellt neues Product."""
    try:
        # SKU eindeutig prüfen (falls angegeben)
        if data.sku:
            existing = get_product_by_sku(db, data.sku)
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail=f"Product with SKU '{data.sku}' already exists"
                )

        # Product erstellen
        product = models.Product(**data.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create product: {str(e)}"
        )


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_product(
    db: Session,
    product_id: uuid.UUID,
    data: schemas.ProductUpdate,
) -> Optional[models.Product]:
    """Aktualisiert Product."""
    product = get_product(db, product_id)
    if not product:
        return None

    try:
        # SKU eindeutig prüfen (falls geändert)
        if data.sku and data.sku != product.sku:
            existing = get_product_by_sku(db, data.sku)
            if existing and existing.id != product_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"Product with SKU '{data.sku}' already exists"
                )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update product: {str(e)}"
        )


# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def delete_product(db: Session, product_id: uuid.UUID) -> bool:
    """Löscht Product."""
    product = get_product(db, product_id)
    if not product:
        return False

    try:
        db.delete(product)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete product: {str(e)}"
        )
