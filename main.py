#!/usr/bin/env python3
"""
ポモドーロタイマー with ゲーミフィケーション

このアプリケーションは既存のキッチンゲームシステムと
新しいポモドーロタイマーのゲーミフィケーション機能を
統合したデモアプリケーションです。
"""

from pomodoro_system import PomodoroGameSystem
from deliverManager import KitchenGameManager
import sys

def main():
    """メインアプリケーション"""
    print("🍅 ポモドーロタイマー with ゲーミフィケーション")
    print("=" * 60)
    print()
    
    # ポモドーロシステムを初期化
    pomodoro_system = PomodoroGameSystem()
    
    # キッチンゲームマネージャーも利用可能
    kitchen_manager = KitchenGameManager.get_instance()
    
    print("✨ ゲーミフィケーション機能:")
    print("  🏆 経験値システム（完了したポモドーロに応じてXPとレベルアップ）")
    print("  🎖️ 達成バッジ（連続達成・回数実績など）")
    print("  📊 週間/月間統計（グラフ表示、完了率/平均集中時間等）")
    print("  🔥 ストリーク表示（連続日数カウント）")
    print()
    
    # 現在の状態を表示
    pomodoro_system.display_status()
    
    print("\n📋 使用方法:")
    print("詳細なデモを実行するには:")
    print("  python pomodoro_demo.py")
    print()
    print("自動デモを実行するには:")
    print("  python pomodoro_demo.py --auto")

if __name__ == "__main__":
    main()