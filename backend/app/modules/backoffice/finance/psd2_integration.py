"""
PSD2 Open Banking API Integration (ING)

Implementiert die europäische PSD2 XS2A (Access to Account) Schnittstelle
mit mTLS (mutual TLS) Authentifizierung und OAuth2.

Standards:
- PSD2 (Payment Services Directive 2)
- XS2A (Access to Account)
- eIDAS (Qualified Certificates)
- OAuth2 Authorization Code Flow

ING Developer Portal: https://developer.ing.com
API Version: v3

Authentifizierung:
- mTLS mit QWAC Zertifikat (Qualified Web Authentication Certificate)
- Request Signing mit QSealC Zertifikat (Qualified Electronic Seal Certificate)
- OAuth2 für User-Consent

Sicherheit:
- Zertifikate werden aus Dateisystem geladen (nie in DB!)
- OAuth2 Tokens werden temporär verschlüsselt gespeichert
- User-Consent erforderlich für jeden Zugriff

APIs:
- Account Information Service (AIS)
- Payment Initiation Service (PIS) - optional
"""
import logging
import ssl
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import uuid

import httpx
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

class PSD2Config:
    """PSD2 API Configuration für ING"""

    # Sandbox vs Production
    SANDBOX_BASE_URL = "https://api.sandbox.ing.com"
    PRODUCTION_BASE_URL = "https://api.ing.com"

    # API Endpoints
    OAUTH_AUTHORIZE_URL = "/oauth2/authorization-server-url"
    OAUTH_TOKEN_URL = "/oauth2/token"
    ACCOUNTS_URL = "/v3/accounts"
    BALANCES_URL = "/v3/accounts/{accountId}/balances"
    TRANSACTIONS_URL = "/v3/accounts/{accountId}/transactions"

    # Default Timeouts
    REQUEST_TIMEOUT = 30

    # Certificate Paths (absolute paths for Docker container)
    CERT_PATH_QWAC = "/app/certificates/psd2/example_client_tls.cer"
    CERT_PATH_QWAC_KEY = "/app/certificates/psd2/example_client_tls.key"
    CERT_PATH_QSEALC = "/app/certificates/psd2/example_client_signing.cer"
    CERT_PATH_QSEALC_KEY = "/app/certificates/psd2/example_client_signing.key"


# ============================================================================
# SCHEMAS (Pydantic Models for API Requests/Responses)
# ============================================================================

from pydantic import BaseModel, Field


class PSD2Credentials(BaseModel):
    """PSD2 API Credentials"""
    client_id: str = Field(..., description="Client ID from ING Developer Portal")
    environment: str = Field(default="sandbox", description="sandbox or production")
    qwac_cert_path: Optional[str] = Field(None, description="Path to QWAC certificate")
    qwac_key_path: Optional[str] = Field(None, description="Path to QWAC private key")
    qsealc_cert_path: Optional[str] = Field(None, description="Path to QSealC certificate")
    qsealc_key_path: Optional[str] = Field(None, description="Path to QSealC private key")


class PSD2Account(BaseModel):
    """PSD2 Account Information"""
    resource_id: str = Field(..., description="Account identifier from bank")
    iban: Optional[str] = None
    currency: str
    name: Optional[str] = None
    product: Optional[str] = None
    cash_account_type: Optional[str] = Field(None, alias="cashAccountType")

    class Config:
        populate_by_name = True


class PSD2Balance(BaseModel):
    """PSD2 Balance Information"""
    balance_amount: Dict[str, Any] = Field(..., alias="balanceAmount")
    balance_type: str = Field(..., alias="balanceType")
    reference_date: Optional[str] = Field(None, alias="referenceDate")

    class Config:
        populate_by_name = True


