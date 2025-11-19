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

from app.modules.backoffice.crm.models import Customer, Contact
from app.modules.backoffice.projects.models import Project
from app.modules.backoffice.invoices.models import Invoice, InvoiceLineItem, Payment
from app.modules.backoffice.finance.models import Expense
from app.modules.backoffice.chat.models import ChatMessage
from app.modules.backoffice.time_tracking.models import TimeEntry



# Explicit exports für besseres Type-Checking
__all__ = [
    "Department",
    "Role", 
    "Employee",
    "Document",
    "Reminder",
    "Dashboard",
    "InfraService",
    "Customer",
    "Contact",
    "Project",
    "Invoice",
    "InvoiceLineItem",
    "Payment",
    "Expense",
    "ChatMessage",
    "TimeEntry",
    
]