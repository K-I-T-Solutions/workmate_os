"""
WorkmateOS Database Configuration
"""
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from app.core.config import settings


# Get DATABASE_URL from settings (Pydantic lädt .env automatisch)
DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "development" else False,
    pool_pre_ping=True,  # Verify connections before using
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Helper functions
def generate_uuid():
    """Generate UUID for primary keys"""
    return uuid.uuid4()


def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
