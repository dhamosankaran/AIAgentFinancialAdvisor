"""
Configuration settings for the Financial Investment Advisor
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    OPENAI_API_KEY: str
    ALPHA_VANTAGE_API_KEY: str
    
    # API Base URLs
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Frontend Settings
    REACT_APP_API_BASE_URL: str = "http://localhost:8000"
    
    # Logging
    LOG_FILE: str = "app.log"
    
    # Database Settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "pwd"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "financial_advisor"
    DATABASE_URL: str = "postgresql://postgres:pwd@localhost:5432/financial_advisor"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Cache Settings
    CACHE_TTL: int = 3600
    CACHE_TYPE: str = "simple"
    
    # Rate Limiting
    RATE_LIMIT: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

# Create settings instance
settings = Settings() 