"""
WorkmateOS Database Configuration — Shim
Re-exportiert alles aus app.core.settings.database damit alle Module
dieselbe Base-Instanz und SQLAlchemy-Registry verwenden.
"""
from app.core.settings.database import (  # noqa: F401
    Base,
    engine,
    SessionLocal,
    get_db,
    generate_uuid,
    DATABASE_URL,
)
