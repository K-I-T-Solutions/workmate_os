"""
SevDesk CRUD Operations

CRUD-Funktionen für SevDesk Config, Mappings und Sync History.
"""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from .models import (
    SevDeskConfig,
    SevDeskInvoiceMapping,
    SevDeskBankAccountMapping,
    SevDeskSyncHistory,
    SevDeskSyncStatus,
)
from .sevdesk_encryption import encrypt_sevdesk_token, decrypt_sevdesk_token

logger = logging.getLogger(__name__)


# ============================================================================
# SEVDESK CONFIG
# ============================================================================

def get_sevdesk_config(db: Session) -> Optional[SevDeskConfig]:
    """
    Get active SevDesk configuration.

    Returns:
        Active SevDesk config or None
    """
    stmt = select(SevDeskConfig).where(SevDeskConfig.is_active == True).limit(1)
    return db.scalars(stmt).first()


def create_or_update_sevdesk_config(
    db: Session,
    api_token: str,
    auto_sync_enabled: bool = False,
    sync_invoices: bool = True,
    sync_bank_accounts: bool = True,
    sync_transactions: bool = True,
) -> SevDeskConfig:
    """
    Create or update SevDesk configuration.

    Deactivates old configs and creates new one or updates existing.

    Args:
        db: Database session
        api_token: Plain text API token (will be encrypted)
        auto_sync_enabled: Enable automatic sync
        sync_invoices: Sync invoices
        sync_bank_accounts: Sync bank accounts
        sync_transactions: Sync transactions

    Returns:
        Created/updated SevDeskConfig
    """
    # Encrypt token
    encrypted_token = encrypt_sevdesk_token(api_token)

    # Get existing active config
    existing = get_sevdesk_config(db)

    if existing:
        # Update existing config
        existing.api_token = encrypted_token
        existing.auto_sync_enabled = auto_sync_enabled
        existing.sync_invoices = sync_invoices
        existing.sync_bank_accounts = sync_bank_accounts
        existing.sync_transactions = sync_transactions
        db.commit()
        db.refresh(existing)
        logger.info("✅ [SevDesk Config] Updated existing configuration")
        return existing
    else:
        # Create new config
        config = SevDeskConfig(
            api_token=encrypted_token,
            auto_sync_enabled=auto_sync_enabled,
            sync_invoices=sync_invoices,
            sync_bank_accounts=sync_bank_accounts,
            sync_transactions=sync_transactions,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        logger.info("✅ [SevDesk Config] Created new configuration")
        return config


def get_decrypted_api_token(db: Session) -> Optional[str]:
    """
    Get decrypted SevDesk API token from active config.

    Returns:
        Plain text API token or None if not configured
    """
    config = get_sevdesk_config(db)
    if not config:
        return None

    try:
        return decrypt_sevdesk_token(config.api_token)
    except Exception as e:
        logger.error(f"❌ [SevDesk] Failed to decrypt API token: {e}")
        return None


def update_last_sync_timestamp(db: Session) -> None:
    """
    Update last_sync_at timestamp of active config.
    """
    config = get_sevdesk_config(db)
    if config:
        config.last_sync_at = datetime.now()
        db.commit()


def deactivate_sevdesk_config(db: Session) -> bool:
    """
    Deactivate SevDesk configuration.

    Returns:
        True if config was deactivated, False if not found
    """
    config = get_sevdesk_config(db)
    if config:
        config.is_active = False
        db.commit()
        logger.info("✅ [SevDesk Config] Configuration deactivated")
        return True
    return False


# ============================================================================
# INVOICE MAPPINGS
# ============================================================================

def get_invoice_mapping(
    db: Session,
    invoice_id: str,
) -> Optional[SevDeskInvoiceMapping]:
    """
    Get invoice mapping by WorkmateOS invoice ID.
    """
    stmt = select(SevDeskInvoiceMapping).where(
        SevDeskInvoiceMapping.invoice_id == invoice_id
    )
    return db.scalars(stmt).first()


def get_invoice_mapping_by_sevdesk_id(
    db: Session,
    sevdesk_invoice_id: str,
) -> Optional[SevDeskInvoiceMapping]:
    """
    Get invoice mapping by SevDesk invoice ID.
    """
    stmt = select(SevDeskInvoiceMapping).where(
        SevDeskInvoiceMapping.sevdesk_invoice_id == sevdesk_invoice_id
    )
    return db.scalars(stmt).first()


def create_invoice_mapping(
    db: Session,
    invoice_id: str,
    sevdesk_invoice_id: str,
    sync_status: str = SevDeskSyncStatus.SUCCESS.value,
) -> SevDeskInvoiceMapping:
    """
    Create new invoice mapping.
    """
    mapping = SevDeskInvoiceMapping(
        invoice_id=invoice_id,
        sevdesk_invoice_id=sevdesk_invoice_id,
        last_synced_at=datetime.now(),
        sync_status=sync_status,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    logger.info(f"✅ [SevDesk] Created invoice mapping: {invoice_id} ↔ {sevdesk_invoice_id}")
    return mapping


def update_invoice_mapping_status(
    db: Session,
    invoice_id: str,
    sync_status: str,
    sync_error: Optional[str] = None,
) -> Optional[SevDeskInvoiceMapping]:
    """
    Update invoice mapping sync status.
    """
    mapping = get_invoice_mapping(db, invoice_id)
    if mapping:
        mapping.sync_status = sync_status
        mapping.sync_error = sync_error
        mapping.last_synced_at = datetime.now()
        db.commit()
        db.refresh(mapping)
    return mapping


# ============================================================================
# BANK ACCOUNT MAPPINGS
# ============================================================================

def get_bank_account_mapping(
    db: Session,
    bank_account_id: str,
) -> Optional[SevDeskBankAccountMapping]:
    """
    Get bank account mapping by WorkmateOS bank account ID.
    """
    stmt = select(SevDeskBankAccountMapping).where(
        SevDeskBankAccountMapping.bank_account_id == bank_account_id
    )
    return db.scalars(stmt).first()


def get_bank_account_mapping_by_sevdesk_id(
    db: Session,
    sevdesk_check_account_id: str,
) -> Optional[SevDeskBankAccountMapping]:
    """
    Get bank account mapping by SevDesk CheckAccount ID.
    """
    stmt = select(SevDeskBankAccountMapping).where(
        SevDeskBankAccountMapping.sevdesk_check_account_id == sevdesk_check_account_id
    )
    return db.scalars(stmt).first()


def create_bank_account_mapping(
    db: Session,
    bank_account_id: str,
    sevdesk_check_account_id: str,
    sync_status: str = SevDeskSyncStatus.SUCCESS.value,
) -> SevDeskBankAccountMapping:
    """
    Create new bank account mapping.
    """
    mapping = SevDeskBankAccountMapping(
        bank_account_id=bank_account_id,
        sevdesk_check_account_id=sevdesk_check_account_id,
        last_synced_at=datetime.now(),
        sync_status=sync_status,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    logger.info(f"✅ [SevDesk] Created bank account mapping: {bank_account_id} ↔ {sevdesk_check_account_id}")
    return mapping


def update_bank_account_mapping_status(
    db: Session,
    bank_account_id: str,
    sync_status: str,
    sync_error: Optional[str] = None,
) -> Optional[SevDeskBankAccountMapping]:
    """
    Update bank account mapping sync status.
    """
    mapping = get_bank_account_mapping(db, bank_account_id)
    if mapping:
        mapping.sync_status = sync_status
        mapping.sync_error = sync_error
        mapping.last_synced_at = datetime.now()
        db.commit()
        db.refresh(mapping)
    return mapping


# ============================================================================
# SYNC HISTORY
# ============================================================================

def create_sync_history(
    db: Session,
    sync_type: str,
    direction: str,
    status: str,
    records_processed: int = 0,
    records_success: int = 0,
    records_failed: int = 0,
    error_message: Optional[str] = None,
) -> SevDeskSyncHistory:
    """
    Create sync history entry.

    Args:
        sync_type: invoice, bank_account, transaction, payment
        direction: push_to_sevdesk, pull_from_sevdesk
        status: success, failed, partial
        records_processed: Total records processed
        records_success: Successfully synced records
        records_failed: Failed records
        error_message: Error message if failed
    """
    history = SevDeskSyncHistory(
        sync_type=sync_type,
        direction=direction,
        status=status,
        records_processed=records_processed,
        records_success=records_success,
        records_failed=records_failed,
        error_message=error_message,
        started_at=datetime.now(),
        completed_at=datetime.now(),
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    logger.info(
        f"📊 [SevDesk Sync] {sync_type} {direction}: "
        f"{records_success}/{records_processed} success, {records_failed} failed"
    )
    return history


def get_sync_history(
    db: Session,
    sync_type: Optional[str] = None,
    limit: int = 50,
) -> list[SevDeskSyncHistory]:
    """
    Get sync history with optional filtering.

    Args:
        sync_type: Filter by sync type (optional)
        limit: Max records to return

    Returns:
        List of sync history entries
    """
    stmt = select(SevDeskSyncHistory)

    if sync_type:
        stmt = stmt.where(SevDeskSyncHistory.sync_type == sync_type)

    stmt = stmt.order_by(desc(SevDeskSyncHistory.started_at)).limit(limit)

    return list(db.scalars(stmt).all())
