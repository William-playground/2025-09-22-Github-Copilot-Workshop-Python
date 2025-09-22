import time
import threading
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional


class TimerState(Enum):
    """Timer state enumeration"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"


class Theme(Enum):
    """UI theme options"""
    LIGHT = "light"
    DARK = "dark"
    FOCUS = "focus"


class WorkDuration(Enum):
    """Work session duration options in minutes"""
    SHORT = 15
    STANDARD = 25
    LONG = 35
    EXTENDED = 45


class BreakDuration(Enum):
    """Break duration options in minutes"""
    SHORT = 5
    MEDIUM = 10
    LONG = 15


@dataclass
class SoundSettings:
    """Sound configuration settings"""
    start_sound: bool = True
    end_sound: bool = True
    tick_sound: bool = False


@dataclass
class PomodoroSettings:
    """Pomodoro timer configuration settings"""
    work_duration: WorkDuration = WorkDuration.STANDARD
    break_duration: BreakDuration = BreakDuration.SHORT
    theme: Theme = Theme.LIGHT
    sound_settings: SoundSettings = None
    
    def __post_init__(self):
        if self.sound_settings is None:
            self.sound_settings = SoundSettings()


class PomodoroTimer:
    """Customizable Pomodoro Timer implementation"""
    
    def __init__(self, settings: PomodoroSettings = None):
        self.settings = settings or PomodoroSettings()
        self.state = TimerState.STOPPED
        self.time_remaining = self.settings.work_duration.value * 60  # Convert to seconds
        self.is_work_session = True
        self.session_count = 0
        
        # Timer thread control
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Event callbacks
        self.on_timer_started: Optional[Callable] = None
        self.on_timer_stopped: Optional[Callable] = None
        self.on_timer_paused: Optional[Callable] = None
        self.on_timer_resumed: Optional[Callable] = None
        self.on_timer_finished: Optional[Callable] = None
        self.on_session_changed: Optional[Callable] = None
        self.on_tick: Optional[Callable[[int], None]] = None
    
    def start(self):
        """Start the timer"""
        if self.state == TimerState.RUNNING:
            return
        
        if self.state == TimerState.STOPPED:
            self._reset_timer()
        
        self.state = TimerState.RUNNING
        self._stop_event.clear()
        
        if self.settings.sound_settings.start_sound:
            self._play_start_sound()
        
        self._timer_thread = threading.Thread(target=self._timer_loop)
        self._timer_thread.daemon = True
        self._timer_thread.start()
        
        if self.on_timer_started:
            self.on_timer_started()
    
    def stop(self):
        """Stop the timer"""
        if self.state == TimerState.STOPPED:
            return
        
        self.state = TimerState.STOPPED
        self._stop_event.set()
        
        if self._timer_thread:
            self._timer_thread.join()
        
        self._reset_timer()
        
        if self.on_timer_stopped:
            self.on_timer_stopped()
    
    def pause(self):
        """Pause the timer"""
        if self.state != TimerState.RUNNING:
            return
        
        self.state = TimerState.PAUSED
        self._stop_event.set()
        
        if self._timer_thread:
            self._timer_thread.join()
        
        if self.on_timer_paused:
            self.on_timer_paused()
    
    def resume(self):
        """Resume the paused timer"""
        if self.state != TimerState.PAUSED:
            return
        
        self.state = TimerState.RUNNING
        self._stop_event.clear()
        
        self._timer_thread = threading.Thread(target=self._timer_loop)
        self._timer_thread.daemon = True
        self._timer_thread.start()
        
        if self.on_timer_resumed:
            self.on_timer_resumed()
    
    def update_settings(self, new_settings: PomodoroSettings):
        """Update timer settings"""
        was_running = self.state == TimerState.RUNNING
        if was_running:
            self.pause()
        
        self.settings = new_settings
        self._reset_timer()
        
        if was_running:
            self.resume()
    
    def get_formatted_time(self) -> str:
        """Get formatted time remaining as MM:SS"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_session_info(self) -> dict:
        """Get current session information"""
        return {
            "session_type": "work" if self.is_work_session else "break",
            "session_count": self.session_count,
            "state": self.state.value,
            "time_remaining": self.time_remaining,
            "formatted_time": self.get_formatted_time(),
            "theme": self.settings.theme.value
        }
    
    def _reset_timer(self):
        """Reset timer to work session"""
        self.is_work_session = True
        self.time_remaining = self.settings.work_duration.value * 60
        self.session_count = 0
    
    def _timer_loop(self):
        """Main timer loop running in separate thread"""
        while not self._stop_event.is_set() and self.time_remaining > 0:
            time.sleep(1)
            if not self._stop_event.is_set():
                self.time_remaining -= 1
                
                if self.settings.sound_settings.tick_sound:
                    self._play_tick_sound()
                
                if self.on_tick:
                    self.on_tick(self.time_remaining)
        
        if self.time_remaining <= 0 and not self._stop_event.is_set():
            self._timer_finished()
    
    def _timer_finished(self):
        """Handle timer completion"""
        if self.settings.sound_settings.end_sound:
            self._play_end_sound()
        
        if self.is_work_session:
            # Switch to break
            self.is_work_session = False
            self.time_remaining = self.settings.break_duration.value * 60
            self.session_count += 1
            self.state = TimerState.BREAK
        else:
            # Switch back to work
            self.is_work_session = True
            self.time_remaining = self.settings.work_duration.value * 60
            self.state = TimerState.STOPPED
        
        if self.on_session_changed:
            self.on_session_changed()
        
        if self.on_timer_finished:
            self.on_timer_finished()
    
    def _play_start_sound(self):
        """Play start sound (placeholder)"""
        print("🔔 Timer started!")
    
    def _play_end_sound(self):
        """Play end sound (placeholder)"""
        print("🔔 Timer finished!")
    
    def _play_tick_sound(self):
        """Play tick sound (placeholder)"""
        print("tick", end="", flush=True)