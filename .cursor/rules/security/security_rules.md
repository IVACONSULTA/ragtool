# SapRagTool Security Rules - OWASP Top 10 Compliance

## Overview

This document defines comprehensive security rules for the SapRagTool based on OWASP Top 10 vulnerabilities. The rules are tailored for the Flask/Python stack deployed on Railway, OpenOcean, Langraph, and other cloud platforms.

## Technology Stack Security Context

- **Framework**: Flask 3.0+ with Flask-CORS and Flask-Limiter
- **AI Components**: CrewAI, OpenAI API, LangSmith monitoring
- **Database**: ChromaDB (vector storage)
- **Deployment**: Railway (current), OpenOcean, Langraph (planned)
- **Authentication**: API Key based (optional)
- **Monitoring**: LangSmith integration

---

## A1 - Injection Attack Prevention

### Rule A1.1: Input Validation and Sanitization

```python
# IMPLEMENTATION REQUIRED
from flask import request, jsonify
import re
from typing import Any, Dict

class InputValidator:
    """Comprehensive input validation for all user inputs"""

    @staticmethod
    def validate_chat_message(message: str) -> Dict[str, Any]:
        """Validate chat message input with comprehensive checks"""
        if not message or not isinstance(message, str):
            return {"valid": False, "error": "Message must be a non-empty string"}

        # Length validation
        if len(message) > 10000:
            return {"valid": False, "error": "Message too long (max 10000 characters)"}

        # SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\s+\w+\s*=\s*\w+)',
            r'(\bUNION\s+SELECT\b)',
            r'(\bDROP\s+TABLE\b)',
            r'(\bDELETE\s+FROM\b)',
            r'(\bINSERT\s+INTO\b)',
            r'(\bUPDATE\s+SET\b)'
        ]

        for pattern in sql_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return {"valid": False, "error": "Potential SQL injection detected"}

        # XSS patterns
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]

        for pattern in xss_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return {"valid": False, "error": "Potential XSS attack detected"}

        # Command injection patterns
        cmd_patterns = [
            r'[;&|`$]',
            r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat)\b',
            r'\.\./',
            r'\.\.\\',
            r'<.*>',
            r'\|.*\|'
        ]

        for pattern in cmd_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return {"valid": False, "error": "Potential command injection detected"}

        return {"valid": True, "sanitized_message": message.strip()}

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations"""
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        # Remove special characters
        filename = re.sub(r'[^\w\-_\.]', '', filename)
        return filename
```

### Rule A1.2: Parameterized Queries and Safe Database Operations

```python
# IMPLEMENTATION REQUIRED
class SafeDatabaseOperations:
    """Safe database operations to prevent injection attacks"""

    @staticmethod
    def safe_chroma_query(query_text: str, collection, limit: int = 10):
        """Execute safe ChromaDB queries with validation"""
        # Validate query before execution
        validator = InputValidator()
        validation_result = validator.validate_chat_message(query_text)

        if not validation_result["valid"]:
            raise ValueError(f"Invalid query: {validation_result['error']}")

        # Use ChromaDB's built-in safe query methods
        try:
            results = collection.query(
                query_texts=[validation_result["sanitized_message"]],
                n_results=limit
            )
            return results
        except Exception as e:
            raise ValueError(f"Database query failed: {str(e)}")
```

### Rule A1.3: API Endpoint Protection

```python
# IMPLEMENTATION REQUIRED
from flask import Flask, request, jsonify
from functools import wraps

def validate_input(f):
    """Decorator to validate all input parameters"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            data = request.get_json()
            if 'message' in data:
                validator = InputValidator()
                validation = validator.validate_chat_message(data['message'])
                if not validation['valid']:
                    return jsonify({
                        'error': validation['error'],
                        'error_type': 'input_validation_failed'
                    }), 400
        return f(*args, **kwargs)
    return decorated_function

# Apply to chat endpoint
@app.route('/chat', methods=['POST'])
@validate_input
def chat_endpoint():
    # Safe endpoint implementation
    pass
