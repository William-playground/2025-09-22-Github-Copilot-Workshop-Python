#!/usr/bin/env python3
"""
カスタマイズ可能なポモドーロタイマー
Customizable Pomodoro Timer

機能 (Features):
- 柔軟な時間設定 (15/25/35/45分選択)
- テーマ切り替え (ダーク/ライト/フォーカスモード)
- サウンド設定 (開始/終了/tick音のオンオフ切替)
- 休憩時間のカスタム (5/10/15分選択)
"""

import os
import sys
import time
import threading
from pomodoro_timer import PomodoroTimer, PomodoroSettings, WorkDuration, BreakDuration, Theme, TimerState
from settings_manager import SettingsManager


class PomodoroUI:
    """Command line interface for Pomodoro Timer"""
    
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        self.timer = PomodoroTimer(self.settings)
        self.running = True
        
        # Setup timer event handlers
        self.timer.on_timer_started = self._on_timer_started
        self.timer.on_timer_stopped = self._on_timer_stopped
        self.timer.on_timer_paused = self._on_timer_paused
        self.timer.on_timer_resumed = self._on_timer_resumed
        self.timer.on_timer_finished = self._on_timer_finished
        self.timer.on_session_changed = self._on_session_changed
        self.timer.on_tick = self._on_tick
    
    def run(self):
        """Main application loop"""
        self._clear_screen()
        self._show_welcome()
        
        while self.running:
            try:
                self._show_main_menu()
                choice = input("\n選択してください (Enter choice): ").strip()
                self._handle_menu_choice(choice)
            except KeyboardInterrupt:
                print("\n\nアプリケーションを終了します...")
                self._quit()
            except Exception as e:
                print(f"\nエラーが発生しました: {e}")
                input("Enterキーを押して続行...")
    
    def _show_welcome(self):
        """Show welcome message with current theme"""
        theme_colors = {
            "light": "📝",
            "dark": "🌙", 
            "focus": "🎯"
        }
        
        theme_icon = theme_colors.get(self.settings.theme.value, "📝")
        print(f"""
{theme_icon} ポモドーロタイマー - Customizable Pomodoro Timer {theme_icon}
{'='*60}
現在のテーマ: {self.settings.theme.value.title()} Mode
作業時間: {self.settings.work_duration.value}分
休憩時間: {self.settings.break_duration.value}分
""")
    
    def _show_main_menu(self):
        """Display main menu"""
        session_info = self.timer.get_session_info()
        status_icon = "🍅" if session_info["session_type"] == "work" else "☕"
        
        print(f"""
{status_icon} セッション情報:
   状態: {self._translate_state(session_info['state'])}
   タイプ: {'作業' if session_info['session_type'] == 'work' else '休憩'}
   残り時間: {session_info['formatted_time']}
   完了セッション数: {session_info['session_count']}

📋 メニュー:
   1. タイマー開始/再開 (Start/Resume Timer)
   2. タイマー一時停止 (Pause Timer)  
   3. タイマー停止 (Stop Timer)
   4. 設定変更 (Settings)
   5. 終了 (Quit)
""")
    
    def _handle_menu_choice(self, choice: str):
        """Handle main menu selection"""
        if choice == "1":
            if self.timer.state == TimerState.PAUSED:
                self.timer.resume()
            else:
                self.timer.start()
            self._timer_display_loop()
        elif choice == "2":
            self.timer.pause()
        elif choice == "3":
            self.timer.stop()
        elif choice == "4":
            self._settings_menu()
        elif choice == "5":
            self._quit()
        else:
            print("無効な選択です。")
    
    def _timer_display_loop(self):
        """Display timer while running"""
        print("\nタイマー実行中... (Ctrl+C で戻る)")
        
        try:
            while self.timer.state == TimerState.RUNNING:
                session_info = self.timer.get_session_info()
                status_icon = "🍅" if session_info["session_type"] == "work" else "☕"
                
                # Clear line and show timer
                print(f"\r{status_icon} {session_info['formatted_time']} - {'作業中' if session_info['session_type'] == 'work' else '休憩中'}", end="", flush=True)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.timer.pause()
            print("\n\nタイマーを一時停止しました。")
    
    def _settings_menu(self):
        """Show settings configuration menu"""
        while True:
            self._clear_screen()
            print("⚙️  設定メニュー - Settings Menu")
            print("="*50)
            print(f"1. 作業時間設定 (現在: {self.settings.work_duration.value}分)")
            print(f"2. 休憩時間設定 (現在: {self.settings.break_duration.value}分)")
            print(f"3. テーマ設定 (現在: {self.settings.theme.value})")
            print(f"4. サウンド設定")
            print(f"5. 設定をリセット (Reset to defaults)")
            print(f"6. メインメニューに戻る (Back to main menu)")
            
            choice = input("\n選択してください: ").strip()
            
            if choice == "1":
                self._configure_work_duration()
            elif choice == "2":
                self._configure_break_duration()
            elif choice == "3":
                self._configure_theme()
            elif choice == "4":
                self._configure_sound_settings()
            elif choice == "5":
                self._reset_settings()
            elif choice == "6":
                break
            else:
                print("無効な選択です。")
                input("Enterキーを押して続行...")
    
    def _configure_work_duration(self):
        """Configure work session duration"""
        print("\n作業時間を選択してください:")
        durations = [(d.value, d) for d in WorkDuration]
        
        for i, (minutes, duration) in enumerate(durations, 1):
            current = " (現在)" if duration == self.settings.work_duration else ""
            print(f"{i}. {minutes}分{current}")
        
        try:
            choice = int(input("選択 (1-4): ")) - 1
            if 0 <= choice < len(durations):
                self.settings.work_duration = durations[choice][1]
                self._save_and_update_settings()
                print(f"作業時間を{durations[choice][0]}分に設定しました。")
            else:
                print("無効な選択です。")
        except ValueError:
            print("無効な入力です。")
        
        input("Enterキーを押して続行...")
    
    def _configure_break_duration(self):
        """Configure break duration"""
        print("\n休憩時間を選択してください:")
        durations = [(d.value, d) for d in BreakDuration]
        
        for i, (minutes, duration) in enumerate(durations, 1):
            current = " (現在)" if duration == self.settings.break_duration else ""
            print(f"{i}. {minutes}分{current}")
        
        try:
            choice = int(input("選択 (1-3): ")) - 1
            if 0 <= choice < len(durations):
                self.settings.break_duration = durations[choice][1]
                self._save_and_update_settings()
                print(f"休憩時間を{durations[choice][0]}分に設定しました。")
            else:
                print("無効な選択です。")
        except ValueError:
            print("無効な入力です。")
        
        input("Enterキーを押して続行...")
    
    def _configure_theme(self):
        """Configure UI theme"""
        print("\nテーマを選択してください:")
        themes = [(t.value, t) for t in Theme]
        
        for i, (name, theme) in enumerate(themes, 1):
            current = " (現在)" if theme == self.settings.theme else ""
            description = {
                "light": "ライトモード - 明るい表示",
                "dark": "ダークモード - 暗い表示", 
                "focus": "フォーカスモード - 集中用"
            }
            print(f"{i}. {description[name]}{current}")
        
        try:
            choice = int(input("選択 (1-3): ")) - 1
            if 0 <= choice < len(themes):
                self.settings.theme = themes[choice][1]
                self._save_and_update_settings()
                print(f"テーマを{themes[choice][0]}に設定しました。")
            else:
                print("無効な選択です。")
        except ValueError:
            print("無効な入力です。")
        
        input("Enterキーを押して続行...")
    
    def _configure_sound_settings(self):
        """Configure sound settings"""
        while True:
            print("\n🔊 サウンド設定:")
            sounds = self.settings.sound_settings
            print(f"1. 開始音: {'ON' if sounds.start_sound else 'OFF'}")
            print(f"2. 終了音: {'ON' if sounds.end_sound else 'OFF'}")
            print(f"3. tick音: {'ON' if sounds.tick_sound else 'OFF'}")
            print("4. 戻る")
            
            choice = input("選択してください: ").strip()
            
            if choice == "1":
                sounds.start_sound = not sounds.start_sound
                self._save_and_update_settings()
                print(f"開始音を{'ON' if sounds.start_sound else 'OFF'}にしました。")
            elif choice == "2":
                sounds.end_sound = not sounds.end_sound
                self._save_and_update_settings()
                print(f"終了音を{'ON' if sounds.end_sound else 'OFF'}にしました。")
            elif choice == "3":
                sounds.tick_sound = not sounds.tick_sound
                self._save_and_update_settings()
                print(f"tick音を{'ON' if sounds.tick_sound else 'OFF'}にしました。")
            elif choice == "4":
                break
            else:
                print("無効な選択です。")
            
            input("Enterキーを押して続行...")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        confirm = input("設定をデフォルトにリセットしますか？ (y/N): ").strip().lower()
        if confirm == 'y':
            self.settings = self.settings_manager.reset_to_defaults()
            self.timer.update_settings(self.settings)
            print("設定をリセットしました。")
        else:
            print("リセットをキャンセルしました。")
        
        input("Enterキーを押して続行...")
    
    def _save_and_update_settings(self):
        """Save settings and update timer"""
        self.settings_manager.save_settings(self.settings)
        self.timer.update_settings(self.settings)
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _translate_state(self, state: str) -> str:
        """Translate timer state to Japanese"""
        translations = {
            "stopped": "停止中",
            "running": "実行中",
            "paused": "一時停止",
            "break": "休憩中"
        }
        return translations.get(state, state)
    
    def _quit(self):
        """Quit application"""
        self.timer.stop()
        self.running = False
        print("アプリケーションを終了しました。お疲れ様でした！")
    
    # Timer event handlers
    def _on_timer_started(self):
        print("タイマーを開始しました！")
    
    def _on_timer_stopped(self):
        print("タイマーを停止しました。")
    
    def _on_timer_paused(self):
        print("タイマーを一時停止しました。")
    
    def _on_timer_resumed(self):
        print("タイマーを再開しました！")
    
    def _on_timer_finished(self):
        session_info = self.timer.get_session_info()
        if session_info["session_type"] == "break":
            print("\n🎉 作業セッション完了！休憩時間です。")
        else:
            print("\n☕ 休憩終了！作業を再開しましょう。")
    
    def _on_session_changed(self):
        print("\nセッションが切り替わりました。")
    
    def _on_tick(self, time_remaining: int):
        # This could be used for additional tick processing if needed
        pass


def main():
    """Main entry point"""
    try:
        app = PomodoroUI()
        app.run()
    except Exception as e:
        print(f"アプリケーションエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()