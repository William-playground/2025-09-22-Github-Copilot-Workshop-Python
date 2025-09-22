#!/usr/bin/env python3
"""
ポモドーロタイマーのテストスクリプト
Test script for Pomodoro Timer functionality
"""

import unittest
import time
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import PomodoroTimer, Particle


class TestParticle(unittest.TestCase):
    """パーティクルクラスのテスト"""
    
    def test_particle_creation(self):
        """パーティクルの作成テスト"""
        particle = Particle(100, 200, 10, -20, "#ff0000", 5.0, 2.0)
        
        self.assertEqual(particle.x, 100)
        self.assertEqual(particle.y, 200)
        self.assertEqual(particle.vx, 10)
        self.assertEqual(particle.vy, -20)
        self.assertEqual(particle.color, "#ff0000")
        self.assertEqual(particle.size, 5.0)
        self.assertEqual(particle.lifetime, 2.0)
        self.assertEqual(particle.max_lifetime, 2.0)
        self.assertEqual(particle.alpha, 1.0)
    
    def test_particle_update(self):
        """パーティクルの更新テスト"""
        particle = Particle(100, 200, 10, -20, "#ff0000", 5.0, 2.0)
        
        # 1秒経過
        is_alive = particle.update(1.0)
        
        self.assertTrue(is_alive)
        self.assertEqual(particle.x, 110)  # 100 + 10*1
        self.assertEqual(particle.y, 180)  # 200 + (-20)*1
        self.assertEqual(particle.lifetime, 1.0)  # 2.0 - 1.0
        self.assertEqual(particle.alpha, 0.5)  # 1.0/2.0
    
    def test_particle_death(self):
        """パーティクルの消滅テスト"""
        particle = Particle(100, 200, 10, -20, "#ff0000", 5.0, 1.0)
        
        # 1.5秒経過（寿命を超える）
        is_alive = particle.update(1.5)
        
        self.assertFalse(is_alive)
        self.assertLessEqual(particle.lifetime, 0)


