"""
Core configuration module for GeoSpark

This file gracefully degrades if optional dependencies like
`pydantic_settings` are not installed. It will fall back to reading
environment variables directly via `os.getenv` with sensible defaults,
so the application can still run in demo mode.
"""

import os
from typing import Optional

try:
    # Prefer pydantic-based settings when available
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        APP_NAME: str = Field(default="GeoSpark", env="APP_NAME")
        APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
        DEBUG: bool = Field(default=False, env="DEBUG")
        HOST: str = Field(default="0.0.0.0", env="HOST")
        PORT: int = Field(default=8000, env="PORT")

        DATABASE_URL: str = Field(default="sqlite:///./geospark.db", env="DATABASE_URL")
        REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

        SECRET_KEY: str = Field(default="dev-secret-key", env="SECRET_KEY")
        ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

        OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
        ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
        SOLAR_API_KEY: Optional[str] = Field(default=None, env="SOLAR_API_KEY")
        WIND_API_KEY: Optional[str] = Field(default=None, env="WIND_API_KEY")
        WEATHER_API_KEY: Optional[str] = Field(default=None, env="WEATHER_API_KEY")

        ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")
        ELASTICSEARCH_INDEX: str = Field(default="renewable_energy_data", env="ELASTICSEARCH_INDEX")

        LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
        LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

        RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
        MAX_REQUESTS_PER_HOUR: int = Field(default=1000, env="MAX_REQUESTS_PER_HOUR")

        MAX_FILE_SIZE_MB: int = Field(default=10, env="MAX_FILE_SIZE_MB")
        ALLOWED_FILE_TYPES: str = Field(default="pdf,txt,csv,json,xlsx", env="ALLOWED_FILE_TYPES")

        ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
        METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")

        class Config:
            env_file = ".env"
            case_sensitive = True

    settings = Settings()

except Exception:
    # Lightweight fallback without external deps
    class Settings:
        def __init__(self):
            self.APP_NAME = os.getenv("APP_NAME", "GeoSpark")
            self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
            self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
            self.HOST = os.getenv("HOST", "0.0.0.0")
            self.PORT = int(os.getenv("PORT", "8000"))

            self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./geospark.db")
            self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

            self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
            self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
            self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
            self.SOLAR_API_KEY = os.getenv("SOLAR_API_KEY")
            self.WIND_API_KEY = os.getenv("WIND_API_KEY")
            self.WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

            self.ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
            self.ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "renewable_energy_data")

            self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
            self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

            self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
            self.MAX_REQUESTS_PER_HOUR = int(os.getenv("MAX_REQUESTS_PER_HOUR", "1000"))

            self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
            self.ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "pdf,txt,csv,json,xlsx")

            self.ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
            self.METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))

    settings = Settings()