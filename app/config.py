"""
Application Configuration Module.

Loads environment variables using pydantic-settings.
Supports AWS S3 credentials and Open-Meteo API configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or .env file.
    """
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "weather-data-bucket"
    OPEN_METEO_BASE_URL: str = "https://archive-api.open-meteo.com/v1/archive"

    # Rate Limiting Configuration
    RATE_LIMIT_STORE: str = "10/minute"
    RATE_LIMIT_LIST: str = "60/minute"
    RATE_LIMIT_CONTENT: str = "60/minute"

    # Logging Level
    LOG_LEVEL: str = "INFO"

    # Local fallback storage path when S3 credentials are not configured or available
    LOCAL_STORAGE_DIR: str = "./data/s3_local_mock"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
