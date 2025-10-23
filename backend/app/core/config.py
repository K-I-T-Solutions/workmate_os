"""
WorkmateOS Core Configuration
Lädt Einstellungen aus ../infra/.env (Docker Compose)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # App Info
    APP_NAME: str = "Workmate OS Backend"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://workmate:workmate@central_postgres:5432/workmate_os"
    
    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    
    # Keycloak (optional, für später)
    KEYCLOAK_URL: str | None = None
    KEYCLOAK_REALM: str = "kit"
    KEYCLOAK_CLIENT_ID: str = "workmate-backend"
    
    model_config = SettingsConfigDict(
        env_file="../infra/.env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()