class PSD2Transaction(BaseModel):
    """PSD2 Transaction Information"""
    transaction_id: str = Field(..., alias="transactionId")
    booking_date: Optional[str] = Field(None, alias="bookingDate")
    value_date: Optional[str] = Field(None, alias="valueDate")
    transaction_amount: Dict[str, Any] = Field(..., alias="transactionAmount")
    creditor_name: Optional[str] = Field(None, alias="creditorName")
    creditor_account: Optional[Dict[str, str]] = Field(None, alias="creditorAccount")
    debtor_name: Optional[str] = Field(None, alias="debtorName")
    debtor_account: Optional[Dict[str, str]] = Field(None, alias="debtorAccount")
    remittance_information_unstructured: Optional[str] = Field(None, alias="remittanceInformationUnstructured")

    class Config:
        populate_by_name = True


class PSD2ConsentRequest(BaseModel):
    """Request to initiate OAuth2 consent flow"""
    client_id: str
    redirect_uri: str = Field(..., description="Redirect URI after consent")
    scope: str = Field(default="payment-accounts:balances:view payment-accounts:transactions:view")
    state: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


class PSD2ConsentResponse(BaseModel):
    """OAuth2 consent authorization URL"""
    authorization_url: str
    state: str


class PSD2TokenRequest(BaseModel):
    """Request to exchange authorization code for access token"""
    client_id: str
    authorization_code: str
    redirect_uri: str


