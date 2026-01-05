"""
Admin Schemas - Pydantic models for Admin APIs
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class SystemSettingsResponse(BaseModel):
    """System Settings Response."""
    id: UUID

    # Company Information
    company_name: str
    company_legal: Optional[str] = ""
    tax_number: Optional[str] = ""
    registration_number: Optional[str] = ""
    address_street: Optional[str] = ""
    address_zip: Optional[str] = ""
    address_city: Optional[str] = ""
    address_country: str = "Deutschland"
    company_email: Optional[str] = ""
    company_phone: Optional[str] = ""
    company_website: Optional[str] = ""

    # Localization
    default_timezone: str = "Europe/Berlin"
    default_language: str = "de"
    default_currency: str = "EUR"
    date_format: str = "DD.MM.YYYY"

    # Working Hours
    working_hours_per_day: int = Field(ge=1, le=24, default=8)
    working_days_per_week: int = Field(ge=1, le=7, default=5)
    vacation_days_per_year: int = Field(ge=0, le=365, default=30)
    weekend_saturday: bool = True
    weekend_sunday: bool = True

    # System Configuration
    maintenance_mode: bool = False
    allow_registration: bool = False
    require_email_verification: bool = True

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemSettingsUpdate(BaseModel):
    """
    System Settings Update Schema.

    All fields are optional. Only provided fields will be updated.
    """
    # Company Information
    company_name: Optional[str] = Field(None, max_length=200)
    company_legal: Optional[str] = Field(None, max_length=50)
    tax_number: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)
    address_street: Optional[str] = Field(None, max_length=200)
    address_zip: Optional[str] = Field(None, max_length=10)
    address_city: Optional[str] = Field(None, max_length=100)
    address_country: Optional[str] = Field(None, max_length=100)
    company_email: Optional[str] = Field(None, max_length=100)
    company_phone: Optional[str] = Field(None, max_length=50)
    company_website: Optional[str] = Field(None, max_length=200)

    # Localization
    default_timezone: Optional[str] = Field(None, max_length=50)
    default_language: Optional[str] = Field(None, max_length=10)
    default_currency: Optional[str] = Field(None, max_length=10)
    date_format: Optional[str] = Field(None, max_length=20)

    # Working Hours
    working_hours_per_day: Optional[int] = Field(None, ge=1, le=24)
    working_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    vacation_days_per_year: Optional[int] = Field(None, ge=0, le=365)
    weekend_saturday: Optional[bool] = None
    weekend_sunday: Optional[bool] = None

    # System Configuration
    maintenance_mode: Optional[bool] = None
    allow_registration: Optional[bool] = None
    require_email_verification: Optional[bool] = None

    @field_validator('company_email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @field_validator('company_website')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @field_validator('default_timezone')
    @classmethod
    def validate_timezone(cls, v):
        """Validate timezone."""
        if v:
            # Basic validation - could be extended with pytz
            valid_timezones = [
                "Europe/Berlin", "Europe/London", "Europe/Paris",
                "America/New_York", "America/Los_Angeles", "Asia/Tokyo",
                "UTC"
            ]
            if v not in valid_timezones:
                # Just a warning, don't fail
                pass
        return v

    @field_validator('default_language')
    @classmethod
    def validate_language(cls, v):
        """Validate language code."""
        if v:
            valid_languages = ["de", "en", "fr", "es", "it"]
            if v not in valid_languages:
                raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v

    @field_validator('default_currency')
    @classmethod
    def validate_currency(cls, v):
        """Validate currency code."""
        if v:
            valid_currencies = ["EUR", "USD", "GBP", "CHF", "JPY"]
            if v not in valid_currencies:
                raise ValueError(f'Currency must be one of: {", ".join(valid_currencies)}')
        return v