```

---

## A2 - Broken Authentication and Session Management

### Rule A2.1: API Key Management

```python
# IMPLEMENTATION REQUIRED
import os
import hashlib
import secrets
from datetime import datetime, timedelta

class APISecurityManager:
    """Secure API key management and validation"""

    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.rate_limit_window = 300  # 5 minutes
        self.max_requests_per_window = 100
        self.request_counts = {}

    def validate_api_key(self, provided_key: str) -> bool:
        """Validate API key with constant-time comparison"""
        if not self.api_key:
            return True  # No API key required in development

        if not provided_key:
            return False

        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(self.api_key, provided_key)

    def generate_secure_api_key(self) -> str:
        """Generate a cryptographically secure API key"""
        return secrets.token_urlsafe(32)

    def check_rate_limit(self, client_ip: str) -> bool:
        """Implement rate limiting per IP address"""
        current_time = datetime.now()
        window_start = current_time - timedelta(seconds=self.rate_limit_window)

        # Clean old entries
        self.request_counts = {
            ip: count for ip, count in self.request_counts.items()
            if count['timestamp'] > window_start
        }

        # Check current IP
        if client_ip in self.request_counts:
            if self.request_counts[client_ip]['count'] >= self.max_requests_per_window:
                return False
            self.request_counts[client_ip]['count'] += 1
        else:
            self.request_counts[client_ip] = {
                'count': 1,
                'timestamp': current_time
            }

        return True
```

### Rule A2.2: Session Security

```python
# IMPLEMENTATION REQUIRED
from flask import session, request
import uuid
from datetime import datetime, timedelta

class SessionManager:
    """Secure session management"""

    def __init__(self):
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_ip = 5

    def create_secure_session(self, client_ip: str) -> str:
        """Create a new secure session"""
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session['created_at'] = datetime.now().isoformat()
        session['client_ip'] = client_ip
        session['csrf_token'] = secrets.token_urlsafe(32)
        return session_id

    def validate_session(self, client_ip: str) -> bool:
        """Validate current session"""
        if 'session_id' not in session:
            return False

        # Check IP address
        if session.get('client_ip') != client_ip:
            return False

        # Check session timeout
        created_at = datetime.fromisoformat(session.get('created_at', ''))
        if datetime.now() - created_at > timedelta(seconds=self.session_timeout):
            session.clear()
            return False

        return True
```

---

## A3 - Sensitive Data Exposure

### Rule A3.1: Data Encryption and Protection

```python
# IMPLEMENTATION REQUIRED
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DataProtection:
    """Encrypt and protect sensitive data"""

    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = '.encryption_key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storage"""
        if not data:
            return data
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            return encrypted_data  # Return as-is if decryption fails

    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return f"{base64.urlsafe_b64encode(salt).decode()}:{key.decode()}"
```

### Rule A3.2: Environment Variable Security

```python
# IMPLEMENTATION REQUIRED
import os
from typing import Dict, Any

class SecureConfig:
    """Secure configuration management"""

    SENSITIVE_VARS = [
        'OPENAI_API_KEY',
        'LANGSMITH_API_KEY',
        'API_KEY',
        'DATABASE_URL',
        'SECRET_KEY'
    ]

    @classmethod
    def get_secure_config(cls) -> Dict[str, Any]:
        """Get configuration with sensitive data protection"""
        config = {}

        for var in cls.SENSITIVE_VARS:
            value = os.getenv(var)
            if value:
                # Mask sensitive values in logs
                if var in ['OPENAI_API_KEY', 'LANGSMITH_API_KEY', 'API_KEY']:
                    config[var] = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    config[var] = value

        return config

    @classmethod
    def validate_required_vars(cls) -> bool:
        """Validate all required environment variables are present"""
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")

        return True
```

---

## A4 - XML External Entity (XXE) Prevention

### Rule A4.1: Safe XML Processing

```python
# IMPLEMENTATION REQUIRED
import xml.etree.ElementTree as ET
from defusedxml import ElementTree as SafeET

