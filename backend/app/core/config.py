# Core Configuration and Security
import os
import secrets
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PDFForge"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
    
    # Google Drive
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    
    # File Processing
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {"pdf"}
    UPLOAD_DIR: Path = Path("/app/uploads")
    OUTPUT_DIR: Path = Path("/app/outputs")
    TEMP_DIR: Path = Path("/app/temp")
    CLEANUP_INTERVAL: int = 3600  # seconds
    
    # Security Limits
    MAX_CONCURRENT_TASKS: int = 5
    RATE_LIMIT_PER_MINUTE: int = 10
    SANITIZE_PDF: bool = True
    
    # OCR
    OCR_ENABLED: bool = True
    TESSERACT_PATH: Optional[str] = os.getenv("TESSERACT_PATH")
    OCR_LANGUAGES: str = "eng,por"
    
    # Database (SQLite for now, easily swappable)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pdfforge.db")
    
    # Redis/Celery (optional)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CELERY_BROKER_URL: Optional[str] = os.getenv("CELERY_BROKER_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create directories
for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption"""
    return Fernet(settings.ENCRYPTION_KEY.encode())
