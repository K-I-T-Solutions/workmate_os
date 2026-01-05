"""
SevDesk API Integration

Bidirektionale Synchronisation zwischen WorkmateOS und SevDesk:
- Push: Rechnungen, Kontakte von WorkmateOS → SevDesk
- Pull: Transaktionen, Rechnungsstatus von SevDesk → WorkmateOS

API Dokumentation: https://api.sevdesk.de/
Base URL: https://my.sevdesk.de/api/v1
Authentication: API Token via Authorization Header
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class SevDeskConfig:
    """SevDesk API Configuration"""
    BASE_URL = "https://my.sevdesk.de/api/v1"
    TIMEOUT = 30


class SevDeskAPIClient:
    """
    SevDesk API Client
    
    Handles all communication with SevDesk API.
    """
    
    def __init__(self, api_token: str):
        """
        Initialize SevDesk API Client
        
        Args:
            api_token: 32-character hexadecimal API token from SevDesk
        """
        self.api_token = api_token
        self.base_url = SevDeskConfig.BASE_URL
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to SevDesk API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/Invoice")
            params: Query parameters
            json: Request body (for POST/PUT)

        Returns:
            API response as dict

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        # Add token to query parameters (required for POST requests)
        if params is None:
            params = {}
        params["token"] = self.api_token

        logger.info(f"🔄 [SevDesk API] {method} {url}")

        async with httpx.AsyncClient(timeout=SevDeskConfig.TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json,
            )

            logger.info(f"📊 [SevDesk API] Response: {response.status_code}")

            if response.status_code >= 400:
                # Log error details before raising
                try:
                    error_body = response.json()
                    logger.error(f"❌ [SevDesk API] Error Response: {error_body}")
                except:
                    logger.error(f"❌ [SevDesk API] Error Body: {response.text[:500]}")

            response.raise_for_status()
            return response.json()
    
    # ========================================================================
    # INVOICES (Rechnungen)
    # ========================================================================
    
    async def get_invoices(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all invoices from SevDesk
        
        Args:
            limit: Max number of results (1-1000)
            offset: Offset for pagination
            status: Invoice status filter (100=draft, 200=open, 1000=paid)
        
        Returns:
            List of invoice objects
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        
        response = await self._request("GET", "/Invoice", params=params)
        return response.get("objects", [])
    
    async def create_invoice(
        self,
        invoice_data: Dict[str, Any],
        positions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create invoice in SevDesk
        
        Args:
            invoice_data: Invoice base data (contact, invoice date, etc.)
            positions: List of invoice line items
        
        Returns:
            Created invoice object
        """
        payload = {
            "invoice": invoice_data,
            "invoicePosSave": positions,
        }
        
        response = await self._request("POST", "/Invoice/Factory/saveInvoice", json=payload)
        return response.get("objects", {}).get("invoice", {})
    
    async def update_invoice_status(
        self,
        invoice_id: str,
        status: int,
    ) -> Dict[str, Any]:
        """
        Update invoice status
        
        Args:
            invoice_id: SevDesk invoice ID
            status: New status (100=draft, 200=open, 1000=paid)
        
        Returns:
            Updated invoice object
        """
        response = await self._request(
            "PUT",
            f"/Invoice/{invoice_id}",
            json={"status": status},
        )
        return response.get("objects", [{}])[0]
    
    # ========================================================================
    # CONTACTS (Kunden)
    # ========================================================================
    
    async def get_contacts(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get all contacts from SevDesk
        
        Args:
            limit: Max number of results
            offset: Offset for pagination
        
        Returns:
            List of contact objects
        """
        params = {"limit": limit, "offset": offset}
        response = await self._request("GET", "/Contact", params=params)
        return response.get("objects", [])
    
    async def create_contact(
        self,
        contact_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create contact in SevDesk
        
        Args:
            contact_data: Contact data (name, email, address, etc.)
        
        Returns:
            Created contact object
        """
        response = await self._request("POST", "/Contact", json=contact_data)
        return response.get("objects", [{}])[0]
    
    async def search_contact_by_email(
        self,
        email: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Search contact by email
        
        Args:
            email: Email address
        
        Returns:
            Contact object or None
        """
        contacts = await self.get_contacts()
        for contact in contacts:
            if contact.get("email") == email:
                return contact
        return None

    async def get_current_sev_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current SevUser (authenticated user)

        Returns:
            Current SevUser object or None
        """
        response = await self._request("GET", "/SevUser")
        users = response.get("objects", [])
        if users:
            return users[0]  # Return first user (usually the authenticated user)
        return None

    # ========================================================================
    # CHECK ACCOUNTS (Bank-Konten)
    # ========================================================================
    
    async def get_check_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all check accounts (bank accounts) from SevDesk
        
        Returns:
            List of check account objects
        """
        response = await self._request("GET", "/CheckAccount")
        return response.get("objects", [])
    
    # ========================================================================
    # TRANSACTIONS (Transaktionen)
    # ========================================================================
    
    async def get_transactions(
        self,
        check_account_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get transactions from SevDesk
        
        Args:
            check_account_id: Filter by check account ID
            limit: Max number of results
            offset: Offset for pagination
        
        Returns:
            List of transaction objects
        """
        params = {"limit": limit, "offset": offset}
        if check_account_id:
            params["checkAccount[id]"] = check_account_id
        
        response = await self._request("GET", "/CheckAccountTransaction", params=params)
        return response.get("objects", [])
    
    async def create_transaction(
        self,
        transaction_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create transaction in SevDesk

        Args:
            transaction_data: Transaction data

        Returns:
            Created transaction object
        """
        response = await self._request("POST", "/CheckAccountTransaction", json=transaction_data)
        return response.get("objects", [{}])[0]

    # ========================================================================
    # VOUCHERS (Belege / Payments)
    # ========================================================================

    async def get_vouchers(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get vouchers from SevDesk (Belege - includes payments)

        Args:
            limit: Max number of results
            offset: Offset for pagination
            status: Filter by status (50=draft, 100=unpaid, 1000=paid)

        Returns:
            List of voucher objects
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        response = await self._request("GET", "/Voucher", params=params)
        return response.get("objects", [])


# ============================================================================
# MAPPING HELPERS
# ============================================================================

def map_workmate_invoice_to_sevdesk(
    invoice: Dict[str, Any],
    contact_id: str,
    contact_person_id: Optional[str] = None,
) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Map WorkmateOS invoice to SevDesk format

    Args:
        invoice: WorkmateOS invoice object
        contact_id: SevDesk contact ID (as string)
        contact_person_id: SevDesk contact person ID (SevUser) - optional, uses contact's default if not provided

    Returns:
        Tuple of (invoice_data, positions)
    """
    # Convert invoice date from ISO to dd.mm.yyyy format
    invoice_date = invoice.get("invoice_date", "")
    if invoice_date and isinstance(invoice_date, str):
        # Convert from YYYY-MM-DD to DD.MM.YYYY
        from datetime import datetime
        try:
            date_obj = datetime.fromisoformat(invoice_date)
            invoice_date = date_obj.strftime("%d.%m.%Y")
        except:
            pass

    # Invoice base data (based on official SevDesk API example)
    invoice_data = {
        "id": None,
        "objectName": "Invoice",
        "invoiceNumber": invoice.get("invoice_number"),
        "contact": {
            "id": int(contact_id),  # Must be Integer!
            "objectName": "Contact",
        },
        "contactPerson": {
            "id": int(contact_person_id) if contact_person_id else int(contact_id),  # Use contact person ID or contact ID
            "objectName": "SevUser",
        },
        "invoiceDate": invoice_date,  # Format: DD.MM.YYYY
        "header": invoice.get("title", ""),
        "headText": invoice.get("notes", ""),
        "footText": "",
        "timeToPay": 20,
        "discount": 0,
        "status": "100",  # String! New invoices MUST be created with status 100 (Draft), can be updated later to 200 (Open)
        "smallSettlement": 0,
        "taxRate": 0,  # This is not used anymore (use taxRate on positions)
        "taxType": "default",
        "taxText": "Umsatzsteuer 19%",
        "invoiceType": "RE",  # Regular invoice
        "currency": "EUR",
        "showNet": "0",  # String, not Boolean! ("0"=gross, "1"=net)
        "sendType": "VPR",
        "mapAll": True,
    }

    # Invoice positions (line items) - based on official example
    positions = []
    for idx, item in enumerate(invoice.get("items", [])):
        positions.append({
            "id": None,
            "objectName": "InvoicePos",
            "mapAll": True,
            "quantity": float(item.get("quantity", 1)),
            "price": float(item.get("unit_price", 0)),
            "name": item.get("description", ""),
            "unity": {
                "id": 1,  # Integer!
                "objectName": "Unity",
            },
            "positionNumber": idx,
            "text": item.get("description", ""),
            "discount": 0,
            "taxRate": float(item.get("tax_rate", 19)),
        })

    return invoice_data, positions


def map_sevdesk_transaction_to_workmate(
    transaction: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Map SevDesk transaction to WorkmateOS format
    
    Args:
        transaction: SevDesk transaction object
    
    Returns:
        WorkmateOS transaction dict
    """
    return {
        "transaction_date": transaction.get("valueDate"),
        "amount": float(transaction.get("amount", 0)),
        "transaction_type": "income" if float(transaction.get("amount", 0)) > 0 else "expense",
        "counterparty_name": transaction.get("payeeName"),
        "purpose": transaction.get("purpose"),
        "reference": transaction.get("entryText"),
        "reconciliation_status": "unreconciled",
        "import_source": "sevdesk",
        # Store SevDesk ID for reference
        "sevdesk_id": transaction.get("id"),
    }
