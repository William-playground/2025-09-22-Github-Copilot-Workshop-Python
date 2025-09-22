"""
ユニットテスト: 状態遷移
Unit tests for game state transitions
"""
import pytest
import time
from deliverManager import (
    KitchenGameManager, 
    GameState, 
    RecipeListSO, 
    RecipeSO, 
    KitchenObjectSO
)


class TestGameStateTransitions:
    """ゲーム状態遷移のテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        KitchenGameManager.reset_instance()
        self.game_manager = KitchenGameManager.get_instance()
    
    def test_initial_state(self):
        """初期状態のテスト"""
        assert self.game_manager.get_game_state() == GameState.STOPPED
        assert not self.game_manager.is_game_playing()
        assert not self.game_manager.is_game_paused()
        assert not self.game_manager.is_game_completed()
        assert self.game_manager.get_elapsed_time() == 0.0
    
    def test_start_game_from_stopped(self):
        """停止状態からゲーム開始"""
        self.game_manager.start_game()
        
        assert self.game_manager.get_game_state() == GameState.PLAYING
        assert self.game_manager.is_game_playing()
        assert not self.game_manager.is_game_paused()
        assert not self.game_manager.is_game_completed()
    
    def test_pause_game_from_playing(self):
        """プレイ中からゲーム一時停止"""
        self.game_manager.start_game()
        time.sleep(0.1)  # 少し経過時間を作る
        
        self.game_manager.pause_game()
        
        assert self.game_manager.get_game_state() == GameState.PAUSED
        assert not self.game_manager.is_game_playing()
        assert self.game_manager.is_game_paused()
        assert not self.game_manager.is_game_completed()
    
    def test_resume_game_from_paused(self):
        """一時停止から再開"""
        self.game_manager.start_game()
        self.game_manager.pause_game()
        
        self.game_manager.resume_game()
        
        assert self.game_manager.get_game_state() == GameState.PLAYING
        assert self.game_manager.is_game_playing()
        assert not self.game_manager.is_game_paused()
        assert not self.game_manager.is_game_completed()
    
    def test_complete_game_from_playing(self):
        """プレイ中からゲーム完了"""
        self.game_manager.start_game()
        time.sleep(0.1)
        
        self.game_manager.complete_game()
        
        assert self.game_manager.get_game_state() == GameState.COMPLETED
        assert not self.game_manager.is_game_playing()
        assert not self.game_manager.is_game_paused()
        assert self.game_manager.is_game_completed()
    
    def test_complete_game_from_paused(self):
        """一時停止中からゲーム完了"""
        self.game_manager.start_game()
        self.game_manager.pause_game()
        
        self.game_manager.complete_game()
        
        assert self.game_manager.get_game_state() == GameState.COMPLETED
        assert self.game_manager.is_game_completed()
    
    def test_stop_game_from_any_state(self):
        """任意の状態からゲーム停止"""
        # プレイ中から停止
        self.game_manager.start_game()
        self.game_manager.stop_game()
        assert self.game_manager.get_game_state() == GameState.STOPPED
        
        # 一時停止から停止
        self.game_manager.start_game()
        self.game_manager.pause_game()
        self.game_manager.stop_game()
        assert self.game_manager.get_game_state() == GameState.STOPPED
        
        # 完了から停止
        self.game_manager.start_game()
        self.game_manager.complete_game()
        self.game_manager.stop_game()
        assert self.game_manager.get_game_state() == GameState.STOPPED
    
    def test_invalid_state_transitions(self):
        """無効な状態遷移のテスト"""
        # 停止状態から一時停止は無効（状態変化なし）
        initial_state = self.game_manager.get_game_state()
        self.game_manager.pause_game()
        assert self.game_manager.get_game_state() == initial_state
        
        # 停止状態から再開は無効（状態変化なし）
        self.game_manager.resume_game()
        assert self.game_manager.get_game_state() == initial_state
    
    def test_start_game_from_paused_resumes(self):
        """一時停止状態からstart_gameを呼ぶと再開される"""
        self.game_manager.start_game()
        self.game_manager.pause_game()
        
        self.game_manager.start_game()  # 一時停止中にstart_gameを呼ぶ
        
        assert self.game_manager.get_game_state() == GameState.PLAYING
        assert self.game_manager.is_game_playing()
    
    def test_singleton_pattern(self):
        """Singletonパターンのテスト"""
        manager1 = KitchenGameManager.get_instance()
        manager2 = KitchenGameManager.get_instance()
        
        assert manager1 is manager2
        
        # 一方で状態変更すると、もう一方にも反映される
        manager1.start_game()
        assert manager2.is_game_playing()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])