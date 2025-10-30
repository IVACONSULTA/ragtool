"""
API Security module for authentication and session management (OWASP A2)
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import request, session
import logging

logger = logging.getLogger(__name__)

class APISecurityManager:
    """Secure API key management and validation"""
    
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.rate_limit_window = 300  # 5 minutes
        self.max_requests_per_window = 100
        self.request_counts = {}
        self.blocked_ips = set()
        self.failed_attempts = {}
    
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
        if client_ip in self.blocked_ips:
            return False
        
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
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                self.blocked_ips.add(client_ip)
                return False
            self.request_counts[client_ip]['count'] += 1
        else:
            self.request_counts[client_ip] = {
                'count': 1,
                'timestamp': current_time
            }
        
        return True
    
    def record_failed_attempt(self, client_ip: str, reason: str = "invalid_api_key"):
        """Record failed authentication attempt"""
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = []
        
        self.failed_attempts[client_ip].append({
            'timestamp': datetime.now(),
            'reason': reason
        })
        
        # Block IP after 5 failed attempts in 1 hour
        recent_failures = [
            attempt for attempt in self.failed_attempts[client_ip]
            if datetime.now() - attempt['timestamp'] < timedelta(hours=1)
        ]
        
        if len(recent_failures) >= 5:
            logger.warning(f"Blocking IP {client_ip} due to repeated failed attempts")
            self.blocked_ips.add(client_ip)
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is blocked"""
        return client_ip in self.blocked_ips
    
    def unblock_ip(self, client_ip: str):
        """Unblock an IP address (admin function)"""
        self.blocked_ips.discard(client_ip)
        if client_ip in self.failed_attempts:
            del self.failed_attempts[client_ip]
        logger.info(f"Unblocked IP: {client_ip}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            'blocked_ips': list(self.blocked_ips),
            'active_connections': len(self.request_counts),
            'failed_attempts_count': len(self.failed_attempts),
            'rate_limit_window': self.rate_limit_window,
            'max_requests_per_window': self.max_requests_per_window
        }

class SessionManager:
    """Secure session management"""
    
    def __init__(self):
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_ip = 5
        self.active_sessions = {}
    
    def create_secure_session(self, client_ip: str) -> str:
        """Create a new secure session"""
        session_id = secrets.token_urlsafe(32)
        
        # Check session limit per IP
        ip_sessions = [s for s in self.active_sessions.values() if s.get('client_ip') == client_ip]
        if len(ip_sessions) >= self.max_sessions_per_ip:
            # Remove oldest session for this IP
            oldest_session = min(ip_sessions, key=lambda x: x['created_at'])
            self.active_sessions.pop(oldest_session['session_id'], None)
        
        session_data = {
            'session_id': session_id,
            'created_at': datetime.now(),
            'client_ip': client_ip,
            'csrf_token': secrets.token_urlsafe(32),
            'last_activity': datetime.now()
        }
        
        self.active_sessions[session_id] = session_data
        
        # Set Flask session data
        session['session_id'] = session_id
        session['created_at'] = session_data['created_at'].isoformat()
        session['client_ip'] = client_ip
        session['csrf_token'] = session_data['csrf_token']
        
        logger.info(f"Created new session for IP: {client_ip}")
        return session_id
    
    def validate_session(self, client_ip: str) -> bool:
        """Validate current session"""
        session_id = session.get('session_id')
        if not session_id:
            return False
        
        if session_id not in self.active_sessions:
            return False
        
        session_data = self.active_sessions[session_id]
        
        # Check IP address
        if session_data.get('client_ip') != client_ip:
            logger.warning(f"Session IP mismatch: {client_ip} vs {session_data.get('client_ip')}")
            return False
        
        # Check session timeout
        if datetime.now() - session_data['created_at'] > timedelta(seconds=self.session_timeout):
            logger.info(f"Session expired for IP: {client_ip}")
            self.active_sessions.pop(session_id, None)
            session.clear()
            return False
        
        # Update last activity
        session_data['last_activity'] = datetime.now()
        return True
    
    def invalidate_session(self, session_id: str = None):
        """Invalidate a session"""
        if session_id:
            self.active_sessions.pop(session_id, None)
        else:
            session_id = session.get('session_id')
            if session_id:
                self.active_sessions.pop(session_id, None)
        
        session.clear()
        logger.info(f"Invalidated session: {session_id}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = [
            sid for sid, data in self.active_sessions.items()
            if current_time - data['created_at'] > timedelta(seconds=self.session_timeout)
        ]
        
        for sid in expired_sessions:
            self.active_sessions.pop(sid, None)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self.active_sessions.get(session_id)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)

class SecurityHeaders:
    """Security headers management"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Cross-Origin-Embedder-Policy': 'require-corp',
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Resource-Policy': 'same-origin'
        }
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to Flask response"""
        headers = SecurityHeaders.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        return response
