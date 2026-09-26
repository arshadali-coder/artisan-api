import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Artisan Platform API"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # Auth Settings
    SECRET_KEY: str = "super-secret-key-change-this-in-production-artisans-sih-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./artisans.db"
    
    # AI Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # File Storage
    UPLOAD_DIR: str = "./static/uploads"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
