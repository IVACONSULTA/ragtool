"""
Input validation module for preventing injection attacks (OWASP A1)
"""
import re
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Comprehensive input validation for all user inputs"""
    
    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\s+\w+\s*=\s*\w+)',
            r'(\bUNION\s+SELECT\b)',
            r'(\bDROP\s+TABLE\b)',
            r'(\bDELETE\s+FROM\b)',
            r'(\bINSERT\s+INTO\b)',
            r'(\bUPDATE\s+SET\b)',
            r'(\bEXEC\s+\w+)',
            r'(\bEXECUTE\s+\w+)',
            r'(\bDECLARE\s+\w+)',
            r'(\bCURSOR\s+\w+)'
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<form[^>]*>',
            r'<input[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<style[^>]*>.*?</style>',
            r'expression\s*\(',
            r'url\s*\(',
            r'@import'
        ]
        
        # Command injection patterns
        self.cmd_patterns = [
            r'[;&|`$]',
            r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|wget|curl|nc|telnet)\b',
            r'\.\./',
            r'\.\.\\',
            r'<.*>',
            r'\|.*\|',
            r'\$\(.*\)',
            r'`.*`'
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'\.\.%2f',
            r'\.\.%5c'
        ]
    
    def validate_chat_message(self, message: str) -> Dict[str, Any]:
        """Validate chat message input with comprehensive checks"""
        if not message or not isinstance(message, str):
            return {"valid": False, "error": "Message must be a non-empty string"}
        
        # Length validation
        if len(message) > 10000:
            return {"valid": False, "error": "Message too long (max 10000 characters)"}
        
        # Check for SQL injection
        sql_result = self._check_sql_injection(message)
        if not sql_result["valid"]:
            return sql_result
        
        # Check for XSS
        xss_result = self._check_xss(message)
        if not xss_result["valid"]:
            return xss_result
        
        # Check for command injection
        cmd_result = self._check_command_injection(message)
        if not cmd_result["valid"]:
            return cmd_result
        
        # Check for path traversal
        path_result = self._check_path_traversal(message)
        if not path_result["valid"]:
            return path_result
        
        return {"valid": True, "sanitized_message": message.strip()}
    
    def _check_sql_injection(self, message: str) -> Dict[str, Any]:
        """Check for SQL injection patterns"""
        for pattern in self.sql_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected: {pattern}")
                return {"valid": False, "error": "Potential SQL injection detected"}
        return {"valid": True}
    
    def _check_xss(self, message: str) -> Dict[str, Any]:
        """Check for XSS patterns"""
        for pattern in self.xss_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"XSS attempt detected: {pattern}")
                return {"valid": False, "error": "Potential XSS attack detected"}
        return {"valid": True}
    
    def _check_command_injection(self, message: str) -> Dict[str, Any]:
        """Check for command injection patterns"""
        for pattern in self.cmd_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"Command injection attempt detected: {pattern}")
                return {"valid": False, "error": "Potential command injection detected"}
        return {"valid": True}
    
    def _check_path_traversal(self, message: str) -> Dict[str, Any]:
        """Check for path traversal patterns"""
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"Path traversal attempt detected: {pattern}")
                return {"valid": False, "error": "Potential path traversal detected"}
        return {"valid": True}
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations"""
        if not filename:
            return "unnamed_file"
        
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        # Remove special characters
        filename = re.sub(r'[^\w\-_\.]', '', filename)
        # Limit length
        filename = filename[:100]
        
        return filename or "unnamed_file"
    
    def validate_json_input(self, json_data: dict) -> Dict[str, Any]:
        """Validate JSON input data"""
        if not isinstance(json_data, dict):
            return {"valid": False, "error": "Input must be a JSON object"}
        
        # Check for required fields
        if 'message' not in json_data:
            return {"valid": False, "error": "Missing required field: message"}
        
        # Validate message content
        message_validation = self.validate_chat_message(json_data['message'])
        if not message_validation['valid']:
            return message_validation
        
        return {"valid": True, "sanitized_data": json_data}
    
    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate API key format"""
        if not api_key:
            return {"valid": False, "error": "API key is required"}
        
        if not isinstance(api_key, str):
            return {"valid": False, "error": "API key must be a string"}
        
        if len(api_key) < 16:
            return {"valid": False, "error": "API key too short (minimum 16 characters)"}
        
        if len(api_key) > 128:
            return {"valid": False, "error": "API key too long (maximum 128 characters)"}
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9\-_]+$', api_key):
            return {"valid": False, "error": "API key contains invalid characters"}
        
        return {"valid": True, "sanitized_key": api_key}
