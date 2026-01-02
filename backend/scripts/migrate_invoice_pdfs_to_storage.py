#!/usr/bin/env python3
"""
Migration Script: Move Invoice PDFs from local filesystem to Nextcloud Storage

This script migrates existing invoice PDFs from the old local storage path
(/root/workmate_os_uploads/invoices/) to the new configurable storage backend
(Nextcloud by default).

Usage:
    python scripts/migrate_invoice_pdfs_to_storage.py [--dry-run]

Options:
    --dry-run    Show what would be done without actually migrating
"""
import sys
import os
import hashlib
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.settings.database import SessionLocal
from app.modules.backoffice.invoices.models import Invoice
from app.modules.documents.models import Document
from app.core.storage.factory import get_storage
from app.core.settings.config import settings


def calculate_checksum(content: bytes) -> str:
    """Calculate SHA256 checksum."""
    return hashlib.sha256(content).hexdigest()


def migrate_pdfs(dry_run: bool = False):
    """
    Migrate all invoice PDFs from local filesystem to storage backend.

    Args:
        dry_run: If True, only show what would be done without actually migrating
    """
    db: Session = SessionLocal()
    storage = get_storage()

    # Old hardcoded path
    old_pdf_dir = "/root/workmate_os_uploads/invoices"

    print("=" * 80)
    print("INVOICE PDF MIGRATION TO STORAGE")
    print("=" * 80)
    print(f"Storage Backend: {settings.STORAGE_BACKEND}")
    print(f"Target Path: {settings.INVOICE_STORAGE_PATH}")
    print(f"Dry Run: {dry_run}")
    print("=" * 80)
    print()

    try:
        # Get all invoices with pdf_path
        invoices = db.query(Invoice).filter(Invoice.pdf_path.isnot(None)).all()

        print(f"Found {len(invoices)} invoices with PDF paths")
        print()

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for invoice in invoices:
            print(f"Processing: {invoice.invoice_number}")
            print(f"  Current path: {invoice.pdf_path}")

            # Check if already migrated (path doesn't start with /)
            if not invoice.pdf_path.startswith("/"):
                print(f"  ✓ Already migrated (remote path detected)")
                skipped_count += 1
                print()
                continue

            # Check if file exists
            if not os.path.exists(invoice.pdf_path):
                print(f"  ⚠️  File not found on disk, skipping")
                skipped_count += 1
                print()
                continue

            try:
                # Read PDF content
                with open(invoice.pdf_path, "rb") as f:
                    pdf_content = f.read()

                # Calculate checksum
                checksum = calculate_checksum(pdf_content)

                # New remote path
                pdf_filename = f"{invoice.invoice_number}.pdf"
                storage_path = settings.INVOICE_STORAGE_PATH.rstrip("/")
                remote_path = f"{storage_path}/{pdf_filename}"

                print(f"  New path: {remote_path}")
                print(f"  Checksum: {checksum}")
                print(f"  Size: {len(pdf_content)} bytes")

                if not dry_run:
                    # Upload to storage
                    storage.upload(remote_path, pdf_content)
                    print(f"  ✓ Uploaded to storage")

                    # Update invoice pdf_path
                    invoice.pdf_path = remote_path
                    print(f"  ✓ Updated invoice.pdf_path")

                    # Find or create document entry
                    doc = (
                        db.query(Document)
                        .filter(
                            Document.linked_module == "invoices",
                            Document.title == f"Rechnung {invoice.invoice_number}",
                        )
                        .first()
                    )

                    if doc:
                        # Update existing document
                        doc.file_path = remote_path
                        doc.checksum = checksum
                        print(f"  ✓ Updated existing Document record")
                    else:
                        # Create new document
                        doc = Document(
                            title=f"Rechnung {invoice.invoice_number}",
                            file_path=remote_path,
                            type="pdf",
                            category="Rechnungen",
                            owner_id=None,
                            linked_module="invoices",
                            checksum=checksum,
                            is_confidential=False,
                        )
                        db.add(doc)
                        print(f"  ✓ Created new Document record")

                    db.commit()
                    migrated_count += 1
                else:
                    print(f"  [DRY RUN] Would migrate to {remote_path}")
                    migrated_count += 1

            except Exception as e:
                print(f"  ❌ Error: {e}")
                error_count += 1
                db.rollback()

            print()

        print("=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print(f"Total invoices: {len(invoices)}")
        print(f"Migrated: {migrated_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Errors: {error_count}")
        print("=" * 80)

        if dry_run:
            print()
            print("This was a DRY RUN. No changes were made.")
            print("Run without --dry-run to actually migrate the files.")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate invoice PDFs to storage backend"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually migrating",
    )

    args = parser.parse_args()

    migrate_pdfs(dry_run=args.dry_run)
