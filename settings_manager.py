import json
import os
from typing import Dict, Any
from pomodoro_timer import PomodoroSettings, SoundSettings, WorkDuration, BreakDuration, Theme


class SettingsManager:
    """Manages Pomodoro timer settings persistence and validation"""
    
    def __init__(self, config_file: str = "pomodoro_settings.json"):
        self.config_file = config_file
        self.default_settings = PomodoroSettings()
    
    def load_settings(self) -> PomodoroSettings:
        """Load settings from file or return defaults"""
        if not os.path.exists(self.config_file):
            return self.default_settings
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return self._dict_to_settings(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading settings: {e}. Using defaults.")
            return self.default_settings
    
    def save_settings(self, settings: PomodoroSettings) -> bool:
        """Save settings to file"""
        try:
            data = self._settings_to_dict(settings)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def update_work_duration(self, settings: PomodoroSettings, duration_minutes: int) -> PomodoroSettings:
        """Update work duration setting"""
        for duration in WorkDuration:
            if duration.value == duration_minutes:
                settings.work_duration = duration
                break
        return settings
    
    def update_break_duration(self, settings: PomodoroSettings, duration_minutes: int) -> PomodoroSettings:
        """Update break duration setting"""
        for duration in BreakDuration:
            if duration.value == duration_minutes:
                settings.break_duration = duration
                break
        return settings
    
    def update_theme(self, settings: PomodoroSettings, theme_name: str) -> PomodoroSettings:
        """Update theme setting"""
        for theme in Theme:
            if theme.value == theme_name:
                settings.theme = theme
                break
        return settings
    
    def update_sound_settings(self, settings: PomodoroSettings, 
                             start_sound: bool = None, 
                             end_sound: bool = None, 
                             tick_sound: bool = None) -> PomodoroSettings:
        """Update sound settings"""
        if start_sound is not None:
            settings.sound_settings.start_sound = start_sound
        if end_sound is not None:
            settings.sound_settings.end_sound = end_sound
        if tick_sound is not None:
            settings.sound_settings.tick_sound = tick_sound
        return settings
    
    def get_available_options(self) -> Dict[str, Any]:
        """Get all available configuration options"""
        return {
            "work_durations": [duration.value for duration in WorkDuration],
            "break_durations": [duration.value for duration in BreakDuration],
            "themes": [theme.value for theme in Theme],
            "sound_options": ["start_sound", "end_sound", "tick_sound"]
        }
    
    def _settings_to_dict(self, settings: PomodoroSettings) -> Dict[str, Any]:
        """Convert settings object to dictionary"""
        return {
            "work_duration": settings.work_duration.value,
            "break_duration": settings.break_duration.value,
            "theme": settings.theme.value,
            "sound_settings": {
                "start_sound": settings.sound_settings.start_sound,
                "end_sound": settings.sound_settings.end_sound,
                "tick_sound": settings.sound_settings.tick_sound
            }
        }
    
    def _dict_to_settings(self, data: Dict[str, Any]) -> PomodoroSettings:
        """Convert dictionary to settings object"""
        # Find matching work duration
        work_duration = WorkDuration.STANDARD
        for duration in WorkDuration:
            if duration.value == data.get("work_duration", 25):
                work_duration = duration
                break
        
        # Find matching break duration
        break_duration = BreakDuration.SHORT
        for duration in BreakDuration:
            if duration.value == data.get("break_duration", 5):
                break_duration = duration
                break
        
        # Find matching theme
        theme = Theme.LIGHT
        for t in Theme:
            if t.value == data.get("theme", "light"):
                theme = t
                break
        
        # Parse sound settings
        sound_data = data.get("sound_settings", {})
        sound_settings = SoundSettings(
            start_sound=sound_data.get("start_sound", True),
            end_sound=sound_data.get("end_sound", True),
            tick_sound=sound_data.get("tick_sound", False)
        )
        
        return PomodoroSettings(
            work_duration=work_duration,
            break_duration=break_duration,
            theme=theme,
            sound_settings=sound_settings
        )
    
    def reset_to_defaults(self) -> PomodoroSettings:
        """Reset settings to defaults and save"""
        settings = PomodoroSettings()
        self.save_settings(settings)
        return settings
    
    def validate_settings(self, settings: PomodoroSettings) -> bool:
        """Validate settings object"""
        try:
            # Check if all enum values are valid
            assert isinstance(settings.work_duration, WorkDuration)
            assert isinstance(settings.break_duration, BreakDuration)
            assert isinstance(settings.theme, Theme)
            assert isinstance(settings.sound_settings, SoundSettings)
            
            # Check sound settings types
            assert isinstance(settings.sound_settings.start_sound, bool)
            assert isinstance(settings.sound_settings.end_sound, bool)
            assert isinstance(settings.sound_settings.tick_sound, bool)
            
            return True
        except (AssertionError, AttributeError):
            return False