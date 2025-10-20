from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Workmate OS Backend"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str | None = None
    ENVIRONMENT: str = "development"
    UPLOAD_DIR: str | None = None
    model_config = SettingsConfigDict(
        env_file="../infra/.env",
        env_file_encoding="utf-8"
    )

settings = Settings()
