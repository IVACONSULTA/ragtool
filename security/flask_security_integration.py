"""
Flask security integration module
Integrates all security measures into Flask application
"""
import re
import time
from functools import wraps
from flask import Flask, request, jsonify, session, g
from typing import Dict, Any, Callable

from .input_validator import InputValidator
from .api_security import APISecurityManager, SessionManager, SecurityHeaders
from .security_logger import security_logger, security_monitor, log_security_event, log_authentication_attempt

class FlaskSecurityIntegration:
    """Integrate security measures into Flask application"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.input_validator = InputValidator()
        self.api_security = APISecurityManager()
        self.session_manager = SessionManager()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize security integration with Flask app"""
        self.app = app
        
        # Add security headers middleware
        @app.after_request
        def add_security_headers(response):
            return SecurityHeaders.add_security_headers(response)
        
        # Add request monitoring
        @app.before_request
        def monitor_request():
            g.request_start_time = time.time()
            g.client_ip = self._get_client_ip()
            
            # Check if IP is blocked
            if self.api_security.is_ip_blocked(g.client_ip):
                log_security_event("blocked_ip_access", {
                    "ip_address": g.client_ip,
                    "endpoint": request.endpoint
                })
                return jsonify({
                    'error': 'Access denied',
                    'error_type': 'ip_blocked'
                }), 403
        
        # Add response monitoring
        @app.after_request
        def monitor_response(response):
            if hasattr(g, 'request_start_time'):
                response_time = time.time() - g.request_start_time
                security_logger.log_api_access(
                    endpoint=request.endpoint or 'unknown',
                    method=request.method,
                    status_code=response.status_code,
                    response_time=response_time
                )
            return response
        
        # Add error handling
        @app.errorhandler(Exception)
        def handle_security_errors(e):
            log_security_event("application_error", {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "endpoint": request.endpoint,
                "method": request.method
            })
            
            # Don't expose internal errors in production
            if app.config.get('DEBUG', False):
                return jsonify({
                    'error': str(e),
                    'error_type': 'internal_error'
                }), 500
            else:
                return jsonify({
                    'error': 'Internal server error',
                    'error_type': 'internal_error'
                }), 500
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or "unknown"
    
    def require_api_key(self, f: Callable) -> Callable:
        """Decorator to require API key authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not self.api_security.validate_api_key(api_key):
                log_authentication_attempt(False, method="api_key")
                self.api_security.record_failed_attempt(g.client_ip, "invalid_api_key")
                return jsonify({
                    'error': 'Invalid or missing API key',
                    'error_type': 'authentication_failed'
                }), 401
            
            log_authentication_attempt(True, method="api_key")
            return f(*args, **kwargs)
        return decorated_function
    
    def require_rate_limit(self, f: Callable) -> Callable:
        """Decorator to enforce rate limiting"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.api_security.check_rate_limit(g.client_ip):
                log_security_event("rate_limit_exceeded", {
                    "ip_address": g.client_ip,
                    "endpoint": request.endpoint
                })
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'error_type': 'rate_limit_exceeded'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    
    def validate_input(self, f: Callable) -> Callable:
        """Decorator to validate all input parameters"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate JSON input
            if request.is_json:
                data = request.get_json()
                if data and 'message' in data:
                    validation = self.input_validator.validate_chat_message(data['message'])
                    if not validation['valid']:
                        log_input_validation_failure(data['message'], validation['error'], request.endpoint)
                        return jsonify({
                            'error': validation['error'],
                            'error_type': 'input_validation_failed'
                        }), 400
                    
                    # Monitor for suspicious activity
                    security_monitor.monitor_request(data, request.endpoint or 'unknown')
            
            return f(*args, **kwargs)
        return decorated_function
    
    def require_session(self, f: Callable) -> Callable:
        """Decorator to require valid session"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.session_manager.validate_session(g.client_ip):
                return jsonify({
                    'error': 'Invalid or expired session',
                    'error_type': 'session_invalid'
                }), 401
            
            return f(*args, **kwargs)
        return decorated_function
    
    def create_secure_endpoint(self, endpoint: str, methods: list = None, require_auth: bool = True, require_rate_limit: bool = True, validate_input: bool = True):
        """Create a secure endpoint with all security measures"""
        def decorator(f: Callable) -> Callable:
            # Apply security decorators in order
            if validate_input:
                f = self.validate_input(f)
            if require_rate_limit:
                f = self.require_rate_limit(f)
            if require_auth:
                f = self.require_api_key(f)
            
            return f
        return decorator

# Security decorators for easy use
def secure_endpoint(require_auth: bool = True, require_rate_limit: bool = True, validate_input: bool = True):
    """Decorator factory for secure endpoints"""
    def decorator(f: Callable) -> Callable:
        # This will be applied when the security integration is initialized
        f._security_config = {
            'require_auth': require_auth,
            'require_rate_limit': require_rate_limit,
            'validate_input': validate_input
        }
        return f
    return decorator

def apply_security_to_endpoints(app: Flask, security_integration: FlaskSecurityIntegration):
    """Apply security measures to all endpoints with security config"""
    for rule in app.url_map.iter_rules():
        endpoint = rule.endpoint
        view_func = app.view_functions.get(endpoint)
        
        if view_func and hasattr(view_func, '_security_config'):
            config = view_func._security_config
            
            # Apply security decorators
            if config.get('validate_input', True):
                view_func = security_integration.validate_input(view_func)
            if config.get('require_rate_limit', True):
                view_func = security_integration.require_rate_limit(view_func)
            if config.get('require_auth', True):
                view_func = security_integration.require_api_key(view_func)
            
            # Update the view function
            app.view_functions[endpoint] = view_func

# Example usage in your Flask app
def create_secure_flask_app() -> Flask:
    """Create a Flask app with integrated security"""
    from flask import Flask
    
    app = Flask(__name__)
    
    # Initialize security integration
    security = FlaskSecurityIntegration(app)
    
    # Example secure endpoint
    @app.route('/chat', methods=['POST'])
    @secure_endpoint(require_auth=True, require_rate_limit=True, validate_input=True)
    def chat_endpoint():
        """Secure chat endpoint"""
        data = request.get_json()
        message = data.get('message', '')
        
        # Your existing chat logic here
        # The security measures are automatically applied
        
        return jsonify({
            'response': f"Processed message: {message}",
            'timestamp': time.time()
        })
    
    @app.route('/health', methods=['GET'])
    @secure_endpoint(require_auth=False, require_rate_limit=False, validate_input=False)
    def health_endpoint():
        """Health check endpoint (no security required)"""
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time()
        })
    
    # Apply security to all endpoints
    apply_security_to_endpoints(app, security)
    
    return app

# Utility functions
def get_security_status() -> Dict[str, Any]:
    """Get current security status"""
    return {
        'api_security': security_integration.api_security.get_security_status(),
        'session_info': {
            'active_sessions': security_integration.session_manager.get_active_sessions_count()
        },
        'monitoring': security_monitor.get_security_metrics()
    }

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log a security event"""
    log_security_event(event_type, details)

def log_authentication_attempt(success: bool, user_id: str = None, method: str = "api_key"):
    """Log authentication attempt"""
    log_authentication_attempt(success, user_id, method)

def log_input_validation_failure(input_data: str, validation_error: str, endpoint: str = None):
    """Log input validation failure"""
    log_input_validation_failure(input_data, validation_error, endpoint)
