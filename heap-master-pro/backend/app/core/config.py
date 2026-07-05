"""
Heap Master Pro - Professional Metallurgical Engineering Platform
Core Configuration Module
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # App Info
    APP_NAME: str = "Heap Master Pro"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Advanced heap leaching simulation and management system"
    DEBUG: bool = False
    
    # API Settings
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./heap_master.db"
    
    # Metallurgical Engine Defaults
    DEFAULT_BASE_RECOVERY: float = 0.85
    DEFAULT_ACID_CONSUMPTION: float = 5.0  # kg/ton
    DEFAULT_EVAPORATION_RATE: float = 0.003  # m/day
    DEFAULT_ORE_DENSITY: float = 1.7  # ton/m³
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
