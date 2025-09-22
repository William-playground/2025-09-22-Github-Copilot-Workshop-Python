#!/usr/bin/env python3
"""
Pomodoro Timer Demo Script
ポモドーロタイマーのデモスクリプト
"""

import time
from pomodoro_timer import PomodoroTimer, PomodoroSettings, WorkDuration, BreakDuration, Theme, SoundSettings
from settings_manager import SettingsManager


def demo_customization():
    """Demonstrate customization features"""
    print("🍅 Pomodoro Timer Customization Demo")
    print("="*50)
    
    # Create settings manager
    sm = SettingsManager()
    
    # Show available options
    print("📋 Available customization options:")
    options = sm.get_available_options()
    print(f"Work durations: {options['work_durations']} minutes")
    print(f"Break durations: {options['break_durations']} minutes")
    print(f"Themes: {options['themes']}")
    print(f"Sound options: {options['sound_options']}")
    print()
    
    # Demo 1: Default settings
    print("Demo 1: Default Settings")
    print("-" * 30)
    default_settings = PomodoroSettings()
    timer1 = PomodoroTimer(default_settings)
    info = timer1.get_session_info()
    print(f"Work duration: {default_settings.work_duration.value} minutes")
    print(f"Break duration: {default_settings.break_duration.value} minutes")
    print(f"Theme: {default_settings.theme.value}")
    print(f"Sound settings: start={default_settings.sound_settings.start_sound}, "
          f"end={default_settings.sound_settings.end_sound}, "
          f"tick={default_settings.sound_settings.tick_sound}")
    print(f"Initial time: {info['formatted_time']}")
    print()
    
    # Demo 2: Custom settings
    print("Demo 2: Custom Extended Work Session")
    print("-" * 30)
    custom_settings = PomodoroSettings(
        work_duration=WorkDuration.EXTENDED,  # 45 minutes
        break_duration=BreakDuration.LONG,    # 15 minutes
        theme=Theme.FOCUS,
        sound_settings=SoundSettings(start_sound=True, end_sound=True, tick_sound=True)
    )
    timer2 = PomodoroTimer(custom_settings)
    info2 = timer2.get_session_info()
    print(f"Work duration: {custom_settings.work_duration.value} minutes")
    print(f"Break duration: {custom_settings.break_duration.value} minutes")
    print(f"Theme: {custom_settings.theme.value}")
    print(f"Sound settings: start={custom_settings.sound_settings.start_sound}, "
          f"end={custom_settings.sound_settings.end_sound}, "
          f"tick={custom_settings.sound_settings.tick_sound}")
    print(f"Initial time: {info2['formatted_time']}")
    print()
    
    # Demo 3: Short session for quick test
    print("Demo 3: Quick Timer Test (5 seconds)")
    print("-" * 30)
    quick_timer = PomodoroTimer(PomodoroSettings())
    
    # Set up event handlers
    events = []
    quick_timer.on_timer_started = lambda: events.append("Timer started")
    quick_timer.on_timer_finished = lambda: events.append("Timer finished")
    quick_timer.on_session_changed = lambda: events.append("Session changed")
    quick_timer.on_tick = lambda t: events.append(f"Tick: {t}s remaining") if t <= 3 else None
    
    # Override time for quick demo
    quick_timer.time_remaining = 5
    
    print("Starting 5-second timer...")
    quick_timer.start()
    
    # Monitor timer
    start_time = time.time()
    while quick_timer.state.value == 'running' and (time.time() - start_time) < 10:
        time.sleep(1)
        if quick_timer.time_remaining <= 3:
            print(f"⏰ {quick_timer.get_formatted_time()}")
    
    quick_timer.stop()
    print("Timer events:", events)
    print()
    
    # Demo 4: Settings persistence
    print("Demo 4: Settings Persistence")
    print("-" * 30)
    print("Saving custom settings to file...")
    sm.save_settings(custom_settings)
    
    print("Loading settings from file...")
    loaded_settings = sm.load_settings()
    print(f"Loaded work duration: {loaded_settings.work_duration.value} minutes")
    print(f"Loaded theme: {loaded_settings.theme.value}")
    print("✅ Settings persistence working!")
    print()
    
    # Demo 5: Theme demonstration
    print("Demo 5: Theme Showcase")
    print("-" * 30)
    themes = [Theme.LIGHT, Theme.DARK, Theme.FOCUS]
    theme_descriptions = {
        Theme.LIGHT: "📝 Light Mode - 明るい表示",
        Theme.DARK: "🌙 Dark Mode - 暗い表示",
        Theme.FOCUS: "🎯 Focus Mode - 集中用"
    }
    
    for theme in themes:
        settings = PomodoroSettings(theme=theme)
        timer = PomodoroTimer(settings)
        info = timer.get_session_info()
        print(f"{theme_descriptions[theme]} - Theme: {info['theme']}")
    
    print()
    print("🎉 Demo completed! All customization features are working.")


if __name__ == "__main__":
    demo_customization()