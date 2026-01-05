#!/usr/bin/env python3
"""
Test Payment Sync from SevDesk
"""
import requests
import json
import sys


def test_payment_sync():
    """Test the payment sync endpoint"""

    print("=" * 80)
    print("TESTING PAYMENT SYNC FROM SEVDESK")
    print("=" * 80)
    print(f"\nEndpoint: POST /api/backoffice/finance/sevdesk/sync/payments")
    print(f"Action: Sync all invoices\n")

    try:
        response = requests.post(
            "http://localhost:8000/api/backoffice/finance/sevdesk/sync/payments",
            headers={
                "Content-Type": "application/json",
                "X-Test-User": json.dumps({
                    "preferred_username": "test",
                    "email": "test@example.com",
                    "role": "hr"
                })
            },
            json={
                "sync_all": True
            },
            timeout=60,
        )

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS\n")
        else:
            print("❌ FAILED\n")

        print(f"📄 Response Body:")
        result = response.json()
        print(json.dumps(result, indent=2, default=str))

        # Print summary
        if response.status_code == 200:
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Total invoices checked: {result.get('total_invoices_checked', 0)}")
            print(f"Payments created: {result.get('payments_created', 0)}")
            print(f"Invoices status updated: {result.get('invoices_status_updated', 0)}")
            print(f"Errors: {len(result.get('errors', []))}")

            if result.get('details'):
                print(f"\nDetails:")
                for detail in result['details']:
                    print(f"\n  Invoice: {detail['invoice_number']}")
                    print(f"    SevDesk paid: €{detail['sevdesk_paid_amount']}")
                    print(f"    WorkmateOS paid: €{detail['workmate_paid_amount']}")
                    if detail['payment_created']:
                        print(f"    ✅ Payment created: €{detail['payment_amount']}")
                    if detail['new_invoice_status']:
                        print(f"    📝 Status updated to: {detail['new_invoice_status']}")

        return response.status_code == 200

    except requests.exceptions.Timeout:
        print("❌ Request timeout after 60 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_payment_sync()
    print("\n" + "=" * 80)
    sys.exit(0 if success else 1)
