"""
Stripe Payment Router

Endpoints:
- POST /stripe/config - Configure Stripe API keys
- GET /stripe/config - Get Stripe configuration status
- POST /stripe/payment-intent - Create Payment Intent for invoice
- POST /stripe/payment-link - Create Payment Link for invoice
- POST /stripe/webhook - Handle Stripe webhooks
"""
import logging
import uuid as uuid_module
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.errors import ErrorCode, get_error_detail
from .stripe_integration import (
    StripeAPIClient,
    get_stripe_config,
    create_or_update_stripe_config,
    deactivate_stripe_config,
)
from .schemas import (
    StripeConfigRequest,
    StripeConfigResponse,
    StripePaymentIntentRequest,
    StripePaymentIntentResponse,
    StripePaymentLinkRequest,
    StripePaymentLinkResponse,
)
from app.modules.backoffice.invoices.models import Invoice, Payment, InvoiceStatus
from app.modules.backoffice.invoices.crud import get_invoice
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stripe", tags=["Stripe Payment"])


# ============================================================================
# Configuration Endpoints
# ============================================================================


@router.get("/config", response_model=StripeConfigResponse)
async def get_config_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get Stripe configuration status"""
    config = get_stripe_config(db)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.STRIPE_NO_CONFIG),
        )

    return StripeConfigResponse(
        id=str(config.id),
        configured=True,
        test_mode=config.test_mode,
        is_active=config.is_active,
        created_at=str(config.created_at),
        updated_at=str(config.updated_at),
    )


@router.post("/config")
async def create_or_update_config_endpoint(
    config_request: StripeConfigRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create or update Stripe configuration"""

    # Validate keys format
    if not config_request.publishable_key.startswith("pk_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.STRIPE_INVALID_KEY),
        )

    if not config_request.secret_key.startswith("sk_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.STRIPE_INVALID_KEY),
        )

    # Create or update config
    # SECURITY: Consider encrypting secret_key before storing (see sevdesk_encryption.py)
    config = create_or_update_stripe_config(
        db=db,
        publishable_key=config_request.publishable_key,
        secret_key=config_request.secret_key,
        webhook_secret=config_request.webhook_secret,
        test_mode=config_request.test_mode,
    )

    return {
        "success": True,
        "message": "Stripe configuration saved successfully",
        "config_id": str(config.id),
    }


