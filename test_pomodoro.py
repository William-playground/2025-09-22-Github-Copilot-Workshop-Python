#!/usr/bin/env python3
"""
Comprehensive tests for the Pomodoro Timer functionality
ポモドーロタイマーの包括的テスト
"""

import unittest
import time
import threading
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

from pomodoro_timer import (
    PomodoroTimer, PomodoroSettings, SoundSettings,
    WorkDuration, BreakDuration, Theme, TimerState
)
from settings_manager import SettingsManager


class TestPomodoroSettings(unittest.TestCase):
    """Test Pomodoro settings configuration"""
    
    def test_default_settings(self):
        """Test default settings creation"""
        settings = PomodoroSettings()
        self.assertEqual(settings.work_duration, WorkDuration.STANDARD)
        self.assertEqual(settings.break_duration, BreakDuration.SHORT)
        self.assertEqual(settings.theme, Theme.LIGHT)
        self.assertIsNotNone(settings.sound_settings)
        self.assertTrue(settings.sound_settings.start_sound)
        self.assertTrue(settings.sound_settings.end_sound)
        self.assertFalse(settings.sound_settings.tick_sound)
    
    def test_custom_settings(self):
        """Test custom settings creation"""
        sound_settings = SoundSettings(start_sound=False, end_sound=True, tick_sound=True)
        settings = PomodoroSettings(
            work_duration=WorkDuration.LONG,
            break_duration=BreakDuration.MEDIUM,
            theme=Theme.DARK,
            sound_settings=sound_settings
        )
        
        self.assertEqual(settings.work_duration, WorkDuration.LONG)
        self.assertEqual(settings.break_duration, BreakDuration.MEDIUM)
        self.assertEqual(settings.theme, Theme.DARK)
        self.assertFalse(settings.sound_settings.start_sound)
        self.assertTrue(settings.sound_settings.end_sound)
        self.assertTrue(settings.sound_settings.tick_sound)
    
    def test_work_duration_values(self):
        """Test work duration enum values"""
        self.assertEqual(WorkDuration.SHORT.value, 15)
        self.assertEqual(WorkDuration.STANDARD.value, 25)
        self.assertEqual(WorkDuration.LONG.value, 35)
        self.assertEqual(WorkDuration.EXTENDED.value, 45)
    
    def test_break_duration_values(self):
        """Test break duration enum values"""
        self.assertEqual(BreakDuration.SHORT.value, 5)
        self.assertEqual(BreakDuration.MEDIUM.value, 10)
        self.assertEqual(BreakDuration.LONG.value, 15)
    
    def test_theme_values(self):
        """Test theme enum values"""
        self.assertEqual(Theme.LIGHT.value, "light")
        self.assertEqual(Theme.DARK.value, "dark")
        self.assertEqual(Theme.FOCUS.value, "focus")


