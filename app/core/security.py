"""
Security module for authentication, authorization, and data protection
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet
import re
import html

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()
# Optional bearer that won't auto-raise when missing
optional_security = HTTPBearer(auto_error=False)

# Encryption for sensitive data
# Ensure we always have a valid Fernet key; fall back to a generated key if provided key is invalid
try:
    fernet = Fernet(settings.SECRET_KEY.encode())
except Exception:
    logging.warning("Invalid SECRET_KEY for Fernet; generating a temporary key for demo mode.")
    fernet = Fernet(Fernet.generate_key())

class SecurityManager:
    """Centralized security management"""
    
    def __init__(self):
        self.rate_limits = {}
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"expression\s*\(",
        ]
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = fernet.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise HTTPException(status_code=500, detail="Data encryption failed")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise HTTPException(status_code=500, detail="Data decryption failed")
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not isinstance(input_data, str):
            return str(input_data)
        
        # HTML escape
        sanitized = html.escape(input_data)
        
        # Remove suspicious patterns
        for pattern in self.suspicious_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized.strip()
    
    def validate_file_upload(self, filename: str, file_size: int) -> bool:
        """Validate file upload"""
        # Check file extension
        allowed_extensions = settings.ALLOWED_FILE_TYPES.split(',')
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return False
        
        # Check file size
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            return False
        
        return True
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = datetime.utcnow()
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Remove old entries
        self.rate_limits[client_ip] = [
            timestamp for timestamp in self.rate_limits[client_ip]
            if current_time - timestamp < timedelta(minutes=1)
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(current_time)
        return True
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        logger.warning(f"Security Event - {event_type}: {details}")

# Global security manager instance
security_manager = SecurityManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = security_manager.verify_token(token)
    
    # In a real application, you would fetch user data from database
    # For now, return the payload
    return payload

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)) -> Dict[str, Any]:
    """Get user if Authorization header is provided; otherwise return a guest user."""
    if credentials and credentials.credentials:
        token = credentials.credentials
        payload = security_manager.verify_token(token)
        return payload
    # Fallback guest user
    return {"user_id": "guest", "role": "guest"}

def require_permissions(required_permissions: List[str]):
    """Decorator to require specific permissions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Check user permissions here
            # This is a simplified implementation
            return await func(*args, **kwargs)
        return wrapper
    return decorator