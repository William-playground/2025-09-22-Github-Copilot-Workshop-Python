"""
統合テスト: start→pause→resume→complete→stats 更新
Integration tests for full workflow: start→pause→resume→complete→stats update
"""
import pytest
import time
from deliverManager import (
    KitchenGameManager,
    DeliveryManager,
    GameState,
    RecipeListSO,
    RecipeSO,
    KitchenObjectSO,
    PlateKitchenObject,
    ErrorResponse
)


class TestIntegrationWorkflow:
    """統合ワークフローのテストクラス"""
    
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
        self.game_manager.set_max_game_duration(30.0)  # テスト用に30秒
        self.delivery_manager = DeliveryManager.get_instance(self.recipe_list)
        
        # イベントカウンター
        self.spawned_count = 0
        self.success_count = 0
        self.failed_count = 0
        
        # イベントハンドラー設定
        def on_recipe_spawned(sender, args):
            self.spawned_count += 1
        
        def on_recipe_success(sender, args):
            self.success_count += 1
        
        def on_recipe_failed(sender, args):
            self.failed_count += 1
        
        self.delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
        self.delivery_manager.on_recipe_success.add_handler(on_recipe_success)
        self.delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    def test_full_workflow_with_success(self):
        """成功ケースでの完全ワークフローテスト"""
        # 1. ゲーム開始
        self.game_manager.start_game()
        assert self.game_manager.get_game_state() == GameState.PLAYING
        
        # 初期統計確認
        initial_stats = self.delivery_manager.get_stats()
        assert initial_stats.successful_recipes == 0
        assert initial_stats.failed_recipes == 0
        
        # 2. 少し実行してレシピをスポーン
        for _ in range(10):  # 最大1秒間更新
            self.delivery_manager.update()
            time.sleep(0.1)
            if len(self.delivery_manager.get_waiting_recipe_so_list()) > 0:
                break
        
        assert len(self.delivery_manager.get_waiting_recipe_so_list()) > 0
        assert self.spawned_count > 0
        
        # 3. ゲーム一時停止
        elapsed_before_pause = self.game_manager.get_elapsed_time()
        self.game_manager.pause_game()
        assert self.game_manager.get_game_state() == GameState.PAUSED
        
        # 一時停止中に時間経過
        time.sleep(0.2)
        
        # 一時停止中は経過時間が進まない
        elapsed_during_pause = self.game_manager.get_elapsed_time()
        assert elapsed_during_pause == pytest.approx(elapsed_before_pause, rel=1e-2)
        
        # 4. ゲーム再開
        self.game_manager.resume_game()
        assert self.game_manager.get_game_state() == GameState.PLAYING
        
        # 5. レシピ配達（成功）
        waiting_recipes = self.delivery_manager.get_waiting_recipe_so_list()
        first_recipe = waiting_recipes[0]
        
        plate = PlateKitchenObject()
        for ingredient in first_recipe.kitchen_object_so_list:
            plate.add_kitchen_object(ingredient)
        
        self.delivery_manager.deliver_recipe(plate)
        
        # 成功イベントとスタッツの確認
        assert self.success_count == 1
        assert self.failed_count == 0
        
        mid_stats = self.delivery_manager.get_stats()
        assert mid_stats.successful_recipes == 1
        assert mid_stats.failed_recipes == 0
        
        # 6. ゲーム完了
        self.game_manager.complete_game()
        assert self.game_manager.get_game_state() == GameState.COMPLETED
        
        # 7. 最終統計確認
        final_stats = self.delivery_manager.get_stats()
        assert final_stats.successful_recipes == 1
        assert final_stats.failed_recipes == 0
        assert final_stats.get_success_rate() == 100.0
        assert final_stats.elapsed_time > 0
        assert final_stats.elapsed_time < 30.0  # 最大時間未満
    
    def test_full_workflow_with_failure(self):
        """失敗ケースでの完全ワークフローテスト"""
        # ゲーム開始
        self.game_manager.start_game()
        
        # レシピ手動追加
        self.delivery_manager._waiting_recipe_so_list.append(self.sandwich_recipe)
        self.delivery_manager._total_recipes_spawned = 1
        
        # 間違った配達
        plate = PlateKitchenObject()
        plate.add_kitchen_object(self.lettuce)  # 不完全な材料
        
        self.delivery_manager.deliver_recipe(plate)
        
        # 失敗イベントとスタッツの確認
        assert self.success_count == 0
        assert self.failed_count == 1
        
        stats = self.delivery_manager.get_stats()
        assert stats.successful_recipes == 0
        assert stats.failed_recipes == 1
        assert stats.get_success_rate() == 0.0
        
        # ゲーム完了
        self.game_manager.complete_game()
        
        final_stats = self.delivery_manager.get_stats()
        assert final_stats.failed_recipes == 1
    
    def test_multiple_pause_resume_cycles(self):
        """複数回の一時停止・再開サイクルテスト"""
        self.game_manager.start_game()
        
        total_play_time = 0.0
        pause_times = []
        
        # 複数回の一時停止・再開
        for i in range(3):
            # プレイ
            play_start = time.time()
            time.sleep(0.1)
            play_end = time.time()
            total_play_time += (play_end - play_start)
            
            # 一時停止
            self.game_manager.pause_game()
            pause_start = time.time()
            time.sleep(0.05)  # 一時停止時間
            pause_end = time.time()
            pause_times.append(pause_end - pause_start)
            
            # 再開
            self.game_manager.resume_game()
        
        # 最終的なプレイ時間
        time.sleep(0.1)
        total_play_time += 0.1
        
        elapsed = self.game_manager.get_elapsed_time()
        
        # 一時停止時間は除外されていることを確認
        assert elapsed == pytest.approx(total_play_time, rel=1e-1)
        assert elapsed < total_play_time + sum(pause_times)
    
    def test_time_up_completion(self):
        """時間切れによる自動完了テスト"""
        # 短い制限時間を設定
        self.game_manager.set_max_game_duration(0.3)
        
        self.game_manager.start_game()
        
        # 制限時間を超過するまで待機
        time.sleep(0.4)
        
        # 残り時間確認で自動完了がトリガーされる
        remaining = self.game_manager.get_remaining_time()
        
        assert remaining == 0.0
        assert self.game_manager.get_game_state() == GameState.COMPLETED
    
    def test_error_handling_during_workflow(self):
        """ワークフロー中のエラーハンドリングテスト"""
        self.game_manager.start_game()
        
        # 無効な皿でレシピ配達を試行
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.deliver_recipe("invalid_plate")
        
        assert "無効な皿オブジェクトです" in str(exc_info.value)
        
        # エラー後もゲーム状態は維持される
        assert self.game_manager.get_game_state() == GameState.PLAYING
    
    def test_stats_consistency_throughout_workflow(self):
        """ワークフロー全体での統計一貫性テスト"""
        self.game_manager.start_game()
        
        # 複数のレシピ操作
        operations = [
            (True, self.sandwich_recipe),   # 成功
            (False, self.salad_recipe),     # 失敗
            (True, self.salad_recipe),      # 成功
            (False, self.sandwich_recipe),  # 失敗
        ]
        
        expected_success = 0
        expected_failure = 0
        
        for should_succeed, recipe in operations:
            # レシピを待機リストに追加
            self.delivery_manager._waiting_recipe_so_list.append(recipe)
            self.delivery_manager._total_recipes_spawned += 1
            
            # 皿を準備
            plate = PlateKitchenObject()
            if should_succeed:
                # 正しい材料
                for ingredient in recipe.kitchen_object_so_list:
                    plate.add_kitchen_object(ingredient)
                expected_success += 1
            else:
                # 間違った材料（空の皿）
                expected_failure += 1
            
            # 配達実行
            self.delivery_manager.deliver_recipe(plate)
            
            # 中間統計確認
            stats = self.delivery_manager.get_stats()
            assert stats.successful_recipes == expected_success
            assert stats.failed_recipes == expected_failure
        
        # 最終統計確認
        self.game_manager.complete_game()
        final_stats = self.delivery_manager.get_stats()
        
        assert final_stats.successful_recipes == expected_success
        assert final_stats.failed_recipes == expected_failure
        assert final_stats.total_recipes_spawned == len(operations)
        assert final_stats.get_success_rate() == 50.0  # 2/4 = 50%
    
    def test_singleton_consistency_during_workflow(self):
        """ワークフロー中のSingleton一貫性テスト"""
        # 異なる参照で同じインスタンスを取得
        game_manager_ref1 = KitchenGameManager.get_instance()
        game_manager_ref2 = KitchenGameManager.get_instance()
        
        delivery_manager_ref1 = DeliveryManager.get_instance(self.recipe_list)
        delivery_manager_ref2 = DeliveryManager.get_instance()
        
        assert game_manager_ref1 is game_manager_ref2
        assert delivery_manager_ref1 is delivery_manager_ref2
        
        # 一方で操作すると他方にも反映される
        game_manager_ref1.start_game()
        assert game_manager_ref2.is_game_playing()
        
        game_manager_ref2.pause_game()
        assert game_manager_ref1.is_game_paused()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])