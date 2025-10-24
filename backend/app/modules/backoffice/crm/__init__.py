# app/modules/backoffice/crm/__init__.py
"""
CRM Module für WorkmateOS.

Customer Relationship Management mit Kunden- und Kontaktverwaltung.
"""
from . import models, schemas, crud, routes

__all__ = ["models", "schemas", "crud", "routes"]