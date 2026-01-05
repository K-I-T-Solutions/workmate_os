"""
SevDesk Sync Router

API Endpoints für bidirektionale Synchronisation mit SevDesk.

Features:
- Token-Management mit Verschlüsselung
- Invoice ↔ SevDesk Invoice Sync
- BankAccount ↔ SevDesk CheckAccount Sync
- Transaction Pull von SevDesk
- Payment Pull von SevDesk
- Sync History & Mappings
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.settings.database import get_db
from app.core.auth.auth import get_current_user
from app.core.errors import ErrorCode, get_error_detail
from .sevdesk_integration import (
    SevDeskAPIClient,
    map_workmate_invoice_to_sevdesk,
    map_sevdesk_transaction_to_workmate,
)
from .models import (
    BankAccount,
    BankTransaction,
    SevDeskSyncStatus,
)
from app.modules.backoffice.invoices.models import Invoice
from app.modules.backoffice.crm.models import Customer
from .schemas import (
    SevDeskConfigRequest,
    SevDeskConfigResponse,
    SevDeskSyncInvoiceRequest,
    SevDeskSyncInvoiceResponse,
    SevDeskSyncBankAccountRequest,
    SevDeskSyncBankAccountResponse,
    SevDeskSyncTransactionsRequest,
    SevDeskSyncTransactionsResponse,
    SevDeskSyncHistoryListResponse,
    SevDeskSyncHistoryRead,
    SevDeskSyncPaymentsRequest,
    SevDeskSyncPaymentsResponse,
    SevDeskPaymentDetail,
)
from .sevdesk_crud import (
    get_sevdesk_config,
    create_or_update_sevdesk_config,
    get_decrypted_api_token,
    deactivate_sevdesk_config,
    update_last_sync_timestamp,
    get_invoice_mapping,
    create_invoice_mapping,
    update_invoice_mapping_status,
    get_bank_account_mapping,
    create_bank_account_mapping,
    update_bank_account_mapping_status,
    create_sync_history,
    get_sync_history,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sevdesk", tags=["SevDesk"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sevdesk_client(db: Session) -> SevDeskAPIClient:
    """
    Get SevDesk API Client with decrypted token from database.

    Raises:
        HTTPException: If no config found or token cannot be decrypted
    """
    api_token = get_decrypted_api_token(db)

    if not api_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.SEVDESK_NOT_CONFIGURED),
        )

    return SevDeskAPIClient(api_token)


# ============================================================================
# CONFIG ENDPOINTS
# ============================================================================

@router.get("/config", response_model=SevDeskConfigResponse)
async def get_config_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get SevDesk configuration status.

    Returns:
        Current configuration or 404 if not configured
    """
    config = get_sevdesk_config(db)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.SEVDESK_NOT_CONFIGURED),
        )

    return SevDeskConfigResponse(
        id=config.id,
        configured=True,
        auto_sync_enabled=config.auto_sync_enabled,
        sync_invoices=config.sync_invoices,
        sync_bank_accounts=config.sync_bank_accounts,
        sync_transactions=config.sync_transactions,
        last_sync_at=config.last_sync_at,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.post("/config")
async def create_or_update_config_endpoint(
    config_request: SevDeskConfigRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Create or update SevDesk configuration.

    Validates API token by making test API call.
    Stores encrypted token in database.
    """
    # Validate token by testing API connection
    try:
        client = SevDeskAPIClient(config_request.api_token)
        await client.get_check_accounts()  # Test API call
        logger.info("✅ [SevDesk] API token validated successfully")
    except Exception as e:
        logger.error(f"❌ [SevDesk] API token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCode.SEVDESK_INVALID_TOKEN),
        )

    # Create or update config with encrypted token
    config = create_or_update_sevdesk_config(
        db=db,
        api_token=config_request.api_token,
        auto_sync_enabled=config_request.auto_sync_enabled,
        sync_invoices=config_request.sync_invoices,
        sync_bank_accounts=config_request.sync_bank_accounts,
        sync_transactions=config_request.sync_transactions,
    )

    return {
        "success": True,
        "message": "SevDesk configuration saved successfully",
        "config_id": str(config.id),
    }


@router.delete("/config")
async def deactivate_config_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Deactivate SevDesk configuration."""
    success = deactivate_sevdesk_config(db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCode.SEVDESK_NOT_CONFIGURED),
        )

    return {"success": True, "message": "SevDesk configuration deactivated"}


@router.get("/test")
async def test_connection_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Test SevDesk API connection.

    Returns:
        API statistics and connection status
    """
    try:
        client = get_sevdesk_client(db)

        # Test multiple API calls
        check_accounts = await client.get_check_accounts()
        invoices = await client.get_invoices(limit=5)
        contacts = await client.get_contacts(limit=5)
        transactions = await client.get_transactions(limit=5)

        return {
            "success": True,
            "check_accounts": len(check_accounts),
            "invoices": len(invoices),
            "contacts": len(contacts),
            "transactions": len(transactions),
            "message": "SevDesk API connection successful",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SevDesk] Connection test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.SEVDESK_API_ERROR, error=str(e)),
        )


# ============================================================================
# INVOICE SYNC ENDPOINTS
# ============================================================================

@router.post("/sync/invoice", response_model=SevDeskSyncInvoiceResponse)
async def sync_invoice_endpoint(
    request: SevDeskSyncInvoiceRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Push single invoice from WorkmateOS to SevDesk.

    Creates or updates invoice in SevDesk and stores mapping.

    Process:
    1. Get invoice from database
    2. Find or create contact in SevDesk
    3. Get SevUser (contactPerson required for invoice)
    4. Map invoice to SevDesk format
    5. Create invoice in SevDesk (status 100 = draft)
    6. Store mapping in database
    """
    logger.info(f"📤 [SevDesk] Pushing invoice {request.invoice_id} to SevDesk")

    try:
        # Get invoice from database
        invoice = db.query(Invoice).filter(Invoice.id == request.invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_error_detail(ErrorCode.INVOICE_NOT_FOUND, invoice_id=str(request.invoice_id)),
            )

        # Check if already synced
        existing_mapping = get_invoice_mapping(db, str(invoice.id))
        if existing_mapping:
            logger.warning(f"⚠️  Invoice {invoice.invoice_number} already synced to SevDesk (ID: {existing_mapping.sevdesk_invoice_id})")
            return SevDeskSyncInvoiceResponse(
                success=True,
                invoice_id=invoice.id,
                sevdesk_invoice_id=existing_mapping.sevdesk_invoice_id,
                message=f"Invoice {invoice.invoice_number} already synced to SevDesk",
                synced_at=existing_mapping.last_synced_at,
            )

        # Get customer
        customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_error_detail(ErrorCode.CUSTOMER_NOT_FOUND),
            )

        # Initialize SevDesk client
        client = get_sevdesk_client(db)

        # Find or create contact in SevDesk
        sevdesk_contact = None
        if customer.email:
            logger.info(f"🔍 Searching contact by email: {customer.email}")
            sevdesk_contact = await client.search_contact_by_email(customer.email)

        if not sevdesk_contact:
            # Try first available contact as fallback
            logger.info("📋 Using first available contact from SevDesk")
            contacts = await client.get_contacts(limit=1)
            if contacts:
                sevdesk_contact = contacts[0]
            else:
                # Create new contact in SevDesk
                logger.info(f"➕ Creating new contact in SevDesk")
                contact_data = {
                    "name": customer.company or customer.name,
                    "email": customer.email,
                    "customerNumber": customer.customer_number,
                    "category": {"id": "3", "objectName": "Category"},
                }
                sevdesk_contact = await client.create_contact(contact_data)
                logger.info(f"✅ Created contact: {sevdesk_contact['id']}")

        contact_id = str(sevdesk_contact.get("id"))
        contact_name = sevdesk_contact.get("name", "Unknown")
        logger.info(f"✅ Using contact: {contact_name} (ID: {contact_id})")

        # Get SevUser for contactPerson (required field)
        logger.info("👤 Getting current SevUser for contactPerson...")
        sev_user = await client.get_current_sev_user()
        if not sev_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_detail(ErrorCode.SEVDESK_NO_USER),
            )

        contact_person_id = str(sev_user.get("id"))
        sev_user_name = sev_user.get("fullname", sev_user.get("username", "Unknown"))
        logger.info(f"✅ SevUser: {sev_user_name} (ID: {contact_person_id})")

        # Map invoice to SevDesk format
        invoice_dict = {
            "invoice_number": invoice.invoice_number,
            "invoice_date": str(invoice.issued_date) if invoice.issued_date else None,
            "title": f"Rechnung {invoice.invoice_number}",
            "notes": invoice.notes or "",
            "items": [
                {
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "tax_rate": float(item.tax_rate),
                }
                for item in invoice.line_items
            ],
        }

        invoice_data, positions = map_workmate_invoice_to_sevdesk(
            invoice_dict,
            contact_id,
            contact_person_id,
        )

        # Create invoice in SevDesk
        logger.info(f"🚀 Creating invoice in SevDesk...")
        sevdesk_invoice = await client.create_invoice(invoice_data, positions)
        sevdesk_invoice_id = str(sevdesk_invoice.get("id"))

        logger.info(f"✅ [SevDesk] Created invoice: {sevdesk_invoice_id} (Status: {sevdesk_invoice.get('status')})")

        # Store mapping
        create_invoice_mapping(
            db,
            str(invoice.id),
            sevdesk_invoice_id,
            SevDeskSyncStatus.SUCCESS.value,
        )

        # Create sync history
        create_sync_history(
            db,
            sync_type="invoice",
            direction="push_to_sevdesk",
            status=SevDeskSyncStatus.SUCCESS.value,
            records_processed=1,
            records_success=1,
            records_failed=0,
        )

        return SevDeskSyncInvoiceResponse(
            success=True,
            invoice_id=invoice.id,
            sevdesk_invoice_id=sevdesk_invoice_id,
            message=f"Invoice {invoice.invoice_number} synced to SevDesk successfully",
            synced_at=datetime.now(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SevDesk] Invoice sync failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

        # Update mapping status (if exists)
        try:
            update_invoice_mapping_status(
                db,
                str(request.invoice_id),
                SevDeskSyncStatus.FAILED.value,
                str(e)[:500],  # Truncate error message
            )
        except:
            pass  # Mapping might not exist yet

        # Create sync history
        create_sync_history(
            db,
            sync_type="invoice",
            direction="push_to_sevdesk",
            status=SevDeskSyncStatus.FAILED.value,
            records_processed=1,
            records_success=0,
            records_failed=1,
            error_message=str(e)[:500],
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


# ============================================================================
# BANK ACCOUNT SYNC ENDPOINTS
# ============================================================================

@router.post("/sync/bank-account", response_model=SevDeskSyncBankAccountResponse)
async def sync_bank_account_endpoint(
    request: SevDeskSyncBankAccountRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Sync BankAccount to SevDesk CheckAccount.

    Creates mapping between WorkmateOS BankAccount and SevDesk CheckAccount.
    """
    logger.info(f"📤 [SevDesk] Syncing bank account {request.bank_account_id}")

    try:
        # Get bank account from database
        bank_account = db.query(BankAccount).filter(
            BankAccount.id == request.bank_account_id
        ).first()

        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
            )

        # Get all CheckAccounts from SevDesk
        client = get_sevdesk_client(db)
        check_accounts = await client.get_check_accounts()

        # Find matching CheckAccount by IBAN
        sevdesk_check_account = None
        for check_account in check_accounts:
            if check_account.get("iban") == bank_account.iban:
                sevdesk_check_account = check_account
                break

        if not sevdesk_check_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_error_detail(ErrorCode.SEVDESK_API_ERROR, error=f"Kein passendes CheckAccount für IBAN {bank_account.iban}"),
            )

        sevdesk_check_account_id = sevdesk_check_account.get("id")

        # Store mapping
        mapping = get_bank_account_mapping(db, str(bank_account.id))
        if mapping:
            update_bank_account_mapping_status(
                db,
                str(bank_account.id),
                SevDeskSyncStatus.SUCCESS.value,
            )
        else:
            create_bank_account_mapping(
                db,
                str(bank_account.id),
                sevdesk_check_account_id,
                SevDeskSyncStatus.SUCCESS.value,
            )

        logger.info(
            f"✅ [SevDesk] Mapped bank account {bank_account.id} ↔ {sevdesk_check_account_id}"
        )

        # Create sync history
        create_sync_history(
            db,
            sync_type="bank_account",
            direction="push_to_sevdesk",
            status=SevDeskSyncStatus.SUCCESS.value,
            records_processed=1,
            records_success=1,
            records_failed=0,
        )

        return SevDeskSyncBankAccountResponse(
            success=True,
            bank_account_id=bank_account.id,
            sevdesk_check_account_id=sevdesk_check_account_id,
            message=f"Bank account {bank_account.account_name} mapped to SevDesk",
            synced_at=datetime.now(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SevDesk] Bank account sync failed: {e}")

        # Update mapping status
        update_bank_account_mapping_status(
            db,
            str(request.bank_account_id),
            SevDeskSyncStatus.FAILED.value,
            str(e),
        )

        # Create sync history
        create_sync_history(
            db,
            sync_type="bank_account",
            direction="push_to_sevdesk",
            status=SevDeskSyncStatus.FAILED.value,
            records_processed=1,
            records_success=0,
            records_failed=1,
            error_message=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


# ============================================================================
# TRANSACTION SYNC ENDPOINTS
# ============================================================================

@router.post("/sync/transactions", response_model=SevDeskSyncTransactionsResponse)
async def sync_transactions_endpoint(
    request: SevDeskSyncTransactionsRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Pull transactions from SevDesk to WorkmateOS.

    Syncs bank transactions that SevDesk already fetched via PSD2.
    """
    logger.info("📥 [SevDesk] Pulling transactions from SevDesk")

    try:
        client = get_sevdesk_client(db)

        # Get transactions from SevDesk
        sevdesk_transactions = await client.get_transactions(
            check_account_id=request.check_account_id,
            limit=request.limit,
        )

        logger.info(f"📊 Found {len(sevdesk_transactions)} transactions in SevDesk")

        # Get default bank account (TODO: Map CheckAccount to BankAccount)
        bank_account = db.query(BankAccount).first()
        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_error_detail(ErrorCode.BANK_ACCOUNT_NOT_FOUND),
            )

        imported = 0
        skipped = 0
        errors = []

        for sevdesk_tx in sevdesk_transactions:
            # Map to WorkmateOS format
            tx_data = map_sevdesk_transaction_to_workmate(sevdesk_tx)

            # Check for duplicates
            existing = db.query(BankTransaction).filter(
                BankTransaction.account_id == bank_account.id,
                BankTransaction.transaction_date == tx_data["transaction_date"],
                BankTransaction.amount == tx_data["amount"],
            ).first()

            if existing:
                skipped += 1
                continue

            # Create transaction
            transaction = BankTransaction(
                account_id=bank_account.id,
                **tx_data,
            )
            db.add(transaction)
            imported += 1

        db.commit()

        logger.info(f"✅ Imported {imported} transactions, skipped {skipped} duplicates")

        # Create sync history
        create_sync_history(
            db,
            sync_type="transaction",
            direction="pull_from_sevdesk",
            status=SevDeskSyncStatus.SUCCESS.value,
            records_processed=len(sevdesk_transactions),
            records_success=imported,
            records_failed=len(errors),
        )

        # Update last sync timestamp
        update_last_sync_timestamp(db)

        return SevDeskSyncTransactionsResponse(
            success=True,
            total=len(sevdesk_transactions),
            imported=imported,
            skipped=skipped,
            errors=errors,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SevDesk] Transaction sync failed: {e}")
        db.rollback()

        # Create sync history
        create_sync_history(
            db,
            sync_type="transaction",
            direction="pull_from_sevdesk",
            status=SevDeskSyncStatus.FAILED.value,
            records_processed=0,
            records_success=0,
            records_failed=0,
            error_message=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


# ============================================================================
# PAYMENT SYNC ENDPOINTS
# ============================================================================

@router.post("/sync/payments", response_model=SevDeskSyncPaymentsResponse)
async def sync_payments_endpoint(
    request: SevDeskSyncPaymentsRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Pull payment status from SevDesk and sync to WorkmateOS.

    Process:
    1. Get all invoice mappings (or specific invoice)
    2. For each invoice: Fetch SevDesk invoice with paidAmount
    3. Compare with WorkmateOS payments
    4. Create missing payments in WorkmateOS
    5. Update invoice status (paid, partial, sent)

    Args:
        request: Contains optional invoice_id or sync_all flag

    Returns:
        Detailed sync results with payment creation info
    """
    logger.info("📥 [SevDesk] Syncing payments from SevDesk to WorkmateOS")

    try:
        client = get_sevdesk_client(db)

        # Get invoice mappings to sync
        from .sevdesk_crud import get_invoice_mapping
        from sqlalchemy import select
        from .models import SevDeskInvoiceMapping
        from app.modules.backoffice.invoices.models import Payment, InvoiceStatus
        from decimal import Decimal

        if request.invoice_id:
            # Sync specific invoice
            mapping = get_invoice_mapping(db, str(request.invoice_id))
            if not mapping:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_error_detail(ErrorCode.SEVDESK_NO_MAPPING, invoice_id=str(request.invoice_id)),
                )
            mappings = [mapping]
        else:
            # Sync all mapped invoices
            stmt = select(SevDeskInvoiceMapping).where(
                SevDeskInvoiceMapping.sync_status == SevDeskSyncStatus.SUCCESS.value
            )
            mappings = list(db.scalars(stmt).all())

        logger.info(f"📊 Found {len(mappings)} invoice mappings to sync")

        details = []
        payments_created = 0
        payments_updated = 0
        invoices_status_updated = 0
        errors = []

        for mapping in mappings:
            try:
                # Get WorkmateOS invoice
                invoice = db.query(Invoice).filter(Invoice.id == mapping.invoice_id).first()
                if not invoice:
                    logger.warning(f"⚠️  Invoice {mapping.invoice_id} not found in database")
                    errors.append(f"Invoice {mapping.invoice_id} not found")
                    continue

                # Get SevDesk invoice details
                sevdesk_invoices = await client.get_invoices()
                sevdesk_invoice = None
                for inv in sevdesk_invoices:
                    if str(inv.get("id")) == mapping.sevdesk_invoice_id:
                        sevdesk_invoice = inv
                        break

                if not sevdesk_invoice:
                    logger.warning(f"⚠️  SevDesk invoice {mapping.sevdesk_invoice_id} not found")
                    errors.append(f"SevDesk invoice {mapping.sevdesk_invoice_id} not found")
                    continue

                # Get payment amounts
                sevdesk_paid_amount = float(sevdesk_invoice.get("paidAmount", 0))
                workmate_paid_amount = float(invoice.paid_amount)

                logger.info(f"   Invoice {invoice.invoice_number}:")
                logger.info(f"      SevDesk paid: €{sevdesk_paid_amount}")
                logger.info(f"      WorkmateOS paid: €{workmate_paid_amount}")

                # Calculate difference
                diff = sevdesk_paid_amount - workmate_paid_amount

                payment_created = False
                payment_id = None
                payment_amount = None
                new_status = None

                # Create payment if there's a difference
                if diff > 0.01:  # Tolerance for floating point
                    # Create payment in WorkmateOS
                    from datetime import date

                    payment = Payment(
                        invoice_id=invoice.id,
                        amount=Decimal(str(diff)),
                        payment_date=date.today(),
                        method="bank_transfer",  # Default
                        reference=f"SevDesk Sync - Invoice {invoice.invoice_number}",
                        note=f"Imported from SevDesk (paid amount: €{sevdesk_paid_amount})",
                    )
                    db.add(payment)
                    db.flush()

                    payment_created = True
                    payment_id = payment.id
                    payment_amount = float(diff)
                    payments_created += 1

                    logger.info(f"      ✅ Created payment: €{diff}")

                # Update invoice status based on payments
                old_status = invoice.status
                invoice.recalculate_totals()

                # Determine new status
                if invoice.is_paid:
                    invoice.status = InvoiceStatus.PAID.value
                elif invoice.paid_amount > Decimal("0.00"):
                    invoice.status = InvoiceStatus.PARTIAL.value
                elif invoice.is_overdue:
                    invoice.status = InvoiceStatus.OVERDUE.value

                if invoice.status != old_status:
                    new_status = invoice.status
                    invoices_status_updated += 1
                    logger.info(f"      📝 Status updated: {old_status} → {new_status}")

                db.commit()

                # Add detail
                details.append(SevDeskPaymentDetail(
                    invoice_id=invoice.id,
                    invoice_number=invoice.invoice_number,
                    sevdesk_invoice_id=mapping.sevdesk_invoice_id,
                    sevdesk_paid_amount=sevdesk_paid_amount,
                    workmate_paid_amount=workmate_paid_amount + (payment_amount or 0),
                    payment_created=payment_created,
                    payment_id=payment_id,
                    payment_amount=payment_amount,
                    new_invoice_status=new_status,
                ))

            except Exception as e:
                logger.error(f"❌ Error syncing invoice {mapping.invoice_id}: {e}")
                errors.append(f"Invoice {mapping.invoice_id}: {str(e)}")
                db.rollback()
                continue

        # Create sync history
        create_sync_history(
            db,
            sync_type="payment",
            direction="pull_from_sevdesk",
            status=SevDeskSyncStatus.SUCCESS.value if len(errors) == 0 else SevDeskSyncStatus.PARTIAL.value,
            records_processed=len(mappings),
            records_success=payments_created,
            records_failed=len(errors),
        )

        # Update last sync timestamp
        update_last_sync_timestamp(db)

        logger.info(f"✅ Payment sync complete: {payments_created} payments created, {invoices_status_updated} invoices updated")

        return SevDeskSyncPaymentsResponse(
            success=len(errors) == 0,
            total_invoices_checked=len(mappings),
            payments_created=payments_created,
            payments_updated=payments_updated,
            invoices_status_updated=invoices_status_updated,
            details=details,
            errors=errors,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SevDesk] Payment sync failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

        # Create sync history
        create_sync_history(
            db,
            sync_type="payment",
            direction="pull_from_sevdesk",
            status=SevDeskSyncStatus.FAILED.value,
            records_processed=0,
            records_success=0,
            records_failed=0,
            error_message=str(e)[:500],
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCode.SYSTEM_ERROR),
        )


# ============================================================================
# SYNC HISTORY ENDPOINTS
# ============================================================================

@router.get("/sync/history", response_model=SevDeskSyncHistoryListResponse)
async def get_sync_history_endpoint(
    sync_type: Optional[str] = Query(None, description="Filter by sync type"),
    limit: int = Query(50, ge=1, le=200, description="Max records"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get sync history with optional filtering.

    Returns:
        List of sync history entries
    """
    history = get_sync_history(db, sync_type=sync_type, limit=limit)

    return SevDeskSyncHistoryListResponse(
        items=[SevDeskSyncHistoryRead.from_orm(h) for h in history],
        total=len(history),
    )
