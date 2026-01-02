"""
XRechnung/ZUGFeRD Generator für E-Rechnungen

Generiert elektronische Rechnungen gemäß:
- XRechnung (EN16931) - XML-Format für öffentliche Auftraggeber
- ZUGFeRD 2.1 - Hybrid-PDF mit eingebetteter XML

Compliance:
- § 14 UStG (E-Rechnung Pflicht ab 01.01.2025)
- EN16931 (Europäischer Standard)
"""
from decimal import Decimal
from datetime import date
from typing import Optional
import io

from facturx import generate_facturx_from_binary
from lxml import etree

from app.modules.backoffice.invoices import models


# ============================================================================
# COMPANY INFORMATION (Seller/Issuer)
# ============================================================================

COMPANY_NAME = "K.I.T. Solutions"
COMPANY_VAT_ID = "DE350814347"  # Deutsche Umsatzsteuer-ID
COMPANY_TAX_NUMBER = "222/156/30361"  # Steuernummer
COMPANY_STREET = "Dietzstr. 1"
COMPANY_ZIP = "56073"
COMPANY_CITY = "Koblenz"
COMPANY_COUNTRY = "DE"
COMPANY_EMAIL = "info@kit-it-koblenz.de"
COMPANY_PHONE = "+49 162 2654262"
COMPANY_IBAN = "DE94100110012706471170"
COMPANY_BIC = "NTSBDEB1XX"
COMPANY_BANK_NAME = "N26 Bank"


# ============================================================================
# XML GENERATION
# ============================================================================

