# app/modules/backoffice/crm/csv_import.py
"""
CSV-Import für CRM Kunden.

Unterstützt Semikolon- und Komma-getrennte Dateien.
Duplikatserkennung per E-Mail-Adresse.
"""
import csv
import io
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from . import models
from .crud import _generate_customer_number


ALLOWED_COLUMNS = {
    "name", "email", "phone", "city", "zip_code",
    "street", "country", "type", "status", "notes",
}

VALID_TYPES = {"individual", "business", "government", "creator"}
VALID_STATUSES = {"active", "inactive", "lead", "blocked"}


@dataclass
class ImportResult:
    imported: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    preview: list[dict] = field(default_factory=list)


def _detect_delimiter(content: str) -> str:
    """Auto-detect CSV-Delimiter (Semikolon oder Komma)."""
    first_line = content.split("\n")[0] if "\n" in content else content
    semicolons = first_line.count(";")
    commas = first_line.count(",")
    return ";" if semicolons >= commas else ","


def import_customers_csv(
    db: Session,
    file_bytes: bytes,
    skip_duplicates: bool = True,
    dry_run: bool = False,
) -> ImportResult:
    """
    Importiert Kunden aus CSV-Daten.

    Args:
        db: Database Session
        file_bytes: Rohe CSV-Bytes
        skip_duplicates: Duplikate (per E-Mail) überspringen statt fehler
        dry_run: Nur Preview ohne DB-Speicherung

    Returns:
        ImportResult mit Statistiken und optionaler Preview
    """
    result = ImportResult()

    try:
        content = file_bytes.decode("utf-8-sig")  # utf-8-sig entfernt BOM
    except UnicodeDecodeError:
        try:
            content = file_bytes.decode("latin-1")
        except UnicodeDecodeError:
            result.errors.append("Datei-Encoding nicht erkannt. Bitte UTF-8 oder Latin-1 verwenden.")
            return result

    delimiter = _detect_delimiter(content)
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

    if not reader.fieldnames:
        result.errors.append("CSV-Datei hat keine Spaltenköpfe.")
        return result

    # Normalisierte Spaltennamen (lowercase, strip)
    fieldnames = [f.strip().lower() for f in reader.fieldnames]

    if "name" not in fieldnames:
        result.errors.append("Pflichtfeld 'name' fehlt in den CSV-Spalten.")
        return result

    for row_num, raw_row in enumerate(reader, start=2):
        # Normalisiere Keys
        row = {k.strip().lower(): (v.strip() if v else "") for k, v in raw_row.items()}

        name = row.get("name", "").strip()
        if not name:
            result.errors.append(f"Zeile {row_num}: 'name' ist leer – übersprungen.")
            result.skipped += 1
            continue

        email = row.get("email", "").strip() or None

        # Duplikatsprüfung per E-Mail
        if email and skip_duplicates:
            existing = db.query(models.Customer).filter(
                models.Customer.email == email
            ).first()
            if existing:
                result.skipped += 1
                continue

        # Typ und Status validieren / bereinigen
        raw_type = row.get("type", "").strip().lower() or None
        customer_type = raw_type if raw_type in VALID_TYPES else None

        raw_status = row.get("status", "").strip().lower() or None
        customer_status = raw_status if raw_status in VALID_STATUSES else "lead"

        customer_data = {
            "name": name,
            "email": email,
            "phone": row.get("phone") or None,
            "city": row.get("city") or None,
            "zip_code": row.get("zip_code") or None,
            "street": row.get("street") or None,
            "country": row.get("country") or "Deutschland",
            "type": customer_type,
            "status": customer_status,
            "notes": row.get("notes") or None,
        }

        if dry_run:
            result.preview.append(customer_data)
            result.imported += 1
            continue

        # Kundennummer generieren und Kunden anlegen
        customer_number = _generate_customer_number(db)
        customer = models.Customer(
            customer_number=customer_number,
            **customer_data,
        )
        db.add(customer)
        try:
            db.flush()
            result.imported += 1
        except Exception as e:
            db.rollback()
            result.errors.append(f"Zeile {row_num}: Datenbankfehler – {str(e)}")
            result.skipped += 1

    if not dry_run and result.imported > 0:
        db.commit()

    return result
