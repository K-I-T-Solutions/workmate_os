"""
System Settings API Routes

Provides endpoints to manage global system settings.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth.permissions import require_permissions
from app.modules.admin import schemas, service

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("", response_model=schemas.SystemSettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    current_user = Depends(require_permissions("admin.settings.*", "admin.*", "*"))
):
    """
    Get system settings.

    Returns the current system settings. If no settings exist yet,
    default settings will be created and returned.

    **Permissions required:** admin.settings.*, admin.*, or *

    **Returns:** SystemSettings object with all configuration
    """
    try:
        settings = await service.get_or_create_settings(db)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.put("", response_model=schemas.SystemSettingsResponse)
async def update_settings(
    settings_update: schemas.SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permissions("admin.settings.*", "admin.*", "*"))
):
    """
    Update system settings.

    All fields are optional. Only provided fields will be updated (PATCH semantics).

    **Permissions required:** admin.settings.*, admin.*, or *

    **Request Body:**
    - company_name: Company name
    - company_legal: Legal form (GmbH, AG, etc.)
    - tax_number: Tax number
    - registration_number: Commercial register number
    - address_*: Company address fields
    - company_email: Company email
    - company_phone: Company phone
    - company_website: Company website
    - default_timezone: Default timezone (Europe/Berlin, UTC, etc.)
    - default_language: Default language code (de, en, fr, etc.)
    - default_currency: Default currency (EUR, USD, GBP, etc.)
    - date_format: Date format (DD.MM.YYYY, MM/DD/YYYY, etc.)
    - working_hours_per_day: Working hours per day (1-24)
    - working_days_per_week: Working days per week (1-7)
    - vacation_days_per_year: Vacation days per year (0-365)
    - weekend_saturday: Saturday is weekend (boolean)
    - weekend_sunday: Sunday is weekend (boolean)
    - maintenance_mode: Maintenance mode active (boolean)
    - allow_registration: Allow user self-registration (boolean)
    - require_email_verification: Require email verification (boolean)

    **Returns:** Updated SystemSettings object
    """
    try:
        # Convert Pydantic model to dict, exclude unset fields
        update_data = settings_update.model_dump(exclude_unset=True)

        settings = await service.update_settings(db, update_data)
        return settings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