def generate_xrechnung_xml(invoice: models.Invoice) -> bytes:
    """
    Generiert XRechnung-XML (EN16931 Profil CIUS).

    XRechnung ist der deutsche Standard für E-Rechnungen an öffentliche
    Auftraggeber gemäß § 4a Abs. 2 UStG.

    Args:
        invoice: Invoice Model mit line_items und customer

    Returns:
        XML als bytes (UTF-8 encoded)
    """
    # Build XML structure for XRechnung (EN16931)
    root = etree.Element(
        "{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice",
        nsmap={
            None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        }
    )

    # Customization ID (XRechnung Profil)
    customization = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CustomizationID"
    )
    customization.text = "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"

    # Profile ID
    profile = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ProfileID"
    )
    profile.text = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"

    # Invoice Number
    id_elem = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
    )
    id_elem.text = invoice.invoice_number

    # Issue Date
    issue_date = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueDate"
    )
    issue_date.text = invoice.issued_date.isoformat() if invoice.issued_date else date.today().isoformat()

    # Due Date
    if invoice.due_date:
        due_date_elem = etree.SubElement(
            root,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DueDate"
        )
        due_date_elem.text = invoice.due_date.isoformat()

    # Invoice Type Code (380 = Commercial Invoice)
    type_code = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoiceTypeCode"
    )
    type_code.text = "380"

    # Document Currency Code
    currency = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DocumentCurrencyCode"
    )
    currency.text = "EUR"

    # Buyer Reference (optional)
    if invoice.customer and hasattr(invoice.customer, 'customer_number'):
        buyer_ref = etree.SubElement(
            root,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}BuyerReference"
        )
        buyer_ref.text = str(invoice.customer.customer_number)

    # ========================================================================
    # SELLER (AccountingSupplierParty)
    # ========================================================================
    supplier_party = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingSupplierParty"
    )

    supplier_party_elem = etree.SubElement(
        supplier_party,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Party"
    )

    # Seller Name
    seller_name = etree.SubElement(
        supplier_party_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyName"
    )
    name_elem = etree.SubElement(
        seller_name,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name"
    )
    name_elem.text = COMPANY_NAME

    # Seller Address
    postal_address = etree.SubElement(
        supplier_party_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PostalAddress"
    )
    street_elem = etree.SubElement(
        postal_address,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}StreetName"
    )
    street_elem.text = COMPANY_STREET
    city_elem = etree.SubElement(
        postal_address,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CityName"
    )
    city_elem.text = COMPANY_CITY
    zip_elem = etree.SubElement(
        postal_address,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PostalZone"
    )
    zip_elem.text = COMPANY_ZIP
    country_elem = etree.SubElement(
        postal_address,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Country"
    )
    country_code = etree.SubElement(
        country_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IdentificationCode"
    )
    country_code.text = COMPANY_COUNTRY

    # Seller VAT ID
    party_tax_scheme = etree.SubElement(
        supplier_party_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyTaxScheme"
    )
    company_id = etree.SubElement(
        party_tax_scheme,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CompanyID"
    )
    company_id.text = COMPANY_VAT_ID
    tax_scheme = etree.SubElement(
        party_tax_scheme,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme"
    )
    tax_scheme_id = etree.SubElement(
        tax_scheme,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
    )
    tax_scheme_id.text = "VAT"

    # Seller Legal Entity
    party_legal_entity = etree.SubElement(
        supplier_party_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyLegalEntity"
    )
    legal_name = etree.SubElement(
        party_legal_entity,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RegistrationName"
    )
    legal_name.text = COMPANY_NAME

    # Seller Contact
    contact = etree.SubElement(
        supplier_party_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Contact"
    )
    contact_email = etree.SubElement(
        contact,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ElectronicMail"
    )
    contact_email.text = COMPANY_EMAIL
    contact_phone = etree.SubElement(
        contact,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Telephone"
    )
    contact_phone.text = COMPANY_PHONE

    # ========================================================================
    # BUYER (AccountingCustomerParty)
    # ========================================================================
    customer_party = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingCustomerParty"
    )

    customer_party_elem = etree.SubElement(
        customer_party,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Party"
    )

    # Buyer Name
    buyer_name = etree.SubElement(
        customer_party_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyName"
    )
    buyer_name_elem = etree.SubElement(
        buyer_name,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name"
    )
    buyer_name_elem.text = invoice.customer.name if invoice.customer else "Unknown Customer"

    # Buyer Address
    if invoice.customer:
        buyer_address = etree.SubElement(
            customer_party_elem,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PostalAddress"
        )
        if invoice.customer.street:
            buyer_street = etree.SubElement(
                buyer_address,
                "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}StreetName"
            )
            buyer_street.text = invoice.customer.street
        if invoice.customer.city:
            buyer_city = etree.SubElement(
                buyer_address,
                "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CityName"
            )
            buyer_city.text = invoice.customer.city
        if hasattr(invoice.customer, 'zip_code') and invoice.customer.zip_code:
            buyer_zip = etree.SubElement(
                buyer_address,
                "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PostalZone"
            )
            buyer_zip.text = invoice.customer.zip_code

        buyer_country = etree.SubElement(
            buyer_address,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Country"
        )
        buyer_country_code = etree.SubElement(
            buyer_country,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IdentificationCode"
        )
        buyer_country_code.text = invoice.customer.country if hasattr(invoice.customer, 'country') and invoice.customer.country else "DE"

    # Buyer VAT ID (if available)
    if invoice.customer and invoice.customer.tax_id:
        buyer_tax_scheme = etree.SubElement(
            customer_party_elem,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyTaxScheme"
        )
        buyer_company_id = etree.SubElement(
            buyer_tax_scheme,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CompanyID"
        )
        buyer_company_id.text = invoice.customer.tax_id
        buyer_tax_scheme_elem = etree.SubElement(
            buyer_tax_scheme,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme"
        )
        buyer_tax_scheme_id = etree.SubElement(
            buyer_tax_scheme_elem,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
        )
        buyer_tax_scheme_id.text = "VAT"

    # Buyer Legal Entity
    buyer_legal_entity = etree.SubElement(
        customer_party_elem,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyLegalEntity"
    )
    buyer_legal_name = etree.SubElement(
        buyer_legal_entity,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RegistrationName"
    )
    buyer_legal_name.text = invoice.customer.name if invoice.customer else "Unknown Customer"

    # ========================================================================
    # PAYMENT MEANS
    # ========================================================================
    payment_means = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PaymentMeans"
    )
    payment_means_code = etree.SubElement(
        payment_means,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PaymentMeansCode"
    )
    payment_means_code.text = "58"  # SEPA Credit Transfer

    # Payment Account (IBAN)
    payee_financial_account = etree.SubElement(
        payment_means,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PayeeFinancialAccount"
    )
    iban_elem = etree.SubElement(
        payee_financial_account,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
    )
    iban_elem.text = COMPANY_IBAN

    financial_institution = etree.SubElement(
        payee_financial_account,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}FinancialInstitutionBranch"
    )
    bic_elem = etree.SubElement(
        financial_institution,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
    )
    bic_elem.text = COMPANY_BIC

    # ========================================================================
    # TAX TOTAL
    # ========================================================================
    tax_total = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal"
    )
    tax_amount_elem = etree.SubElement(
        tax_total,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount",
        currencyID="EUR"
    )
    tax_amount_elem.text = f"{invoice.tax_amount:.2f}"

    # Tax Subtotal (grouped by tax rate)
    tax_rates = {}
    for item in invoice.line_items:
        rate = float(item.tax_rate)
        if rate not in tax_rates:
            tax_rates[rate] = {
                'taxable_amount': Decimal("0.00"),
                'tax_amount': Decimal("0.00")
            }
        tax_rates[rate]['taxable_amount'] += item.subtotal_after_discount
        tax_rates[rate]['tax_amount'] += item.tax_amount

    for rate, amounts in tax_rates.items():
        tax_subtotal = etree.SubElement(
            tax_total,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxSubtotal"
        )
        taxable_amount = etree.SubElement(
            tax_subtotal,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxableAmount",
            currencyID="EUR"
        )
        taxable_amount.text = f"{amounts['taxable_amount']:.2f}"

        subtotal_tax_amount = etree.SubElement(
            tax_subtotal,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount",
            currencyID="EUR"
        )
        subtotal_tax_amount.text = f"{amounts['tax_amount']:.2f}"

        tax_category = etree.SubElement(
            tax_subtotal,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxCategory"
        )
        tax_category_id = etree.SubElement(
            tax_category,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
        )
        tax_category_id.text = "S"  # Standard rate

        tax_percent = etree.SubElement(
            tax_category,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Percent"
        )
        tax_percent.text = f"{rate:.2f}"

        tax_scheme_ref = etree.SubElement(
            tax_category,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme"
        )
        tax_scheme_ref_id = etree.SubElement(
            tax_scheme_ref,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
        )
        tax_scheme_ref_id.text = "VAT"

    # ========================================================================
    # LEGAL MONETARY TOTAL
    # ========================================================================
    monetary_total = etree.SubElement(
        root,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}LegalMonetaryTotal"
    )

    line_extension = etree.SubElement(
        monetary_total,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount",
        currencyID="EUR"
    )
    line_extension.text = f"{invoice.subtotal:.2f}"

    tax_exclusive = etree.SubElement(
        monetary_total,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxExclusiveAmount",
        currencyID="EUR"
    )
    tax_exclusive.text = f"{invoice.subtotal:.2f}"

    tax_inclusive = etree.SubElement(
        monetary_total,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxInclusiveAmount",
        currencyID="EUR"
    )
    tax_inclusive.text = f"{invoice.total:.2f}"

    payable_amount = etree.SubElement(
        monetary_total,
        "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PayableAmount",
        currencyID="EUR"
    )
    payable_amount.text = f"{invoice.total:.2f}"

    # ========================================================================
    # INVOICE LINES
    # ========================================================================
    for idx, item in enumerate(invoice.line_items, start=1):
        invoice_line = etree.SubElement(
            root,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}InvoiceLine"
        )

        line_id = etree.SubElement(
            invoice_line,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
        )
        line_id.text = str(idx)

        invoiced_quantity = etree.SubElement(
            invoice_line,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoicedQuantity",
            unitCode="C62"  # Unit: piece
        )
        invoiced_quantity.text = f"{item.quantity:.2f}"

        line_extension_amount = etree.SubElement(
            invoice_line,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount",
            currencyID="EUR"
        )
        line_extension_amount.text = f"{item.subtotal_after_discount:.2f}"

        # Item
        item_elem = etree.SubElement(
            invoice_line,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Item"
        )
        item_name = etree.SubElement(
            item_elem,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name"
        )
        item_name.text = item.description

        # Item Tax Category
        item_tax_category = etree.SubElement(
            item_elem,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}ClassifiedTaxCategory"
        )
        item_tax_id = etree.SubElement(
            item_tax_category,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
        )
        item_tax_id.text = "S"  # Standard rate

        item_tax_percent = etree.SubElement(
            item_tax_category,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Percent"
        )
        item_tax_percent.text = f"{item.tax_rate:.2f}"

        item_tax_scheme = etree.SubElement(
            item_tax_category,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme"
        )
        item_tax_scheme_id = etree.SubElement(
            item_tax_scheme,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"
        )
        item_tax_scheme_id.text = "VAT"

        # Price
        price = etree.SubElement(
            invoice_line,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Price"
        )
        price_amount = etree.SubElement(
            price,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PriceAmount",
            currencyID="EUR"
        )
        price_amount.text = f"{item.unit_price:.2f}"

    # Convert to bytes
    xml_bytes = etree.tostring(
        root,
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8'
    )

    return xml_bytes


