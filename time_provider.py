"""
Time provider abstraction for testable time operations.
"""
import time
from abc import ABC, abstractmethod
from typing import Protocol

class TimeProvider(Protocol):
    """Protocol for time provider implementations."""
    
    def current_time(self) -> float:
        """Return the current time as a float (seconds since epoch)."""
        ...
    
    def sleep(self, duration: float) -> None:
        """Sleep for the specified duration in seconds."""
        ...

class RealTimeProvider:
    """Real time provider using system time."""
    
    def current_time(self) -> float:
        """Return the current system time."""
        return time.time()
    
    def sleep(self, duration: float) -> None:
        """Sleep using system time."""
        time.sleep(duration)

class MockTimeProvider:
    """Mock time provider for testing."""
    
    def __init__(self, initial_time: float = 0.0):
        self._current_time = initial_time
    
    def current_time(self) -> float:
        """Return the mocked current time."""
        return self._current_time
    
    def sleep(self, duration: float) -> None:
        """Advance the mocked time by duration."""
        self._current_time += duration
    
    def advance_time(self, duration: float) -> None:
        """Manually advance the mocked time."""
        self._current_time += duration
    
    def set_time(self, new_time: float) -> None:
        """Set the mocked time to a specific value."""
        self._current_time = new_time

# Default time provider instance
default_time_provider: TimeProvider = RealTimeProvider()