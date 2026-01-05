"""
Error Messages & Codes

Zentrale Error Message Registry für konsistente, benutzerfreundliche Fehlermeldungen.

Struktur:
- Error Codes: Eindeutige Identifikatoren für Client-Side Error Handling
- Messages: Benutzerfreundliche Texte (Deutsch)
- Hints: Lösungsvorschläge für den User
"""

from typing import Optional, Any
from dataclasses import dataclass


class ErrorCode:
    """
    Error Codes für konsistentes Error Handling

    Namenskonvention: <MODULE>_<NUMBER>
    - 1xxx: Authentication & Authorization
    - 2xxx: Invoices
    - 3xxx: Finance
    - 4xxx: CRM & Customers
    - 5xxx: Projects & Time Tracking
    - 6xxx: Documents & Storage
    - 9xxx: System & Generic Errors
    """

    # =============================================================================
    # 1xxx: Authentication & Authorization
    # =============================================================================
    AUTH_NOT_AUTHENTICATED = "AUTH_1001"
    AUTH_INVALID_TOKEN = "AUTH_1002"
    AUTH_EXPIRED_TOKEN = "AUTH_1003"
    AUTH_INVALID_PAYLOAD = "AUTH_1004"
    AUTH_USER_NOT_FOUND = "AUTH_1005"
    AUTH_USER_INACTIVE = "AUTH_1006"
    AUTH_INVALID_CREDENTIALS = "AUTH_1007"
    AUTH_OIDC_FAILED = "AUTH_1008"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_1009"
    AUTH_PASSWORD_TOO_SHORT = "AUTH_1010"
    AUTH_WRONG_PASSWORD = "AUTH_1011"
    AUTH_NO_PASSWORD_SET = "AUTH_1012"

    # =============================================================================
    # 2xxx: Invoices
    # =============================================================================
    INVOICE_NOT_FOUND = "INVOICE_2001"
    INVOICE_ALREADY_PAID = "INVOICE_2002"
    INVOICE_ALREADY_DELETED = "INVOICE_2003"
    INVOICE_NOT_DELETED = "INVOICE_2004"
    INVOICE_NUMBER_EXISTS = "INVOICE_2005"
    INVOICE_CUSTOMER_NOT_FOUND = "INVOICE_2006"
    INVOICE_PROJECT_NOT_FOUND = "INVOICE_2007"
    INVOICE_GENERATION_FAILED = "INVOICE_2008"
    INVOICE_PDF_FAILED = "INVOICE_2009"
    INVOICE_XML_FAILED = "INVOICE_2010"

    # Payments
    PAYMENT_NOT_FOUND = "PAYMENT_2050"
    PAYMENT_EXCEEDS_AMOUNT = "PAYMENT_2051"

    # =============================================================================
    # 3xxx: Finance
    # =============================================================================
    # Bank Accounts
    BANK_ACCOUNT_NOT_FOUND = "FINANCE_3001"
    BANK_ACCOUNT_NO_IBAN = "FINANCE_3002"

    # Transactions
    TRANSACTION_NOT_FOUND = "FINANCE_3010"
    TRANSACTION_NO_MATCH = "FINANCE_3011"
    TRANSACTION_LINK_INVALID = "FINANCE_3012"

    # Expenses
    EXPENSE_NOT_FOUND = "FINANCE_3020"

    # CSV Import
    CSV_INVALID_FORMAT = "FINANCE_3030"
    CSV_ENCODING_ERROR = "FINANCE_3031"
    CSV_IMPORT_FAILED = "FINANCE_3032"

    # FinTS/HBCI
    FINTS_SYNC_FAILED = "FINANCE_3040"
    FINTS_ACCOUNT_SYNC_FAILED = "FINANCE_3041"

    # PSD2
    PSD2_CONSENT_FAILED = "FINANCE_3050"
    PSD2_AUTH_FAILED = "FINANCE_3051"
    PSD2_SYNC_FAILED = "FINANCE_3052"

    # Stripe
    STRIPE_NOT_CONFIGURED = "FINANCE_3060"
    STRIPE_INVALID_KEY = "FINANCE_3061"
    STRIPE_NO_CONFIG = "FINANCE_3062"
    STRIPE_WEBHOOK_NOT_CONFIGURED = "FINANCE_3063"

    # SevDesk
    SEVDESK_NOT_CONFIGURED = "FINANCE_3070"
    SEVDESK_INVALID_TOKEN = "FINANCE_3071"
    SEVDESK_API_ERROR = "FINANCE_3072"
    SEVDESK_NO_MAPPING = "FINANCE_3073"
    SEVDESK_NO_USER = "FINANCE_3074"

    # =============================================================================
    # 4xxx: CRM & Customers
    # =============================================================================
    CUSTOMER_NOT_FOUND = "CRM_4001"

    # =============================================================================
    # 5xxx: Projects & Products
    # =============================================================================
    PROJECT_NOT_FOUND = "PROJECT_5001"
    PRODUCT_NOT_FOUND = "PRODUCT_5010"
    PRODUCT_SKU_EXISTS = "PRODUCT_5011"

    # =============================================================================
    # 6xxx: Documents & Storage
    # =============================================================================
    DOCUMENT_NOT_FOUND = "DOCUMENT_6001"
    DOCUMENT_NO_FILENAME = "DOCUMENT_6002"

    # =============================================================================
    # 7xxx: Dashboards & Settings
    # =============================================================================
    DASHBOARD_NOT_FOUND = "DASHBOARD_7001"
    DASHBOARD_ALREADY_EXISTS = "DASHBOARD_7002"

    # =============================================================================
    # 8xxx: Reminders & Notifications
    # =============================================================================
    REMINDER_NOT_FOUND = "REMINDER_8001"

    # =============================================================================
    # 9xxx: System & Generic Errors
    # =============================================================================
    SYSTEM_ERROR = "SYSTEM_9000"
    VALIDATION_ERROR = "SYSTEM_9001"
    NOT_FOUND = "SYSTEM_9404"
    EMPLOYEE_NOT_FOUND = "SYSTEM_9010"


