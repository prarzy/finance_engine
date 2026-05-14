from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Claims to encode in the token.
        expires_delta: Optional custom expiration time delta.
        
    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string.
        
    Returns:
        Decoded payload dict on success, None on error.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.JWTError):
        return None


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)
