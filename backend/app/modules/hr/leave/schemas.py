"""
Leave Management Schemas
Pydantic Schemas für Request/Response Validierung.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


# ============================================================================
# LEAVE POLICY SCHEMAS
# ============================================================================

class LeavePolicyBase(BaseModel):
    """Basis-Schema für Leave Policy"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    vacation_days: int = Field(default=20, ge=0, le=365)
    sick_days: int = Field(default=10, ge=0, le=365)
    parental_days: int = Field(default=0, ge=0, le=365)
    carryover_allowed: bool = True
    max_carryover_days: int = Field(default=5, ge=0, le=50)


class LeavePolicyCreate(LeavePolicyBase):
    """Schema für Erstellung einer Policy"""
    pass


class LeavePolicyUpdate(BaseModel):
    """Schema für Update einer Policy (alle Felder optional)"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    vacation_days: Optional[int] = Field(None, ge=0, le=365)
    sick_days: Optional[int] = Field(None, ge=0, le=365)
    parental_days: Optional[int] = Field(None, ge=0, le=365)
    carryover_allowed: Optional[bool] = None
    max_carryover_days: Optional[int] = Field(None, ge=0, le=50)
    is_active: Optional[bool] = None


class LeavePolicyResponse(LeavePolicyBase):
    """Response Schema für Leave Policy"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeavePolicyListResponse(BaseModel):
    """Paginierte Liste von Policies"""
    items: list[LeavePolicyResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# LEAVE BALANCE SCHEMAS
# ============================================================================

class LeaveBalanceBase(BaseModel):
    """Basis-Schema für Leave Balance"""
    year: int = Field(..., ge=2020, le=2100)
    vacation_total: Decimal = Field(default=Decimal("0.00"), ge=0)
    vacation_used: Decimal = Field(default=Decimal("0.00"), ge=0)
    vacation_remaining: Decimal = Field(default=Decimal("0.00"), ge=0)
    sick_total: Decimal = Field(default=Decimal("0.00"), ge=0)
    sick_used: Decimal = Field(default=Decimal("0.00"), ge=0)
    other_total: Decimal = Field(default=Decimal("0.00"), ge=0)
    other_used: Decimal = Field(default=Decimal("0.00"), ge=0)


class LeaveBalanceCreate(BaseModel):
    """Schema für Erstellung eines Balance"""
    employee_id: UUID
    year: int = Field(..., ge=2020, le=2100)
    policy_id: Optional[UUID] = None
    vacation_total: Decimal = Field(default=Decimal("20.00"), ge=0)
    sick_total: Decimal = Field(default=Decimal("10.00"), ge=0)
    other_total: Decimal = Field(default=Decimal("0.00"), ge=0)


class LeaveBalanceUpdate(BaseModel):
    """Schema für Update eines Balance"""
    vacation_total: Optional[Decimal] = Field(None, ge=0)
    sick_total: Optional[Decimal] = Field(None, ge=0)
    other_total: Optional[Decimal] = Field(None, ge=0)
    policy_id: Optional[UUID] = None


class LeaveBalanceResponse(LeaveBalanceBase):
    """Response Schema für Leave Balance"""
    id: UUID
    employee_id: UUID
    policy_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeaveBalanceListResponse(BaseModel):
    """Paginierte Liste von Balances"""
    items: list[LeaveBalanceResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# LEAVE REQUEST SCHEMAS
# ============================================================================

class LeaveRequestBase(BaseModel):
    """Basis-Schema für Leave Request"""
    leave_type: str = Field(..., description="Type of leave")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    total_days: Decimal = Field(..., gt=0, description="Total days")
    half_day_start: bool = Field(default=False)
    half_day_end: bool = Field(default=False)
    reason: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        """Validiert dass end_date nach start_date liegt"""
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after or equal to start_date")
        return v

    @field_validator("leave_type")
    @classmethod
    def validate_leave_type(cls, v):
        """Validiert Leave Type"""
        valid_types = ["vacation", "sick", "unpaid", "parental", "bereavement", "training", "remote", "other"]
        if v not in valid_types:
            raise ValueError(f"leave_type must be one of {valid_types}")
        return v


class LeaveRequestCreate(LeaveRequestBase):
    """Schema für Erstellung eines Leave Request"""
    employee_id: Optional[UUID] = None  # Optional wenn HR für Mitarbeiter erstellt
    attachment_path: Optional[str] = None


class LeaveRequestUpdate(BaseModel):
    """Schema für Update eines Leave Request"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_days: Optional[Decimal] = Field(None, gt=0)
    half_day_start: Optional[bool] = None
    half_day_end: Optional[bool] = None
    reason: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = None
    attachment_path: Optional[str] = None


class LeaveRequestApprove(BaseModel):
    """Schema für Genehmigung"""
    notes: Optional[str] = None


class LeaveRequestReject(BaseModel):
    """Schema für Ablehnung"""
    rejection_reason: str = Field(..., min_length=1, max_length=1000)


class LeaveRequestResponse(LeaveRequestBase):
    """Response Schema für Leave Request"""
    id: UUID
    employee_id: UUID
    status: str
    approved_by_id: Optional[UUID] = None
    approved_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    attachment_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeaveRequestListResponse(BaseModel):
    """Paginierte Liste von Leave Requests"""
    items: list[LeaveRequestResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# ABSENCE CALENDAR SCHEMAS
# ============================================================================

class AbsenceCalendarResponse(BaseModel):
    """Response Schema für Absence Calendar Entry"""
    id: UUID
    employee_id: UUID
    leave_request_id: UUID
    absence_date: date
    is_full_day: bool
    leave_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AbsenceCalendarListResponse(BaseModel):
    """Paginierte Liste von Absence Calendar Entries"""
    items: list[AbsenceCalendarResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# SUMMARY SCHEMAS
# ============================================================================

class LeaveBalanceSummary(BaseModel):
    """Summary für Mitarbeiter-Self-Service"""
    year: int
    vacation_total: Decimal
    vacation_used: Decimal
    vacation_remaining: Decimal
    pending_vacation_days: Decimal = Field(default=Decimal("0.00"))
    sick_used: Decimal


class TeamAbsenceSummary(BaseModel):
    """Team-Abwesenheitsübersicht für einen Tag"""
    date: date
    total_absent: int
    absent_employees: list[dict]  # {employee_id, name, leave_type}
