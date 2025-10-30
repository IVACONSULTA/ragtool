"""
Security logging and monitoring module (OWASP A10)
"""
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from flask import request
import threading

class SecurityLogger:
    """Comprehensive security logging system"""
    
    def __init__(self, log_file: str = 'security.log'):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Create file handler for security logs
            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
            
            # Also log to console in development
            if os.getenv('FLASK_ENV') == 'development':
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events with structured data"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "ip_address": self._get_client_ip(),
            "user_agent": request.headers.get('User-Agent') if request else "unknown",
            "request_id": getattr(request, 'id', None) if request else None
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_authentication_attempt(self, success: bool, user_id: str = None, method: str = "api_key"):
        """Log authentication attempts"""
        self.log_security_event("authentication_attempt", {
            "success": success,
            "user_id": user_id,
            "method": method,
            "ip_address": self._get_client_ip()
        })
    
    def log_input_validation_failure(self, input_data: str, validation_error: str, endpoint: str = None):
        """Log input validation failures"""
        self.log_security_event("input_validation_failure", {
            "input_data": input_data[:100] if input_data else None,  # Truncate for security
            "validation_error": validation_error,
            "endpoint": endpoint or (request.endpoint if request else None),
            "ip_address": self._get_client_ip()
        })
    
    def log_rate_limit_exceeded(self, client_ip: str, endpoint: str, limit: int):
        """Log rate limit violations"""
        self.log_security_event("rate_limit_exceeded", {
            "client_ip": client_ip,
            "endpoint": endpoint,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activities"""
        self.log_security_event("suspicious_activity", {
            "activity_type": activity_type,
            "details": details,
            "ip_address": self._get_client_ip(),
            "user_agent": request.headers.get('User-Agent') if request else "unknown"
        })
    
    def log_api_access(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Log API access for monitoring"""
        self.log_security_event("api_access", {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "ip_address": self._get_client_ip()
        })
    
    def log_error(self, error_type: str, error_message: str, stack_trace: str = None):
        """Log application errors"""
        self.log_security_event("application_error", {
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace[:500] if stack_trace else None,  # Truncate stack trace
            "ip_address": self._get_client_ip()
        })
    
    def log_configuration_change(self, config_key: str, old_value: Any, new_value: Any):
        """Log configuration changes"""
        self.log_security_event("configuration_change", {
            "config_key": config_key,
            "old_value": str(old_value)[:100] if old_value else None,
            "new_value": str(new_value)[:100] if new_value else None,
            "ip_address": self._get_client_ip()
        })
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        if not request:
            return "unknown"
        
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or "unknown"

class SecurityMonitor:
    """Real-time security monitoring"""
    
    def __init__(self):
        self.logger = SecurityLogger()
        self.alert_thresholds = {
            'failed_auth_attempts': 5,
            'rate_limit_violations': 10,
            'input_validation_failures': 20,
            'suspicious_activities': 3,
            'errors_per_minute': 10
        }
        self.counters = {}
        self.alerts_sent = set()
        self.lock = threading.Lock()
    
    def check_alert_conditions(self, event_type: str, details: Dict[str, Any] = None) -> bool:
        """Check if alert conditions are met"""
        with self.lock:
            current_time = datetime.now()
            
            # Initialize counter if not exists
            if event_type not in self.counters:
                self.counters[event_type] = []
            
            # Add current event
            self.counters[event_type].append({
                'timestamp': current_time,
                'details': details or {}
            })
            
            # Clean old entries (older than 1 hour)
            cutoff_time = current_time - timedelta(hours=1)
            self.counters[event_type] = [
                event for event in self.counters[event_type]
                if event['timestamp'] > cutoff_time
            ]
            
            # Check threshold
            threshold = self.alert_thresholds.get(event_type, float('inf'))
            if len(self.counters[event_type]) >= threshold:
                # Check if we already sent an alert for this event type recently
                alert_key = f"{event_type}_{current_time.strftime('%Y%m%d%H')}"
                if alert_key not in self.alerts_sent:
                    self.alerts_sent.add(alert_key)
                    self._send_alert(event_type, len(self.counters[event_type]), threshold)
                    return True
        
        return False
    
    def _send_alert(self, event_type: str, count: int, threshold: int):
        """Send security alert"""
        alert_details = {
            "event_type": event_type,
            "count": count,
            "threshold": threshold,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.log_security_event("security_alert", alert_details)
        
        # Here you could add additional alert mechanisms:
        # - Email notifications
        # - Slack/Discord webhooks
        # - SMS alerts
        # - External monitoring systems
    
    def monitor_request(self, request_data: Dict[str, Any], endpoint: str):
        """Monitor individual requests for security issues"""
        # Check for suspicious patterns in request data
        if 'message' in request_data:
            message = request_data['message']
            
            # Check for potential attacks
            attack_patterns = [
                (r'<script', 'xss_script_tag'),
                (r'javascript:', 'xss_javascript'),
                (r'<iframe', 'xss_iframe'),
                (r'union\s+select', 'sql_injection_union'),
                (r'drop\s+table', 'sql_injection_drop'),
                (r'\.\./', 'path_traversal'),
                (r'\.\.\\', 'path_traversal_windows'),
                (r'<.*>', 'command_injection'),
                (r'\|.*\|', 'command_injection_pipe')
            ]
            
            for pattern, attack_type in attack_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    self.logger.log_suspicious_activity("potential_attack", {
                        "pattern": pattern,
                        "attack_type": attack_type,
                        "input": message[:100],
                        "endpoint": endpoint
                    })
                    
                    # Check if this should trigger an alert
                    self.check_alert_conditions('suspicious_activities', {
                        'attack_type': attack_type,
                        'endpoint': endpoint
                    })
                    break
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get current security metrics"""
        with self.lock:
            current_time = datetime.now()
            metrics = {}
            
            for event_type, events in self.counters.items():
                # Count events in last hour
                recent_events = [
                    event for event in events
                    if current_time - event['timestamp'] < timedelta(hours=1)
                ]
                
                metrics[event_type] = {
                    'total_events': len(events),
                    'recent_events': len(recent_events),
                    'threshold': self.alert_thresholds.get(event_type, 'N/A')
                }
            
            return {
                'timestamp': current_time.isoformat(),
                'metrics': metrics,
                'alerts_sent_today': len([
                    alert for alert in self.alerts_sent
                    if alert.endswith(current_time.strftime('%Y%m%d'))
                ])
            }
    
    def reset_counters(self, event_type: str = None):
        """Reset security counters"""
        with self.lock:
            if event_type:
                self.counters.pop(event_type, None)
            else:
                self.counters.clear()
            self.alerts_sent.clear()

# Global instances
security_logger = SecurityLogger()
security_monitor = SecurityMonitor()

# Convenience functions
def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log a security event"""
    security_logger.log_security_event(event_type, details)

def log_authentication_attempt(success: bool, user_id: str = None, method: str = "api_key"):
    """Log authentication attempt"""
    security_logger.log_authentication_attempt(success, user_id, method)

def log_input_validation_failure(input_data: str, validation_error: str, endpoint: str = None):
    """Log input validation failure"""
    security_logger.log_input_validation_failure(input_data, validation_error, endpoint)

def log_suspicious_activity(activity_type: str, details: Dict[str, Any]):
    """Log suspicious activity"""
    security_logger.log_suspicious_activity(activity_type, details)

def check_alert_conditions(event_type: str, details: Dict[str, Any] = None) -> bool:
    """Check alert conditions"""
    return security_monitor.check_alert_conditions(event_type, details)
