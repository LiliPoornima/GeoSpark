"""
Configuration settings for GeoSpark application.
"""

import os
from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # Ignore extra fields from .env
    )
    
    # Application
    APP_NAME: str = "GeoSpark"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"  # console or json
    
    # Database
    DATABASE_URL: Optional[str] = None
    DB_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]


settings = Settings()
