from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Rate Limited API Gateway"
    DEBUG: bool = False
    
    # Redis Config
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Rate Limiter Defaults
    DEFAULT_RATE_LIMIT_RPM: int = 60
    DEFAULT_BURST_SIZE: int = 60
    
    # Cache Defaults
    CACHE_TTL_SECONDS: int = 300
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
