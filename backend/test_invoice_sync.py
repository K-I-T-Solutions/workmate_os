#!/usr/bin/env python3
"""
Test script for SevDesk invoice sync
"""
import asyncio
import sys
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.modules.backoffice.invoices.models import Invoice
from app.modules.backoffice.finance.sevdesk_integration import SevDeskAPIClient, map_workmate_invoice_to_sevdesk
from app.modules.backoffice.finance.sevdesk_crud import get_decrypted_api_token, create_invoice_mapping, get_invoice_mapping
from app.modules.backoffice.finance.models import SevDeskSyncStatus
import os

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def test_invoice_push():
    """Test pushing an invoice to SevDesk"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("🧪 TESTING INVOICE SYNC TO SEVDESK")
        print("=" * 80)

        # Get API token
        print("\n[1/6] Getting SevDesk API token...")
        api_token = get_decrypted_api_token(db)
        if not api_token:
            print("   ❌ No SevDesk API token configured")
            return False
        print(f"   ✅ Got API token: {api_token[:8]}...")

        # Get invoice RE-2026-0005
        print("\n[2/6] Loading invoice from database...")
        invoice_id = "746e9efb-a89f-4140-a541-9ee61c428147"
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        invoice = db.scalars(stmt).first()

        if not invoice:
            print(f"   ❌ Invoice {invoice_id} not found")
            return False

        print(f"   ✅ Found invoice: {invoice.invoice_number}")
        print(f"      Customer: {invoice.customer.name if invoice.customer else 'N/A'}")
        print(f"      Items: {len(invoice.line_items)}")

        # Check if already synced
        existing_mapping = get_invoice_mapping(db, str(invoice.id))
        if existing_mapping:
            print(f"\n   ⚠️  Invoice already synced to SevDesk!")
            print(f"      SevDesk ID: {existing_mapping.sevdesk_invoice_id}")
            print(f"      Status: {existing_mapping.sync_status}")
            print(f"      Last synced: {existing_mapping.last_synced_at}")
            return False

        # Initialize SevDesk client
        print("\n[3/6] Initializing SevDesk client...")
        client = SevDeskAPIClient(api_token)
        print(f"   ✅ Client initialized")

        # Get contact from SevDesk
        print("\n[4/6] Finding contact in SevDesk...")

        # Try by email first
        customer_email = invoice.customer.email if invoice.customer else None
        contact = None

        if customer_email:
            print(f"   Trying by email: {customer_email}")
            contact = await client.search_contact_by_email(customer_email)

        # If not found, use first available contact
        if not contact:
            print(f"   Email not found, using first available contact")
            contacts = await client.get_contacts(limit=1)
            contact = contacts[0] if contacts else None

        if not contact:
            print("   ❌ No contact found in SevDesk")
            return False

        contact_id = str(contact.get("id"))
        contact_name = contact.get("name", "Unknown")

        print(f"   ✅ Found contact: {contact_name} (ID: {contact_id})")

        # Get SevUser (contactPerson required for invoice)
        print(f"   Getting current SevUser for contactPerson...")
        sev_user = await client.get_current_sev_user()
        if not sev_user:
            print("   ❌ No SevUser found")
            return False

        contact_person_id = str(sev_user.get("id"))
        sev_user_name = sev_user.get("fullname", sev_user.get("username", "Unknown"))
        print(f"   ✅ SevUser: {sev_user_name} (ID: {contact_person_id})")

        # Convert invoice to dict
        print("\n[5/6] Mapping invoice to SevDesk format...")
        invoice_dict = {
            "invoice_number": invoice.invoice_number,
            "invoice_date": str(invoice.issued_date),  # Use issued_date from Invoice model
            "title": "",  # Invoice model doesn't have title field
            "notes": invoice.notes or "",
            "items": [
                {
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "tax_rate": float(item.tax_rate) if item.tax_rate else 19.0,
                }
                for item in invoice.line_items
            ]
        }

        invoice_data, positions = map_workmate_invoice_to_sevdesk(invoice_dict, contact_id, contact_person_id)

        print(f"   Invoice Number: {invoice_data.get('invoiceNumber')}")
        print(f"   Invoice Date: {invoice_data.get('invoiceDate')}")
        print(f"   Contact ID: {invoice_data.get('contact', {}).get('id')} (type: {type(invoice_data.get('contact', {}).get('id')).__name__})")
        print(f"   Status: '{invoice_data.get('status')}' (type: {type(invoice_data.get('status')).__name__})")
        print(f"   ShowNet: '{invoice_data.get('showNet')}' (type: {type(invoice_data.get('showNet')).__name__})")
        print(f"   Positions: {len(positions)} items")
        for idx, pos in enumerate(positions, 1):
            print(f"      {idx}. {pos.get('name')} - {pos.get('quantity')}x €{pos.get('price')} ({pos.get('taxRate')}% MwSt)")

        # Push to SevDesk
        print(f"\n[6/6] Pushing invoice to SevDesk...")
        print(f"   ⏳ Sending request to SevDesk API...")

        # Debug: Print the full payload
        import json as json_lib
        payload = {
            "invoice": invoice_data,
            "invoicePosSave": positions,
        }
        print(f"\n   📤 Payload:")
        print(json_lib.dumps(payload, indent=2, default=str))

        sevdesk_invoice = await client.create_invoice(invoice_data, positions)

        sevdesk_invoice_id = str(sevdesk_invoice.get("id"))

        print(f"\n   ✅ SUCCESS! Invoice created in SevDesk")
        print(f"      SevDesk Invoice ID: {sevdesk_invoice_id}")
        print(f"      Invoice Number: {sevdesk_invoice.get('invoiceNumber')}")
        print(f"      Status: {sevdesk_invoice.get('status')}")

        # Create mapping
        print(f"\n[7/6] Creating mapping in database...")
        create_invoice_mapping(
            db,
            str(invoice.id),
            sevdesk_invoice_id,
            sync_status=SevDeskSyncStatus.SUCCESS.value
        )
        print(f"   ✅ Mapping created")

        print("\n" + "=" * 80)
        print("✅ INVOICE SYNC COMPLETED SUCCESSFULLY")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = asyncio.run(test_invoice_push())
    sys.exit(0 if success else 1)
