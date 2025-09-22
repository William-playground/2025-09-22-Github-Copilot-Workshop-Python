"""
残り時間計算テスト
Remaining time calculation tests
"""
import pytest
import time
from deliverManager import KitchenGameManager, GameState


class TestRemainingTimeCalculation:
    """残り時間計算のテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        KitchenGameManager.reset_instance()
        self.game_manager = KitchenGameManager.get_instance()
        # テスト用に短いゲーム時間を設定
        self.game_manager.set_max_game_duration(10.0)  # 10秒
    
    def test_initial_remaining_time(self):
        """初期残り時間のテスト"""
        remaining = self.game_manager.get_remaining_time()
        assert remaining == 10.0  # 最大時間と同じ
    
    def test_remaining_time_during_play(self):
        """プレイ中の残り時間テスト"""
        self.game_manager.start_game()
        time.sleep(0.1)  # 0.1秒経過
        
        remaining = self.game_manager.get_remaining_time()
        elapsed = self.game_manager.get_elapsed_time()
        
        assert remaining == pytest.approx(10.0 - elapsed, rel=1e-2)
        assert remaining < 10.0
        assert remaining > 0.0
    
    def test_remaining_time_during_pause(self):
        """一時停止中の残り時間テスト"""
        self.game_manager.start_game()
        time.sleep(0.1)  # 0.1秒経過
        
        # 一時停止前の残り時間を記録
        self.game_manager.pause_game()
        remaining_at_pause = self.game_manager.get_remaining_time()
        
        time.sleep(0.1)  # 一時停止中に0.1秒経過
        
        # 一時停止中は残り時間が変わらない
        remaining_during_pause = self.game_manager.get_remaining_time()
        assert remaining_during_pause == pytest.approx(remaining_at_pause, rel=1e-2)
    
    def test_remaining_time_after_resume(self):
        """再開後の残り時間テスト"""
        self.game_manager.start_game()
        time.sleep(0.05)
        
        self.game_manager.pause_game()
        time.sleep(0.05)  # 一時停止中
        
        self.game_manager.resume_game()
        time.sleep(0.05)
        
        # 一時停止時間は経過時間に含まれない
        elapsed = self.game_manager.get_elapsed_time()
        remaining = self.game_manager.get_remaining_time()
        
        assert elapsed < 0.15  # 一時停止時間は除外される
        assert remaining == pytest.approx(10.0 - elapsed, rel=1e-1)
    
    def test_time_up_auto_completion(self):
        """時間切れ自動完了のテスト"""
        # 非常に短い時間でテスト
        self.game_manager.set_max_game_duration(0.2)  # 0.2秒
        
        self.game_manager.start_game()
        time.sleep(0.3)  # 制限時間を超過
        
        remaining = self.game_manager.get_remaining_time()
        
        # 時間切れでゲーム完了状態になる
        assert remaining == 0.0
        assert self.game_manager.get_game_state() == GameState.COMPLETED
    
    def test_remaining_time_after_completion(self):
        """完了後の残り時間テスト"""
        self.game_manager.start_game()
        time.sleep(0.1)
        
        self.game_manager.complete_game()
        
        # 完了後は経過時間は固定され、残り時間も固定される
        elapsed_at_completion = self.game_manager.get_elapsed_time()
        remaining_at_completion = self.game_manager.get_remaining_time()
        
        time.sleep(0.1)  # さらに時間経過
        
        # 完了後は時間が進まない
        assert self.game_manager.get_elapsed_time() == pytest.approx(elapsed_at_completion, rel=1e-2)
        assert self.game_manager.get_remaining_time() == pytest.approx(remaining_at_completion, rel=1e-2)
    
    def test_max_duration_change(self):
        """最大時間変更のテスト"""
        # 初期状態で最大時間を変更
        self.game_manager.set_max_game_duration(20.0)
        assert self.game_manager.get_max_game_duration() == 20.0
        assert self.game_manager.get_remaining_time() == 20.0
        
        # ゲーム中に最大時間を変更
        self.game_manager.start_game()
        time.sleep(0.1)
        
        self.game_manager.set_max_game_duration(15.0)
        
        elapsed = self.game_manager.get_elapsed_time()
        remaining = self.game_manager.get_remaining_time()
        
        assert remaining == pytest.approx(15.0 - elapsed, rel=1e-2)
    
    def test_invalid_max_duration(self):
        """無効な最大時間設定のテスト"""
        # 負の値は設定されない
        original_duration = self.game_manager.get_max_game_duration()
        self.game_manager.set_max_game_duration(-5.0)
        assert self.game_manager.get_max_game_duration() == original_duration
        
        # ゼロは設定されない
        self.game_manager.set_max_game_duration(0.0)
        assert self.game_manager.get_max_game_duration() == original_duration
    
    def test_elapsed_time_accuracy(self):
        """経過時間の精度テスト"""
        self.game_manager.start_game()
        start_wall_time = time.time()
        
        time.sleep(0.2)
        
        end_wall_time = time.time()
        elapsed_game_time = self.game_manager.get_elapsed_time()
        wall_elapsed = end_wall_time - start_wall_time
        
        # ゲーム内経過時間とリアルタイムがほぼ一致することを確認
        assert elapsed_game_time == pytest.approx(wall_elapsed, rel=1e-1)
    
    def test_pause_duration_not_counted(self):
        """一時停止時間が経過時間に含まれないことのテスト"""
        self.game_manager.start_game()
        time.sleep(0.1)  # 0.1秒プレイ
        
        self.game_manager.pause_game()
        time.sleep(0.2)  # 0.2秒一時停止
        
        self.game_manager.resume_game()
        time.sleep(0.1)  # さらに0.1秒プレイ
        
        elapsed = self.game_manager.get_elapsed_time()
        
        # 合計プレイ時間は約0.2秒（一時停止時間は除外）
        assert elapsed == pytest.approx(0.2, rel=1e-1)
        assert elapsed < 0.4  # 一時停止時間が含まれていないことを確認


if __name__ == "__main__":
    pytest.main([__file__, "-v"])