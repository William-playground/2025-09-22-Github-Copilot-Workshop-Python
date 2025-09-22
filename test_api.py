#!/usr/bin/env python3
"""
Test script for timer API endpoints
"""

import requests
import time
import json
import sys

BASE_URL = "http://localhost:5000"

def test_api_endpoint(method, endpoint, expected_status=200, data=None):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"{method} {endpoint} -> {response.status_code}")
        if response.status_code == expected_status:
            print(f"✓ Response: {response.json()}")
            return response.json()
        else:
            print(f"✗ Expected {expected_status}, got {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed to {url}")
        print("  Make sure the API server is running on localhost:5000")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def main():
    """Test the timer API"""
    print("Testing Timer API Endpoints...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check")
    result = test_api_endpoint("GET", "/health")
    if not result:
        print("❌ Health check failed - server may not be running")
        return False
    
    # Test 2: Get initial state
    print("\n2. Get Initial State")
    result = test_api_endpoint("GET", "/api/timer/state")
    if not result or result.get('state') != 'idle':
        print("❌ Initial state test failed")
        return False
    
    # Test 3: Start timer
    print("\n3. Start Timer")
    result = test_api_endpoint("POST", "/api/timer/start")
    if not result or result.get('state') != 'focus_running':
        print("❌ Start timer test failed")
        return False
    
    # Test 4: Pause timer
    print("\n4. Pause Timer")
    time.sleep(1)  # Let it run for a moment
    result = test_api_endpoint("POST", "/api/timer/pause")
    if not result or result.get('state') != 'focus_paused':
        print("❌ Pause timer test failed")
        return False
    
    # Test 5: Resume timer
    print("\n5. Resume Timer")
    result = test_api_endpoint("POST", "/api/timer/resume")
    if not result or result.get('state') != 'focus_running':
        print("❌ Resume timer test failed")
        return False
    
    # Test 6: Reset timer
    print("\n6. Reset Timer")
    result = test_api_endpoint("POST", "/api/timer/reset")
    if not result or result.get('state') != 'idle':
        print("❌ Reset timer test failed")
        return False
    
    # Test 7: Invalid transition (start while already started)
    print("\n7. Invalid Transition Test")
    test_api_endpoint("POST", "/api/timer/start")  # Start first
    result = test_api_endpoint("POST", "/api/timer/start", expected_status=409)  # Should fail
    if result and result.get('type') == 'invalid_transition':
        print("✓ Invalid transition correctly rejected")
    else:
        print("❌ Invalid transition test failed")
        return False
    
    # Test 8: Get config
    print("\n8. Get Configuration")
    result = test_api_endpoint("GET", "/api/timer/config")
    if not result or 'focus_duration' not in result:
        print("❌ Get config test failed")
        return False
    
    print("\n🎉 All API tests passed!")
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1)