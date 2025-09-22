#!/usr/bin/env python3
"""
Demo script for Pomodoro Timer API
Shows complete workflow with shortened durations for demonstration
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def make_request(method, endpoint, data=None):
    """Make API request and display result"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔄 {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            if 'state' in result:
                state = result['state']
                remaining = result.get('remaining_time', 0)
                elapsed = result.get('elapsed_time', 0)
                cycles = result.get('cycles_completed', 0)
                print(f"   State: {state}")
                if remaining > 0:
                    print(f"   Remaining: {remaining:.1f}s")
                if elapsed > 0:
                    print(f"   Elapsed: {elapsed:.1f}s")
                if cycles > 0:
                    print(f"   Cycles: {cycles}")
            else:
                print(f"   Response: {result}")
        else:
            print(f"   Error: {result}")
        
        return result
    except Exception as e:
        print(f"   Error: {e}")
        return None

def wait_with_progress(seconds, message="Waiting"):
    """Wait with progress dots"""
    print(f"\n⏳ {message} for {seconds} seconds", end="")
    for i in range(seconds):
        print(".", end="", flush=True)
        time.sleep(1)
    print(" Done!")

def main():
    """Demo the Pomodoro Timer API"""
    print("🍅 Pomodoro Timer API Demo")
    print("=" * 50)
    
    # 1. Check health
    make_request("GET", "/health")
    
    # 2. Get initial state
    make_request("GET", "/api/timer/state")
    
    # 3. Get configuration
    config = make_request("GET", "/api/timer/config")
    if config:
        print(f"\n📋 Timer Configuration:")
        print(f"   Focus Duration: {config['focus_duration']}s ({config['focus_duration']//60}min)")
        print(f"   Short Break: {config['short_break_duration']}s ({config['short_break_duration']//60}min)")
        print(f"   Long Break: {config['long_break_duration']}s ({config['long_break_duration']//60}min)")
    
    # 4. Start a focus session
    print(f"\n🎯 Starting Focus Session")
    make_request("POST", "/api/timer/start")
    
    # 5. Let it run for a few seconds
    wait_with_progress(3, "Focus session running")
    
    # 6. Check state
    make_request("GET", "/api/timer/state")
    
    # 7. Pause the session
    print(f"\n⏸️  Pausing Focus Session")
    make_request("POST", "/api/timer/pause")
    
    # 8. Wait while paused
    wait_with_progress(2, "Session paused")
    
    # 9. Check state while paused
    make_request("GET", "/api/timer/state")
    
    # 10. Resume the session
    print(f"\n▶️  Resuming Focus Session")
    make_request("POST", "/api/timer/resume")
    
    # 11. Try invalid transition
    print(f"\n❌ Testing Invalid Transition (start while running)")
    make_request("POST", "/api/timer/start")
    
    # 12. Try another invalid transition (resume while running)
    print(f"\n❌ Testing Invalid Transition (pause from wrong state)")
    make_request("POST", "/api/timer/reset")
    make_request("POST", "/api/timer/resume")  # Should fail - can't resume from idle
    
    # 13. Final state check
    print(f"\n📊 Final State Check")
    make_request("GET", "/api/timer/state")
    
    print(f"\n✅ Demo completed!")
    print(f"\n💡 The timer supports the full Pomodoro workflow:")
    print(f"   • IDLE → FOCUS_RUNNING → FOCUS_PAUSED/RESUME → BREAK_RUNNING → IDLE")
    print(f"   • Auto-transitions when sessions complete")
    print(f"   • Error handling for invalid state transitions (409 status)")
    print(f"   • Comprehensive logging of all state changes")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()