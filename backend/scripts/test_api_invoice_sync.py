#!/usr/bin/env python3
"""
Test invoice sync via API endpoint
"""
import requests
import json
import sys

def test_invoice_sync():
    """Test the invoice sync endpoint"""

    # Test with RE-2026-0004
    invoice_id = "64f5e323-8e13-46de-a362-969ea893fc3f"

    print("=" * 80)
    print("TESTING INVOICE SYNC VIA API ENDPOINT")
    print("=" * 80)
    print(f"\nInvoice ID: {invoice_id}")
    print(f"Endpoint: POST /api/backoffice/finance/sevdesk/sync/invoice")

    try:
        response = requests.post(
            "http://localhost:8000/api/backoffice/finance/sevdesk/sync/invoice",
            headers={
                "Content-Type": "application/json",
                "X-Test-User": json.dumps({
                    "preferred_username": "test",
                    "email": "test@example.com",
                    "role": "hr"
                })
            },
            json={"invoice_id": invoice_id},
            timeout=60,
        )

        print(f"\n📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")

        print(f"\n📄 Response Body:")
        print(json.dumps(response.json(), indent=2, default=str))

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
    success = test_invoice_sync()
    print("\n" + "=" * 80)
    sys.exit(0 if success else 1)
