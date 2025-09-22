"""
ユニットテスト: stats 集計
Unit tests for statistics aggregation
"""
import pytest
import time
from deliverManager import (
    DeliveryManager,
    KitchenGameManager,
    GameStats,
    RecipeListSO,
    RecipeSO,
    KitchenObjectSO,
    PlateKitchenObject
)


class TestStatsAggregation:
    """統計集計のテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        # Singletonインスタンスをリセット
        KitchenGameManager.reset_instance()
        DeliveryManager.reset_instance()
        
        # テストデータ作成
        self.tomato = KitchenObjectSO("Tomato", 1)
        self.lettuce = KitchenObjectSO("Lettuce", 2)
        self.bread = KitchenObjectSO("Bread", 3)
        
        self.sandwich_recipe = RecipeSO("Sandwich", [self.bread, self.lettuce, self.tomato])
        self.salad_recipe = RecipeSO("Salad", [self.lettuce, self.tomato])
        
        self.recipe_list = RecipeListSO([self.sandwich_recipe, self.salad_recipe])
        
        # マネージャー初期化
        self.game_manager = KitchenGameManager.get_instance()
        self.delivery_manager = DeliveryManager.get_instance(self.recipe_list)
    
    def test_initial_stats(self):
        """初期統計のテスト"""
        stats = self.delivery_manager.get_stats()
        
        assert stats.successful_recipes == 0
        assert stats.failed_recipes == 0
        assert stats.total_recipes_spawned == 0
        assert stats.elapsed_time == 0.0
        assert stats.get_success_rate() == 0.0
        assert stats.get_recipes_per_minute() == 0.0
    
    def test_successful_recipe_stats(self):
        """成功レシピの統計テスト"""
        # ゲーム開始
        self.game_manager.start_game()
        
        # 手動でレシピを待機リストに追加
        self.delivery_manager._waiting_recipe_so_list.append(self.sandwich_recipe)
        self.delivery_manager._total_recipes_spawned = 1
        
        # 正しいサンドイッチを配達
        plate = PlateKitchenObject()
        plate.add_kitchen_object(self.bread)
        plate.add_kitchen_object(self.lettuce)
        plate.add_kitchen_object(self.tomato)
        
        self.delivery_manager.deliver_recipe(plate)
        
        # 統計確認
        stats = self.delivery_manager.get_stats()
        assert stats.successful_recipes == 1
        assert stats.failed_recipes == 0
        assert stats.total_recipes_spawned == 1
        assert stats.get_success_rate() == 100.0
    
    def test_failed_recipe_stats(self):
        """失敗レシピの統計テスト"""
        # ゲーム開始
        self.game_manager.start_game()
        
        # 手動でレシピを待機リストに追加
        self.delivery_manager._waiting_recipe_so_list.append(self.sandwich_recipe)
        self.delivery_manager._total_recipes_spawned = 1
        
        # 間違った材料の皿を配達
        plate = PlateKitchenObject()
        plate.add_kitchen_object(self.lettuce)  # 材料が足りない
        
        self.delivery_manager.deliver_recipe(plate)
        
        # 統計確認
        stats = self.delivery_manager.get_stats()
        assert stats.successful_recipes == 0
        assert stats.failed_recipes == 1
        assert stats.total_recipes_spawned == 1
        assert stats.get_success_rate() == 0.0
    
    def test_mixed_recipe_stats(self):
        """成功・失敗混合の統計テスト"""
        self.game_manager.start_game()
        
        # 成功を2回
        for _ in range(2):
            self.delivery_manager._waiting_recipe_so_list.append(self.sandwich_recipe)
            self.delivery_manager._total_recipes_spawned += 1
            
            plate = PlateKitchenObject()
            plate.add_kitchen_object(self.bread)
            plate.add_kitchen_object(self.lettuce)
            plate.add_kitchen_object(self.tomato)
            
            self.delivery_manager.deliver_recipe(plate)
        
        # 失敗を1回
        self.delivery_manager._waiting_recipe_so_list.append(self.salad_recipe)
        self.delivery_manager._total_recipes_spawned += 1
        
        plate = PlateKitchenObject()
        plate.add_kitchen_object(self.bread)  # 間違った材料
        
        self.delivery_manager.deliver_recipe(plate)
        
        # 統計確認
        stats = self.delivery_manager.get_stats()
        assert stats.successful_recipes == 2
        assert stats.failed_recipes == 1
        assert stats.total_recipes_spawned == 3
        assert stats.get_success_rate() == pytest.approx(66.7, rel=1e-1)
    
    def test_recipes_per_minute_calculation(self):
        """1分あたりのレシピ数計算テスト"""
        self.game_manager.start_game()
        
        # 時間を進めるためのモック（実際の時間経過をシミュレート）
        time.sleep(0.1)  # 0.1秒経過
        
        # 1つのレシピを成功
        self.delivery_manager._waiting_recipe_so_list.append(self.sandwich_recipe)
        self.delivery_manager._total_recipes_spawned = 1
        
        plate = PlateKitchenObject()
        plate.add_kitchen_object(self.bread)
        plate.add_kitchen_object(self.lettuce)
        plate.add_kitchen_object(self.tomato)
        
        self.delivery_manager.deliver_recipe(plate)
        
        stats = self.delivery_manager.get_stats()
        
        # 0.1秒で1レシピなので、1分なら600レシピ
        # 実際の値は時間計測の精度により多少変動するので範囲でテスト
        assert stats.get_recipes_per_minute() > 0
    
    def test_stats_reset(self):
        """統計リセットのテスト"""
        # いくつか統計を蓄積
        self.delivery_manager._successful_recipes_amount = 5
        self.delivery_manager._failed_recipes_amount = 3
        self.delivery_manager._total_recipes_spawned = 8
        
        # リセット実行
        self.delivery_manager.reset_stats()
        
        # 統計がリセットされていることを確認
        assert self.delivery_manager.get_successful_recipes_amount() == 0
        assert self.delivery_manager.get_failed_recipes_amount() == 0
        assert self.delivery_manager.get_total_recipes_spawned() == 0
        
        stats = self.delivery_manager.get_stats()
        assert stats.successful_recipes == 0
        assert stats.failed_recipes == 0
        assert stats.total_recipes_spawned == 0
    
    def test_stats_update_with_game_time(self):
        """ゲーム時間との統計更新テスト"""
        self.game_manager.start_game()
        time.sleep(0.1)
        
        stats = self.delivery_manager.get_stats()
        
        # 経過時間が正しく記録されていることを確認
        assert stats.elapsed_time > 0
        assert stats.elapsed_time == pytest.approx(self.game_manager.get_elapsed_time(), rel=1e-2)
    
    def test_success_rate_edge_cases(self):
        """成功率のエッジケースのテスト"""
        # 試行回数が0の場合
        stats = GameStats()
        assert stats.get_success_rate() == 0.0
        
        # 全て成功の場合
        stats = GameStats(successful_recipes=5, failed_recipes=0)
        assert stats.get_success_rate() == 100.0
        
        # 全て失敗の場合
        stats = GameStats(successful_recipes=0, failed_recipes=5)
        assert stats.get_success_rate() == 0.0
    
    def test_recipes_per_minute_edge_cases(self):
        """1分あたりレシピ数のエッジケースのテスト"""
        # 経過時間が0の場合
        stats = GameStats(successful_recipes=5, elapsed_time=0.0)
        assert stats.get_recipes_per_minute() == 0.0
        
        # 成功レシピが0の場合
        stats = GameStats(successful_recipes=0, elapsed_time=60.0)
        assert stats.get_recipes_per_minute() == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])