"""
WorkmateOS Core Configuration
Lädt Einstellungen aus ../infra/.env (Docker Compose)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # App Info
    APP_NAME: str = "Workmate OS Backend"
    APP_VERSION: str = "3.0.0"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://workmate:workmate@central_postgres:5432/workmate_os"

    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    ASSETS_DIR: str = os.getenv("ASSETS_DIR", "/app/assets")

    # Storage Backend Configuration
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "nextcloud")  # "local" or "nextcloud" or "s3"
    INVOICE_STORAGE_PATH: str = os.getenv("INVOICE_STORAGE_PATH", "workmate/invoices")

    # Nextcloud
    NEXTCLOUD_URL: str = os.getenv("NEXTCLOUD_URL", "https://cloud.kit-it-koblenz.de/remote.php/dav/files/workmate-storage")
    NEXTCLOUD_USER: str = os.getenv("NEXTCLOUD_USER","workmate-storage")
    NEXTCLOUD_PASSWORD: str = os.getenv("NEXTCLOUD_PASSWORD","workmate123!")
    NEXTCLOUD_BASE_PATH: str = os.getenv("NEXTCLOUD_BASE_PATH","")

    # Keycloak OIDC Configuration
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "https://login.intern.phudevelopement.xyz")
    KEYCLOAK_INTERNAL_URL: str = os.getenv("KEYCLOAK_INTERNAL_URL", "http://keycloak:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "kit")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "workmate-backend")

    @property
    def KEYCLOAK_ISSUER(self) -> str:
        """External issuer URL (must match 'iss' claim in tokens)"""
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}"

    @property
    def KEYCLOAK_JWKS_URI(self) -> str:
        """Internal JWKS URL (backend-to-keycloak via Docker network)"""
        return f"{self.KEYCLOAK_INTERNAL_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"

    @property
    def KEYCLOAK_USERINFO_URI(self) -> str:
        """Internal userinfo URL (backend-to-keycloak via Docker network)"""
        return f"{self.KEYCLOAK_INTERNAL_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "CHANGE-THIS-IN-PRODUCTION-USE-RANDOM-256BIT-KEY"  # Fallback for dev
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # PSD2/Banking Configuration
    PSD2_ENVIRONMENT: str = os.getenv("PSD2_ENVIRONMENT", "sandbox")  # "sandbox" or "production"

    model_config = SettingsConfigDict(
        env_file=".env",  # In Docker: /app/.env
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