@router.delete("/config")
async def deactivate_config_endpoint(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Deactivate Stripe configuration"""
    success = deactivate_stripe_config(db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.STRIPE_NO_CONFIG),
        )

    return {"success": True, "message": "Stripe configuration deactivated"}


# ============================================================================
# Payment Intent Endpoints
# ============================================================================


@router.post("/payment-intent", response_model=StripePaymentIntentResponse)
async def create_payment_intent_endpoint(
    request: StripePaymentIntentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a Stripe Payment Intent for an invoice

    Returns client_secret for frontend Stripe Elements
    """
    # Get Stripe config
    config = get_stripe_config(db)
    if not config or not config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.STRIPE_NOT_CONFIGURED),
        )

    # Get invoice
    invoice = get_invoice(db, request.invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.INVOICE_NOT_FOUND, invoice_id=str(request.invoice_id)),
        )

    # Check if invoice is already paid
    if invoice.status == InvoiceStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.INVOICE_ALREADY_PAID),
        )

    # Calculate outstanding amount
    outstanding = invoice.outstanding_amount

    # Initialize Stripe client
    client = StripeAPIClient(config.secret_key)

    # Create Payment Intent
    try:
        payment_intent = await client.create_payment_intent(
            amount=outstanding,
            currency="eur",
            metadata={
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "customer_id": str(invoice.customer_id) if invoice.customer_id else None,
            },
        )

        logger.info(
            f"✅ [Stripe] Payment Intent created for Invoice {invoice.invoice_number}"
        )

        return StripePaymentIntentResponse(
            success=True,
            payment_intent_id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            amount=float(payment_intent["amount"]),
            currency=payment_intent["currency"],
            invoice_id=str(invoice.id),
            invoice_number=invoice.invoice_number,
        )

    except Exception as e:
        logger.error(f"❌ [Stripe] Payment Intent creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


@router.post("/payment-link", response_model=StripePaymentLinkResponse)
async def create_payment_link_endpoint(
    request: StripePaymentLinkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a Stripe Payment Link (Hosted Checkout) for an invoice

    Returns shareable payment URL
    """
    # Get Stripe config
    config = get_stripe_config(db)
    if not config or not config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.STRIPE_NOT_CONFIGURED),
        )

    # Get invoice
    invoice = get_invoice(db, request.invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.INVOICE_NOT_FOUND, invoice_id=str(request.invoice_id)),
        )

    # Calculate outstanding amount
    outstanding = invoice.outstanding_amount

    # Initialize Stripe client
    client = StripeAPIClient(config.secret_key)

    # Create Payment Link
    try:
        payment_link = await client.create_payment_link(
            amount=outstanding,
            invoice_number=invoice.invoice_number,
            description=f"Rechnung {invoice.invoice_number}",
            currency="eur",
            metadata={
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
            },
        )

        logger.info(
            f"✅ [Stripe] Payment Link created for Invoice {invoice.invoice_number}"
        )

        return StripePaymentLinkResponse(
            success=True,
            payment_link_id=payment_link["id"],
            payment_url=payment_link["url"],
            amount=float(payment_link["amount"]),
            currency=payment_link["currency"],
            invoice_id=str(invoice.id),
            invoice_number=invoice.invoice_number,
        )

    except Exception as e:
        logger.error(f"❌ [Stripe] Payment Link creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


# ============================================================================
# Webhook Endpoint
# ============================================================================


@router.post("/webhook")
async def webhook_endpoint(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
):
    """
    Handle Stripe webhook events

    Processes:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    """
    # Get Stripe config
    config = get_stripe_config(db)
    if not config or not config.webhook_secret:
        logger.error("❌ [Stripe] Webhook secret not configured")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.STRIPE_WEBHOOK_NOT_CONFIGURED),
        )

    # Read raw body
    payload = await request.body()

    # Verify webhook signature
    try:
        event = StripeAPIClient.construct_webhook_event(
            payload, stripe_signature, config.webhook_secret
        )
    except Exception as e:
        logger.error(f"❌ [Stripe] Webhook verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )

    # Handle event types
    event_type = event["type"]
    logger.info(f"📨 [Stripe] Webhook received: {event_type}")

    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        await handle_payment_success(db, payment_intent)

    elif event_type == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        await handle_payment_failure(db, payment_intent)

    else:
        logger.info(f"ℹ️ [Stripe] Unhandled event type: {event_type}")

    return {"success": True}


# ============================================================================
# Webhook Handlers
# ============================================================================


async def handle_payment_success(db: Session, payment_intent: dict):
    """Handle successful payment"""
    try:
        invoice_id_str = payment_intent["metadata"].get("invoice_id")
        if not invoice_id_str:
            logger.warning("⚠️ [Stripe] Payment without invoice_id in metadata")
            return

        # Convert to UUID
        try:
            invoice_id = uuid_module.UUID(invoice_id_str)
        except ValueError:
            logger.error(f"❌ [Stripe] Invalid invoice_id format: {invoice_id_str}")
            return

        # Get invoice
        invoice = get_invoice(db, invoice_id)
        if not invoice:
            logger.error(f"❌ [Stripe] Invoice {invoice_id} not found")
            return

        # Calculate amount (Stripe returns cents)
        amount = payment_intent["amount"] / 100

        # Create Payment record
        payment = Payment(
            invoice_id=invoice.id,
            amount=amount,
            payment_date=None,  # Set to today
            method="credit_card",  # Stripe payment
            reference=f"Stripe Payment Intent: {payment_intent['id']}",
            stripe_payment_intent_id=payment_intent["id"],
        )

        db.add(payment)

        # Update invoice status (Invoice model auto-calculates paid_amount from payments)
        # After adding payment, refresh to get updated paid_amount
        db.flush()
        db.refresh(invoice)

        # Update status based on outstanding amount
        if invoice.outstanding_amount <= 0:
            invoice.status = InvoiceStatus.PAID.value
        else:
            invoice.status = InvoiceStatus.PARTIAL.value

        db.commit()

        logger.info(
            f"✅ [Stripe] Payment recorded for Invoice {invoice.invoice_number}: €{amount}"
        )

    except Exception as e:
        logger.error(f"❌ [Stripe] Error handling payment success: {e}")
        db.rollback()


async def handle_payment_failure(db: Session, payment_intent: dict):
    """Handle failed payment"""
    invoice_id = payment_intent["metadata"].get("invoice_id")
    logger.warning(
        f"⚠️ [Stripe] Payment failed for Invoice {invoice_id}: {payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')}"
    )
    # Optionally: Send notification to admin/customer