class TestPomodoroTimer(unittest.TestCase):
    """Test Pomodoro timer functionality"""
    
    def setUp(self):
        """Set up test timer with short durations for testing"""
        self.sound_settings = SoundSettings(start_sound=False, end_sound=False, tick_sound=False)
        # Use short durations for faster testing
        self.settings = PomodoroSettings(
            work_duration=WorkDuration.SHORT,
            break_duration=BreakDuration.SHORT,
            sound_settings=self.sound_settings
        )
        self.timer = PomodoroTimer(self.settings)
    
    def test_initial_state(self):
        """Test timer initial state"""
        self.assertEqual(self.timer.state, TimerState.STOPPED)
        self.assertTrue(self.timer.is_work_session)
        self.assertEqual(self.timer.session_count, 0)
        self.assertEqual(self.timer.time_remaining, 15 * 60)  # 15 minutes in seconds
    
    def test_timer_start_stop(self):
        """Test timer start and stop functionality"""
        # Test start
        self.timer.start()
        self.assertEqual(self.timer.state, TimerState.RUNNING)
        
        # Wait a bit to ensure timer is actually running
        time.sleep(0.1)
        
        # Test stop
        self.timer.stop()
        self.assertEqual(self.timer.state, TimerState.STOPPED)
        self.assertEqual(self.timer.time_remaining, 15 * 60)  # Should reset
    
    def test_timer_pause_resume(self):
        """Test timer pause and resume functionality"""
        self.timer.start()
        time.sleep(0.1)
        
        # Test pause
        initial_time = self.timer.time_remaining
        self.timer.pause()
        self.assertEqual(self.timer.state, TimerState.PAUSED)
        
        # Wait a bit and check time didn't change
        time.sleep(0.1)
        self.assertEqual(self.timer.time_remaining, initial_time)
        
        # Test resume
        self.timer.resume()
        self.assertEqual(self.timer.state, TimerState.RUNNING)
    
    def test_get_formatted_time(self):
        """Test time formatting"""
        self.timer.time_remaining = 125  # 2:05
        self.assertEqual(self.timer.get_formatted_time(), "02:05")
        
        self.timer.time_remaining = 3661  # 61:01
        self.assertEqual(self.timer.get_formatted_time(), "61:01")
        
        self.timer.time_remaining = 0
        self.assertEqual(self.timer.get_formatted_time(), "00:00")
    
    def test_session_info(self):
        """Test session information retrieval"""
        info = self.timer.get_session_info()
        
        self.assertEqual(info["session_type"], "work")
        self.assertEqual(info["session_count"], 0)
        self.assertEqual(info["state"], "stopped")
        self.assertEqual(info["theme"], "light")
        self.assertIn("time_remaining", info)
        self.assertIn("formatted_time", info)
    
    def test_settings_update(self):
        """Test updating timer settings"""
        new_settings = PomodoroSettings(
            work_duration=WorkDuration.EXTENDED,
            theme=Theme.DARK
        )
        
        self.timer.update_settings(new_settings)
        self.assertEqual(self.timer.settings.work_duration, WorkDuration.EXTENDED)
        self.assertEqual(self.timer.settings.theme, Theme.DARK)
        self.assertEqual(self.timer.time_remaining, 45 * 60)  # Should reset to new duration
    
    def test_event_callbacks(self):
        """Test event callback functionality"""
        callback_calls = {
            'started': 0,
            'stopped': 0,
            'paused': 0,
            'resumed': 0
        }
        
        def on_started():
            callback_calls['started'] += 1
        
        def on_stopped():
            callback_calls['stopped'] += 1
        
        def on_paused():
            callback_calls['paused'] += 1
        
        def on_resumed():
            callback_calls['resumed'] += 1
        
        self.timer.on_timer_started = on_started
        self.timer.on_timer_stopped = on_stopped
        self.timer.on_timer_paused = on_paused
        self.timer.on_timer_resumed = on_resumed
        
        # Test event firing
        self.timer.start()
        time.sleep(0.1)
        self.timer.pause()
        self.timer.resume()
        time.sleep(0.1)
        self.timer.stop()
        
        self.assertEqual(callback_calls['started'], 1)
        self.assertEqual(callback_calls['paused'], 1)
        self.assertEqual(callback_calls['resumed'], 1)
        self.assertEqual(callback_calls['stopped'], 1)


