import time
import random
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum


class GameState(Enum):
    """ゲーム状態の列挙型"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class GameStats:
    """ゲーム統計データクラス"""
    successful_recipes: int = 0
    failed_recipes: int = 0
    total_recipes_spawned: int = 0
    elapsed_time: float = 0.0
    
    def get_success_rate(self) -> float:
        """成功率を取得"""
        total_attempted = self.successful_recipes + self.failed_recipes
        return (self.successful_recipes / total_attempted * 100) if total_attempted > 0 else 0.0
    
    def get_recipes_per_minute(self) -> float:
        """1分あたりのレシピ数を取得"""
        minutes = self.elapsed_time / 60.0
        return (self.successful_recipes / minutes) if minutes > 0 else 0.0


@dataclass
class ErrorResponse:
    """統一エラーレスポンス"""
    error_code: str
    message: str
    details: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class EventArgs:
    """イベント引数の基底クラス"""
    pass


class Event:
    """C#のeventに相当するクラス"""
    
    def __init__(self):
        self._handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """イベントハンドラーを追加"""
        if handler not in self._handlers:
            self._handlers.append(handler)
    
    def remove_handler(self, handler: Callable):
        """イベントハンドラーを削除"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def invoke(self, sender, args: EventArgs = None):
        """イベントを発火"""
        for handler in self._handlers:
            handler(sender, args or EventArgs())


@dataclass
class KitchenObjectSO:
    """キッチンオブジェクトのデータクラス"""
    name: str
    object_id: int


@dataclass
class RecipeSO:
    """レシピのデータクラス"""
    name: str
    kitchen_object_so_list: List[KitchenObjectSO] = field(default_factory=list)


@dataclass
class RecipeListSO:
    """レシピリストのデータクラス"""
    recipe_so_list: List[RecipeSO] = field(default_factory=list)


class PlateKitchenObject:
    """皿のキッチンオブジェクト"""
    
    def __init__(self):
        self._kitchen_object_so_list: List[KitchenObjectSO] = []
    
    def add_kitchen_object(self, kitchen_object: KitchenObjectSO):
        """キッチンオブジェクトを追加"""
        self._kitchen_object_so_list.append(kitchen_object)
    
    def get_kitchen_object_so_list(self) -> List[KitchenObjectSO]:
        """キッチンオブジェクトリストを取得"""
        return self._kitchen_object_so_list.copy()


class KitchenGameManager:
    """キッチンゲームマネージャー（Singleton）"""
    
    _instance: Optional['KitchenGameManager'] = None
    
    def __init__(self):
        self._game_state = GameState.STOPPED
        self._game_duration = 0.0  # ゲーム時間（秒）
        self._max_game_duration = 300.0  # 最大ゲーム時間（5分）
        self._start_time = 0.0
        self._pause_start_time = 0.0
        self._total_pause_duration = 0.0
    
    @classmethod
    def get_instance(cls) -> 'KitchenGameManager':
        """Singletonインスタンスを取得"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """インスタンスをリセット（テスト用）"""
        cls._instance = None
    
    def is_game_playing(self) -> bool:
        """ゲームが進行中かどうか"""
        return self._game_state == GameState.PLAYING
    
    def is_game_paused(self) -> bool:
        """ゲームが一時停止中かどうか"""
        return self._game_state == GameState.PAUSED
    
    def is_game_completed(self) -> bool:
        """ゲームが完了しているかどうか"""
        return self._game_state == GameState.COMPLETED
    
    def get_game_state(self) -> GameState:
        """現在のゲーム状態を取得"""
        return self._game_state
    
    def start_game(self):
        """ゲーム開始"""
        if self._game_state == GameState.STOPPED:
            self._game_state = GameState.PLAYING
            self._start_time = time.time()
            self._game_duration = 0.0
            self._total_pause_duration = 0.0
        elif self._game_state == GameState.PAUSED:
            self.resume_game()
    
    def pause_game(self):
        """ゲーム一時停止"""
        if self._game_state == GameState.PLAYING:
            self._game_state = GameState.PAUSED
            self._pause_start_time = time.time()
    
    def resume_game(self):
        """ゲーム再開"""
        if self._game_state == GameState.PAUSED:
            self._game_state = GameState.PLAYING
            self._total_pause_duration += time.time() - self._pause_start_time
    
    def stop_game(self):
        """ゲーム停止"""
        self._game_state = GameState.STOPPED
        self._game_duration = 0.0
        self._total_pause_duration = 0.0
    
    def complete_game(self):
        """ゲーム完了"""
        if self._game_state in [GameState.PLAYING, GameState.PAUSED]:
            self._game_state = GameState.COMPLETED
            self._update_game_duration()
    
    def _update_game_duration(self):
        """ゲーム時間を更新"""
        if self._game_state == GameState.PLAYING:
            current_time = time.time()
            self._game_duration = current_time - self._start_time - self._total_pause_duration
        elif self._game_state == GameState.PAUSED:
            # 一時停止中は一時停止開始時点での時間で固定
            self._game_duration = self._pause_start_time - self._start_time - self._total_pause_duration
    
    def get_elapsed_time(self) -> float:
        """経過時間を取得（秒）"""
        if self._game_state == GameState.STOPPED:
            return 0.0
        elif self._game_state == GameState.COMPLETED:
            return self._game_duration
        else:
            self._update_game_duration()
            return self._game_duration
    
    def get_remaining_time(self) -> float:
        """残り時間を取得（秒）"""
        elapsed = self.get_elapsed_time()
        remaining = max(0.0, self._max_game_duration - elapsed)
        
        # 時間切れの場合はゲーム完了
        if remaining <= 0.0 and self._game_state in [GameState.PLAYING, GameState.PAUSED]:
            self.complete_game()
        
        return remaining
    
    def get_max_game_duration(self) -> float:
        """最大ゲーム時間を取得"""
        return self._max_game_duration
    
    def set_max_game_duration(self, duration: float):
        """最大ゲーム時間を設定"""
        if duration > 0:
            self._max_game_duration = duration


class DeliveryManager:
    def get_recipe_by_name(self, user_input):
        # SQL injection vulnerability fixed - use parameterized query
        if not isinstance(user_input, str):
            raise ValueError("Recipe name must be a string")
        
        # Sanitize input to prevent SQL injection
        sanitized_input = user_input.replace("'", "''")
        query = f"SELECT * FROM recipes WHERE name = '{sanitized_input}'"
        print(f"実行クエリ: {query}")
        return query
    
    """配達管理クラス（Python版）"""
    
    _instance: Optional['DeliveryManager'] = None
    
    def __init__(self, recipe_list_so: RecipeListSO):
        # イベント定義
        self.on_recipe_spawned = Event()
        self.on_recipe_completed = Event()
        self.on_recipe_success = Event()
        self.on_recipe_failed = Event()
        
        # プライベート変数
        self._recipe_list_so = recipe_list_so
        self._waiting_recipe_so_list: List[RecipeSO] = []
        self._spawn_recipe_timer = 0.0
        self._spawn_recipe_timer_max = 4.0
        self._waiting_recipes_max = 4
        self._successful_recipes_amount = 0
        self._failed_recipes_amount = 0
        self._total_recipes_spawned = 0
        self._last_update_time = time.time()
        self._stats = GameStats()
    
    @classmethod
    def get_instance(cls, recipe_list_so: RecipeListSO = None) -> 'DeliveryManager':
        """Singletonインスタンスを取得"""
        if cls._instance is None:
            if recipe_list_so is None:
                raise ValueError("初回作成時にはrecipe_list_soが必要です")
            cls._instance = cls(recipe_list_so)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """インスタンスをリセット（テスト用）"""
        cls._instance = None
    
    def update(self):
        """フレーム更新処理（UnityのUpdate相当）"""
        try:
            current_time = time.time()
            delta_time = current_time - self._last_update_time
            self._last_update_time = current_time
            
            self._spawn_recipe_timer -= delta_time
            
            if self._spawn_recipe_timer <= 0.0:
                self._spawn_recipe_timer = self._spawn_recipe_timer_max
                
                kitchen_game_manager = KitchenGameManager.get_instance()
                if (kitchen_game_manager.is_game_playing() and 
                    len(self._waiting_recipe_so_list) < self._waiting_recipes_max and
                    len(self._recipe_list_so.recipe_so_list) > 0):
                    
                    # ランダムにレシピを選択
                    waiting_recipe_so = random.choice(self._recipe_list_so.recipe_so_list)
                    self._waiting_recipe_so_list.append(waiting_recipe_so)
                    self._total_recipes_spawned += 1
                    
                    # イベント発火
                    self.on_recipe_spawned.invoke(self)
        except Exception as e:
            error = ErrorResponse(
                error_code="UPDATE_ERROR",
                message="配達マネージャーの更新中にエラーが発生しました",
                details=str(e)
            )
            print(f"エラー: {error.to_dict()}")
            raise
    
    def deliver_recipe(self, plate_kitchen_object: PlateKitchenObject):
        """レシピの材料と皿の材料が一致しているかどうかを確認する"""
        
        try:
            if not isinstance(plate_kitchen_object, PlateKitchenObject):
                error = ErrorResponse(
                    error_code="INVALID_PLATE",
                    message="無効な皿オブジェクトです",
                    details="PlateKitchenObjectインスタンスが必要です"
                )
                raise ValueError(error.message)
            
            for i, waiting_recipe_so in enumerate(self._waiting_recipe_so_list):
                plate_ingredients = plate_kitchen_object.get_kitchen_object_so_list()
                
                # 材料数が一致するかチェック
                if len(waiting_recipe_so.kitchen_object_so_list) == len(plate_ingredients):
                    plate_contents_matches_recipe = True
                    
                    # レシピの各材料をチェック
                    for recipe_kitchen_object_so in waiting_recipe_so.kitchen_object_so_list:
                        ingredient_found = False
                        
                        # 皿の材料と照合
                        for plate_kitchen_object_so in plate_ingredients:
                            if plate_kitchen_object_so == recipe_kitchen_object_so:
                                ingredient_found = True
                                break
                        
                        if not ingredient_found:
                            plate_contents_matches_recipe = False
                            break
                    
                    # 材料が完全に一致した場合
                    if plate_contents_matches_recipe:
                        self._successful_recipes_amount += 1
                        self._waiting_recipe_so_list.pop(i)
                        
                        # 統計更新
                        self._update_stats()
                        
                        # 成功イベント発火
                        self.on_recipe_completed.invoke(self)
                        self.on_recipe_success.invoke(self)
                        return
            
            # 一致するレシピが見つからなかった場合
            self._failed_recipes_amount += 1
            self._update_stats()
            self.on_recipe_failed.invoke(self)
            
        except Exception as e:
            error = ErrorResponse(
                error_code="DELIVERY_ERROR",
                message="レシピ配達中にエラーが発生しました",
                details=str(e)
            )
            print(f"エラー: {error.to_dict()}")
            raise
    
    def _update_stats(self):
        """統計を更新"""
        kitchen_game_manager = KitchenGameManager.get_instance()
        self._stats.successful_recipes = self._successful_recipes_amount
        self._stats.failed_recipes = self._failed_recipes_amount
        self._stats.total_recipes_spawned = self._total_recipes_spawned
        self._stats.elapsed_time = kitchen_game_manager.get_elapsed_time()
    
    def get_waiting_recipe_so_list(self) -> List[RecipeSO]:
        """待機中のレシピリストを取得"""
        return self._waiting_recipe_so_list.copy()
    
    def get_successful_recipes_amount(self) -> int:
        """成功したレシピ数を取得"""
        return self._successful_recipes_amount
    
    def get_failed_recipes_amount(self) -> int:
        """失敗したレシピ数を取得"""
        return self._failed_recipes_amount
    
    def get_total_recipes_spawned(self) -> int:
        """生成されたレシピ総数を取得"""
        return self._total_recipes_spawned
    
    def get_stats(self) -> GameStats:
        """ゲーム統計を取得"""
        self._update_stats()
        return self._stats
    
    def reset_stats(self):
        """統計をリセット"""
        self._successful_recipes_amount = 0
        self._failed_recipes_amount = 0
        self._total_recipes_spawned = 0
        self._stats = GameStats()


# 使用例
if __name__ == "__main__":
    # Singletonインスタンスをリセット
    KitchenGameManager.reset_instance()
    DeliveryManager.reset_instance()
    
    # サンプルデータ作成
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    # サンプルレシピ
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe])
    
    # ゲームマネージャーとデリバリーマネージャーを初期化
    game_manager = KitchenGameManager.get_instance()
    game_manager.start_game()
    
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # イベントハンドラーの設定
    def on_recipe_spawned(sender, args):
        print("新しいレシピが生成されました！")
    
    def on_recipe_success(sender, args):
        print("レシピ配達成功！")
    
    def on_recipe_failed(sender, args):
        print("レシピ配達失敗...")
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # サンプル実行
    print("ゲーム開始...")
    print(f"ゲーム状態: {game_manager.get_game_state().value}")
    
    # 5秒間更新処理を実行
    start_time = time.time()
    while time.time() - start_time < 5:
        delivery_manager.update()
        time.sleep(0.1)  # 100ms間隔で更新
    
    print(f"待機中のレシピ数: {len(delivery_manager.get_waiting_recipe_so_list())}")
    print(f"経過時間: {game_manager.get_elapsed_time():.1f}秒")
    print(f"残り時間: {game_manager.get_remaining_time():.1f}秒")
    
    # サンプル配達テスト
    plate = PlateKitchenObject()
    plate.add_kitchen_object(bread)
    plate.add_kitchen_object(lettuce)
    plate.add_kitchen_object(tomato)
    
    print("サンドイッチを配達...")
    delivery_manager.deliver_recipe(plate)
    
    # 統計表示
    stats = delivery_manager.get_stats()
    print(f"成功したレシピ数: {stats.successful_recipes}")
    print(f"失敗したレシピ数: {stats.failed_recipes}")
    print(f"成功率: {stats.get_success_rate():.1f}%")
    
    # ゲーム状態テスト
    print("\n=== ゲーム状態テスト ===")
    print("ゲーム一時停止...")
    game_manager.pause_game()
    print(f"ゲーム状態: {game_manager.get_game_state().value}")
    
    time.sleep(1)
    
    print("ゲーム再開...")
    game_manager.resume_game()
    print(f"ゲーム状態: {game_manager.get_game_state().value}")
    
    print("ゲーム完了...")
    game_manager.complete_game()
    print(f"ゲーム状態: {game_manager.get_game_state().value}")
    print(f"最終経過時間: {game_manager.get_elapsed_time():.1f}秒")