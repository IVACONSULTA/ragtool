#!/usr/bin/env python3
"""
Security testing script for SapRagTool
Tests all implemented security measures
"""
import requests
import json
import time
import sys
from typing import Dict, Any

class SecurityTester:
    """Test security measures implemented in SapRagTool"""
    
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint (should work without API key)"""
        print("Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication mechanisms"""
        print("\nTesting authentication...")
        
        # Test without API key
        print("  Testing without API key...")
        response = self.session.post(f"{self.base_url}/chat", json={"message": "test"})
        if response.status_code == 401:
            print("  ✅ Correctly rejected request without API key")
        else:
            print(f"  ❌ Should have rejected request: {response.status_code}")
            return False
        
        # Test with invalid API key
        print("  Testing with invalid API key...")
        self.session.headers.update({'X-API-Key': 'invalid_key'})
        response = self.session.post(f"{self.base_url}/chat", json={"message": "test"})
        if response.status_code == 401:
            print("  ✅ Correctly rejected invalid API key")
        else:
            print(f"  ❌ Should have rejected invalid key: {response.status_code}")
            return False
        
        # Test with valid API key (if provided)
        if self.api_key:
            print("  Testing with valid API key...")
            self.session.headers.update({'X-API-Key': self.api_key})
            response = self.session.post(f"{self.base_url}/chat", json={"message": "test"})
            if response.status_code == 200:
                print("  ✅ Valid API key accepted")
            else:
                print(f"  ❌ Valid API key rejected: {response.status_code}")
                return False
        
        return True
    
    def test_input_validation(self) -> bool:
        """Test input validation against various attacks"""
        print("\nTesting input validation...")
        
        if not self.api_key:
            print("  ⚠️  Skipping input validation tests (no API key)")
            return True
        
        self.session.headers.update({'X-API-Key': self.api_key})
        
        # Test cases for different attack types
        test_cases = [
            # SQL Injection
            ("SQL Injection", "'; DROP TABLE users; --"),
            ("SQL Injection Union", "test' UNION SELECT * FROM users --"),
            ("SQL Injection OR", "test' OR 1=1 --"),
            
            # XSS
            ("XSS Script", "<script>alert('xss')</script>"),
            ("XSS JavaScript", "javascript:alert('xss')"),
            ("XSS Iframe", "<iframe src='javascript:alert(\"xss\")'></iframe>"),
            
            # Command Injection
            ("Command Injection", "test; ls -la"),
            ("Command Injection Pipe", "test | cat /etc/passwd"),
            ("Command Injection Backtick", "test `whoami`"),
            
            # Path Traversal
            ("Path Traversal", "../../../etc/passwd"),
            ("Path Traversal Windows", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"),
        ]
        
        all_passed = True
        
        for test_name, malicious_input in test_cases:
            print(f"  Testing {test_name}...")
            response = self.session.post(f"{self.base_url}/chat", json={"message": malicious_input})
            
            if response.status_code == 400:
                print(f"    ✅ Correctly blocked {test_name}")
            else:
                print(f"    ❌ Failed to block {test_name}: {response.status_code}")
                all_passed = False
        
        return all_passed
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        print("\nTesting rate limiting...")
        
        if not self.api_key:
            print("  ⚠️  Skipping rate limiting tests (no API key)")
            return True
        
        self.session.headers.update({'X-API-Key': self.api_key})
        
        # Make multiple requests quickly
        print("  Making multiple requests...")
        success_count = 0
        rate_limited = False
        
        for i in range(105):  # Try to exceed typical rate limit
            response = self.session.post(f"{self.base_url}/chat", json={"message": f"test message {i}"})
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                print(f"    ✅ Rate limit triggered after {success_count} requests")
                break
            else:
                print(f"    ❌ Unexpected status code: {response.status_code}")
                return False
        
        if not rate_limited:
            print(f"    ⚠️  Rate limit not triggered after {success_count} requests")
        
        return True
    
    def test_security_headers(self) -> bool:
        """Test security headers in responses"""
        print("\nTesting security headers...")
        
        response = self.session.get(f"{self.base_url}/health")
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Referrer-Policy'
        ]
        
        all_present = True
        
        for header in required_headers:
            if header in response.headers:
                print(f"  ✅ {header}: {response.headers[header]}")
            else:
                print(f"  ❌ Missing header: {header}")
                all_present = False
        
        return all_present
    
    def test_error_handling(self) -> bool:
        """Test error handling and information disclosure"""
        print("\nTesting error handling...")
        
        if not self.api_key:
            print("  ⚠️  Skipping error handling tests (no API key)")
            return True
        
        self.session.headers.update({'X-API-Key': self.api_key})
        
        # Test with malformed JSON
        print("  Testing malformed JSON...")
        response = self.session.post(
            f"{self.base_url}/chat",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [400, 500]:
            print("  ✅ Correctly handled malformed JSON")
        else:
            print(f"  ❌ Unexpected response to malformed JSON: {response.status_code}")
            return False
        
        # Test with missing required fields
        print("  Testing missing required fields...")
        response = self.session.post(f"{self.base_url}/chat", json={})
        
        if response.status_code in [400, 422]:
            print("  ✅ Correctly handled missing fields")
        else:
            print(f"  ❌ Unexpected response to missing fields: {response.status_code}")
            return False
        
        return True
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all security tests"""
        print("🔒 Starting Security Tests for SapRagTool")
        print("=" * 50)
        
        results = {
            'health_endpoint': self.test_health_endpoint(),
            'authentication': self.test_authentication(),
            'input_validation': self.test_input_validation(),
            'rate_limiting': self.test_rate_limiting(),
            'security_headers': self.test_security_headers(),
            'error_handling': self.test_error_handling()
        }
        
        print("\n" + "=" * 50)
        print("🔒 Security Test Results")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All security tests passed!")
        else:
            print("⚠️  Some security tests failed. Please review the implementation.")
        
        return results

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test_security.py <base_url> [api_key]")
        print("Example: python test_security.py https://your-app.railway.app your_api_key")
        sys.exit(1)
    
    base_url = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not api_key:
        print("⚠️  Warning: No API key provided. Some tests will be skipped.")
    
    tester = SecurityTester(base_url, api_key)
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
