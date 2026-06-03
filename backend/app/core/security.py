# Security utilities
import re
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, status, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

def generate_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\.\.', '', filename)
    filename = filename.strip()
    
    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = f"{name[:255-len(ext)]}{ext}"
    
    return filename

def validate_file(file_path: Path, allowed_extensions: set = None) -> Tuple[bool, str]:
    """Validate file type and size"""
    if not file_path.exists():
        return False, "File does not exist"
    
    if allowed_extensions is None:
        allowed_extensions = settings.ALLOWED_EXTENSIONS
    
    # Check extension
    if file_path.suffix.lower().lstrip('.') not in allowed_extensions:
        return False, f"File type not allowed. Allowed: {allowed_extensions}"
    
    # Check size
    file_size = file_path.stat().st_size
    if file_size > settings.MAX_FILE_SIZE:
        return False, f"File too large. Max: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    return True, "Valid"

def get_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> HTTPException:
    """Custom rate limit exceeded handler"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded. Please try again later.",
        headers={"Retry-After": str(exc.detail.retry_after)},
    )

async def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> int:
    """Clean up old temporary files"""
    if not directory.exists():
        return 0
    
    cleaned = 0
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff:
                try:
                    file_path.unlink()
                    cleaned += 1
                except Exception:
                    pass
    
    return cleaned