class TestPomodoroTimerLogic(unittest.TestCase):
    """ポモドーロタイマーのロジックテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        # GUI要素をモック化
        with patch('main.tk.Tk'), \
             patch('main.tk.Frame'), \
             patch('main.tk.Label'), \
             patch('main.tk.Canvas'), \
             patch('main.tk.Button'):
            self.timer = PomodoroTimer()
    
    def test_time_formatting(self):
        """時間フォーマットのテスト"""
        self.assertEqual(self.timer.format_time(3661), "61:01")  # 61分1秒
        self.assertEqual(self.timer.format_time(1500), "25:00")  # 25分
        self.assertEqual(self.timer.format_time(300), "05:00")   # 5分
        self.assertEqual(self.timer.format_time(59), "00:59")    # 59秒
        self.assertEqual(self.timer.format_time(0), "00:00")     # 0秒
    
    def test_progress_color_calculation(self):
        """進行状況に基づく色計算のテスト"""
        # 開始時（青色系）
        color = self.timer.get_progress_color(0.0)
        self.assertEqual(color, "#4a9eff")
        
        # 中間時（黄色系）
        color = self.timer.get_progress_color(0.5)
        self.assertEqual(color, "#ffb200")
        
        # 終了時（赤色系）
        color = self.timer.get_progress_color(1.0)
        self.assertEqual(color, "#ff6b6b")
    
    def test_initial_state(self):
        """初期状態のテスト"""
        self.assertEqual(self.timer.work_duration, 25 * 60)
        self.assertEqual(self.timer.break_duration, 5 * 60)
        self.assertEqual(self.timer.remaining_time, 25 * 60)
        self.assertEqual(self.timer.current_duration, 25 * 60)
        self.assertFalse(self.timer.is_running)
        self.assertTrue(self.timer.is_work_session)
        self.assertEqual(len(self.timer.particles), 0)
    
    def test_timer_reset(self):
        """タイマーリセットのテスト"""
        # タイマー状態を変更
        self.timer.remaining_time = 100
        self.timer.is_running = True
        self.timer.particles = [Mock()]
        
        # リセット実行
        self.timer.reset_timer()
        
        # 状態確認
        self.assertFalse(self.timer.is_running)
        self.assertEqual(self.timer.remaining_time, self.timer.work_duration)
        self.assertEqual(self.timer.current_duration, self.timer.work_duration)
        self.assertEqual(len(self.timer.particles), 0)
    
    def test_session_switching(self):
        """セッション切り替えのテスト"""
        # 作業セッション終了
        self.timer.remaining_time = 0
        self.timer.timer_finished()
        
        # 休憩セッションに切り替わることを確認
        self.assertFalse(self.timer.is_work_session)
        self.assertEqual(self.timer.current_duration, self.timer.break_duration)
        self.assertEqual(self.timer.remaining_time, self.timer.break_duration)
        
        # 休憩セッション終了
        self.timer.remaining_time = 0
        self.timer.timer_finished()
        
        # 作業セッションに戻ることを確認
        self.assertTrue(self.timer.is_work_session)
        self.assertEqual(self.timer.current_duration, self.timer.work_duration)
        self.assertEqual(self.timer.remaining_time, self.timer.work_duration)
    
    def test_blend_alpha(self):
        """アルファブレンドのテスト"""
        # 完全不透明
        result = self.timer.blend_alpha("#ff0000", 1.0)
        self.assertEqual(result, "#ff0000")
        
        # 完全透明（背景色に近い）
        result = self.timer.blend_alpha("#ff0000", 0.0)
        self.assertEqual(result, "#0f0f1e")
        
        # 半透明 - 実際の計算結果を使用
        result = self.timer.blend_alpha("#ff0000", 0.5)
        self.assertEqual(result, "#87070f")


class TestPomodoroIntegration(unittest.TestCase):
    """統合テスト"""
    
    def test_particle_system_integration(self):
        """パーティクルシステムの統合テスト"""
        with patch('main.tk.Tk'), \
             patch('main.tk.Frame'), \
             patch('main.tk.Label'), \
             patch('main.tk.Canvas'), \
             patch('main.tk.Button'):
            timer = PomodoroTimer()
        
        # 初期状態確認
        self.assertEqual(len(timer.particles), 0)
        
        # パーティクル生成テスト
        timer.is_running = True
        timer.spawn_particles()
        
        # パーティクルが生成されたことを確認
        self.assertGreater(len(timer.particles), 0)
        
        # パーティクル更新テスト
        initial_count = len(timer.particles)
        timer.update_particles(0.1)
        
        # パーティクルがまだ生存していることを確認
        self.assertEqual(len(timer.particles), initial_count)


def run_functional_test():
    """機能テスト（GUI要素なし）"""
    print("=== ポモドーロタイマー機能テスト ===")
    
    # タイマーインスタンス作成（GUI無し）
    with patch('main.tk.Tk'), \
         patch('main.tk.Frame'), \
         patch('main.tk.Label'), \
         patch('main.tk.Canvas'), \
         patch('main.tk.Button'):
        timer = PomodoroTimer()
    
    print(f"初期時間: {timer.format_time(timer.remaining_time)}")
    print(f"作業セッション: {timer.is_work_session}")
    
    # 色グラデーションテスト
    print("\n色グラデーションテスト:")
    for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
        color = timer.get_progress_color(progress)
        print(f"進行度 {progress:3.0%}: {color}")
    
    # パーティクルテスト
    print("\nパーティクルシステムテスト:")
    timer.is_running = True
    timer.spawn_particles()
    print(f"生成されたパーティクル数: {len(timer.particles)}")
    
    # パーティクル更新テスト
    timer.update_particles(1.0)
    print(f"1秒後のパーティクル数: {len(timer.particles)}")
    
    print("\n✅ 全ての機能テストが正常に完了しました！")


if __name__ == "__main__":
    # ユニットテスト実行
    print("=== ユニットテスト実行 ===")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n")
    
    # 機能テスト実行
    run_functional_test()