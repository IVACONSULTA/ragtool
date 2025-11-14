# Security Implementation Guide for SapRagTool

## Overview

This guide provides step-by-step instructions for implementing the OWASP Top 10 security measures in your SapRagTool Flask application.

## Quick Start

### 1. Install Security Dependencies

Add these to your `requirements.txt`:

```txt
# Security Dependencies
cryptography>=41.0.0
defusedxml>=0.7.1
safety>=2.3.0
```

### 2. Update Your Flask Application

Modify your `agents/crew_agent_server.py`:

```python
from security.flask_security_integration import FlaskSecurityIntegration, secure_endpoint
from security.security_logger import log_security_event

# Initialize security integration
security = FlaskSecurityIntegration(app)

# Apply security to your existing endpoints
@app.route('/chat', methods=['POST'])
@secure_endpoint(require_auth=True, require_rate_limit=True, validate_input=True)
def chat_endpoint():
    # Your existing chat logic
    pass

@app.route('/health', methods=['GET'])
@secure_endpoint(require_auth=False, require_rate_limit=False, validate_input=False)
def health_endpoint():
    # Your existing health check
    pass
```

### 3. Environment Variables

Add these to your `.env` file:

```bash
# Security Configuration
API_KEY=your_secure_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=production  # or development

# Optional: Custom security settings
RATE_LIMIT_WINDOW=300
MAX_REQUESTS_PER_WINDOW=100
SESSION_TIMEOUT=3600
```

## Detailed Implementation

### Step 1: Input Validation (OWASP A1)

The `InputValidator` class automatically protects against:

- SQL injection attacks
- XSS attacks
- Command injection
- Path traversal

**Usage:**

```python
from security.input_validator import InputValidator

validator = InputValidator()
result = validator.validate_chat_message(user_input)

if not result['valid']:
    return jsonify({'error': result['error']}), 400
```

### Step 2: Authentication & Authorization (OWASP A2)

The `APISecurityManager` provides:

- API key validation
- Rate limiting
- IP blocking
- Failed attempt tracking

**Usage:**

```python
from security.api_security import APISecurityManager

security_manager = APISecurityManager()

# Check API key
if not security_manager.validate_api_key(provided_key):
    return jsonify({'error': 'Invalid API key'}), 401

# Check rate limit
if not security_manager.check_rate_limit(client_ip):
    return jsonify({'error': 'Rate limit exceeded'}), 429
```

### Step 3: Data Protection (OWASP A3)

The `DataProtection` class handles:

- Sensitive data encryption
- Password hashing
- Secure configuration management

**Usage:**

```python
from security.data_protection import DataProtection

data_protection = DataProtection()

# Encrypt sensitive data
encrypted_data = data_protection.encrypt_sensitive_data(sensitive_string)

# Decrypt when needed
decrypted_data = data_protection.decrypt_sensitive_data(encrypted_data)
```

### Step 4: Security Logging (OWASP A10)

The `SecurityLogger` provides comprehensive logging:

**Usage:**

```python
from security.security_logger import log_security_event, log_authentication_attempt

# Log security events
log_security_event("suspicious_activity", {
    "activity_type": "potential_attack",
    "details": {"pattern": "script_tag"}
})

# Log authentication attempts
log_authentication_attempt(success=True, user_id="user123")
```

## Integration with Existing Code

### 1. Update Your Main Server File

```python
# agents/crew_agent_server.py
from flask import Flask, request, jsonify
from security.flask_security_integration import FlaskSecurityIntegration, secure_endpoint
from security.security_logger import log_security_event

app = Flask(__name__)

# Initialize security
security = FlaskSecurityIntegration(app)

# Your existing imports and setup...

@app.route('/chat', methods=['POST'])
@secure_endpoint(require_auth=True, require_rate_limit=True, validate_input=True)
def chat():
    """Secure chat endpoint with all security measures"""
    try:
        data = request.get_json()
        message = data.get('message', '')

        # Your existing chat logic here
        # Input validation is already applied by the decorator

        # Process the message with your CrewAI agent
        response = your_crew_agent.process(message)

        return jsonify({
            'response': response,
            'timestamp': time.time()
        })

    except Exception as e:
        log_security_event("application_error", {
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        return jsonify({
            'error': 'Internal server error',
            'error_type': 'internal_error'
        }), 500

@app.route('/health', methods=['GET'])
@secure_endpoint(require_auth=False, require_rate_limit=False, validate_input=False)
def health():
    """Health check endpoint (no security required)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'security_enabled': True
    })
```

### 2. Add Security Monitoring

Create a new endpoint for security monitoring:

