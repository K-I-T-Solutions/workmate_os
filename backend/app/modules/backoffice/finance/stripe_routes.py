"""
Stripe Payment Integration Routes
Konfiguration und Webhook-Handling für Stripe-Zahlungen.
"""
import hashlib
import hmac
import json
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.auth.roles import require_permissions

from .models import StripeConfig
from .schemas import StripeConfigCreate, StripeConfigUpdate, StripeConfigResponse

router = APIRouter(prefix="/backoffice/finance/stripe", tags=["Stripe"])


def _get_active_config(db: Session) -> StripeConfig:
    config = db.query(StripeConfig).filter(StripeConfig.is_active == True).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keine aktive Stripe-Konfiguration gefunden."
        )
    return config


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return key[:7] + "..." + key[-4:]


# ============================================================================
# CONFIG ENDPOINTS
# ============================================================================

@router.get("", response_model=list[StripeConfigResponse])
@require_permissions(["admin.manage"])
async def list_stripe_configs(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Alle Stripe-Konfigurationen (benötigt: admin.manage)"""
    configs = db.query(StripeConfig).order_by(StripeConfig.created_at.desc()).all()
    # Secret Keys maskieren
    for c in configs:
        c.secret_key = _mask_key(c.secret_key)
        if c.webhook_secret:
            c.webhook_secret = _mask_key(c.webhook_secret)
    return configs


@router.post("", response_model=StripeConfigResponse, status_code=status.HTTP_201_CREATED)
@require_permissions(["admin.manage"])
async def create_stripe_config(
    data: StripeConfigCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Stripe-Konfiguration anlegen (benötigt: admin.manage)"""
    if not data.publishable_key.startswith(("pk_test_", "pk_live_")):
        raise HTTPException(status_code=400, detail="Publishable Key muss mit pk_test_ oder pk_live_ beginnen.")
    if not data.secret_key.startswith(("sk_test_", "sk_live_")):
        raise HTTPException(status_code=400, detail="Secret Key muss mit sk_test_ oder sk_live_ beginnen.")

    # Test/Live Modus konsistent halten
    is_test = data.publishable_key.startswith("pk_test_")

    # Wenn neue Config aktiv → alte deaktivieren
    if data.is_active:
        db.query(StripeConfig).update({"is_active": False})

    config = StripeConfig(
        publishable_key=data.publishable_key,
        secret_key=data.secret_key,
        webhook_secret=data.webhook_secret,
        test_mode=is_test,
        is_active=data.is_active,
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    config.secret_key = _mask_key(config.secret_key)
    if config.webhook_secret:
        config.webhook_secret = _mask_key(config.webhook_secret)
    return config


@router.put("/{config_id}", response_model=StripeConfigResponse)
@require_permissions(["admin.manage"])
async def update_stripe_config(
    config_id: str,
    data: StripeConfigUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Stripe-Konfiguration aktualisieren (benötigt: admin.manage)"""
    config = db.query(StripeConfig).filter(StripeConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Konfiguration nicht gefunden.")

    if data.publishable_key is not None:
        if not data.publishable_key.startswith(("pk_test_", "pk_live_")):
            raise HTTPException(status_code=400, detail="Publishable Key muss mit pk_test_ oder pk_live_ beginnen.")
        config.publishable_key = data.publishable_key

    if data.secret_key is not None:
        if not data.secret_key.startswith(("sk_test_", "sk_live_")):
            raise HTTPException(status_code=400, detail="Secret Key muss mit sk_test_ oder sk_live_ beginnen.")
        config.secret_key = data.secret_key

    if data.webhook_secret is not None:
        config.webhook_secret = data.webhook_secret
    if data.test_mode is not None:
        config.test_mode = data.test_mode

    # Wenn auf aktiv gesetzt → andere deaktivieren
    if data.is_active is True:
        db.query(StripeConfig).filter(StripeConfig.id != config_id).update({"is_active": False})
        config.is_active = True
    elif data.is_active is False:
        config.is_active = False

    db.commit()
    db.refresh(config)

    config.secret_key = _mask_key(config.secret_key)
    if config.webhook_secret:
        config.webhook_secret = _mask_key(config.webhook_secret)
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions(["admin.manage"])
async def delete_stripe_config(
    config_id: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Stripe-Konfiguration löschen (benötigt: admin.manage)"""
    config = db.query(StripeConfig).filter(StripeConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Konfiguration nicht gefunden.")
    db.delete(config)
    db.commit()


# ============================================================================
# WEBHOOK ENDPOINT
# ============================================================================

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stripe Webhook Empfänger.
    Signatur wird via HMAC-SHA256 gegen den Webhook-Secret geprüft.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    # Aktive Config laden
    config = db.query(StripeConfig).filter(StripeConfig.is_active == True).first()
    if not config or not config.webhook_secret:
        raise HTTPException(status_code=400, detail="Stripe Webhook nicht konfiguriert.")

    # Signatur prüfen
    if not _verify_stripe_signature(payload, sig_header, config.webhook_secret):
        raise HTTPException(status_code=400, detail="Ungültige Webhook-Signatur.")

    event = json.loads(payload)
    event_type = event.get("type", "")

    # Event-Handler
    if event_type == "payment_intent.succeeded":
        await _handle_payment_succeeded(db, event)
    elif event_type == "payment_intent.payment_failed":
        await _handle_payment_failed(db, event)
    elif event_type == "invoice.payment_succeeded":
        await _handle_invoice_paid(db, event)
    elif event_type == "invoice.payment_failed":
        await _handle_invoice_payment_failed(db, event)
    else:
        # Unbekannte Events still akzeptieren (Stripe erwartet 200)
        pass

    return {"received": True, "type": event_type}


def _verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """HMAC-SHA256 Signaturprüfung nach Stripe-Spec."""
    try:
        parts = {k: v for k, v in (p.split("=", 1) for p in sig_header.split(",") if "=" in p)}
        timestamp = int(parts.get("t", 0))
        signature = parts.get("v1", "")

        # Zeitfenster: max. 5 Minuten
        if abs(time.time() - timestamp) > 300:
            return False

        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected = hmac.new(
            key=secret.encode("utf-8"),
            msg=signed_payload.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


async def _handle_payment_succeeded(db: Session, event: dict) -> None:
    """payment_intent.succeeded — Zahlung erfolgreich."""
    payment_intent = event.get("data", {}).get("object", {})
    pi_id = payment_intent.get("id")
    amount = payment_intent.get("amount", 0) / 100  # Cent → Euro
    metadata = payment_intent.get("metadata", {})
    invoice_id = metadata.get("invoice_id")

    if invoice_id:
        from app.modules.backoffice.invoices.models import Invoice, Payment
        from app.core.settings.database import generate_uuid
        from decimal import Decimal

        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            payment = Payment(
                id=generate_uuid(),
                invoice_id=invoice.id,
                amount=Decimal(str(amount)),
                payment_method="stripe",
                reference=pi_id,
                note=f"Stripe PaymentIntent {pi_id}",
            )
            db.add(payment)
            db.commit()


async def _handle_payment_failed(db: Session, event: dict) -> None:
    """payment_intent.payment_failed — Zahlung fehlgeschlagen."""
    # Logging reicht erstmal — kein weiterer State-Change nötig
    payment_intent = event.get("data", {}).get("object", {})
    print(f"[Stripe] PaymentIntent fehlgeschlagen: {payment_intent.get('id')}")


async def _handle_invoice_paid(db: Session, event: dict) -> None:
    """invoice.payment_succeeded — Stripe-Rechnung bezahlt."""
    stripe_invoice = event.get("data", {}).get("object", {})
    metadata = stripe_invoice.get("metadata", {})
    invoice_id = metadata.get("invoice_id")

    if invoice_id:
        from app.modules.backoffice.invoices.models import Invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice and invoice.status != "paid":
            invoice.status = "paid"
            db.commit()


async def _handle_invoice_payment_failed(db: Session, event: dict) -> None:
    """invoice.payment_failed — Stripe-Rechnung Zahlung fehlgeschlagen."""
    stripe_invoice = event.get("data", {}).get("object", {})
    metadata = stripe_invoice.get("metadata", {})
    invoice_id = metadata.get("invoice_id")

    if invoice_id:
        from app.modules.backoffice.invoices.models import Invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice and invoice.status == "draft":
            invoice.status = "overdue"
            db.commit()
