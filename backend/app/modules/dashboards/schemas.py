"""
WorkmateOS - Dashboards Schemas
Pydantic models for user dashboard configuration
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID


class DashboardBase(BaseModel):
    """Base dashboard fields"""
    widgets_json: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Widget configuration"
    )
    layout_json: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Layout configuration"
    )
    theme: str = Field(default="catppuccin-frappe")


class DashboardCreate(DashboardBase):
    """Create new dashboard"""
    owner_id: UUID


class DashboardUpdate(BaseModel):
    """Update existing dashboard"""
    widgets_json: Optional[dict[str, Any]] = None
    layout_json: Optional[dict[str, Any]] = None
    theme: Optional[str] = None


class DashboardResponse(DashboardBase):
    """Dashboard response with all fields"""
    id: UUID
    owner_id: UUID
    last_accessed: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DashboardListResponse(BaseModel):
    """List of dashboards"""
    total: int
    dashboards: list[DashboardResponse]