# app/modules/backoffice/products/routes.py
"""
Products & Services API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.settings.database import get_db
from app.modules.backoffice.products import crud, schemas


router = APIRouter(prefix="/backoffice/products", tags=["Backoffice Products"])


# ============================================================================
# LIST & FILTERS
# ============================================================================

@router.get("", response_model=schemas.ProductListResponse)
def list_products(
    skip: int = Query(0, ge=0, description="Offset für Pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max Anzahl Ergebnisse"),
    category: Optional[str] = Query(None, description="Filter nach Kategorie"),
    is_active: Optional[bool] = Query(None, description="Filter nach Aktiv/Inaktiv"),
    is_service: Optional[bool] = Query(None, description="Filter nach Dienstleistung/Produkt"),
    search: Optional[str] = Query(None, description="Suche in Name, Beschreibung, SKU"),
    db: Session = Depends(get_db)
):
    """
    Liste aller Products mit Pagination und Filtern.

    **Filter-Optionen:**
    - `category`: private_customer, small_business, etc.
    - `is_active`: true/false
    - `is_service`: true/false
    - `search`: Volltextsuche

    **Pagination:**
    - `skip`: Offset (Standard: 0)
    - `limit`: Max Anzahl (Standard: 100, Max: 500)
    """
    products = crud.get_products(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        is_active=is_active,
        is_service=is_service,
        search=search,
    )

    total = crud.count_products(
        db=db,
        category=category,
        is_active=is_active,
        is_service=is_service,
        search=search,
    )

    return schemas.ProductListResponse(
        items=products,
        total=total,
        skip=skip,
        limit=limit
    )


# ============================================================================
# SINGLE PRODUCT
# ============================================================================

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Einzelnes Product abrufen."""
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    return product


@router.get("/by-sku/{sku}", response_model=schemas.ProductResponse)
def get_product_by_sku(
    sku: str,
    db: Session = Depends(get_db)
):
    """Product nach SKU abrufen."""
    product = crud.get_product_by_sku(db, sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    return product


# ============================================================================
# CREATE
# ============================================================================

@router.post(
    "",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    data: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Neues Product erstellen.

    **Validierung:**
    - Name ist erforderlich
    - SKU muss eindeutig sein (falls angegeben)
    - unit_price muss >= 0 sein
    """
    return crud.create_product(db=db, data=data)


# ============================================================================
# UPDATE
# ============================================================================

@router.patch("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: uuid.UUID,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Product aktualisieren (Partial Update).

    **Erlaubte Felder:**
    - Alle Product-Felder können geändert werden
    - SKU muss eindeutig bleiben
    """
    product = crud.update_product(db, product_id, data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    return product


# ============================================================================
# DELETE
# ============================================================================

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Product löschen.

    **Hinweis:** Products können gelöscht werden, auch wenn sie in Invoices verwendet wurden.
    Die Rechnungen behalten ihre Line Item-Daten.
    """
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    return None
