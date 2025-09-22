#!/usr/bin/env python3
"""
ポモドーロシステムの単体テスト

このファイルはポモドーロタイマーのゲーミフィケーション機能の
基本的な動作を検証します。
"""

import unittest
import tempfile
import os
from datetime import datetime, date, timedelta
from pomodoro_system import (
    PomodoroTimer, ExperienceSystem, BadgeManager, 
    StatisticsManager, StreakManager, PomodoroGameSystem,
    PomodoroState, PomodoroSession
)


class TestPomodoroSystem(unittest.TestCase):
    """ポモドーロシステムのテストクラス"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        # 一時ファイルを使用してテスト
        self.temp_dir = tempfile.mkdtemp()
        self.user_data_file = os.path.join(self.temp_dir, "test_user_data.json")
        self.badges_data_file = os.path.join(self.temp_dir, "test_badges_data.json")
        self.stats_data_file = os.path.join(self.temp_dir, "test_statistics_data.json")
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ファイルを削除
        for file_path in [self.user_data_file, self.badges_data_file, self.stats_data_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)
    
    def test_pomodoro_timer_basic_functionality(self):
        """ポモドーロタイマーの基本機能テスト"""
        timer = PomodoroTimer()
        
        # 初期状態確認
        self.assertEqual(timer.state, PomodoroState.STOPPED)
        self.assertEqual(timer.get_remaining_time(), 0)
        self.assertEqual(timer.get_progress(), 0.0)
        
        # 作業セッション開始
        result = timer.start_work_session()
        self.assertTrue(result)
        self.assertEqual(timer.state, PomodoroState.WORK)
        self.assertIsNotNone(timer.current_session)
        
        # セッション停止
        result = timer.stop_session()
        self.assertTrue(result)
        self.assertEqual(timer.state, PomodoroState.STOPPED)
    
    def test_experience_system(self):
        """経験値システムのテスト"""
        exp_system = ExperienceSystem(self.user_data_file)
        
        # 初期状態確認
        self.assertEqual(exp_system.level, 1)
        self.assertEqual(exp_system.xp, 0)
        
        # 経験値獲得
        exp_system.gain_xp(500)
        self.assertEqual(exp_system.xp, 500)
        self.assertEqual(exp_system.level, 1)  # まだレベル1
        
        # レベルアップするまで経験値獲得
        exp_system.gain_xp(500)
        self.assertEqual(exp_system.xp, 1000)
        self.assertEqual(exp_system.level, 2)  # レベル2になる
    
    def test_badge_system(self):
        """バッジシステムのテスト"""
        stats = StatisticsManager(self.stats_data_file)
        badges = BadgeManager(self.badges_data_file)
        
        # 初期状態確認
        unlocked = badges.get_unlocked_badges()
        self.assertEqual(len(unlocked), 0)
        
        # ポモドーロセッションを追加
        session = PomodoroSession(
            start_time=datetime.now(),
            end_time=datetime.now(),
            completed=True,
            session_type=PomodoroState.WORK
        )
        stats.add_session(session)
        
        # バッジ条件をチェック
        badges.check_badge_conditions(stats)
        
        # 初回完了バッジが獲得されているはず
        unlocked = badges.get_unlocked_badges()
        self.assertEqual(len(unlocked), 1)
        self.assertEqual(unlocked[0].id, "first_pomodoro")
    
    def test_statistics_manager(self):
        """統計管理システムのテスト"""
        stats = StatisticsManager(self.stats_data_file)
        
        # 初期状態確認
        self.assertEqual(stats.get_total_completed_pomodoros(), 0)
        
        # セッション追加
        session = PomodoroSession(
            start_time=datetime.now(),
            end_time=datetime.now(),
            completed=True,
            session_type=PomodoroState.WORK
        )
        stats.add_session(session)
        
        # 統計確認
        self.assertEqual(stats.get_total_completed_pomodoros(), 1)
        today_count = stats.get_daily_pomodoros(date.today())
        self.assertEqual(today_count, 1)
    
    def test_streak_manager(self):
        """ストリーク管理システムのテスト"""
        stats = StatisticsManager(self.stats_data_file)
        streak_manager = StreakManager(stats)
        
        # 今日のセッションを追加
        session = PomodoroSession(
            start_time=datetime.now(),
            end_time=datetime.now(),
            completed=True,
            session_type=PomodoroState.WORK
        )
        stats.add_session(session)
        
        # ストリーク確認
        current_streak = streak_manager.get_current_streak()
        self.assertEqual(current_streak, 1)
    
    def test_integrated_system(self):
        """統合システムのテスト"""
        # 新しいシステムを個別コンポーネントで作成
        from pomodoro_system import PomodoroTimer, ExperienceSystem, StatisticsManager, BadgeManager, StreakManager
        
        timer = PomodoroTimer()
        experience = ExperienceSystem(self.user_data_file)
        statistics = StatisticsManager(self.stats_data_file)
        badges = BadgeManager(self.badges_data_file)
        streaks = StreakManager(statistics)
        
        # 初期状態確認
        self.assertEqual(timer.state, PomodoroState.STOPPED)
        self.assertEqual(experience.level, 1)
        self.assertEqual(statistics.get_total_completed_pomodoros(), 0)
        
        # 作業セッション開始と完了をシミュレート
        timer.work_duration = 1  # 1秒に短縮
        result = timer.start_work_session()
        self.assertTrue(result)
        
        # 短時間待機してタイマー更新
        import time
        time.sleep(1.1)
        timer.update()
        
        # セッションが完了しているかチェック
        self.assertEqual(timer.state, PomodoroState.STOPPED)
        
        # 手動でセッション完了処理をテスト
        session = PomodoroSession(
            start_time=datetime.now(),
            end_time=datetime.now(),
            completed=True,
            session_type=PomodoroState.WORK
        )
        statistics.add_session(session)
        experience.gain_xp(100)
        
        # 完了後の状態確認
        self.assertGreater(experience.xp, 0)  # 経験値が増加している
        self.assertGreater(statistics.get_total_completed_pomodoros(), 0)  # 完了数が増加している


def run_tests():
    """テストを実行"""
    print("🧪 ポモドーロシステムのテストを開始...")
    
    # テストスイートを作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestPomodoroSystem)
    
    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果表示
    if result.wasSuccessful():
        print("\n✅ すべてのテストが成功しました！")
        return True
    else:
        print(f"\n❌ {len(result.failures)} 個のテストが失敗しました。")
        print(f"❌ {len(result.errors)} 個のエラーが発生しました。")
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)