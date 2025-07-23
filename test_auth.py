#!/usr/bin/env python3
"""
Simple test script to verify API authentication implementation
"""

import requests
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '.')

# Test configuration
BASE_URL = 'http://localhost:5000/api'
TEST_API_KEY = 'ai-video-gpt-default-key-2025'
INVALID_API_KEY = 'invalid-key-12345'

def test_endpoint(endpoint, method='GET', api_key=None, expected_status=200, description=""):
    """Test an API endpoint with optional authentication"""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if api_key:
        headers['X-API-Key'] = api_key
    
    print(f"Testing {method} {endpoint} - {description}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json={}, timeout=10)
        
        print(f"  Status: {response.status_code} (expected: {expected_status})")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"  Response (text): {response.text[:200]}...")
        else:
            print(f"  Response (text): {response.text[:200]}...")
        
        success = response.status_code == expected_status
        print(f"  Result: {'✅ PASS' if success else '❌ FAIL'}")
        print()
        return success
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ CONNECTION ERROR: Flask app is not running")
        print(f"  Please start the Flask app first: python3 app.py")
        print()
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        print()
        return False

def main():
    print("🧪 Testing AI Video GPT API Authentication Implementation\n")
    
    tests = [
        # Public endpoints (should work without API key)
        ('/health', 'GET', None, 200, "Health check (public)"),
        ('/auth/info', 'GET', None, 200, "Auth info (public)"),
        
        # Authentication validation
        ('/auth/validate', 'POST', TEST_API_KEY, 200, "Validate API key (valid key)"),
        ('/auth/validate', 'POST', INVALID_API_KEY, 401, "Validate API key (invalid key)"),
        ('/auth/validate', 'POST', None, 401, "Validate API key (no key)"),
        
        # Protected endpoints with valid key
        ('/jobs', 'GET', TEST_API_KEY, 200, "List jobs (valid key)"),
        ('/image-presets', 'GET', TEST_API_KEY, 200, "Get image presets (valid key)"),
        
        # Protected endpoints with invalid key
        ('/jobs', 'GET', INVALID_API_KEY, 401, "List jobs (invalid key)"),
        ('/image-presets', 'GET', None, 401, "Get image presets (no key)"),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, api_key, expected_status, description in tests:
        if test_endpoint(endpoint, method, api_key, expected_status, description):
            passed += 1
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)