class PSD2TokenResponse(BaseModel):
    """OAuth2 Token Response"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


# ============================================================================
# mTLS CLIENT
# ============================================================================

class PSD2Client:
    """
    HTTP Client with mTLS (mutual TLS) support for PSD2 API.

    Features:
    - QWAC certificate for TLS connection
    - QSealC certificate for request signing
    - Automatic signature generation (Digest + Signature headers)
    """

    def __init__(self, credentials: PSD2Credentials):
        self.credentials = credentials
        self.base_url = (
            PSD2Config.SANDBOX_BASE_URL
            if credentials.environment == "sandbox"
            else PSD2Config.PRODUCTION_BASE_URL
        )

        # Load certificates
        self.qwac_cert = credentials.qwac_cert_path or PSD2Config.CERT_PATH_QWAC
        self.qwac_key = credentials.qwac_key_path or PSD2Config.CERT_PATH_QWAC_KEY
        self.qsealc_cert = credentials.qsealc_cert_path or PSD2Config.CERT_PATH_QSEALC
        self.qsealc_key = credentials.qsealc_key_path or PSD2Config.CERT_PATH_QSEALC_KEY

        logger.info(f"PSD2Client initialized for {credentials.environment}")

    def _create_http_client(self) -> httpx.Client:
        """Creates HTTP client with mTLS configuration"""
        try:
            return httpx.Client(
                cert=(self.qwac_cert, self.qwac_key),
                verify=True,
                timeout=PSD2Config.REQUEST_TIMEOUT,
                http2=False,  # Disable HTTP/2 (requires h2 package)
            )
        except Exception as e:
            logger.error(f"Failed to create mTLS client: {e}")
            raise ValueError(f"Certificate error: {e}")

    def _sign_request(self, method: str, path: str, body: Optional[bytes] = None) -> Dict[str, str]:
        """
        Signs HTTP request using QSealC certificate.

        Generates required headers:
        - Digest: SHA-256 hash of request body
        - Signature: Signed headers (date, digest, x-ing-reqid)
        """
        headers = {}

        # Generate Digest header (SHA-256 of body)
        if body:
            digest_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest_hash.update(body)
            digest_b64 = digest_hash.finalize().hex()
            headers["Digest"] = f"SHA-256={digest_b64}"

        # Generate Signature header
        # TODO: Implement full signature generation
        # For sandbox, simplified version may work
        headers["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers["X-ING-ReqID"] = str(uuid.uuid4())

        return headers

    def request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Makes authenticated request to PSD2 API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., /v3/accounts)
            headers: Additional headers
            params: Query parameters
            json_data: JSON request body
            access_token: OAuth2 access token

        Returns:
            Response JSON
        """
        url = f"{self.base_url}{path}"

        # Prepare headers
        req_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if access_token:
            req_headers["Authorization"] = f"Bearer {access_token}"

        # Add signature headers
        body_bytes = None
        if json_data:
            import json
            body_bytes = json.dumps(json_data).encode("utf-8")

        signature_headers = self._sign_request(method, path, body_bytes)
        req_headers.update(signature_headers)

        if headers:
            req_headers.update(headers)

        # Make request
        try:
            with self._create_http_client() as client:
                response = client.request(
                    method,
                    url,
                    headers=req_headers,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"PSD2 API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"PSD2 request failed: {e}")
            raise


# ============================================================================
# HTTPS SIGNATURE HELPERS (ING Granting Flow)
# ============================================================================

def calculate_digest(payload: str) -> str:
    """
    Berechnet SHA-256 Digest für Request Body.

    Args:
        payload: Request body as string

    Returns:
        Digest Header Value (format: "SHA-256=base64...")
    """
    payload_bytes = payload.encode('utf-8')
    digest_hash = hashlib.sha256(payload_bytes).digest()
    digest_b64 = base64.b64encode(digest_hash).decode('utf-8')
    return f"SHA-256={digest_b64}"


def calculate_date() -> str:
    """
    Berechnet RFC7231 Date Header.

    Returns:
        Date Header Value (format: "Mon, 01 Jan 2025 12:00:00 GMT")
    """
    from email.utils import formatdate
    return formatdate(timeval=None, localtime=False, usegmt=True)


def get_certificate_serial_number(cert_path: str) -> str:
    """
    Liest Serial Number aus Zertifikat für keyId.

    Args:
        cert_path: Path to certificate file

    Returns:
        Serial number in hex format (e.g., "546212fb")
    """
    try:
        with open(cert_path, 'rb') as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        serial_hex = format(cert.serial_number, 'x')

        logger.info(f"Certificate serial number: {serial_hex}")
        return serial_hex

    except Exception as e:
        logger.error(f"Failed to read certificate serial: {e}")
        raise ValueError(f"Certificate read error: {e}")


def load_certificate_content(cert_path: str) -> str:
    """
    Liest Zertifikat-Content als Base64 String (ohne BEGIN/END Marker).

    Args:
        cert_path: Path to certificate file

    Returns:
        Base64-encoded certificate content (single line)
    """
    try:
        with open(cert_path, 'r') as f:
            cert_content = f.read()

        # Remove BEGIN/END markers and newlines
        cert_lines = cert_content.replace('-----BEGIN CERTIFICATE-----', '') \
                                 .replace('-----END CERTIFICATE-----', '') \
                                 .replace('\n', '') \
                                 .replace('\r', '')

        return cert_lines.strip()

    except Exception as e:
        logger.error(f"Failed to load certificate content: {e}")
        raise ValueError(f"Certificate load error: {e}")


def calculate_signature(
    method: str,
    path: str,
    date: str,
    digest: str,
    signing_key_path: str,
) -> str:
    """
    Berechnet HTTPS Signature für ING Granting Flow.

    Signing String Format:
        (request-target): post /oauth2/token
        date: Mon, 01 Jan 2025 12:00:00 GMT
        digest: SHA-256=abc123...

    Args:
        method: HTTP method (lowercase, e.g., "post")
        path: Request path (e.g., "/oauth2/token")
        date: Date header value
        digest: Digest header value
        signing_key_path: Path to QSealC private key

    Returns:
        Base64-encoded signature
    """
    try:
        # Load private key
        with open(signing_key_path, 'rb') as f:
            private_key = load_pem_private_key(f.read(), password=None, backend=default_backend())

        # Construct signing string
        signing_string = f"(request-target): {method.lower()} {path}\ndate: {date}\ndigest: {digest}"

        logger.debug(f"Signing string:\n{signing_string}")

        # Sign with RSA-SHA256
        signature = private_key.sign(
            signing_string.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Base64 encode
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        logger.info("Signature calculated successfully")
        return signature_b64

    except Exception as e:
        logger.error(f"Failed to calculate signature: {e}")
        raise ValueError(f"Signature calculation error: {e}")


def build_authorization_signature_header(
    keyId: str,
    signature: str,
    algorithm: str = "rsa-sha256",
    headers: str = "(request-target) date digest",
) -> str:
    """
    Erstellt Authorization Signature Header.

    Format:
        Signature keyId="SN=546212fb",algorithm="rsa-sha256",headers="(request-target) date digest",signature="..."

    Args:
        keyId: Certificate serial number (format: "SN=546212fb")
        signature: Base64-encoded signature
        algorithm: Signature algorithm (default: rsa-sha256)
        headers: Signed headers (default: (request-target) date digest)

    Returns:
        Complete Authorization header value
    """
    return (
        f'Signature keyId="{keyId}",'
        f'algorithm="{algorithm}",'
        f'headers="{headers}",'
        f'signature="{signature}"'
    )


# ============================================================================
# MTLS APPLICATION ACCESS TOKEN
# ============================================================================

def request_application_access_token(
    credentials: PSD2Credentials,
    scope: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Holt Application Access Token via HTTPS Signature (Granting Flow - Step 3c).

    **ING Granting Flow:**
    - Requires mTLS + HTTPS Signature
    - Digest, Date, Signature headers
    - TPP-Signature-Certificate header

    Args:
        credentials: PSD2 Credentials
        scope: Optional Scope (default: all scopes in certificate)

    Returns:
        Application Access Token Response
    """
    client = PSD2Client(credentials)

    try:
        # Form data
        form_data = {
            "grant_type": "client_credentials",
        }

        if scope:
            form_data["scope"] = scope

        # Encode as x-www-form-urlencoded
        from urllib.parse import urlencode
        payload = urlencode(form_data)

        # Calculate HTTPS Signature headers
        digest = calculate_digest(payload)
        date = calculate_date()
        signature = calculate_signature(
            method="post",
            path=PSD2Config.OAUTH_TOKEN_URL,
            date=date,
            digest=digest,
            signing_key_path=client.qsealc_key,
        )

        # Get certificate serial for keyId
        serial_number = get_certificate_serial_number(client.qsealc_cert)
        keyId = f"SN={serial_number}"

        # Build Authorization Signature header
        auth_header = build_authorization_signature_header(
            keyId=keyId,
            signature=signature,
        )

        # Load TPP-Signature-Certificate
        cert_content = load_certificate_content(client.qsealc_cert)

        # Make mTLS request WITH HTTPS Signature
        with client._create_http_client() as http_client:
            response = http_client.post(
                f"{client.base_url}{PSD2Config.OAUTH_TOKEN_URL}",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Digest": digest,
                    "Date": date,
                    "TPP-Signature-Certificate": cert_content,
                    "Authorization": auth_header,
                },
                content=payload,
            )
            response.raise_for_status()
            result = response.json()

        logger.info("Successfully obtained application access token via HTTPS Signature")
        return result

    except Exception as e:
        logger.error(f"Failed to get application access token: {e}")
        raise ValueError(f"Token request failed: {e}")


# ============================================================================
# OAUTH2 CONSENT FLOW
# ============================================================================

def initiate_consent(
    credentials: PSD2Credentials,
    redirect_uri: str,
    scope: str = "payment-accounts:balances:view payment-accounts:transactions:view",
    country_code: str = "DE",
) -> PSD2ConsentResponse:
    """
    Initiiert OAuth2 Consent Flow für User-Authentifizierung.

    Returns authorization URL für User-Redirect.
    User muss zu dieser URL weitergeleitet werden, um Consent zu geben.

    **ING PSD2 Flow:**
    - Keine API-Call nötig
    - Authorization URL wird direkt konstruiert
    - User wird zu ING myaccount weitergeleitet

    Args:
        credentials: PSD2 Credentials
        redirect_uri: Callback URL nach Consent
        scope: OAuth2 Scopes (default: Accounts + Transactions)
        country_code: ING Country (DE, NL, BE, etc.)

    Returns:
        Authorization URL und State
    """
    # Generate state for CSRF protection
    state = str(uuid.uuid4())

    # ING myaccount base URL (sandbox vs production)
    if credentials.environment == "sandbox":
        myaccount_base = "https://myaccount.sandbox.ing.com"
    else:
        myaccount_base = "https://myaccount.ing.com"

    # URL-encode scope (spaces to %20 or +)
    from urllib.parse import urlencode, quote_plus

    params = {
        "client_id": credentials.client_id,
        "scope": scope.replace(" ", "+"),  # Spaces to +
        "state": state,
        "redirect_uri": redirect_uri,
        "response_type": "code",
    }

    # Construct authorization URL
    query_string = urlencode(params, safe='+')
    authorization_url = f"{myaccount_base}/authorize/v2/{country_code}?{query_string}"

    logger.info(f"Consent initiated. Redirect user to: {authorization_url}")

    return PSD2ConsentResponse(
        authorization_url=authorization_url,
        state=state
    )


def exchange_authorization_code(
    credentials: PSD2Credentials,
    authorization_code: str,
    application_access_token: str,
) -> PSD2TokenResponse:
    """
    Tauscht Authorization Code gegen Customer Access Token (Granting Flow - Step 3d).

    **ING Granting Flow:**
    - Requires mTLS + HTTPS Signature
    - Digest, Date, Signature headers
    - TPP-Signature-Certificate header
    - Bearer token from application access token

    Args:
        credentials: PSD2 Credentials
        authorization_code: Code from redirect callback
        application_access_token: Application access token from Step 3c

    Returns:
        Customer Access Token Response
    """
    client = PSD2Client(credentials)

    try:
        # Form data for token exchange
        form_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
        }

        # Encode as x-www-form-urlencoded
        from urllib.parse import urlencode
        payload = urlencode(form_data)

        # Calculate HTTPS Signature headers
        digest = calculate_digest(payload)
        date = calculate_date()
        signature = calculate_signature(
            method="post",
            path=PSD2Config.OAUTH_TOKEN_URL,
            date=date,
            digest=digest,
            signing_key_path=client.qsealc_key,
        )

        # Get certificate serial for keyId
        serial_number = get_certificate_serial_number(client.qsealc_cert)
        keyId = f"SN={serial_number}"

        # Build Authorization Signature header
        auth_signature_header = build_authorization_signature_header(
            keyId=keyId,
            signature=signature,
        )

        # Load TPP-Signature-Certificate
        cert_content = load_certificate_content(client.qsealc_cert)

        # Make mTLS request WITH HTTPS Signature
        with client._create_http_client() as http_client:
            response = http_client.post(
                f"{client.base_url}{PSD2Config.OAUTH_TOKEN_URL}",
                headers={
                    "Authorization": f"Bearer {application_access_token}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "Digest": digest,
                    "Date": date,
                    "TPP-Signature-Certificate": cert_content,
                    "Signature": auth_signature_header,
                },
                content=payload,
            )
            response.raise_for_status()
            result = response.json()

        logger.info("Successfully exchanged authorization code for customer access token")

        return PSD2TokenResponse(**result)

    except Exception as e:
        logger.error(f"Failed to exchange authorization code: {e}")
        raise ValueError(f"Token exchange failed: {e}")


# ============================================================================
# ACCOUNT INFORMATION SERVICE (AIS)
# ============================================================================

def get_accounts(
    credentials: PSD2Credentials,
    access_token: str,
) -> List[PSD2Account]:
    """
    Holt Liste aller verfügbaren Konten.

    Args:
        credentials: PSD2 Credentials
        access_token: OAuth2 Access Token

    Returns:
        Liste von Konten
    """
    client = PSD2Client(credentials)

    try:
        response = client.request(
            method="GET",
            path=PSD2Config.ACCOUNTS_URL,
            access_token=access_token,
        )

        accounts_data = response.get("accounts", [])
        accounts = [PSD2Account(**acc) for acc in accounts_data]

        logger.info(f"Retrieved {len(accounts)} accounts")
        return accounts

    except Exception as e:
        logger.error(f"Failed to get accounts: {e}")
        raise ValueError(f"Get accounts failed: {e}")


def get_balances(
    credentials: PSD2Credentials,
    access_token: str,
    account_id: str,
) -> List[PSD2Balance]:
    """
    Holt Kontostand für ein Konto.

    Args:
        credentials: PSD2 Credentials
        access_token: OAuth2 Access Token
        account_id: Account resource ID

    Returns:
        Liste von Balances (meist mehrere: booked, expected, etc.)
    """
    client = PSD2Client(credentials)

    try:
        path = PSD2Config.BALANCES_URL.format(accountId=account_id)
        response = client.request(
            method="GET",
            path=path,
            access_token=access_token,
        )

        balances_data = response.get("balances", [])
        balances = [PSD2Balance(**bal) for bal in balances_data]

        logger.info(f"Retrieved {len(balances)} balances for account {account_id}")
        return balances

    except Exception as e:
        logger.error(f"Failed to get balances: {e}")
        raise ValueError(f"Get balances failed: {e}")


def get_transactions(
    credentials: PSD2Credentials,
    access_token: str,
    account_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[PSD2Transaction]:
    """
    Holt Transaktionen für ein Konto.

    Args:
        credentials: PSD2 Credentials
        access_token: OAuth2 Access Token
        account_id: Account resource ID
        date_from: Start date (ISO format: YYYY-MM-DD)
        date_to: End date (ISO format: YYYY-MM-DD)

    Returns:
        Liste von Transaktionen
    """
    client = PSD2Client(credentials)

    try:
        path = PSD2Config.TRANSACTIONS_URL.format(accountId=account_id)
        params = {}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to

        response = client.request(
            method="GET",
            path=path,
            params=params,
            access_token=access_token,
        )

        transactions_data = response.get("transactions", {}).get("booked", [])
        transactions = [PSD2Transaction(**txn) for txn in transactions_data]

        logger.info(f"Retrieved {len(transactions)} transactions for account {account_id}")
        return transactions

    except Exception as e:
        logger.error(f"Failed to get transactions: {e}")
        raise ValueError(f"Get transactions failed: {e}")


# ============================================================================
# CONVERSION TO WORKMATEOS FORMAT
# ============================================================================

def convert_psd2_account_to_bank_account(psd2_account: PSD2Account) -> Dict[str, Any]:
    """Konvertiert PSD2 Account zu WorkmateOS BankAccount Format"""
    return {
        "account_number": psd2_account.resource_id,
        "iban": psd2_account.iban,
        "account_name": psd2_account.name or f"ING {psd2_account.product or 'Account'}",
        "bank_name": "ING",
        "bic_swift": "INGDDEFFXXX",  # ING Germany
        "currency": psd2_account.currency,
        "account_type": "checking",  # Default
        "connection_type": "psd2_api",
    }


def convert_psd2_transaction_to_bank_transaction(
    psd2_transaction: PSD2Transaction,
    account_id: uuid.UUID,
) -> Dict[str, Any]:
    """Konvertiert PSD2 Transaction zu WorkmateOS BankTransaction Format"""
    amount_data = psd2_transaction.transaction_amount
    amount = float(amount_data.get("amount", 0))
    currency = amount_data.get("currency", "EUR")

    # Determine transaction type
    is_credit = amount > 0
    transaction_type = "credit" if is_credit else "debit"

    return {
        "account_id": account_id,
        "transaction_date": psd2_transaction.booking_date or psd2_transaction.value_date,
        "value_date": psd2_transaction.value_date,
        "amount": abs(amount),
        "currency": currency,
        "transaction_type": transaction_type,
        "counterparty_name": (
            psd2_transaction.creditor_name if is_credit
            else psd2_transaction.debtor_name
        ),
        "counterparty_iban": (
            (psd2_transaction.creditor_account or {}).get("iban") if is_credit
            else (psd2_transaction.debtor_account or {}).get("iban")
        ),
        "purpose": psd2_transaction.remittance_information_unstructured,
        "reference": psd2_transaction.transaction_id,
        "reconciliation_status": "unreconciled",
        "import_source": "psd2_api",
    }
