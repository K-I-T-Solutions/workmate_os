# test_invoice_fixed.py
import requests
import json
from datetime import date, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://api.workmate.intern.phudevelopement.xyz/api/backoffice/invoices"
PDF_URL = f"{BASE_URL}/{{invoice_id}}/pdf"

HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer <dein_token>"
}

invoice_data = {
    "invoice_number": "RE-2025-TEST",
    "issued_date": str(date.today()),
    "due_date": str(date.today() + timedelta(days=14)),
    "customer_id": "e6c54ba1-1f5c-4f43-a65f-2769e960f8a4",
    "project_id": "98df25ce-da24-49b8-9d84-4686e936f41f",
    "status": "draft",
    "notes": "Automatischer Testlauf über interne API",
    "terms": "Zahlbar innerhalb von 14 Tagen.",
    "line_items": [
        {
            "position": 1,
            "description": "IT-Support – Systemwartung",
            "quantity": 2,
            "unit": "Stunden",
            "unit_price": 85.00,
            "tax_rate": 19.00,
            "discount_percent": 0.00
        },
        {
            "position": 2,
            "description": "Netzwerkanalyse & Audit",
            "quantity": 1,
            "unit": "Pauschal",
            "unit_price": 250.00,
            "tax_rate": 19.00,
            "discount_percent": 5.00
        }
    ]
}

print("→ Erstelle neue Invoice...")
res = requests.post(BASE_URL + "/", headers=HEADERS, json=invoice_data, verify=False)
if res.status_code in (200, 201):
    invoice = res.json()
    print("✅ Rechnung erstellt:", invoice["invoice_number"])
    print("   ID:", invoice["id"])
else:
    print("❌ Fehler beim Erstellen:", res.status_code, res.text)
    exit(1)

invoice_id = invoice["id"]

print("\n→ Lade Invoice...")
res = requests.get(f"{BASE_URL}/{invoice_id}", headers=HEADERS, verify=False)
print("📄 Status:", res.status_code)
print(json.dumps(res.json(), indent=2, ensure_ascii=False))

print("\n→ Lade PDF...")
pdf_res = requests.get(PDF_URL.format(invoice_id=invoice_id), headers=HEADERS, verify=False)
if pdf_res.status_code == 200:
    with open("invoice_test.pdf", "wb") as f:
        f.write(pdf_res.content)
    print("🧾 PDF gespeichert: invoice_test.pdf")
else:
    print("❌ PDF-Fehler:", pdf_res.status_code, pdf_res.text)
