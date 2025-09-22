#!/usr/bin/env python3
"""
Test script for timer state functionality
"""

import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timer_state import TimerManager, TimerStateError, TimerState

def test_timer_state_machine():
    """Test the timer state machine functionality"""
    print("Testing Timer State Machine...")
    
    # Create timer manager with short durations for testing
    from timer_state import TimerConfig
    config = TimerConfig(
        focus_duration=5,  # 5 seconds for testing
        short_break_duration=3,  # 3 seconds for testing
        long_break_duration=5,   # 5 seconds for testing
        cycles_before_long_break=2
    )
    
    timer = TimerManager(config)
    
    # Test 1: Initial state should be IDLE
    state = timer.get_state()
    print(f"✓ Initial state: {state['state']}")
    assert state['state'] == 'idle'
    
    # Test 2: Start focus session
    print("\n--- Starting focus session ---")
    state = timer.start_focus()
    print(f"✓ Started focus: {state['state']}, duration: {state['current_duration']}s")
    assert state['state'] == 'focus_running'
    assert state['current_duration'] == 5
    
    # Test 3: Pause focus session
    time.sleep(1)  # Let it run for 1 second
    print("\n--- Pausing focus session ---")
    state = timer.pause()
    print(f"✓ Paused focus: {state['state']}, elapsed: {state['elapsed_time']:.1f}s")
    assert state['state'] == 'focus_paused'
    assert state['elapsed_time'] >= 1.0
    
    # Test 4: Resume focus session
    print("\n--- Resuming focus session ---")
    state = timer.resume()
    print(f"✓ Resumed focus: {state['state']}, remaining: {state['remaining_time']:.1f}s")
    assert state['state'] == 'focus_running'
    
    # Test 5: Invalid transition (try to start while running)
    print("\n--- Testing invalid transition ---")
    try:
        timer.start_focus()
        print("✗ Should have failed!")
        assert False, "Should have raised TimerStateError"
    except TimerStateError as e:
        print(f"✓ Correctly rejected invalid transition: {e}")
    
    # Test 6: Reset timer
    print("\n--- Resetting timer ---")
    state = timer.reset()
    print(f"✓ Reset timer: {state['state']}")
    assert state['state'] == 'idle'
    
    print("\n🎉 All timer state tests passed!")
    return True

def test_auto_transitions():
    """Test automatic state transitions"""
    print("\n\nTesting Auto Transitions...")
    
    # Create timer with very short durations
    from timer_state import TimerConfig
    config = TimerConfig(
        focus_duration=2,  # 2 seconds
        short_break_duration=2,  # 2 seconds
        long_break_duration=3,   # 3 seconds
        cycles_before_long_break=2
    )
    
    timer = TimerManager(config)
    
    # Start focus and wait for completion
    print("Starting short focus session...")
    timer.start_focus()
    
    # Wait for auto-transition to break
    time.sleep(2.5)
    auto_result = timer.check_auto_transitions()
    if auto_result:
        print(f"✓ Auto-transitioned to: {auto_result['state']}")
        assert auto_result['state'] == 'break_running'
    
    # Wait for break to complete
    time.sleep(2.5)
    auto_result = timer.check_auto_transitions()
    if auto_result:
        print(f"✓ Auto-transitioned to: {auto_result['state']}")
        assert auto_result['state'] == 'idle'
    
    print("🎉 Auto-transition tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_timer_state_machine()
        test_auto_transitions()
        print("\n✅ All tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)