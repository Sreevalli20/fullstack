"""
Application Configuration Module.

Loads environment variables using pydantic-settings.
Supports Google Cloud Storage and local storage configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or .env file.
    """
    # Storage Configuration
    STORAGE_TYPE: str = "local"  # Options: "local" or "gcs"
    GCS_BUCKET: str = "weather-data-bucket"
    LOCAL_STORAGE_DIR: str = "./data"
    
    # Open-Meteo Historical Weather API Base URL
    OPEN_METEO_BASE_URL: str = "https://archive-api.open-meteo.com/v1/archive"

    # Rate Limiting Configuration
    RATE_LIMIT_STORE: str = "10/minute"
    RATE_LIMIT_LIST: str = "60/minute"
    RATE_LIMIT_CONTENT: str = "60/minute"

    # Logging Level
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
