"""
Admin Models - Database models for Admin module
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.mixins import UUIDMixin


class SystemSettings(Base, UUIDMixin):
    """
    Global System Settings (Singleton Pattern).

    Only one record should exist in this table.
    Contains company information, localization settings, and system configuration.
    """
    __tablename__ = "system_settings"

    # ========================================================================
    # Company Information
    # ========================================================================
    company_name = Column(String(200), nullable=False, default="WorkmateOS")
    company_legal = Column(String(50), default="")
    tax_number = Column(String(50), default="")
    registration_number = Column(String(50), default="")
    address_street = Column(String(200), default="")
    address_zip = Column(String(10), default="")
    address_city = Column(String(100), default="")
    address_country = Column(String(100), default="Deutschland")
    company_email = Column(String(100), default="")
    company_phone = Column(String(50), default="")
    company_website = Column(String(200), default="")

    # ========================================================================
    # Localization
    # ========================================================================
    default_timezone = Column(String(50), nullable=False, default="Europe/Berlin")
    default_language = Column(String(10), nullable=False, default="de")
    default_currency = Column(String(10), nullable=False, default="EUR")
    date_format = Column(String(20), nullable=False, default="DD.MM.YYYY")

    # ========================================================================
    # Working Hours
    # ========================================================================
    working_hours_per_day = Column(Integer, nullable=False, default=8)
    working_days_per_week = Column(Integer, nullable=False, default=5)
    vacation_days_per_year = Column(Integer, nullable=False, default=30)
    weekend_saturday = Column(Boolean, nullable=False, default=True)
    weekend_sunday = Column(Boolean, nullable=False, default=True)

    # ========================================================================
    # System Configuration
    # ========================================================================
    maintenance_mode = Column(Boolean, nullable=False, default=False)
    allow_registration = Column(Boolean, nullable=False, default=False)
    require_email_verification = Column(Boolean, nullable=False, default=True)

    # ========================================================================
    # Timestamps
    # ========================================================================
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
