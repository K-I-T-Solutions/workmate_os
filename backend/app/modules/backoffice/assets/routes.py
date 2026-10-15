# app/modules/backoffice/assets/routes.py
"""
WorkmateOS - Kunden-Assets (v5.0)

Ablaufüberwachung für n8n:
    GET /api/backoffice/assets/jobs/expiring?within_days=30   (API-Key, Scope assets:read)
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions
from app.core.settings.database import get_db
from app.modules.backoffice.assets import crud, schemas
from app.modules.email_intake.auth import require_api_key_scope

router = APIRouter(prefix="/backoffice/assets", tags=["Backoffice Assets"])


# ─── Ablaufüberwachung (VOR /{asset_id}) ─────────────────────

@router.get("/expiring", response_model=schemas.ExpiringResponse)
@require_permissions(["backoffice.assets.read", "backoffice.*"])
def get_expiring(
    within_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return {"within_days": within_days, "items": crud.get_expiring(db, within_days)}


@router.get("/jobs/expiring", response_model=schemas.ExpiringResponse)
def get_expiring_job(
    within_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    api_key=Depends(require_api_key_scope("assets:read")),
):
    return {"within_days": within_days, "items": crud.get_expiring(db, within_days)}


# ─── Lizenzen (VOR /{asset_id}) ──────────────────────────────

@router.get("/licenses", response_model=schemas.LicenseListResponse)
@require_permissions(["backoffice.assets.read", "backoffice.*"])
def list_licenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[uuid.UUID] = Query(None),
    asset_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    items, total = crud.get_licenses(db, skip=skip, limit=limit, customer_id=customer_id, asset_id=asset_id, search=search)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/licenses", response_model=schemas.LicenseResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["backoffice.assets.write", "backoffice.*"])
def create_license(data: schemas.LicenseCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.create_license(db, data)


@router.get("/licenses/{license_id}", response_model=schemas.LicenseResponse)
@require_permissions(["backoffice.assets.read", "backoffice.*"])
def get_license(license_id: uuid.UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    lic = crud.get_license(db, license_id)
    if not lic:
        raise HTTPException(status_code=404, detail="Lizenz nicht gefunden")
    return lic


@router.put("/licenses/{license_id}", response_model=schemas.LicenseResponse)
@require_permissions(["backoffice.assets.write", "backoffice.*"])
def update_license(
    license_id: uuid.UUID,
    data: schemas.LicenseUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    lic = crud.update_license(db, license_id, data)
    if not lic:
        raise HTTPException(status_code=404, detail="Lizenz nicht gefunden")
    return lic


@router.delete("/licenses/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["backoffice.assets.delete", "backoffice.*"])
def delete_license(license_id: uuid.UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if not crud.delete_license(db, license_id):
        raise HTTPException(status_code=404, detail="Lizenz nicht gefunden")


# ─── Geräte ──────────────────────────────────────────────────

@router.get("/", response_model=schemas.AssetListResponse)
@require_permissions(["backoffice.assets.read", "backoffice.*"])
def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    customer_id: Optional[uuid.UUID] = Query(None),
    asset_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    items, total = crud.get_assets(
        db, skip=skip, limit=limit, customer_id=customer_id,
        asset_type=asset_type, status=status_filter, search=search,
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/", response_model=schemas.AssetResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["backoffice.assets.write", "backoffice.*"])
def create_asset(data: schemas.AssetCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.create_asset(db, data)


@router.get("/{asset_id}", response_model=schemas.AssetResponse)
@require_permissions(["backoffice.assets.read", "backoffice.*"])
def get_asset(asset_id: uuid.UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    return asset


@router.put("/{asset_id}", response_model=schemas.AssetResponse)
@require_permissions(["backoffice.assets.write", "backoffice.*"])
def update_asset(
    asset_id: uuid.UUID,
    data: schemas.AssetUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    asset = crud.update_asset(db, asset_id, data)
    if not asset:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["backoffice.assets.delete", "backoffice.*"])
def delete_asset(asset_id: uuid.UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if not crud.delete_asset(db, asset_id):
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
