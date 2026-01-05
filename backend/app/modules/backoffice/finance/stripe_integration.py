"""
Stripe Payment Integration

Handles:
- Payment Intent creation for invoices
- Webhook events (payment success/failure)
- Payment Link generation
"""
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
import stripe
from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import StripeConfig
from app.modules.backoffice.invoices.models import Invoice

logger = logging.getLogger(__name__)


class StripeAPIClient:
    """Stripe API Client for payment processing"""

    def __init__(self, api_key: str):
        """Initialize Stripe client with API key"""
        self.api_key = api_key
        stripe.api_key = api_key
        logger.info("✅ [Stripe] API Client initialized")

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str = "eur",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent

        Args:
            amount: Amount in Decimal (e.g., 100.50)
            currency: Currency code (default: EUR)
            metadata: Additional metadata (e.g., invoice_id)

        Returns:
            Payment Intent object with client_secret for frontend
        """
        try:
            # Convert Decimal to cents (Stripe requires integer)
            amount_cents = int(amount * 100)

            logger.info(f"💳 [Stripe] Creating Payment Intent for {amount} {currency.upper()}")

            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )

            logger.info(f"✅ [Stripe] Payment Intent created: {payment_intent.id}")

            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": payment_intent.status,
            }

        except stripe.error.StripeError as e:
            logger.error(f"❌ [Stripe] Payment Intent creation failed: {e}")
            raise Exception(f"Stripe Error: {e.user_message or str(e)}")

    async def create_payment_link(
        self,
        amount: Decimal,
        invoice_number: str,
        description: str,
        currency: str = "eur",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Link (Hosted Checkout)

        Args:
            amount: Amount in Decimal
            invoice_number: Invoice number for reference
            description: Payment description
            currency: Currency code
            metadata: Additional metadata

        Returns:
            Payment Link URL and ID
        """
        try:
            amount_cents = int(amount * 100)

            logger.info(f"🔗 [Stripe] Creating Payment Link for Invoice {invoice_number}")

            # Create a product first (required for payment link)
            product = stripe.Product.create(
                name=f"Rechnung {invoice_number}",
                description=description,
            )

            # Create a price for the product
            price = stripe.Price.create(
                product=product.id,
                unit_amount=amount_cents,
                currency=currency,
            )

            # Create payment link
            payment_link = stripe.PaymentLink.create(
                line_items=[{"price": price.id, "quantity": 1}],
                metadata=metadata or {},
                # IMPORTANT: Transfer metadata to automatically created Payment Intent
                payment_intent_data={
                    "metadata": metadata or {},
                },
            )

            logger.info(f"✅ [Stripe] Payment Link created: {payment_link.url}")

            return {
                "id": payment_link.id,
                "url": payment_link.url,
                "amount": amount,
                "currency": currency,
                "active": payment_link.active,
            }

        except stripe.error.StripeError as e:
            logger.error(f"❌ [Stripe] Payment Link creation failed: {e}")
            raise Exception(f"Stripe Error: {e.user_message or str(e)}")

    async def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Retrieve Payment Intent details"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                "id": payment_intent.id,
                "amount": Decimal(payment_intent.amount) / 100,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
                "metadata": payment_intent.metadata,
            }

        except stripe.error.StripeError as e:
            logger.error(f"❌ [Stripe] Failed to retrieve Payment Intent: {e}")
            raise Exception(f"Stripe Error: {e.user_message or str(e)}")

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str, webhook_secret: str):
        """
        Verify and construct webhook event

        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header
            webhook_secret: Webhook signing secret

        Returns:
            Verified Stripe Event object
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            logger.info(f"✅ [Stripe] Webhook verified: {event.type}")
            return event

        except ValueError as e:
            logger.error(f"❌ [Stripe] Invalid webhook payload: {e}")
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"❌ [Stripe] Invalid webhook signature: {e}")
            raise Exception("Invalid signature")


# ============================================================================
# Config Helper Functions
# ============================================================================


def get_stripe_config(db: Session) -> Optional[StripeConfig]:
    """Get active Stripe configuration"""
    stmt = select(StripeConfig).where(StripeConfig.is_active == True).limit(1)
    return db.scalar(stmt)


def create_or_update_stripe_config(
    db: Session,
    publishable_key: str,
    secret_key: str,
    webhook_secret: Optional[str] = None,
    test_mode: bool = True,
) -> StripeConfig:
    """Create or update Stripe configuration"""

    # Deactivate existing configs
    db.query(StripeConfig).update({"is_active": False})

    # Create new config
    # SECURITY: secret_key is stored in plain text. Consider implementing encryption
    # using the same approach as SevDesk (see app/modules/backoffice/finance/sevdesk_encryption.py)
    config = StripeConfig(
        publishable_key=publishable_key,
        secret_key=secret_key,
        webhook_secret=webhook_secret,
        test_mode=test_mode,
        is_active=True,
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    logger.info(f"✅ [Stripe] Config {'created' if test_mode else 'updated'} (Test Mode: {test_mode})")
    return config


def deactivate_stripe_config(db: Session) -> bool:
    """Deactivate Stripe configuration"""
    result = db.query(StripeConfig).update({"is_active": False})
    db.commit()

    logger.info(f"🔒 [Stripe] Config deactivated")
    return result > 0
