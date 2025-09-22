#!/usr/bin/env python3
"""
Test script for Pomodoro Session API
Tests all the core functionality including database persistence and API endpoints
"""

import requests
import time
import json
from datetime import datetime


def test_pomodoro_api():
    """Test the Pomodoro API functionality"""
    base_url = "http://localhost:5000"
    
    print("🍅 Pomodoro API Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    response = requests.get(f"{base_url}/api/health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["success"] is True
    print("   ✅ Health check passed")
    
    # Test 2: Get initial stats
    print("\n2. Testing today's stats (initial)...")
    response = requests.get(f"{base_url}/api/stats/today")
    assert response.status_code == 200
    initial_stats = response.json()
    assert initial_stats["success"] is True
    initial_count = initial_stats["data"]["total_sessions"]
    print(f"   ✅ Initial sessions today: {initial_count}")
    
    # Test 3: Check session status (should be no active session)
    print("\n3. Testing session status (no active session)...")
    response = requests.get(f"{base_url}/api/session/status")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["success"] is True
    assert status_data["data"]["is_running"] is False
    print("   ✅ No active session confirmed")
    
    # Test 4: Start a new session
    print("\n4. Testing session start...")
    session_data = {
        "duration_minutes": 1,
        "task_description": "Test Session for API"
    }
    response = requests.post(f"{base_url}/api/session/start", json=session_data)
    assert response.status_code == 200
    start_data = response.json()
    assert start_data["success"] is True
    assert start_data["data"]["duration_minutes"] == 1
    print("   ✅ Session started successfully")
    
    # Test 5: Check session status (should be active)
    print("\n5. Testing session status (active session)...")
    response = requests.get(f"{base_url}/api/session/status")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["success"] is True
    assert status_data["data"]["is_running"] is True
    elapsed_time = status_data["data"]["session"]["elapsed_minutes"]
    remaining_time = status_data["data"]["session"]["remaining_minutes"]
    print(f"   ✅ Active session: {elapsed_time:.2f}min elapsed, {remaining_time:.2f}min remaining")
    
    # Test 6: Try to start another session (should fail)
    print("\n6. Testing duplicate session start (should fail)...")
    response = requests.post(f"{base_url}/api/session/start", json=session_data)
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["success"] is False
    print("   ✅ Duplicate session prevented")
    
    # Test 7: Wait a bit and check time progression
    print("\n7. Testing time progression...")
    time.sleep(2)
    response = requests.get(f"{base_url}/api/session/status")
    status_data = response.json()
    new_elapsed = status_data["data"]["session"]["elapsed_minutes"]
    assert new_elapsed > elapsed_time
    print(f"   ✅ Time progressed: {new_elapsed:.2f}min elapsed")
    
    # Test 8: Complete the session
    print("\n8. Testing session completion...")
    response = requests.post(f"{base_url}/api/session/complete")
    assert response.status_code == 200
    complete_data = response.json()
    assert complete_data["success"] is True
    assert complete_data["data"]["completed"] is True
    session_id = complete_data["data"]["session_id"]
    print(f"   ✅ Session completed with ID: {session_id}")
    
    # Test 9: Verify no active session after completion
    print("\n9. Testing session status after completion...")
    response = requests.get(f"{base_url}/api/session/status")
    status_data = response.json()
    assert status_data["data"]["is_running"] is False
    print("   ✅ No active session after completion")
    
    # Test 10: Check updated stats
    print("\n10. Testing updated today's stats...")
    response = requests.get(f"{base_url}/api/stats/today")
    final_stats = response.json()
    final_count = final_stats["data"]["total_sessions"]
    completed_count = final_stats["data"]["completed_sessions"]
    assert final_count == initial_count + 1
    assert completed_count >= 1
    print(f"   ✅ Stats updated: {final_count} total, {completed_count} completed")
    
    # Test 11: Test session cancellation
    print("\n11. Testing session cancellation...")
    # Start another session
    response = requests.post(f"{base_url}/api/session/start", json={
        "duration_minutes": 5,
        "task_description": "Session to be cancelled"
    })
    assert response.status_code == 200
    
    # Cancel it
    response = requests.post(f"{base_url}/api/session/cancel")
    assert response.status_code == 200
    cancel_data = response.json()
    assert cancel_data["success"] is True
    assert cancel_data["data"]["completed"] is False
    print("   ✅ Session cancelled successfully")
    
    # Test 12: Invalid duration test
    print("\n12. Testing invalid session duration...")
    response = requests.post(f"{base_url}/api/session/start", json={
        "duration_minutes": 0  # Invalid
    })
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["success"] is False
    print("   ✅ Invalid duration rejected")
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Pomodoro API is working correctly.")
    print("\nKey features verified:")
    print("  • Session creation and management")
    print("  • Database persistence")
    print("  • Time tracking and statistics")
    print("  • Error handling and validation")
    print("  • RESTful API endpoints")


if __name__ == "__main__":
    try:
        test_pomodoro_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("Please start the server first with: python3 pomodoro_api.py")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")