@dataclass
class ErrorMessage:
    """Error Message with user-friendly text and hint"""
    message: str
    hint: Optional[str] = None

    def format(self, **kwargs) -> "ErrorMessage":
        """Format message and hint with variables"""
        return ErrorMessage(
            message=self.message.format(**kwargs),
            hint=self.hint.format(**kwargs) if self.hint else None
        )


# =============================================================================
# Error Message Registry
# =============================================================================

ERROR_MESSAGES: dict[str, ErrorMessage] = {
    # -------------------------------------------------------------------------
    # Authentication & Authorization
    # -------------------------------------------------------------------------
    ErrorCode.AUTH_NOT_AUTHENTICATED: ErrorMessage(
        message="Sie sind nicht angemeldet.",
        hint="Bitte melden Sie sich erneut an."
    ),
    ErrorCode.AUTH_INVALID_TOKEN: ErrorMessage(
        message="Ihr Sitzungstoken ist ungültig.",
        hint="Bitte melden Sie sich erneut an."
    ),
    ErrorCode.AUTH_EXPIRED_TOKEN: ErrorMessage(
        message="Ihre Sitzung ist abgelaufen.",
        hint="Bitte melden Sie sich erneut an."
    ),
    ErrorCode.AUTH_INVALID_PAYLOAD: ErrorMessage(
        message="Die Authentifizierungsdaten sind ungültig.",
        hint="Bitte melden Sie sich erneut an."
    ),
    ErrorCode.AUTH_USER_NOT_FOUND: ErrorMessage(
        message="Ihr Benutzerkonto wurde nicht gefunden.",
        hint="Bitte wenden Sie sich an den Administrator."
    ),
    ErrorCode.AUTH_USER_INACTIVE: ErrorMessage(
        message="Ihr Benutzerkonto ist deaktiviert.",
        hint="Bitte wenden Sie sich an den Administrator."
    ),
    ErrorCode.AUTH_INVALID_CREDENTIALS: ErrorMessage(
        message="E-Mail oder Passwort ist falsch.",
        hint="Bitte überprüfen Sie Ihre Eingaben."
    ),
    ErrorCode.AUTH_OIDC_FAILED: ErrorMessage(
        message="Die Anmeldung über den externen Dienst ist fehlgeschlagen.",
        hint="Bitte versuchen Sie es erneut oder melden Sie sich mit E-Mail/Passwort an."
    ),
    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS: ErrorMessage(
        message="Sie haben keine Berechtigung für diese Aktion.",
        hint="Wenden Sie sich an Ihren Administrator, falls Sie Zugriff benötigen."
    ),
    ErrorCode.AUTH_PASSWORD_TOO_SHORT: ErrorMessage(
        message="Das Passwort muss mindestens 8 Zeichen lang sein.",
        hint="Wählen Sie ein längeres Passwort."
    ),
    ErrorCode.AUTH_WRONG_PASSWORD: ErrorMessage(
        message="Das aktuelle Passwort ist falsch.",
        hint="Bitte überprüfen Sie Ihre Eingabe."
    ),
    ErrorCode.AUTH_NO_PASSWORD_SET: ErrorMessage(
        message="Für dieses Konto wurde noch kein Passwort gesetzt.",
        hint="Bitte nutzen Sie die Single Sign-On Anmeldung."
    ),

    # -------------------------------------------------------------------------
    # Invoices
    # -------------------------------------------------------------------------
    ErrorCode.INVOICE_NOT_FOUND: ErrorMessage(
        message="Rechnung '{invoice_id}' wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Rechnungsnummer."
    ),
    ErrorCode.INVOICE_ALREADY_PAID: ErrorMessage(
        message="Diese Rechnung wurde bereits vollständig bezahlt.",
        hint=None
    ),
    ErrorCode.INVOICE_ALREADY_DELETED: ErrorMessage(
        message="Rechnung '{invoice_number}' wurde bereits gelöscht.",
        hint="Nutzen Sie die Wiederherstellen-Funktion, um die Rechnung wiederherzustellen."
    ),
    ErrorCode.INVOICE_NOT_DELETED: ErrorMessage(
        message="Rechnung '{invoice_id}' ist nicht gelöscht und kann nicht wiederhergestellt werden.",
        hint="Nur gelöschte Rechnungen können wiederhergestellt werden."
    ),
    ErrorCode.INVOICE_NUMBER_EXISTS: ErrorMessage(
        message="Rechnungsnummer '{invoice_number}' existiert bereits.",
        hint="Bitte verwenden Sie eine andere Rechnungsnummer."
    ),
    ErrorCode.INVOICE_CUSTOMER_NOT_FOUND: ErrorMessage(
        message="Kunde '{customer_id}' wurde nicht gefunden.",
        hint="Bitte wählen Sie einen existierenden Kunden."
    ),
    ErrorCode.INVOICE_PROJECT_NOT_FOUND: ErrorMessage(
        message="Projekt '{project_id}' wurde nicht gefunden.",
        hint="Bitte wählen Sie ein existierendes Projekt."
    ),
    ErrorCode.INVOICE_GENERATION_FAILED: ErrorMessage(
        message="Die Rechnungsnummer konnte nicht generiert werden.",
        hint="Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
    ),
    ErrorCode.INVOICE_PDF_FAILED: ErrorMessage(
        message="Die PDF-Datei konnte nicht erstellt werden.",
        hint="Bitte versuchen Sie es erneut. Falls der Fehler weiterhin auftritt, kontaktieren Sie den Support."
    ),
    ErrorCode.INVOICE_XML_FAILED: ErrorMessage(
        message="Die XRechnung XML-Datei konnte nicht erstellt werden.",
        hint="Bitte versuchen Sie es erneut. Falls der Fehler weiterhin auftritt, kontaktieren Sie den Support."
    ),

    # Payments
    ErrorCode.PAYMENT_NOT_FOUND: ErrorMessage(
        message="Zahlung '{payment_id}' wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Zahlungs-ID."
    ),
    ErrorCode.PAYMENT_EXCEEDS_AMOUNT: ErrorMessage(
        message="Der Zahlungsbetrag ({amount}€) übersteigt den offenen Betrag ({outstanding}€).",
        hint="Bitte reduzieren Sie den Zahlungsbetrag."
    ),

    # -------------------------------------------------------------------------
    # Finance
    # -------------------------------------------------------------------------
    # Bank Accounts
    ErrorCode.BANK_ACCOUNT_NOT_FOUND: ErrorMessage(
        message="Bankkonto wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Konto-ID."
    ),
    ErrorCode.BANK_ACCOUNT_NO_IBAN: ErrorMessage(
        message="Das Bankkonto hat keine IBAN.",
        hint="Bitte fügen Sie eine IBAN hinzu, um diese Funktion zu nutzen."
    ),

    # Transactions
    ErrorCode.TRANSACTION_NOT_FOUND: ErrorMessage(
        message="Transaktion wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Transaktions-ID."
    ),
    ErrorCode.TRANSACTION_NO_MATCH: ErrorMessage(
        message="Es wurde keine passende Rechnung gefunden (Mindest-Übereinstimmung: 90%).",
        hint="Bitte verknüpfen Sie die Transaktion manuell."
    ),
    ErrorCode.TRANSACTION_LINK_INVALID: ErrorMessage(
        message="Es muss entweder eine Zahlung oder eine Ausgabe verknüpft werden.",
        hint="Bitte wählen Sie entweder payment_id oder expense_id."
    ),

    # Expenses
    ErrorCode.EXPENSE_NOT_FOUND: ErrorMessage(
        message="Ausgabe wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Ausgaben-ID."
    ),

    # CSV Import
    ErrorCode.CSV_INVALID_FORMAT: ErrorMessage(
        message="Nur CSV-Dateien sind erlaubt.",
        hint="Bitte laden Sie eine CSV-Datei hoch."
    ),
    ErrorCode.CSV_ENCODING_ERROR: ErrorMessage(
        message="Die CSV-Datei konnte nicht gelesen werden.",
        hint="Unterstützte Encodings: UTF-8, Latin-1, Windows-1252. Bitte speichern Sie die Datei in einem dieser Formate."
    ),
    ErrorCode.CSV_IMPORT_FAILED: ErrorMessage(
        message="Der CSV-Import ist fehlgeschlagen: {error}",
        hint="Bitte überprüfen Sie das Dateiformat und versuchen Sie es erneut."
    ),

    # FinTS/HBCI
    ErrorCode.FINTS_SYNC_FAILED: ErrorMessage(
        message="FinTS-Synchronisation fehlgeschlagen: {error}",
        hint="Bitte überprüfen Sie Ihre FinTS-Zugangsdaten."
    ),
    ErrorCode.FINTS_ACCOUNT_SYNC_FAILED: ErrorMessage(
        message="Konto-Synchronisation via FinTS fehlgeschlagen: {error}",
        hint="Bitte überprüfen Sie Ihre FinTS-Zugangsdaten."
    ),

    # PSD2
    ErrorCode.PSD2_CONSENT_FAILED: ErrorMessage(
        message="PSD2-Zustimmung konnte nicht initiiert werden: {error}",
        hint="Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
    ),
    ErrorCode.PSD2_AUTH_FAILED: ErrorMessage(
        message="PSD2-Autorisierung fehlgeschlagen: {error}",
        hint="Bitte überprüfen Sie Ihre Bankzugangsdaten."
    ),
    ErrorCode.PSD2_SYNC_FAILED: ErrorMessage(
        message="PSD2-Synchronisation fehlgeschlagen: {error}",
        hint="Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
    ),

    # Stripe
    ErrorCode.STRIPE_NOT_CONFIGURED: ErrorMessage(
        message="Stripe ist nicht konfiguriert.",
        hint="Bitte konfigurieren Sie Stripe in den Einstellungen."
    ),
    ErrorCode.STRIPE_INVALID_KEY: ErrorMessage(
        message="Ungültiges Stripe-API-Key-Format.",
        hint="Publishable Keys beginnen mit 'pk_', Secret Keys mit 'sk_'."
    ),
    ErrorCode.STRIPE_NO_CONFIG: ErrorMessage(
        message="Keine aktive Stripe-Konfiguration gefunden.",
        hint="Bitte konfigurieren Sie Stripe in den Einstellungen."
    ),
    ErrorCode.STRIPE_WEBHOOK_NOT_CONFIGURED: ErrorMessage(
        message="Stripe Webhooks sind nicht konfiguriert.",
        hint="Bitte konfigurieren Sie den Webhook Secret in den Einstellungen."
    ),

    # SevDesk
    ErrorCode.SEVDESK_NOT_CONFIGURED: ErrorMessage(
        message="SevDesk ist nicht konfiguriert.",
        hint="Bitte konfigurieren Sie Ihren SevDesk API-Token in den Einstellungen."
    ),
    ErrorCode.SEVDESK_INVALID_TOKEN: ErrorMessage(
        message="Ungültiger SevDesk API-Token.",
        hint="Bitte überprüfen Sie Ihren API-Token in den SevDesk-Einstellungen."
    ),
    ErrorCode.SEVDESK_API_ERROR: ErrorMessage(
        message="SevDesk API-Fehler: {error}",
        hint="Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
    ),
    ErrorCode.SEVDESK_NO_MAPPING: ErrorMessage(
        message="Keine SevDesk-Verknüpfung gefunden für Rechnung {invoice_id}.",
        hint="Bitte synchronisieren Sie die Rechnung zuerst mit SevDesk."
    ),
    ErrorCode.SEVDESK_NO_USER: ErrorMessage(
        message="Kein SevUser gefunden.",
        hint="Dies ist ein SevDesk API-Konfigurationsproblem. Bitte kontaktieren Sie den Support."
    ),

    # -------------------------------------------------------------------------
    # CRM & Customers
    # -------------------------------------------------------------------------
    ErrorCode.CUSTOMER_NOT_FOUND: ErrorMessage(
        message="Kunde wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Kunden-ID."
    ),

    # -------------------------------------------------------------------------
    # Projects & Products
    # -------------------------------------------------------------------------
    ErrorCode.PROJECT_NOT_FOUND: ErrorMessage(
        message="Projekt wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Projekt-ID."
    ),
    ErrorCode.PRODUCT_NOT_FOUND: ErrorMessage(
        message="Produkt '{product_id}' wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Produkt-ID oder SKU."
    ),
    ErrorCode.PRODUCT_SKU_EXISTS: ErrorMessage(
        message="Produkt mit SKU '{sku}' existiert bereits.",
        hint="Bitte verwenden Sie eine andere SKU."
    ),

    # -------------------------------------------------------------------------
    # Documents & Storage
    # -------------------------------------------------------------------------
    ErrorCode.DOCUMENT_NOT_FOUND: ErrorMessage(
        message="Dokument wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Dokument-ID."
    ),
    ErrorCode.DOCUMENT_NO_FILENAME: ErrorMessage(
        message="Kein Dateiname angegeben.",
        hint="Bitte geben Sie einen Dateinamen an."
    ),

    # -------------------------------------------------------------------------
    # Dashboards & Settings
    # -------------------------------------------------------------------------
    ErrorCode.DASHBOARD_NOT_FOUND: ErrorMessage(
        message="Dashboard wurde nicht gefunden.",
        hint="Bitte erstellen Sie zuerst ein Dashboard."
    ),
    ErrorCode.DASHBOARD_ALREADY_EXISTS: ErrorMessage(
        message="Sie haben bereits ein Dashboard.",
        hint="Nutzen Sie die Update-Funktion, um Ihr Dashboard zu ändern."
    ),

    # -------------------------------------------------------------------------
    # Reminders
    # -------------------------------------------------------------------------
    ErrorCode.REMINDER_NOT_FOUND: ErrorMessage(
        message="Erinnerung wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Erinnerungs-ID."
    ),

    # -------------------------------------------------------------------------
    # System & Generic
    # -------------------------------------------------------------------------
    ErrorCode.SYSTEM_ERROR: ErrorMessage(
        message="Ein unerwarteter Fehler ist aufgetreten.",
        hint="Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
    ),
    ErrorCode.EMPLOYEE_NOT_FOUND: ErrorMessage(
        message="Mitarbeiter wurde nicht gefunden.",
        hint="Bitte überprüfen Sie die Mitarbeiter-ID."
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_error_detail(error_code: str, **kwargs) -> dict[str, Any]:
    """
    Get error detail dictionary for HTTPException

    Args:
        error_code: Error code from ErrorCode class
        **kwargs: Variables for message formatting

    Returns:
        Dictionary with error_code, message, and optional hint

    Example:
        >>> get_error_detail(ErrorCode.INVOICE_NOT_FOUND, invoice_id="RE-2025-001")
        {
            "error_code": "INVOICE_2001",
            "message": "Rechnung 'RE-2025-001' wurde nicht gefunden.",
            "hint": "Bitte überprüfen Sie die Rechnungsnummer."
        }
    """
    error_msg = ERROR_MESSAGES.get(error_code)

    if not error_msg:
        # Fallback für unbekannte Error Codes
        return {
            "error_code": "SYSTEM_9000",
            "message": "Ein unerwarteter Fehler ist aufgetreten.",
            "hint": "Bitte kontaktieren Sie den Support mit Error Code: " + error_code
        }

    # Format message with variables
    formatted = error_msg.format(**kwargs)

    result = {
        "error_code": error_code,
        "message": formatted.message,
    }

    if formatted.hint:
        result["hint"] = formatted.hint

    return result


def get_error_message(error_code: str, **kwargs) -> str:
    """
    Get formatted error message only (for simple use cases)

    Args:
        error_code: Error code from ErrorCode class
        **kwargs: Variables for message formatting

    Returns:
        Formatted error message string
    """
    detail = get_error_detail(error_code, **kwargs)
    return detail["message"]