```python
@app.route('/security/status', methods=['GET'])
@secure_endpoint(require_auth=True, require_rate_limit=True, validate_input=False)
def security_status():
    """Get security status (admin only)"""
    from security.flask_security_integration import get_security_status

    return jsonify(get_security_status())
```

### 3. Update Your Configuration

Add security settings to your configuration:

```python
# utils/config.py
import os

class SecurityConfig:
    API_KEY = os.getenv('API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 300))
    MAX_REQUESTS_PER_WINDOW = int(os.getenv('MAX_REQUESTS_PER_WINDOW', 100))
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    DEBUG = os.getenv('FLASK_ENV') == 'development'
```

## Deployment-Specific Security

### Railway Deployment

For Railway deployment, ensure these environment variables are set:

```bash
# In Railway dashboard
API_KEY=your_secure_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
RATE_LIMIT_WINDOW=300
MAX_REQUESTS_PER_WINDOW=200
```

### OpenOcean Deployment

For OpenOcean deployment:

```bash
# In OpenOcean environment
API_KEY=your_secure_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
RATE_LIMIT_WINDOW=300
MAX_REQUESTS_PER_WINDOW=300
```

### Langraph Deployment

For Langraph deployment:

```bash
# In Langraph environment
API_KEY=your_secure_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
RATE_LIMIT_WINDOW=300
MAX_REQUESTS_PER_WINDOW=150
```

## Testing Security Measures

### 1. Test Input Validation

```bash
# Test SQL injection
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"message": "'; DROP TABLE users; --"}'

# Should return: {"error": "Potential SQL injection detected"}

# Test XSS
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"message": "<script>alert(\"xss\")</script>"}'

# Should return: {"error": "Potential XSS attack detected"}
```

### 2. Test Rate Limiting

```bash
# Make multiple requests quickly
for i in {1..101}; do
  curl -X POST https://your-app.railway.app/chat \
    -H "Content-Type: application/json" \
    -H "X-API-Key: your_api_key" \
    -d '{"message": "test message"}'
done

# After 100 requests, should return: {"error": "Rate limit exceeded"}
```

### 3. Test Authentication

```bash
# Test without API key
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test message"}'

# Should return: {"error": "Invalid or missing API key"}

# Test with invalid API key
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid_key" \
  -d '{"message": "test message"}'

# Should return: {"error": "Invalid or missing API key"}
```

## Monitoring and Alerts

### 1. Security Logs

Security events are logged to `security.log`:

```bash
# View security logs
tail -f security.log

# Search for specific events
grep "suspicious_activity" security.log
grep "rate_limit_exceeded" security.log
grep "authentication_attempt" security.log
```

### 2. Security Metrics

Access security metrics via the `/security/status` endpoint:

```bash
curl -X GET https://your-app.railway.app/security/status \
  -H "X-API-Key: your_api_key"
```

### 3. Set Up Alerts

Configure alerts for critical security events:

```python
# In your monitoring system
from security.security_logger import security_monitor

# Check for alerts
metrics = security_monitor.get_security_metrics()
if metrics['alerts_sent_today'] > 0:
    # Send notification to admin
    send_admin_alert("Security alerts detected")
```

## Maintenance

### 1. Regular Security Updates

```bash
# Update security dependencies
pip install --upgrade cryptography defusedxml safety

# Check for vulnerabilities
safety check

# Update all dependencies
pip install --upgrade -r requirements.txt
```

### 2. Security Monitoring

- Review security logs daily
- Monitor failed authentication attempts
- Check for suspicious activity patterns
- Update API keys regularly

### 3. Configuration Review

- Verify environment variables are set correctly
- Check rate limiting settings
- Review access control policies
- Update security headers as needed

## Troubleshooting

### Common Issues

1. **"Invalid API key" errors**

   - Check `API_KEY` environment variable
   - Verify API key format
   - Check request headers

2. **"Rate limit exceeded" errors**

   - Adjust `MAX_REQUESTS_PER_WINDOW` setting
   - Check `RATE_LIMIT_WINDOW` setting
   - Review client request patterns

3. **"Input validation failed" errors**

   - Check input format
   - Review validation rules
   - Check for special characters

4. **Security logs not appearing**
   - Check file permissions
   - Verify logging configuration
   - Check disk space

### Debug Mode

Enable debug mode for detailed security information:

```bash
# Set environment variable
export FLASK_ENV=development

# Or in your .env file
FLASK_ENV=development
```

## Support

For security-related issues:

1. Check the security logs first
2. Review the security status endpoint
3. Verify environment configuration
4. Check the OWASP Top 10 documentation
5. Contact your security team if needed

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Python Security Best Practices](https://python.org/dev/security/)
- [Railway Security Guide](https://docs.railway.app/security/)