def generate_zugferd_pdf(invoice: models.Invoice, pdf_binary: bytes) -> bytes:
    """
    Generiert ZUGFeRD-PDF (Hybrid-PDF mit eingebetteter XML).

    ZUGFeRD = Zentraler User Guide des Forums elektronische Rechnung Deutschland
    Kombiniert menschenlesbares PDF mit maschinenlesbarer XML.

    Args:
        invoice: Invoice Model
        pdf_binary: Bestehendes PDF als bytes

    Returns:
        ZUGFeRD-PDF als bytes (PDF/A-3 mit eingebetteter XML)
    """
    # Generate XRechnung XML
    xml_bytes = generate_xrechnung_xml(invoice)

    # Create ZUGFeRD PDF by embedding XML
    pdf_input = io.BytesIO(pdf_binary)
    zugferd_pdf = generate_facturx_from_binary(
        pdf_input.read(),
        xml_bytes,
        flavor='factur-x',  # ZUGFeRD 2.1 / Factur-X
        level='en16931',    # EN16931 Profile (XRechnung compatible)
        pdf_metadata={
            'title': f'Rechnung {invoice.invoice_number}',
            'author': COMPANY_NAME,
            'subject': f'Rechnung vom {invoice.issued_date}',
            'keywords': 'Rechnung, Invoice, ZUGFeRD, XRechnung',
        }
    )

    return zugferd_pdf
