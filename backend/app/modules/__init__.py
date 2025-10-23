"""
WorkmateOS - Central Models Import
Importiert alle Models für Alembic und andere Module

USAGE:
    # In alembic/env.py oder anderen Modulen:
    from app.models import Employee, Department, Role, Document
    
    # Oder alle auf einmal (für Alembic):
    import app.models  # Registriert alle Models in Base.metadata
"""

# Core / Employees Module
from app.modules.employees.models import (
    Department,
    Role,
    Employee,
)

# Documents Module
from app.modules.documents.models import Document

# Reminders Module
from app.modules.reminders.models import Reminder

# Dashboards Module
from app.modules.dashboards.models import Dashboard

# System / Infrastructure
from app.modules.system.models import InfraService


# Explicit exports für besseres Type-Checking
__all__ = [
    "Department",
    "Role", 
    "Employee",
    "Document",
    "Reminder",
    "Dashboard",
    "InfraService",
]