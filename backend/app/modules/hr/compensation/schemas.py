"""
Compensation Schemas
Pydantic Schemas für Gehalt, Boni und Benefits.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================================
# SALARY RECORD SCHEMAS
# ============================================================================

class SalaryRecordCreate(BaseModel):
    amount: Decimal
    currency: str = "EUR"
    effective_date: date
    end_date: Optional[date] = None
    compensation_type: str = "base_salary"
    notes: Optional[str] = None


class SalaryRecordResponse(BaseModel):
    id: UUID
    employee_id: UUID
    amount: Decimal
    currency: str
    effective_date: date
    end_date: Optional[date] = None
    compensation_type: str
    notes: Optional[str] = None
    created_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# BONUS SCHEMAS
# ============================================================================

class BonusCreate(BaseModel):
    amount: Decimal
    currency: str = "EUR"
    bonus_type: str
    description: Optional[str] = None
    payment_date: date


class BonusResponse(BaseModel):
    id: UUID
    employee_id: UUID
    amount: Decimal
    currency: str
    bonus_type: str
    description: Optional[str] = None
    payment_date: date
    created_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# BENEFIT SCHEMAS
# ============================================================================

class BenefitCreate(BaseModel):
    benefit_type: str
    description: Optional[str] = None
    value: Optional[Decimal] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True


class BenefitResponse(BaseModel):
    id: UUID
    employee_id: UUID
    benefit_type: str
    description: Optional[str] = None
    value: Optional[Decimal] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
