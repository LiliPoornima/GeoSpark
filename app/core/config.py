"""
Core configuration module for GeoSpark
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Configuration
    APP_NAME: str = Field(default="GeoSpark", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database Configuration
    DATABASE_URL: str = Field(env="DATABASE_URL")
    REDIS_URL: str = Field(env="REDIS_URL")
    
    # Security Configuration
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    SOLAR_API_KEY: Optional[str] = Field(default=None, env="SOLAR_API_KEY")
    WIND_API_KEY: Optional[str] = Field(default=None, env="WIND_API_KEY")
    WEATHER_API_KEY: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # Elasticsearch Configuration
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")
    ELASTICSEARCH_INDEX: str = Field(default="renewable_energy_data", env="ELASTICSEARCH_INDEX")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    MAX_REQUESTS_PER_HOUR: int = Field(default=1000, env="MAX_REQUESTS_PER_HOUR")
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    ALLOWED_FILE_TYPES: str = Field(default="pdf,txt,csv,json,xlsx", env="ALLOWED_FILE_TYPES")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env file


# Global settings instance
settings = Settings()