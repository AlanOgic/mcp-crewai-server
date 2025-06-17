#!/usr/bin/env python3
"""
🔒 Security Framework for MCP CrewAI Server
Phase 1 Critical Security Implementation
"""

import hashlib
import hmac
import jwt
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import re
import logging
from functools import wraps
from pydantic import BaseModel, Field, validator
import os

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration constants"""
    # Authentication
    JWT_SECRET_KEY = os.getenv("MCP_JWT_SECRET", secrets.token_urlsafe(32))
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    API_KEY_LENGTH = 32
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per hour
    BURST_LIMIT = 10  # requests per minute
    
    # File system security
    ALLOWED_EXTENSIONS = {'.txt', '.json', '.md', '.csv', '.log'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9._/-]+$')
    
    # Input validation
    MAX_STRING_LENGTH = 10000
    MAX_LIST_LENGTH = 1000


class AuthenticationError(Exception):
    """Authentication failed"""
    pass


class AuthorizationError(Exception):
    """Authorization denied"""
    pass


class ValidationError(Exception):
    """Input validation failed"""
    pass


class SecurityViolationError(Exception):
    """Security policy violated"""
    pass


class APIKey(BaseModel):
    """API Key model for authentication"""
    key_id: str
    key_hash: str
    permissions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None


class RateLimitEntry(BaseModel):
    """Rate limiting tracking"""
    client_id: str
    requests: List[datetime] = Field(default_factory=list)
    blocked_until: Optional[datetime] = None


class SecurityValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_string(value: str, max_length: int = SecurityConfig.MAX_STRING_LENGTH) -> str:
        """Validate and sanitize string input"""
        if not isinstance(value, str):
            raise ValidationError(f"Expected string, got {type(value)}")
        
        if len(value) > max_length:
            raise ValidationError(f"String too long: {len(value)} > {max_length}")
        
        # Remove null bytes and control characters
        cleaned = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
        return cleaned
    
    @staticmethod
    def validate_path(path: str, base_dir: Optional[Path] = None) -> Path:
        """Validate file path for security"""
        if not isinstance(path, str):
            raise ValidationError(f"Path must be string, got {type(path)}")
        
        # Check for dangerous patterns
        if '..' in path or path.startswith('/'):
            raise SecurityViolationError("Path traversal attempt detected")
        
        if not SecurityConfig.SAFE_PATH_PATTERN.match(path):
            raise SecurityViolationError("Unsafe characters in path")
        
        # Convert to Path and resolve
        safe_path = Path(path).resolve()
        
        # Ensure within base directory if specified
        if base_dir:
            try:
                safe_path.relative_to(base_dir.resolve())
            except ValueError:
                raise SecurityViolationError("Path outside allowed directory")
        
        return safe_path
    
    @staticmethod
    def validate_file_extension(path: Path) -> None:
        """Validate file extension"""
        if path.suffix.lower() not in SecurityConfig.ALLOWED_EXTENSIONS:
            raise SecurityViolationError(f"File extension {path.suffix} not allowed")
    
    @staticmethod
    def validate_json(data: Any, max_depth: int = 10) -> Any:
        """Validate JSON data structure"""
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise ValidationError("JSON structure too deep")
            
            if isinstance(obj, dict):
                if len(obj) > SecurityConfig.MAX_LIST_LENGTH:
                    raise ValidationError("Dictionary too large")
                for key, value in obj.items():
                    SecurityValidator.validate_string(str(key), 100)
                    check_depth(value, current_depth + 1)
            elif isinstance(obj, list):
                if len(obj) > SecurityConfig.MAX_LIST_LENGTH:
                    raise ValidationError("List too long")
                for item in obj:
                    check_depth(item, current_depth + 1)
            elif isinstance(obj, str):
                SecurityValidator.validate_string(obj)
        
        check_depth(data)
        return data


class AuthenticationManager:
    """Manages API keys and JWT tokens"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self._load_api_keys()
    
    def _load_api_keys(self) -> None:
        """Load API keys from secure storage"""
        # In production, load from encrypted database or secure key store
        # For now, create a default admin key
        admin_key = self.generate_api_key("admin", ["*"])
        logger.info(f"🔑 Admin API key generated: {admin_key[:8]}...")
    
    def generate_api_key(self, client_id: str, permissions: List[str]) -> str:
        """Generate new API key"""
        raw_key = secrets.token_urlsafe(SecurityConfig.API_KEY_LENGTH)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=client_id,
            key_hash=key_hash,
            permissions=permissions
        )
        
        self.api_keys[key_hash] = api_key
        return raw_key
    
    def validate_api_key(self, raw_key: str) -> APIKey:
        """Validate API key and return key info"""
        if not raw_key:
            raise AuthenticationError("API key required")
        
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        if key_hash not in self.api_keys:
            raise AuthenticationError("Invalid API key")
        
        api_key = self.api_keys[key_hash]
        
        if not api_key.is_active:
            raise AuthenticationError("API key deactivated")
        
        if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("API key expired")
        
        # Update usage tracking
        api_key.usage_count += 1
        api_key.last_used = datetime.now(timezone.utc)
        
        return api_key
    
    def generate_jwt_token(self, api_key: APIKey) -> str:
        """Generate JWT token for authenticated session"""
        payload = {
            'client_id': api_key.key_id,
            'permissions': api_key.permissions,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=SecurityConfig.JWT_EXPIRATION_HOURS)
        }
        
        return jwt.encode(payload, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(
                token, 
                SecurityConfig.JWT_SECRET_KEY, 
                algorithms=[SecurityConfig.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.clients: Dict[str, RateLimitEntry] = {}
    
    def check_rate_limit(self, client_id: str, limit: int = SecurityConfig.DEFAULT_RATE_LIMIT) -> bool:
        """Check if client exceeds rate limit"""
        now = datetime.now(timezone.utc)
        
        if client_id not in self.clients:
            self.clients[client_id] = RateLimitEntry(client_id=client_id)
        
        client = self.clients[client_id]
        
        # Check if currently blocked
        if client.blocked_until and client.blocked_until > now:
            return False
        
        # Clean old requests (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        client.requests = [req for req in client.requests if req > cutoff]
        
        # Check hourly limit
        if len(client.requests) >= limit:
            # Block for 1 hour
            client.blocked_until = now + timedelta(hours=1)
            logger.warning(f"🚫 Rate limit exceeded for client {client_id}")
            return False
        
        # Check burst limit (10 requests per minute)
        burst_cutoff = now - timedelta(minutes=1)
        recent_requests = [req for req in client.requests if req > burst_cutoff]
        
        if len(recent_requests) >= SecurityConfig.BURST_LIMIT:
            logger.warning(f"🚫 Burst limit exceeded for client {client_id}")
            return False
        
        # Record request
        client.requests.append(now)
        return True
    
    def get_rate_limit_status(self, client_id: str) -> Dict[str, Any]:
        """Get current rate limit status"""
        if client_id not in self.clients:
            return {
                "requests_remaining": SecurityConfig.DEFAULT_RATE_LIMIT,
                "reset_time": None,
                "blocked": False
            }
        
        client = self.clients[client_id]
        now = datetime.now(timezone.utc)
        
        # Clean old requests
        cutoff = now - timedelta(hours=1)
        current_requests = [req for req in client.requests if req > cutoff]
        
        return {
            "requests_remaining": max(0, SecurityConfig.DEFAULT_RATE_LIMIT - len(current_requests)),
            "reset_time": (now + timedelta(hours=1)).isoformat(),
            "blocked": client.blocked_until and client.blocked_until > now,
            "block_expires": client.blocked_until.isoformat() if client.blocked_until else None
        }


class SecurityMiddleware:
    """Security middleware for tool execution"""
    
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.rate_limiter = RateLimiter()
        self.validator = SecurityValidator()
    
    def authenticate_request(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate incoming request"""
        # Check for API key in headers
        api_key = headers.get('X-API-Key') or headers.get('Authorization', '').replace('Bearer ', '')
        
        if not api_key:
            raise AuthenticationError("Authentication required")
        
        # Validate API key
        key_info = self.auth_manager.validate_api_key(api_key)
        
        # Check rate limits
        if not self.rate_limiter.check_rate_limit(key_info.key_id):
            raise AuthorizationError("Rate limit exceeded")
        
        return {
            'client_id': key_info.key_id,
            'permissions': key_info.permissions,
            'authenticated': True
        }
    
    def authorize_tool_access(self, auth_context: Dict[str, Any], tool_name: str) -> bool:
        """Check if client can access specific tool"""
        permissions = auth_context.get('permissions', [])
        
        # Admin permission grants access to everything
        if '*' in permissions:
            return True
        
        # Check specific tool permission
        if tool_name in permissions:
            return True
        
        # Check category permissions
        tool_categories = {
            'crew_': 'crew_management',
            'agent_': 'agent_management', 
            'evolution_': 'evolution_control',
            'memory_': 'memory_access',
            'web_search': 'web_access'
        }
        
        for prefix, category in tool_categories.items():
            if tool_name.startswith(prefix) and category in permissions:
                return True
        
        return False
    
    def validate_tool_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize tool arguments"""
        validated = {}
        
        for key, value in arguments.items():
            # Validate key name
            safe_key = self.validator.validate_string(key, 100)
            
            # Validate value based on type
            if isinstance(value, str):
                validated[safe_key] = self.validator.validate_string(value)
            elif isinstance(value, (dict, list)):
                validated[safe_key] = self.validator.validate_json(value)
            elif isinstance(value, (int, float, bool)) or value is None:
                validated[safe_key] = value
            else:
                raise ValidationError(f"Unsupported argument type: {type(value)}")
        
        return validated
    
    def secure_file_operation(self, file_path: str, operation: str = "read") -> Path:
        """Secure file operations"""
        # Get safe export directory
        export_dir = Path(__file__).parent.parent.parent / "exported_results"
        export_dir.mkdir(exist_ok=True)
        
        # Validate path
        safe_path = self.validator.validate_path(file_path, export_dir)
        
        # Check file extension for write operations
        if operation in ("write", "create"):
            self.validator.validate_file_extension(safe_path)
        
        # Check file size for read operations
        if operation == "read" and safe_path.exists():
            if safe_path.stat().st_size > SecurityConfig.MAX_FILE_SIZE:
                raise SecurityViolationError("File too large")
        
        return safe_path


def require_auth(permissions: List[str] = None):
    """Decorator for requiring authentication"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request context (would be passed in real implementation)
            # For now, assume middleware has already authenticated
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def security_audit_log(event: str, details: Dict[str, Any]) -> None:
    """Log security events for auditing"""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_entry = {
        "timestamp": timestamp,
        "event": event,
        "details": details
    }
    
    # In production, send to SIEM or security log aggregator
    logger.warning(f"🔒 SECURITY AUDIT: {event} - {details}")


# Global security instance
security_middleware = SecurityMiddleware()