class SafeXMLProcessor:
    """Safe XML processing to prevent XXE attacks"""

    @staticmethod
    def safe_parse_xml(xml_content: str) -> ET.Element:
        """Parse XML safely without external entity processing"""
        try:
            # Use defusedxml for safe parsing
            root = SafeET.fromstring(xml_content)
            return root
        except Exception as e:
            raise ValueError(f"Invalid XML content: {str(e)}")

    @staticmethod
    def validate_xml_structure(xml_content: str, allowed_elements: list) -> bool:
        """Validate XML structure against allowed elements"""
        try:
            root = SafeET.fromstring(xml_content)

            def check_elements(element):
                if element.tag not in allowed_elements:
                    return False
                for child in element:
                    if not check_elements(child):
                        return False
                return True

            return check_elements(root)
        except Exception:
            return False
```

---

## A5 - Broken Access Control

### Rule A5.1: Role-Based Access Control

```python
# IMPLEMENTATION REQUIRED
from enum import Enum
from functools import wraps

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"
    API_CLIENT = "api_client"

class AccessControl:
    """Role-based access control system"""

    def __init__(self):
        self.role_permissions = {
            UserRole.ADMIN: ['read', 'write', 'delete', 'admin'],
            UserRole.USER: ['read', 'write'],
            UserRole.READONLY: ['read'],
            UserRole.API_CLIENT: ['read', 'write']
        }

    def check_permission(self, role: UserRole, action: str) -> bool:
        """Check if role has permission for action"""
        if role not in self.role_permissions:
            return False
        return action in self.role_permissions[role]

    def require_permission(self, action: str):
        """Decorator to require specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get user role from session or API key
                user_role = self.get_user_role()
                if not self.check_permission(user_role, action):
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'error_type': 'access_denied'
                    }), 403
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def get_user_role(self) -> UserRole:
        """Get current user role based on context"""
        # Implementation depends on your authentication system
        if request.headers.get('X-API-Key'):
            return UserRole.API_CLIENT
        elif session.get('user_role'):
            return UserRole(session['user_role'])
        else:
            return UserRole.READONLY
```

### Rule A5.2: Endpoint Protection

```python
# IMPLEMENTATION REQUIRED
from flask import request, jsonify

class EndpointProtection:
    """Protect endpoints from unauthorized access"""

    @staticmethod
    def validate_request_source() -> bool:
        """Validate request source and headers"""
        # Check for required headers
        required_headers = ['Content-Type']
        for header in required_headers:
            if header not in request.headers:
                return False

        # Validate Content-Type
        if request.is_json and request.headers.get('Content-Type') != 'application/json':
            return False

        return True

    @staticmethod
    def check_csrf_protection() -> bool:
        """Check CSRF protection for state-changing operations"""
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            csrf_token = request.headers.get('X-CSRF-Token')
            if not csrf_token or csrf_token != session.get('csrf_token'):
                return False
        return True
```

---

## A6 - Security Misconfiguration

### Rule A6.1: Secure Flask Configuration

```python
# IMPLEMENTATION REQUIRED
from flask import Flask
import os

class SecureFlaskConfig:
    """Secure Flask application configuration"""

    @staticmethod
    def create_secure_app() -> Flask:
        """Create Flask app with secure configuration"""
        app = Flask(__name__)

        # Security configurations
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
        app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
        app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
        app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # CSRF protection
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

        # Disable debug in production
        app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'

        # Security headers
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            return response

        return app
```

### Rule A6.2: Environment-Specific Security

```python
# IMPLEMENTATION REQUIRED
class EnvironmentSecurity:
    """Environment-specific security configurations"""

    @staticmethod
    def get_security_config() -> dict:
        """Get security configuration based on environment"""
        environment = os.getenv('FLASK_ENV', 'production')

        configs = {
            'development': {
                'debug': True,
                'ssl_required': False,
                'cors_origins': ['http://localhost:3000', 'http://localhost:8000'],
                'rate_limit': 1000,
                'log_level': 'DEBUG'
            },
            'production': {
                'debug': False,
                'ssl_required': True,
                'cors_origins': [],  # Configure based on your frontend
                'rate_limit': 100,
                'log_level': 'WARNING'
            },
            'railway': {
                'debug': False,
                'ssl_required': True,
                'cors_origins': [],  # Configure based on your frontend
                'rate_limit': 200,
                'log_level': 'INFO'
            }
        }

        return configs.get(environment, configs['production'])
```

---

## A7 - Cross-Site Scripting (XSS) Prevention

### Rule A7.1: Input Sanitization and Output Encoding

```python
# IMPLEMENTATION REQUIRED
import html
import re
from markupsafe import Markup, escape

class XSSProtection:
    """Cross-Site Scripting protection"""

    @staticmethod
    def sanitize_html_input(text: str) -> str:
        """Sanitize HTML input to prevent XSS"""
        if not text:
            return text

        # Remove script tags and event handlers
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

        # Escape remaining HTML
        return escape(text)

    @staticmethod
    def safe_json_response(data: dict) -> str:
        """Create safe JSON response with proper escaping"""
        import json
        return json.dumps(data, ensure_ascii=True, separators=(',', ':'))

    @staticmethod
    def validate_content_type(request) -> bool:
        """Validate content type to prevent XSS via file uploads"""
        if request.files:
            allowed_types = ['application/pdf', 'text/plain']
            for file in request.files.values():
                if file.content_type not in allowed_types:
                    return False
        return True
```

### Rule A7.2: Content Security Policy

```python
# IMPLEMENTATION REQUIRED
class ContentSecurityPolicy:
    """Content Security Policy implementation"""

    @staticmethod
    def get_csp_header() -> str:
        """Get Content Security Policy header"""
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self' https://api.openai.com https://api.smith.langchain.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        return "; ".join(csp_directives)
```

---

## A8 - Insecure Deserialization Prevention

### Rule A8.1: Safe Serialization

```python
# IMPLEMENTATION REQUIRED
import json
import pickle
import base64
from typing import Any

class SafeSerialization:
    """Safe serialization and deserialization"""

    @staticmethod
    def safe_serialize(data: Any) -> str:
        """Safely serialize data using JSON"""
        try:
            return json.dumps(data, ensure_ascii=True, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Serialization failed: {str(e)}")

    @staticmethod
    def safe_deserialize(json_str: str) -> Any:
        """Safely deserialize JSON data"""
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Deserialization failed: {str(e)}")

    @staticmethod
    def validate_serialized_data(data: Any) -> bool:
        """Validate data before serialization"""
        # Check for potentially dangerous objects
        dangerous_types = (type, object, type(None))
        if isinstance(data, dangerous_types):
            return False

        # Check for functions and methods
        if callable(data):
            return False

        return True

    @staticmethod
    def never_use_pickle(data: Any) -> None:
        """NEVER use pickle for user-provided data"""
        raise SecurityError("Pickle deserialization is not allowed for security reasons")
```

---

## A9 - Using Components with Known Vulnerabilities

### Rule A9.1: Dependency Security Management

```python
# IMPLEMENTATION REQUIRED
import subprocess
import json
import os
from typing import List, Dict

class DependencySecurity:
    """Manage dependency security and vulnerability scanning"""

    @staticmethod
    def scan_vulnerabilities() -> Dict[str, List[Dict]]:
        """Scan for known vulnerabilities in dependencies"""
        try:
            # Use safety to check for known vulnerabilities
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return {"vulnerabilities": [], "status": "clean"}
            else:
                vulnerabilities = json.loads(result.stdout) if result.stdout else []
                return {"vulnerabilities": vulnerabilities, "status": "vulnerable"}
        except Exception as e:
            return {"error": str(e), "status": "error"}

    @staticmethod
    def update_dependencies() -> bool:
        """Update dependencies to latest secure versions"""
        try:
            # Update pip first
            subprocess.run(['pip', 'install', '--upgrade', 'pip'], check=True)

            # Update requirements
            subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--upgrade'], check=True)

            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def generate_security_report() -> Dict[str, Any]:
        """Generate comprehensive security report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dependencies": [],
            "vulnerabilities": [],
            "recommendations": []
        }

        # Check requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                report["dependencies"] = [line.strip() for line in f if line.strip()]

        # Scan for vulnerabilities
        vuln_scan = DependencySecurity.scan_vulnerabilities()
        report["vulnerabilities"] = vuln_scan.get("vulnerabilities", [])

        return report
