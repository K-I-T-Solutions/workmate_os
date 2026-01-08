"""
HR Module Utilities
Shared utility functions für das HR-Modul.
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import List


def calculate_business_days(start_date: date, end_date: date, half_day_start: bool = False, half_day_end: bool = False) -> Decimal:
    """
    Berechnet die Anzahl der Arbeitstage zwischen zwei Daten (Montag-Freitag).

    Args:
        start_date: Startdatum
        end_date: Enddatum
        half_day_start: Halber Tag am Start
        half_day_end: Halber Tag am Ende

    Returns:
        Anzahl der Arbeitstage als Decimal
    """
    if start_date > end_date:
        return Decimal("0.00")

    days = Decimal("0.00")
    current_date = start_date

    while current_date <= end_date:
        # Montag = 0, Sonntag = 6
        if current_date.weekday() < 5:  # Montag bis Freitag
            if current_date == start_date and half_day_start:
                days += Decimal("0.50")
            elif current_date == end_date and half_day_end:
                days += Decimal("0.50")
            else:
                days += Decimal("1.00")

        current_date += timedelta(days=1)

    return days


def get_date_ranges_between(start_date: date, end_date: date) -> List[date]:
    """
    Gibt eine Liste aller Daten zwischen Start und End zurück.

    Args:
        start_date: Startdatum
        end_date: Enddatum

    Returns:
        Liste aller Daten
    """
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def calculate_leave_balance_remaining(total: Decimal, used: Decimal) -> Decimal:
    """
    Berechnet verbleibende Urlaubstage.

    Args:
        total: Gesamte verfügbare Tage
        used: Bereits genutzte Tage

    Returns:
        Verbleibende Tage
    """
    return max(Decimal("0.00"), total - used)


def is_date_in_range(check_date: date, start_date: date, end_date: date) -> bool:
    """
    Prüft ob ein Datum innerhalb eines Bereichs liegt.

    Args:
        check_date: Zu prüfendes Datum
        start_date: Start des Bereichs
        end_date: Ende des Bereichs

    Returns:
        True wenn Datum im Bereich liegt
    """
    return start_date <= check_date <= end_date


def format_employee_code(prefix: str, number: int, digits: int = 4) -> str:
    """
    Formatiert einen Mitarbeiter-Code.

    Args:
        prefix: Präfix (z.B. "KIT")
        number: Nummer
        digits: Anzahl der Stellen (mit führenden Nullen)

    Returns:
        Formatierter Code (z.B. "KIT-0001")
    """
    return f"{prefix}-{number:0{digits}d}"


def calculate_years_of_experience(start_date: date, end_date: date | None = None) -> int:
    """
    Berechnet Jahre an Erfahrung.

    Args:
        start_date: Startdatum
        end_date: Enddatum (oder heute wenn None)

    Returns:
        Anzahl der Jahre
    """
    if end_date is None:
        end_date = date.today()

    years = end_date.year - start_date.year

    # Wenn Geburtstag noch nicht war dieses Jahr, ein Jahr abziehen
    if (end_date.month, end_date.day) < (start_date.month, start_date.day):
        years -= 1

    return max(0, years)


def calculate_days_until(target_date: date) -> int:
    """
    Berechnet Tage bis zu einem Zieldatum.

    Args:
        target_date: Zieldatum

    Returns:
        Anzahl der Tage (negativ wenn in der Vergangenheit)
    """
    delta = target_date - date.today()
    return delta.days


def is_expiring_soon(expiry_date: date, warning_days: int = 30) -> bool:
    """
    Prüft ob ein Ablaufdatum bald erreicht ist.

    Args:
        expiry_date: Ablaufdatum
        warning_days: Warnung X Tage vorher

    Returns:
        True wenn Ablauf bald
    """
    days_until = calculate_days_until(expiry_date)
    return 0 < days_until <= warning_days
