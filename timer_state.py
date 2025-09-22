"""
Pomodoro Timer State Management System
Implements a state machine for IDLE→FOCUS_RUNNING→PAUSE/RESUME→BREAK_RUNNING→IDLE transitions
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TimerState(Enum):
    """Timer states for Pomodoro technique"""
    IDLE = "idle"
    FOCUS_RUNNING = "focus_running"
    FOCUS_PAUSED = "focus_paused"
    BREAK_RUNNING = "break_running"
    BREAK_PAUSED = "break_paused"


@dataclass
class TimerConfig:
    """Configuration for timer durations"""
    focus_duration: int = 25 * 60  # 25 minutes in seconds
    short_break_duration: int = 5 * 60  # 5 minutes in seconds
    long_break_duration: int = 15 * 60  # 15 minutes in seconds
    cycles_before_long_break: int = 4


class TimerStateError(Exception):
    """Exception raised for invalid state transitions"""
    pass


class TimerManager:
    """Manages Pomodoro timer state and transitions"""
    
    def __init__(self, config: Optional[TimerConfig] = None):
        self.config = config or TimerConfig()
        self.state = TimerState.IDLE
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        self.cycles_completed: int = 0
        self.current_duration: int = 0
        
        # Valid state transitions
        self.valid_transitions = {
            TimerState.IDLE: [TimerState.FOCUS_RUNNING],
            TimerState.FOCUS_RUNNING: [TimerState.FOCUS_PAUSED, TimerState.BREAK_RUNNING, TimerState.IDLE],
            TimerState.FOCUS_PAUSED: [TimerState.FOCUS_RUNNING, TimerState.IDLE],
            TimerState.BREAK_RUNNING: [TimerState.BREAK_PAUSED, TimerState.IDLE, TimerState.FOCUS_RUNNING],
            TimerState.BREAK_PAUSED: [TimerState.BREAK_RUNNING, TimerState.IDLE]
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current timer state information"""
        remaining_time = self._get_remaining_time()
        
        return {
            "state": self.state.value,
            "remaining_time": max(0, remaining_time),
            "elapsed_time": self.elapsed_time,
            "cycles_completed": self.cycles_completed,
            "current_duration": self.current_duration,
            "is_running": self.state in [TimerState.FOCUS_RUNNING, TimerState.BREAK_RUNNING]
        }
    
    def start_focus(self) -> Dict[str, Any]:
        """Start a focus session"""
        if not self._can_transition_to(TimerState.FOCUS_RUNNING):
            raise TimerStateError(f"Cannot start focus from {self.state.value}")
        
        self._transition_to(TimerState.FOCUS_RUNNING)
        self.current_duration = self.config.focus_duration
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.pause_time = None
        
        logger.info(f"Started focus session - Duration: {self.current_duration}s")
        return self.get_state()
    
    def pause(self) -> Dict[str, Any]:
        """Pause current session"""
        if self.state == TimerState.FOCUS_RUNNING:
            target_state = TimerState.FOCUS_PAUSED
        elif self.state == TimerState.BREAK_RUNNING:
            target_state = TimerState.BREAK_PAUSED
        else:
            raise TimerStateError(f"Cannot pause from {self.state.value}")
        
        if not self._can_transition_to(target_state):
            raise TimerStateError(f"Cannot pause from {self.state.value}")
        
        self._update_elapsed_time()
        self.pause_time = time.time()
        self._transition_to(target_state)
        
        logger.info(f"Paused session - Elapsed: {self.elapsed_time}s")
        return self.get_state()
    
    def resume(self) -> Dict[str, Any]:
        """Resume paused session"""
        if self.state == TimerState.FOCUS_PAUSED:
            target_state = TimerState.FOCUS_RUNNING
        elif self.state == TimerState.BREAK_PAUSED:
            target_state = TimerState.BREAK_RUNNING
        else:
            raise TimerStateError(f"Cannot resume from {self.state.value}")
        
        if not self._can_transition_to(target_state):
            raise TimerStateError(f"Cannot resume from {self.state.value}")
        
        self.start_time = time.time() - self.elapsed_time
        self.pause_time = None
        self._transition_to(target_state)
        
        logger.info(f"Resumed session - Remaining: {self._get_remaining_time()}s")
        return self.get_state()
    
    def reset(self) -> Dict[str, Any]:
        """Reset timer to idle state"""
        self._transition_to(TimerState.IDLE)
        self.start_time = None
        self.pause_time = None
        self.elapsed_time = 0.0
        self.current_duration = 0
        
        logger.info("Timer reset to idle state")
        return self.get_state()
    
    def _update_elapsed_time(self):
        """Update elapsed time based on current time"""
        if self.start_time and not self.pause_time:
            self.elapsed_time = time.time() - self.start_time
    
    def _get_remaining_time(self) -> float:
        """Calculate remaining time in current session"""
        if self.state in [TimerState.FOCUS_PAUSED, TimerState.BREAK_PAUSED]:
            return max(0, self.current_duration - self.elapsed_time)
        elif self.state in [TimerState.FOCUS_RUNNING, TimerState.BREAK_RUNNING]:
            self._update_elapsed_time()
            return max(0, self.current_duration - self.elapsed_time)
        else:
            return 0.0
    
    def _can_transition_to(self, target_state: TimerState) -> bool:
        """Check if transition to target state is valid"""
        return target_state in self.valid_transitions.get(self.state, [])
    
    def _transition_to(self, new_state: TimerState):
        """Transition to new state with logging"""
        old_state = self.state
        self.state = new_state
        logger.info(f"State transition: {old_state.value} -> {new_state.value}")
    
    def check_auto_transitions(self) -> Optional[Dict[str, Any]]:
        """Check for automatic state transitions (when timer completes)"""
        if self.state in [TimerState.FOCUS_RUNNING, TimerState.BREAK_RUNNING]:
            remaining = self._get_remaining_time()
            
            if remaining <= 0:
                if self.state == TimerState.FOCUS_RUNNING:
                    # Focus session completed
                    self.cycles_completed += 1
                    
                    # Determine break type
                    if self.cycles_completed % self.config.cycles_before_long_break == 0:
                        break_duration = self.config.long_break_duration
                        logger.info(f"Focus completed! Starting long break ({break_duration}s)")
                    else:
                        break_duration = self.config.short_break_duration
                        logger.info(f"Focus completed! Starting short break ({break_duration}s)")
                    
                    # Auto-start break
                    self._transition_to(TimerState.BREAK_RUNNING)
                    self.current_duration = break_duration
                    self.start_time = time.time()
                    self.elapsed_time = 0.0
                    self.pause_time = None
                    
                    return self.get_state()
                
                elif self.state == TimerState.BREAK_RUNNING:
                    # Break session completed
                    logger.info("Break completed! Ready for next focus session")
                    self._transition_to(TimerState.IDLE)
                    self.start_time = None
                    self.pause_time = None
                    self.elapsed_time = 0.0
                    self.current_duration = 0
                    
                    return self.get_state()
        
        return None