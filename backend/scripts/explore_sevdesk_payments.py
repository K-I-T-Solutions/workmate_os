#!/usr/bin/env python3
"""
Explore SevDesk Payment/Voucher API
"""
import asyncio
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modules.backoffice.finance.sevdesk_integration import SevDeskAPIClient
from app.modules.backoffice.finance.sevdesk_crud import get_decrypted_api_token
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def explore_payments():
    """Explore SevDesk payment structures"""
    db = SessionLocal()

    try:
        token = get_decrypted_api_token(db)
        if not token:
            print("❌ No SevDesk token found")
            return

        client = SevDeskAPIClient(token)

        print("=" * 80)
        print("EXPLORING SEVDESK PAYMENT/VOUCHER API")
        print("=" * 80)

        # 1. Get invoices with payment info
        print("\n[1] Getting invoices with payment information...")
        invoices = await client.get_invoices(limit=3)
        print(f"   Found {len(invoices)} invoices\n")

        for inv in invoices:
            print(f"   Invoice: {inv.get('invoiceNumber')}")
            print(f"      ID: {inv.get('id')}")
            print(f"      Status: {inv.get('status')}")
            print(f"      Sum Gross: {inv.get('sumGross')} EUR")
            print(f"      Paid Amount: {inv.get('paidAmount', 0)} EUR")
            print(f"      Outstanding: {float(inv.get('sumGross', 0)) - float(inv.get('paidAmount', 0))} EUR")
            print()

        # 2. Try Voucher endpoint
        print("\n[2] Exploring Voucher endpoint (Belege/Payments)...")
        try:
            response = await client._request("GET", "/Voucher", params={"limit": 5})
            vouchers = response.get("objects", [])
            print(f"   ✅ Found {len(vouchers)} vouchers\n")

            if vouchers:
                voucher = vouchers[0]
                print(f"   Voucher structure:")
                print(f"   Keys: {list(voucher.keys())}\n")
                print(f"   Sample voucher:")
                print(json.dumps(voucher, indent=2, default=str))
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # 3. Try getting related objects for an invoice
        if invoices:
            invoice_id = invoices[0].get("id")
            print(f"\n[3] Getting related objects for invoice {invoice_id}...")
            try:
                response = await client._request("GET", f"/Invoice/{invoice_id}/getRelatedObjects")
                print(f"   ✅ Related objects:")
                print(json.dumps(response, indent=2, default=str)[:1000])
            except Exception as e:
                print(f"   ❌ Error: {e}")

        # 4. Check CheckAccountTransaction with invoice reference
        print(f"\n[4] Getting CheckAccountTransactions...")
        try:
            transactions = await client.get_transactions(limit=5)
            print(f"   ✅ Found {len(transactions)} transactions\n")

            if transactions:
                tx = transactions[0]
                print(f"   Transaction structure:")
                print(f"   Keys: {list(tx.keys())}\n")
                print(f"   Sample transaction:")
                print(json.dumps(tx, indent=2, default=str)[:800])
        except Exception as e:
            print(f"   ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(explore_payments())
