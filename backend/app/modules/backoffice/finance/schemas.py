# app/modules/backoffice/finance/schemas.py
from __future__ import annotations

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import ExpenseCategory


class ExpenseBase(BaseModel):
    """Gemeinsame Felder für Expense-Create/Update."""
    title: str = Field(
        description="Bezeichnung der kosten"
    )
    category: ExpenseCategory = Field(
        description="Ausgabenkategorie (travel, material, software, etc.)"
    )
    amount: Decimal = Field(
        gt=0,
        description="Ausgabenbetrag"
    )
    description: str = Field(
        description="Beschreibung der Ausgabe"
    )
    receipt_path: Optional[str] = Field(
        default=None,
        description="Pfad zum Beleg/Quittung (PDF, Bild)"
    )
    note: Optional[str] = Field(
        default=None,
        description="Zusätzliche Notizen"
    )
    is_billable: bool = Field(
        default=True,
        description="Kann an Kunden weiterberechnet werden"
    )
    project_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional zugehöriges Projekt"
    )
    invoice_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional zugehörige Rechnung (wenn bereits abgerechnet)"
    )


class ExpenseCreate(ExpenseBase):
    """Schema zum Anlegen einer neuen Ausgabe."""
    pass


class ExpenseUpdate(BaseModel):
    """Schema für partielle Updates (PATCH). Alle Felder optional."""
    title : Optional[str] = ""
    category: Optional[ExpenseCategory] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    description: Optional[str] = None
    receipt_path: Optional[str] = None
    note: Optional[str] = None
    is_billable: Optional[bool] = None
    project_id: Optional[uuid.UUID] = None
    invoice_id: Optional[uuid.UUID] = None


class ExpenseRead(BaseModel):
    """Ausgabe einer Expense Richtung API-Consumer."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title:str
    category: ExpenseCategory
    amount: Decimal
    description: str
    receipt_path: Optional[str]
    note: Optional[str]
    is_billable: bool

    project_id: Optional[uuid.UUID]
    invoice_id: Optional[uuid.UUID]

    created_at: datetime
    updated_at: datetime

    @property
    def is_invoiced(self) -> bool:
        return self.invoice_id is not None


class ExpenseListResponse(BaseModel):
    """Standard-Liste mit Paging-Option (für später vorbereitet)."""
    items: list[ExpenseRead]
    total: int


class ExpenseKpiRequest(BaseModel):
    """Optional – falls du später einen POST-KPI-Endpoint willst."""
    month: Optional[str] = Field(
        default=None,
        description="Optional: Monat im Format YYYY-MM"
    )
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    project_id: Optional[uuid.UUID] = None
    category: Optional[ExpenseCategory] = None


class ExpenseKpiResponse(BaseModel):
    """KPI Antwort – Summe und Verteilung nach Kategorie."""
    total: Decimal
    by_category: dict[ExpenseCategory, Decimal]
