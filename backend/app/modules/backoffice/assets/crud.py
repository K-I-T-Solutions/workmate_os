# app/modules/backoffice/assets/crud.py
from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.modules.backoffice.assets import schemas
from app.modules.backoffice.assets.models import AssetStatus, CustomerAsset, SoftwareLicense
from app.modules.backoffice.contracts.models import Contract
from app.modules.backoffice.crm.models import Contact, Customer


def _next_asset_tag(db: Session) -> str:
    # Fortlaufend ohne Jahres-Reset → Jahr 0 im Nummernkreis
    from app.modules.backoffice.invoices.crud import _generate_next_number

    return f"AS-{_generate_next_number(db, doc_type='asset', year=0):05d}"


def _validate_refs(
    db: Session,
    customer_id: uuid.UUID,
    contact_id: Optional[uuid.UUID] = None,
    contract_id: Optional[uuid.UUID] = None,
    asset_id: Optional[uuid.UUID] = None,
) -> None:
    """Referenzen müssen existieren und zum selben Kunden gehören."""
    if not db.get(Customer, customer_id):
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    checks = [
        (contact_id, Contact, "Kontakt"),
        (contract_id, Contract, "Vertrag"),
        (asset_id, CustomerAsset, "Gerät"),
    ]
    for ref_id, model, label in checks:
        if ref_id is None:
            continue
        obj = db.get(model, ref_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{label} nicht gefunden")
        if obj.customer_id != customer_id:
            raise HTTPException(status_code=422, detail=f"{label} gehört zu einem anderen Kunden")


# ─── Geräte ──────────────────────────────────────────────────

def _asset_query(db: Session):
    return db.query(CustomerAsset).options(
        selectinload(CustomerAsset.customer), selectinload(CustomerAsset.contract)
    )


def get_assets(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[uuid.UUID] = None,
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[CustomerAsset], int]:
    query = _asset_query(db)
    if customer_id:
        query = query.filter(CustomerAsset.customer_id == customer_id)
    if asset_type:
        query = query.filter(CustomerAsset.asset_type == asset_type)
    if status:
        query = query.filter(CustomerAsset.status == status)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(
            CustomerAsset.name.ilike(like),
            CustomerAsset.asset_tag.ilike(like),
            CustomerAsset.serial_number.ilike(like),
            CustomerAsset.hostname.ilike(like),
            CustomerAsset.ip_address.ilike(like),
            CustomerAsset.model.ilike(like),
        ))
    total = query.count()
    items = query.order_by(CustomerAsset.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get_asset(db: Session, asset_id: uuid.UUID) -> Optional[CustomerAsset]:
    return _asset_query(db).filter(CustomerAsset.id == asset_id).first()


def create_asset(db: Session, data: schemas.AssetCreate) -> CustomerAsset:
    _validate_refs(db, data.customer_id, data.contact_id, data.contract_id)
    asset = CustomerAsset(**data.model_dump(), asset_tag=_next_asset_tag(db))
    db.add(asset)
    db.commit()
    return get_asset(db, asset.id)


def update_asset(db: Session, asset_id: uuid.UUID, data: schemas.AssetUpdate) -> Optional[CustomerAsset]:
    asset = db.get(CustomerAsset, asset_id)
    if not asset:
        return None
    changes = data.model_dump(exclude_unset=True)
    _validate_refs(
        db, asset.customer_id,
        contact_id=changes.get("contact_id"),
        contract_id=changes.get("contract_id"),
    )
    for k, v in changes.items():
        setattr(asset, k, v)
    db.commit()
    return get_asset(db, asset.id)


def delete_asset(db: Session, asset_id: uuid.UUID) -> bool:
    asset = db.get(CustomerAsset, asset_id)
    if not asset:
        return False
    db.delete(asset)
    db.commit()
    return True


# ─── Lizenzen ────────────────────────────────────────────────

def _license_query(db: Session):
    return db.query(SoftwareLicense).options(
        selectinload(SoftwareLicense.customer), selectinload(SoftwareLicense.asset)
    )


def get_licenses(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[uuid.UUID] = None,
    asset_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
) -> tuple[list[SoftwareLicense], int]:
    query = _license_query(db)
    if customer_id:
        query = query.filter(SoftwareLicense.customer_id == customer_id)
    if asset_id:
        query = query.filter(SoftwareLicense.asset_id == asset_id)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(SoftwareLicense.product_name.ilike(like), SoftwareLicense.vendor.ilike(like)))
    total = query.count()
    items = query.order_by(SoftwareLicense.valid_until.asc().nullslast()).offset(skip).limit(limit).all()
    return items, total


def get_license(db: Session, license_id: uuid.UUID) -> Optional[SoftwareLicense]:
    return _license_query(db).filter(SoftwareLicense.id == license_id).first()


def create_license(db: Session, data: schemas.LicenseCreate) -> SoftwareLicense:
    _validate_refs(db, data.customer_id, contract_id=data.contract_id, asset_id=data.asset_id)
    lic = SoftwareLicense(**data.model_dump())
    db.add(lic)
    db.commit()
    return get_license(db, lic.id)


def update_license(db: Session, license_id: uuid.UUID, data: schemas.LicenseUpdate) -> Optional[SoftwareLicense]:
    lic = db.get(SoftwareLicense, license_id)
    if not lic:
        return None
    changes = data.model_dump(exclude_unset=True)
    _validate_refs(
        db, lic.customer_id,
        contract_id=changes.get("contract_id"),
        asset_id=changes.get("asset_id"),
    )
    for k, v in changes.items():
        setattr(lic, k, v)
    db.commit()
    return get_license(db, lic.id)


def delete_license(db: Session, license_id: uuid.UUID) -> bool:
    lic = db.get(SoftwareLicense, license_id)
    if not lic:
        return False
    db.delete(lic)
    db.commit()
    return True


# ─── Ablaufüberwachung ───────────────────────────────────────

def get_expiring(db: Session, within_days: int = 30, today: Optional[date] = None) -> list[schemas.ExpiringItem]:
    """Garantien und Lizenzen, die in `within_days` Tagen ablaufen (inkl. bereits heute)."""
    today = today or date.today()
    horizon = today + timedelta(days=within_days)
    items: list[schemas.ExpiringItem] = []

    assets = (
        _asset_query(db)
        .filter(
            CustomerAsset.status != AssetStatus.RETIRED.value,
            CustomerAsset.warranty_until.isnot(None),
            CustomerAsset.warranty_until >= today,
            CustomerAsset.warranty_until <= horizon,
        )
        .all()
    )
    for a in assets:
        items.append(schemas.ExpiringItem(
            kind="warranty", id=a.id, name=f"{a.name} ({a.asset_tag})",
            customer_id=a.customer_id, customer_name=a.customer_name,
            expires_on=a.warranty_until, days_left=(a.warranty_until - today).days,
        ))

    licenses = (
        _license_query(db)
        .filter(
            SoftwareLicense.valid_until.isnot(None),
            SoftwareLicense.valid_until >= today,
            SoftwareLicense.valid_until <= horizon,
        )
        .all()
    )
    for lic in licenses:
        items.append(schemas.ExpiringItem(
            kind="license", id=lic.id, name=lic.product_name,
            customer_id=lic.customer_id, customer_name=lic.customer_name,
            expires_on=lic.valid_until, days_left=(lic.valid_until - today).days,
            auto_renew=lic.auto_renew,
        ))

    return sorted(items, key=lambda i: i.expires_on)