```

### Rule A9.2: Dependency Monitoring

```python
# IMPLEMENTATION REQUIRED
class DependencyMonitor:
    """Monitor dependencies for security updates"""

    def __init__(self):
        self.critical_packages = [
            'flask', 'crewai', 'openai', 'chromadb', 'langsmith'
        ]

    def check_critical_updates(self) -> Dict[str, str]:
        """Check for updates to critical packages"""
        updates = {}

        for package in self.critical_packages:
            try:
                result = subprocess.run(
                    ['pip', 'show', package],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    # Parse version information
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if line.startswith('Version:'):
                            current_version = line.split(':')[1].strip()
                            updates[package] = current_version
                            break
            except Exception:
                updates[package] = "unknown"

        return updates
```

---

## A10 - Insufficient Logging & Monitoring

### Rule A10.1: Comprehensive Security Logging

```python
# IMPLEMENTATION REQUIRED
import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityLogger:
    """Comprehensive security logging system"""

    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)

        # Create file handler for security logs
        handler = logging.FileHandler('security.log')
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events with structured data"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "ip_address": request.remote_addr if request else "unknown",
            "user_agent": request.headers.get('User-Agent') if request else "unknown"
        }

        self.logger.info(json.dumps(log_entry))

    def log_authentication_attempt(self, success: bool, user_id: str = None):
        """Log authentication attempts"""
        self.log_security_event("authentication_attempt", {
            "success": success,
            "user_id": user_id
        })

    def log_input_validation_failure(self, input_data: str, validation_error: str):
        """Log input validation failures"""
        self.log_security_event("input_validation_failure", {
            "input_data": input_data[:100],  # Truncate for security
            "validation_error": validation_error
        })

    def log_rate_limit_exceeded(self, client_ip: str, endpoint: str):
        """Log rate limit violations"""
        self.log_security_event("rate_limit_exceeded", {
            "client_ip": client_ip,
            "endpoint": endpoint
        })

    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activities"""
        self.log_security_event("suspicious_activity", {
            "activity_type": activity_type,
            "details": details
        })
```

### Rule A10.2: Real-time Monitoring

```python
# IMPLEMENTATION REQUIRED
class SecurityMonitor:
    """Real-time security monitoring"""

    def __init__(self):
        self.logger = SecurityLogger()
        self.alert_thresholds = {
            'failed_auth_attempts': 5,
            'rate_limit_violations': 10,
            'input_validation_failures': 20
        }
        self.counters = {}

    def check_alert_conditions(self, event_type: str) -> bool:
        """Check if alert conditions are met"""
        if event_type not in self.counters:
            self.counters[event_type] = 0

        self.counters[event_type] += 1

        threshold = self.alert_thresholds.get(event_type, float('inf'))
        if self.counters[event_type] >= threshold:
            self.logger.log_security_event("alert_triggered", {
                "event_type": event_type,
                "count": self.counters[event_type],
                "threshold": threshold
            })
            return True

        return False

    def monitor_request(self, request_data: Dict[str, Any]):
        """Monitor individual requests for security issues"""
        # Check for suspicious patterns
        if 'message' in request_data:
            message = request_data['message']

            # Check for potential attacks
            attack_patterns = [
                r'<script', r'javascript:', r'<iframe',
                r'union\s+select', r'drop\s+table',
                r'\.\./', r'\.\.\\'
            ]

            for pattern in attack_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    self.logger.log_suspicious_activity("potential_attack", {
                        "pattern": pattern,
                        "input": message[:100]
                    })
                    break
```

---

## Implementation Checklist

### Immediate Actions Required

1. **Input Validation** ✅

   - [ ] Implement `InputValidator` class
   - [ ] Add validation decorators to all endpoints
   - [ ] Test with malicious inputs

2. **Authentication & Authorization** ✅

   - [ ] Implement `APISecurityManager`
   - [ ] Add rate limiting
   - [ ] Implement session management

3. **Data Protection** ✅

   - [ ] Implement `DataProtection` class
   - [ ] Encrypt sensitive data
   - [ ] Secure environment variables

4. **Security Headers** ✅

   - [ ] Add security headers middleware
   - [ ] Implement CSP
   - [ ] Configure CORS properly

5. **Logging & Monitoring** ✅
   - [ ] Implement `SecurityLogger`
   - [ ] Add real-time monitoring
   - [ ] Set up alerting

### Deployment-Specific Security

#### Railway Deployment

```python
# Railway-specific security configurations
RAILWAY_SECURITY_CONFIG = {
    'cors_origins': ['https://your-frontend.railway.app'],
    'rate_limit': 200,
    'ssl_required': True,
    'health_check_path': '/health'
}
```

#### OpenOcean Deployment

```python
# OpenOcean-specific security configurations
OPENOCEAN_SECURITY_CONFIG = {
    'cors_origins': ['https://your-frontend.openocean.com'],
    'rate_limit': 300,
    'ssl_required': True,
    'container_security': True
}
```

#### Langraph Deployment

```python
# Langraph-specific security configurations
LANGGRAPH_SECURITY_CONFIG = {
    'cors_origins': ['https://your-frontend.langraph.com'],
    'rate_limit': 150,
    'ssl_required': True,
    'ai_model_security': True
}
```

---

## Security Testing

### Automated Security Tests

```python
# security_tests.py
import pytest
from unittest.mock import patch, MagicMock

class TestSecurityRules:
    def test_input_validation_sql_injection(self):
        validator = InputValidator()
        result = validator.validate_chat_message("'; DROP TABLE users; --")
        assert not result['valid']
        assert 'SQL injection' in result['error']

    def test_input_validation_xss(self):
        validator = InputValidator()
        result = validator.validate_chat_message("<script>alert('xss')</script>")
        assert not result['valid']
        assert 'XSS attack' in result['error']

    def test_rate_limiting(self):
        security_manager = APISecurityManager()
        client_ip = "192.168.1.1"

        # Should allow first 100 requests
        for i in range(100):
            assert security_manager.check_rate_limit(client_ip)

        # Should block 101st request
        assert not security_manager.check_rate_limit(client_ip)

    def test_api_key_validation(self):
        security_manager = APISecurityManager()
        assert security_manager.validate_api_key("invalid_key") == False
```

---

## Monitoring Dashboard

### Security Metrics to Track

1. **Authentication Events**

   - Successful/failed login attempts
   - API key usage patterns
   - Session management events

2. **Input Validation**

   - Validation failures by type
   - Malicious input patterns
   - Rate limit violations

3. **System Security**

   - Dependency vulnerabilities
   - Configuration changes
   - Error rates and patterns

4. **Performance Impact**
   - Security overhead metrics
   - Response time impact
   - Resource usage

---

## Emergency Response

### Incident Response Plan

1. **Detection**: Automated monitoring alerts
2. **Assessment**: Determine severity and impact
3. **Containment**: Immediate security measures
4. **Investigation**: Detailed analysis and forensics
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Update security measures

### Contact Information

- **Security Team**: [Add contact information]
- **Emergency Escalation**: [Add escalation procedures]
- **External Security**: [Add external security contacts]

---

This security rules document provides comprehensive protection against OWASP Top 10 vulnerabilities specifically tailored for your SapRagTool Flask application. Implement these rules systematically, starting with the most critical vulnerabilities (A1, A2, A3) and progressing through all categories.

Remember to regularly update and test these security measures, especially when deploying to new platforms or making significant changes to your application.
