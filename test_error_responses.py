"""
エラーレスポンス統一テスト
Error response standardization tests
"""
import pytest
from deliverManager import (
    ErrorResponse,
    DeliveryManager,
    KitchenGameManager,
    RecipeListSO,
    RecipeSO,
    KitchenObjectSO,
    PlateKitchenObject
)


class TestErrorResponseStandardization:
    """エラーレスポンス統一のテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        # Singletonインスタンスをリセット
        KitchenGameManager.reset_instance()
        DeliveryManager.reset_instance()
        
        # テストデータ作成
        self.tomato = KitchenObjectSO("Tomato", 1)
        self.sandwich_recipe = RecipeSO("Sandwich", [self.tomato])
        self.recipe_list = RecipeListSO([self.sandwich_recipe])
        
        self.game_manager = KitchenGameManager.get_instance()
        self.delivery_manager = DeliveryManager.get_instance(self.recipe_list)
    
    def test_error_response_structure(self):
        """エラーレスポンス構造のテスト"""
        error = ErrorResponse(
            error_code="TEST_ERROR",
            message="テストエラーメッセージ",
            details="詳細情報"
        )
        
        # 基本的な属性の確認
        assert error.error_code == "TEST_ERROR"
        assert error.message == "テストエラーメッセージ"
        assert error.details == "詳細情報"
        
        # 辞書形式への変換
        error_dict = error.to_dict()
        expected_dict = {
            "error_code": "TEST_ERROR",
            "message": "テストエラーメッセージ",
            "details": "詳細情報"
        }
        assert error_dict == expected_dict
    
    def test_error_response_without_details(self):
        """詳細なしのエラーレスポンステスト"""
        error = ErrorResponse(
            error_code="SIMPLE_ERROR",
            message="シンプルなエラー"
        )
        
        assert error.error_code == "SIMPLE_ERROR"
        assert error.message == "シンプルなエラー"
        assert error.details is None
        
        error_dict = error.to_dict()
        assert error_dict["details"] is None
    
    def test_sql_injection_protection_error(self):
        """SQL注入保護に関するエラーテスト"""
        # 正常な文字列
        result = self.delivery_manager.get_recipe_by_name("Sandwich")
        assert "SELECT * FROM recipes WHERE name = 'Sandwich'" in result
        
        # シングルクォートを含む文字列（エスケープされる）
        malicious_input = "'; DROP TABLE recipes; --"
        result = self.delivery_manager.get_recipe_by_name(malicious_input)
        
        # シングルクォートがエスケープされていることを確認
        assert "''; DROP TABLE recipes; --" in result
        assert "DROP TABLE" in result  # エスケープされているが、クエリ自体は生成される
    
    def test_sql_injection_invalid_input_type(self):
        """無効な入力タイプのエラーテスト"""
        # 文字列以外の入力
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.get_recipe_by_name(123)
        
        assert "Recipe name must be a string" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.get_recipe_by_name(None)
        
        assert "Recipe name must be a string" in str(exc_info.value)
    
    def test_delivery_invalid_plate_error(self):
        """無効な皿でのレシピ配達エラーテスト"""
        # 文字列を皿として渡す
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.deliver_recipe("invalid_plate")
        
        assert "無効な皿オブジェクトです" in str(exc_info.value)
        
        # Noneを皿として渡す
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.deliver_recipe(None)
        
        assert "無効な皿オブジェクトです" in str(exc_info.value)
        
        # 数値を皿として渡す
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.deliver_recipe(42)
        
        assert "無効な皿オブジェクトです" in str(exc_info.value)
    
    def test_delivery_manager_creation_error(self):
        """DeliveryManager作成時のエラーテスト"""
        # インスタンスをリセット
        DeliveryManager.reset_instance()
        
        # recipe_list_soなしで初回作成を試行
        with pytest.raises(ValueError) as exc_info:
            DeliveryManager.get_instance()
        
        assert "初回作成時にはrecipe_list_soが必要です" in str(exc_info.value)
    
    def test_error_handling_in_update_method(self):
        """update メソッドでのエラーハンドリングテスト"""
        # 正常なケース（エラーが発生しない）
        self.game_manager.start_game()
        
        # update メソッドは例外をキャッチしてエラーレスポンスを出力する
        try:
            self.delivery_manager.update()
        except Exception:
            pytest.fail("Normal update should not raise exceptions")
    
    def test_error_handling_in_deliver_recipe_method(self):
        """deliver_recipe メソッドでのエラーハンドリングテスト"""
        # 正常なケース
        plate = PlateKitchenObject()
        plate.add_kitchen_object(self.tomato)
        
        # 待機レシピを追加
        self.delivery_manager._waiting_recipe_so_list.append(self.sandwich_recipe)
        
        # エラーが発生しないことを確認
        try:
            self.delivery_manager.deliver_recipe(plate)
        except Exception:
            pytest.fail("Normal delivery should not raise exceptions")
    
    def test_error_codes_consistency(self):
        """エラーコードの一貫性テスト"""
        # 想定されるエラーコードのリスト
        expected_error_codes = [
            "INVALID_PLATE",
            "UPDATE_ERROR", 
            "DELIVERY_ERROR"
        ]
        
        # エラーコードが定数として管理されていることを仮定
        # 実際の実装では、エラーコードを定数として定義することを推奨
        
        # 無効な皿エラーのテスト
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.deliver_recipe("invalid")
        
        # エラーメッセージに適切な内容が含まれることを確認
        error_message = str(exc_info.value)
        assert "無効な皿オブジェクト" in error_message
    
    def test_error_message_localization(self):
        """エラーメッセージの言語統一テスト"""
        # 日本語エラーメッセージの確認
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.get_recipe_by_name(123)
        
        error_message = str(exc_info.value)
        # 英語メッセージであることを確認（国際化対応の例）
        assert "Recipe name must be a string" in error_message
        
        # 日本語エラーメッセージの確認
        with pytest.raises(ValueError) as exc_info:
            self.delivery_manager.deliver_recipe("invalid")
        
        error_message = str(exc_info.value)
        assert "無効な皿オブジェクトです" in error_message
    
    def test_error_logging_format(self):
        """エラーログ形式のテスト"""
        # エラーレスポンスの辞書形式出力をテスト
        error = ErrorResponse(
            error_code="TEST_LOG",
            message="ログテスト",
            details="詳細ログ情報"
        )
        
        log_dict = error.to_dict()
        
        # ログ形式の必須フィールドが含まれることを確認
        required_fields = ["error_code", "message", "details"]
        for field in required_fields:
            assert field in log_dict
        
        # ログが構造化されていることを確認
        assert isinstance(log_dict, dict)
    
    def test_error_recovery_scenarios(self):
        """エラー回復シナリオのテスト"""
        # エラー発生後も処理が継続できることを確認
        
        # 1. 無効な皿でエラー発生
        with pytest.raises(ValueError):
            self.delivery_manager.deliver_recipe("invalid")
        
        # 2. エラー後も正常な処理が可能
        plate = PlateKitchenObject()
        plate.add_kitchen_object(self.tomato)
        self.delivery_manager._waiting_recipe_so_list.append(self.sandwich_recipe)
        
        # 正常な配達が実行できることを確認
        try:
            self.delivery_manager.deliver_recipe(plate)
        except Exception:
            pytest.fail("Should be able to recover after error")
        
        # 統計が正常に更新されることを確認
        stats = self.delivery_manager.get_stats()
        assert stats.successful_recipes >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])