class TestSettingsManager(unittest.TestCase):
    """Test settings management functionality"""
    
    def setUp(self):
        """Set up temporary settings file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.settings_manager = SettingsManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_load_default_settings(self):
        """Test loading default settings when no file exists"""
        # Delete the temp file to simulate no config file
        os.unlink(self.temp_file.name)
        
        settings = self.settings_manager.load_settings()
        self.assertEqual(settings.work_duration, WorkDuration.STANDARD)
        self.assertEqual(settings.break_duration, BreakDuration.SHORT)
        self.assertEqual(settings.theme, Theme.LIGHT)
    
    def test_save_and_load_settings(self):
        """Test saving and loading settings"""
        # Create custom settings
        custom_settings = PomodoroSettings(
            work_duration=WorkDuration.LONG,
            break_duration=BreakDuration.MEDIUM,
            theme=Theme.DARK,
            sound_settings=SoundSettings(start_sound=False, end_sound=True, tick_sound=True)
        )
        
        # Save settings
        self.assertTrue(self.settings_manager.save_settings(custom_settings))
        
        # Load settings
        loaded_settings = self.settings_manager.load_settings()
        
        self.assertEqual(loaded_settings.work_duration, WorkDuration.LONG)
        self.assertEqual(loaded_settings.break_duration, BreakDuration.MEDIUM)
        self.assertEqual(loaded_settings.theme, Theme.DARK)
        self.assertFalse(loaded_settings.sound_settings.start_sound)
        self.assertTrue(loaded_settings.sound_settings.end_sound)
        self.assertTrue(loaded_settings.sound_settings.tick_sound)
    
    def test_update_work_duration(self):
        """Test updating work duration"""
        settings = PomodoroSettings()
        updated_settings = self.settings_manager.update_work_duration(settings, 35)
        self.assertEqual(updated_settings.work_duration, WorkDuration.LONG)
    
    def test_update_break_duration(self):
        """Test updating break duration"""
        settings = PomodoroSettings()
        updated_settings = self.settings_manager.update_break_duration(settings, 10)
        self.assertEqual(updated_settings.break_duration, BreakDuration.MEDIUM)
    
    def test_update_theme(self):
        """Test updating theme"""
        settings = PomodoroSettings()
        updated_settings = self.settings_manager.update_theme(settings, "dark")
        self.assertEqual(updated_settings.theme, Theme.DARK)
    
    def test_update_sound_settings(self):
        """Test updating sound settings"""
        settings = PomodoroSettings()
        updated_settings = self.settings_manager.update_sound_settings(
            settings, start_sound=False, tick_sound=True
        )
        self.assertFalse(updated_settings.sound_settings.start_sound)
        self.assertTrue(updated_settings.sound_settings.end_sound)  # Should remain unchanged
        self.assertTrue(updated_settings.sound_settings.tick_sound)
    
    def test_get_available_options(self):
        """Test getting available configuration options"""
        options = self.settings_manager.get_available_options()
        
        self.assertIn("work_durations", options)
        self.assertIn("break_durations", options)
        self.assertIn("themes", options)
        self.assertIn("sound_options", options)
        
        self.assertIn(15, options["work_durations"])
        self.assertIn(25, options["work_durations"])
        self.assertIn(35, options["work_durations"])
        self.assertIn(45, options["work_durations"])
        
        self.assertIn(5, options["break_durations"])
        self.assertIn(10, options["break_durations"])
        self.assertIn(15, options["break_durations"])
        
        self.assertIn("light", options["themes"])
        self.assertIn("dark", options["themes"])
        self.assertIn("focus", options["themes"])
    
    def test_reset_to_defaults(self):
        """Test resetting settings to defaults"""
        # First save custom settings
        custom_settings = PomodoroSettings(
            work_duration=WorkDuration.EXTENDED,
            theme=Theme.FOCUS
        )
        self.settings_manager.save_settings(custom_settings)
        
        # Reset to defaults
        default_settings = self.settings_manager.reset_to_defaults()
        
        self.assertEqual(default_settings.work_duration, WorkDuration.STANDARD)
        self.assertEqual(default_settings.theme, Theme.LIGHT)
        
        # Verify file was updated
        loaded_settings = self.settings_manager.load_settings()
        self.assertEqual(loaded_settings.work_duration, WorkDuration.STANDARD)
    
    def test_validate_settings(self):
        """Test settings validation"""
        valid_settings = PomodoroSettings()
        self.assertTrue(self.settings_manager.validate_settings(valid_settings))
        
        # Test with invalid settings (this would require modifying the object inappropriately)
        # For now, just test that valid settings pass validation
        self.assertTrue(self.settings_manager.validate_settings(valid_settings))
    
    def test_load_corrupted_settings(self):
        """Test loading corrupted settings file"""
        # Write invalid JSON to file
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json content")
        
        # Should load default settings when JSON is corrupted
        settings = self.settings_manager.load_settings()
        self.assertEqual(settings.work_duration, WorkDuration.STANDARD)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        self.settings_manager = SettingsManager(self.temp_file.name)
        self.settings = self.settings_manager.load_settings()
        self.timer = PomodoroTimer(self.settings)
    
    def tearDown(self):
        """Clean up integration test environment"""
        self.timer.stop()
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_full_customization_workflow(self):
        """Test complete customization workflow"""
        # Start with default settings
        self.assertEqual(self.timer.settings.work_duration, WorkDuration.STANDARD)
        
        # Update work duration
        self.settings = self.settings_manager.update_work_duration(self.settings, 35)
        self.settings = self.settings_manager.update_break_duration(self.settings, 10)
        self.settings = self.settings_manager.update_theme(self.settings, "dark")
        self.settings = self.settings_manager.update_sound_settings(
            self.settings, start_sound=False, tick_sound=True
        )
        
        # Save and apply settings
        self.settings_manager.save_settings(self.settings)
        self.timer.update_settings(self.settings)
        
        # Verify settings are applied
        self.assertEqual(self.timer.settings.work_duration, WorkDuration.LONG)
        self.assertEqual(self.timer.settings.break_duration, BreakDuration.MEDIUM)
        self.assertEqual(self.timer.settings.theme, Theme.DARK)
        self.assertFalse(self.timer.settings.sound_settings.start_sound)
        self.assertTrue(self.timer.settings.sound_settings.tick_sound)
        
        # Verify timer time is updated
        self.assertEqual(self.timer.time_remaining, 35 * 60)
        
        # Test persistence by creating new instances
        new_settings_manager = SettingsManager(self.temp_file.name)
        loaded_settings = new_settings_manager.load_settings()
        
        self.assertEqual(loaded_settings.work_duration, WorkDuration.LONG)
        self.assertEqual(loaded_settings.theme, Theme.DARK)


def run_tests():
    """Run all tests with detailed output"""
    print("🧪 Running Pomodoro Timer Tests")
    print("="*50)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)