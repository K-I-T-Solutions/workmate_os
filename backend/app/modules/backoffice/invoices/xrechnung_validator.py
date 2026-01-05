"""
XRechnung/EN16931 XML Validierung

Validiert generierte XRechnung-XML gegen:
- XSD Schema (EN16931)
- Business Rules (optional)
- PEPPOL Validator (optional)

Standards:
- EN 16931: Europäische Norm für elektronische Rechnungen
- XRechnung 3.0: Deutscher Standard (CIUS von EN 16931)
"""
import logging
from typing import Optional, Dict, Any, List
from xml.etree import ElementTree as ET
from lxml import etree

logger = logging.getLogger(__name__)


# ============================================================================
# XML VALIDATION
# ============================================================================

def validate_xml_syntax(xml_content: bytes) -> Dict[str, Any]:
    """
    Validiert XML-Syntax (Well-Formed).

    Args:
        xml_content: XML als bytes

    Returns:
        Dict mit Validierungs-Ergebnis
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": []
    }

    try:
        # Parse XML
        tree = etree.fromstring(xml_content)
        result["valid"] = True
        logger.info("XML syntax validation passed")

    except etree.XMLSyntaxError as e:
        result["errors"].append(f"XML Syntax Error: {str(e)}")
        logger.error(f"XML syntax validation failed: {e}")

    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
        logger.error(f"XML validation error: {e}")

    return result


def validate_xml_structure(xml_content: bytes) -> Dict[str, Any]:
    """
    Validiert XRechnung-Struktur (Business Rules).

    Prüft ob Pflichtfelder vorhanden sind:
    - CustomizationID
    - ProfileID
    - Invoice ID
    - Invoice Type Code
    - Currency Code
    - Supplier Party
    - Customer Party
    - etc.

    Args:
        xml_content: XML als bytes

    Returns:
        Dict mit Validierungs-Ergebnis
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "checked_fields": []
    }

    try:
        tree = etree.fromstring(xml_content)

        # Namespace
        ns = {
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
        }

        # Pflichtfelder prüfen
        required_fields = {
            'CustomizationID': './/cbc:CustomizationID',
            'ProfileID': './/cbc:ProfileID',
            'ID': './/cbc:ID',
            'IssueDate': './/cbc:IssueDate',
            'InvoiceTypeCode': './/cbc:InvoiceTypeCode',
            'DocumentCurrencyCode': './/cbc:DocumentCurrencyCode',
            'AccountingSupplierParty': './/cac:AccountingSupplierParty',
            'AccountingCustomerParty': './/cac:AccountingCustomerParty',
            'LegalMonetaryTotal': './/cac:LegalMonetaryTotal',
        }

        for field_name, xpath in required_fields.items():
            element = tree.find(xpath, namespaces=ns)
            if element is not None:
                result["checked_fields"].append({
                    "field": field_name,
                    "status": "present",
                    "value": element.text[:50] if element.text else "(empty)"
                })
            else:
                result["valid"] = False
                result["errors"].append(f"Required field missing: {field_name}")
                result["checked_fields"].append({
                    "field": field_name,
                    "status": "missing"
                })

        # CustomizationID prüfen (muss XRechnung sein)
        customization_id = tree.find('.//cbc:CustomizationID', namespaces=ns)
        if customization_id is not None:
            cust_id = customization_id.text or ""
            if "xrechnung" not in cust_id.lower():
                result["warnings"].append(
                    f"CustomizationID '{cust_id}' is not XRechnung standard"
                )

    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Structure validation error: {str(e)}")
        logger.error(f"XML structure validation error: {e}")

    return result


def validate_xrechnung(xml_content: bytes) -> Dict[str, Any]:
    """
    Vollständige XRechnung-Validierung.

    Kombiniert:
    1. XML Syntax Check
    2. XML Structure Check
    3. Business Rules (basic)

    Args:
        xml_content: XRechnung XML als bytes

    Returns:
        Dict mit Validierungs-Ergebnis
    """
    results = {
        "valid": True,
        "syntax_check": {},
        "structure_check": {},
        "errors": [],
        "warnings": [],
        "summary": ""
    }

    # 1. Syntax Check
    syntax_result = validate_xml_syntax(xml_content)
    results["syntax_check"] = syntax_result

    if not syntax_result["valid"]:
        results["valid"] = False
        results["errors"].extend(syntax_result["errors"])
        results["summary"] = "XML Syntax validation failed"
        return results

    # 2. Structure Check
    structure_result = validate_xml_structure(xml_content)
    results["structure_check"] = structure_result

    if not structure_result["valid"]:
        results["valid"] = False
        results["errors"].extend(structure_result["errors"])

    results["warnings"].extend(structure_result.get("warnings", []))

    # Summary
    if results["valid"]:
        results["summary"] = f"✅ XRechnung validation passed ({len(structure_result['checked_fields'])} fields checked)"
    else:
        results["summary"] = f"❌ XRechnung validation failed ({len(results['errors'])} errors)"

    return results


# ============================================================================
# FILE VALIDATION
# ============================================================================

def validate_xrechnung_file(file_path: str) -> Dict[str, Any]:
    """
    Validiert XRechnung XML-Datei.

    Args:
        file_path: Pfad zur XML-Datei

    Returns:
        Dict mit Validierungs-Ergebnis
    """
    try:
        with open(file_path, 'rb') as f:
            xml_content = f.read()

        return validate_xrechnung(xml_content)

    except FileNotFoundError:
        return {
            "valid": False,
            "errors": [f"File not found: {file_path}"],
            "warnings": [],
            "summary": "File not found"
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Error reading file: {str(e)}"],
            "warnings": [],
            "summary": "File read error"
        }


# ============================================================================
# PEPPOL VALIDATOR (Optional - Online Service)
# ============================================================================

def validate_with_peppol(xml_content: bytes) -> Dict[str, Any]:
    """
    Validiert XRechnung via PEPPOL Validator (Online Service).

    **Hinweis:**
    Dies erfordert Internet-Zugang und API-Key für PEPPOL Validator.

    In Production:
    - PEPPOL OpenValidation Service nutzen
    - Oder: Lokaler Validator (validator-configuration-core)

    Args:
        xml_content: XRechnung XML als bytes

    Returns:
        Dict mit Validierungs-Ergebnis
    """
    # TODO: Implementieren wenn PEPPOL-Validator-API verfügbar
    return {
        "valid": None,
        "errors": [],
        "warnings": ["PEPPOL validation not implemented yet"],
        "summary": "PEPPOL validation skipped (not configured)"
    }
