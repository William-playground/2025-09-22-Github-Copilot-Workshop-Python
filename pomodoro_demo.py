#!/usr/bin/env python3
"""
ポモドーロタイマー ゲーミフィケーション デモ

このスクリプトはポモドーロタイマーのゲーミフィケーション機能を
デモンストレーションします。

使用方法:
    python pomodoro_demo.py
"""

import time
import threading
from pomodoro_system import PomodoroGameSystem, PomodoroState


class PomodoroDemo:
    """ポモドーロタイマーのデモクラス"""
    
    def __init__(self):
        self.system = PomodoroGameSystem()
        self.running = True
        self.update_thread = None
    
    def start_update_loop(self):
        """バックグラウンドでタイマー更新を開始"""
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self):
        """タイマー更新ループ"""
        while self.running:
            self.system.update()
            time.sleep(0.1)  # 100ms間隔で更新
    
    def run_interactive_demo(self):
        """インタラクティブなデモを実行"""
        print("🍅 ポモドーロタイマー ゲーミフィケーション デモ")
        print("=" * 60)
        print()
        
        # バックグラウンド更新を開始
        self.start_update_loop()
        
        # 初期状態表示
        self.system.display_status()
        
        while True:
            print("\n📋 操作メニュー:")
            print("1. 作業セッション開始")
            print("2. 休憩開始")
            print("3. セッション停止")
            print("4. ステータス表示")
            print("5. 週間チャート表示")
            print("6. 簡易テスト実行")
            print("7. 終了")
            
            try:
                choice = input("\n選択してください (1-7): ").strip()
                
                if choice == "1":
                    self.system.start_work_session()
                elif choice == "2":
                    self.system.start_break()
                elif choice == "3":
                    self.system.stop_session()
                elif choice == "4":
                    self.system.display_status()
                elif choice == "5":
                    self.system.display_weekly_chart()
                elif choice == "6":
                    self.run_quick_test()
                elif choice == "7":
                    print("👋 デモを終了します。")
                    self.running = False
                    break
                else:
                    print("❌ 無効な選択です。")
                    
            except KeyboardInterrupt:
                print("\n👋 デモを終了します。")
                self.running = False
                break
            except EOFError:
                print("\n👋 デモを終了します。")
                self.running = False
                break
    
    def run_quick_test(self):
        """ゲーミフィケーション機能の簡易テスト"""
        print("\n🧪 簡易テスト実行中...")
        print("(実際の25分ではなく、5秒でポモドーロを完了させます)")
        
        # テスト用に短い時間設定
        original_work_duration = self.system.timer.work_duration
        original_break_duration = self.system.timer.short_break_duration
        
        self.system.timer.work_duration = 3  # 3秒
        self.system.timer.short_break_duration = 2  # 2秒
        
        try:
            # 複数のポモドーロを実行してゲーミフィケーション要素をテスト
            for i in range(3):
                print(f"\n🔄 テストポモドーロ {i+1}/3")
                
                # 作業セッション開始
                self.system.start_work_session()
                print("⏳ 作業中...")
                
                # 完了まで待機
                while self.system.timer.state == PomodoroState.WORK:
                    time.sleep(0.1)
                
                print("✅ 作業完了!")
                
                # 短い休憩
                if i < 2:  # 最後以外は休憩
                    self.system.start_break()
                    print("☕ 休憩中...")
                    
                    while self.system.timer.state == PomodoroState.SHORT_BREAK:
                        time.sleep(0.1)
                    
                    print("✅ 休憩完了!")
                
                time.sleep(0.5)  # 少し待機
            
            print("\n🎉 テスト完了！ゲーミフィケーション要素が動作しました。")
            
        finally:
            # 元の設定に戻す
            self.system.timer.work_duration = original_work_duration
            self.system.timer.short_break_duration = original_break_duration
        
        # 結果表示
        self.system.display_status()
    
    def run_automated_demo(self):
        """自動実行デモ"""
        print("🍅 ポモドーロタイマー 自動デモ")
        print("=" * 50)
        print("ゲーミフィケーション機能を自動的にデモンストレーションします...")
        print()
        
        # バックグラウンド更新を開始
        self.start_update_loop()
        
        # 初期状態
        print("📊 初期状態:")
        self.system.display_status()
        
        # 短時間でのテスト
        self.run_quick_test()
        
        print("\n✨ ゲーミフィケーション要素のデモが完了しました！")
        print("実際の使用では25分の作業と5分の休憩サイクルで動作します。")
        
        self.running = False


def main():
    """メイン関数"""
    import sys
    
    demo = PomodoroDemo()
    
    # コマンドライン引数で動作モードを選択
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        demo.run_automated_demo()
    else:
        demo.run_interactive_demo()


if __name__ == "__main__":
    main()